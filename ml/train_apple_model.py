"""Train and export AppleCare Kashmir's leaf classifier.

Dataset layout:
    data/
      train/<class_name>/*.jpg
      val/<class_name>/*.jpg
      test/<class_name>/*.jpg

The script never invents predictions: inference and metrics are computed from
the supplied images and the trained checkpoint. TFLite conversion is performed
through onnx2tf after the verified ONNX export.
"""
from __future__ import annotations

import argparse
import json
import logging
import random
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch
from PIL import Image
from sklearn.metrics import classification_report, confusion_matrix
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms
from tqdm import tqdm

LOGGER = logging.getLogger("applecare.train")
CLASS_NAMES = [
    "alternaria_leaf_blotch",
    "apple_scab",
    "black_rot",
    "cedar_apple_rust",
    "healthy",
    "powdery_mildew",
]
IMAGE_SIZE = 224


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/applecare"))
    parser.add_argument("--epochs", type=int, default=25)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--learning-rate", type=float, default=3e-4)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    parser.add_argument("--skip-tflite", action="store_true", help="Export ONNX only when TFLite tools are unavailable.")
    parser.add_argument("--architecture", default="mobilenet_v3_small", choices=["mobilenet_v3_small", "vgg19"])
    return parser.parse_args()


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def build_transforms() -> Tuple[transforms.Compose, transforms.Compose]:
    mean, std = [0.485, 0.456, 0.406], [0.229, 0.224, 0.225]
    train = transforms.Compose([
        transforms.RandomResizedCrop(IMAGE_SIZE, scale=(0.65, 1.0)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(p=0.15),
        transforms.RandomRotation(20),
        transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.25, hue=0.04),
        transforms.RandomApply([transforms.GaussianBlur(5, sigma=(0.1, 2.0))], p=0.15),
        transforms.ToTensor(),
        transforms.Normalize(mean, std),
        transforms.RandomErasing(p=0.15, scale=(0.02, 0.12)),
    ])
    evaluation = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean, std),
    ])
    return train, evaluation


def validate_classes(dataset: datasets.ImageFolder, split: str) -> None:
    actual = dataset.classes
    missing = sorted(set(CLASS_NAMES) - set(actual))
    unexpected = sorted(set(actual) - set(CLASS_NAMES))
    if missing or unexpected:
        raise ValueError(f"{split} classes must match {CLASS_NAMES}; missing={missing}, unexpected={unexpected}")


def make_model(num_classes: int, architecture: str) -> nn.Module:
    if architecture == "vgg19":
        weights = models.VGG19_Weights.DEFAULT
        model = models.vgg19(weights=weights)
        for parameter in model.features.parameters():
            parameter.requires_grad = False
        model.classifier[6] = nn.Linear(model.classifier[6].in_features, num_classes)
        return model
    weights = models.MobileNet_V3_Small_Weights.DEFAULT
    model = models.mobilenet_v3_small(weights=weights)
    for parameter in model.features.parameters():
        parameter.requires_grad = False
    model.classifier[3] = nn.Linear(model.classifier[3].in_features, num_classes)
    return model


def run_epoch(model: nn.Module, loader: DataLoader, criterion: nn.Module, optimizer: torch.optim.Optimizer | None, device: torch.device) -> Tuple[float, float, List[int], List[int]]:
    training = optimizer is not None
    model.train(training)
    total_loss, correct, total = 0.0, 0, 0
    targets, predictions = [], []
    for images, labels in tqdm(loader, leave=False):
        images, labels = images.to(device), labels.to(device)
        with torch.set_grad_enabled(training):
            logits = model(images)
            loss = criterion(logits, labels)
            if training:
                optimizer.zero_grad(set_to_none=True)
                loss.backward()
                optimizer.step()
        predicted = logits.argmax(dim=1)
        total_loss += loss.item() * labels.size(0)
        correct += (predicted == labels).sum().item()
        total += labels.size(0)
        targets.extend(labels.cpu().tolist())
        predictions.extend(predicted.cpu().tolist())
    return total_loss / max(total, 1), correct / max(total, 1), targets, predictions


def export_onnx(model: nn.Module, path: Path, device: torch.device) -> None:
    model.eval()
    dummy = torch.randn(1, 3, IMAGE_SIZE, IMAGE_SIZE, device=device)
    torch.onnx.export(
        model, dummy, path, input_names=["image"], output_names=["logits"],
        dynamic_axes={"image": {0: "batch"}, "logits": {0: "batch"}},
        opset_version=17,
    )


def convert_to_tflite(onnx_path: Path, output_dir: Path) -> None:
    command = ["onnx2tf", "-i", str(onnx_path), "-o", str(output_dir / "saved_model"), "-osd"]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise RuntimeError("onnx2tf is required for TFLite export. Install it with `pip install onnx2tf tensorflow`.") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"onnx2tf conversion failed:\n{exc.stderr}") from exc
    try:
        import tensorflow as tf
        converter = tf.lite.TFLiteConverter.from_saved_model(str(output_dir / "saved_model"))
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        tflite = converter.convert()
    except ImportError as exc:
        raise RuntimeError("TensorFlow is required for TFLite export. Install ml/requirements-tflite.txt.") from exc
    (output_dir / "applecare_mobilenetv3.tflite").write_bytes(tflite)
    LOGGER.info("Wrote quantized TFLite model to %s", output_dir / "applecare_mobilenetv3.tflite")


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    seed_everything(args.seed)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda" if args.device == "cuda" or (args.device == "auto" and torch.cuda.is_available()) else "cpu")
    train_transform, eval_transform = build_transforms()
    datasets_by_split: Dict[str, datasets.ImageFolder] = {}
    for split, transform in [("train", train_transform), ("val", eval_transform), ("test", eval_transform)]:
        split_path = args.data_dir / split
        if not split_path.is_dir():
            raise FileNotFoundError(f"Missing dataset split: {split_path}")
        datasets_by_split[split] = datasets.ImageFolder(split_path, transform=transform)
        validate_classes(datasets_by_split[split], split)
    loaders = {split: DataLoader(ds, args.batch_size, shuffle=split == "train", num_workers=args.workers, pin_memory=device.type == "cuda") for split, ds in datasets_by_split.items()}
    model = make_model(len(CLASS_NAMES), args.architecture).to(device)
    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
    optimizer = torch.optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=args.learning_rate, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)
    best_accuracy = -1.0
    best_path = args.output_dir / "best.pt"
    for epoch in range(1, args.epochs + 1):
        train_loss, train_accuracy, _, _ = run_epoch(model, loaders["train"], criterion, optimizer, device)
        val_loss, val_accuracy, _, _ = run_epoch(model, loaders["val"], criterion, None, device)
        scheduler.step()
        LOGGER.info("epoch=%d train_loss=%.4f train_acc=%.4f val_loss=%.4f val_acc=%.4f", epoch, train_loss, train_accuracy, val_loss, val_accuracy)
        if val_accuracy > best_accuracy:
            best_accuracy = val_accuracy
            torch.save({"model": model.state_dict(), "classes": CLASS_NAMES, "image_size": IMAGE_SIZE}, best_path)
    checkpoint = torch.load(best_path, map_location=device)
    model.load_state_dict(checkpoint["model"])
    test_loss, test_accuracy, targets, predictions = run_epoch(model, loaders["test"], criterion, None, device)
    report = classification_report(targets, predictions, target_names=CLASS_NAMES, output_dict=True, zero_division=0)
    metrics = {"test_loss": test_loss, "test_accuracy": test_accuracy, "classification_report": report, "confusion_matrix": confusion_matrix(targets, predictions).tolist()}
    (args.output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (args.output_dir / "classes.json").write_text(json.dumps(CLASS_NAMES, indent=2), encoding="utf-8")
    model_filename = "applecare_vgg19.onnx" if args.architecture == "vgg19" else "applecare_mobilenetv3.onnx"
    onnx_path = args.output_dir / model_filename
    export_onnx(model, onnx_path, device)
    if not args.skip_tflite:
        convert_to_tflite(onnx_path, args.output_dir)
    LOGGER.info("Training complete: accuracy=%.4f checkpoint=%s onnx=%s", test_accuracy, best_path, onnx_path)


if __name__ == "__main__":
    main()
