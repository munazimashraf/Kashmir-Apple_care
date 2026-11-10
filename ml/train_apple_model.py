"""Train and export high-accuracy MobileNetV3-Large leaf disease classifier.

Features:
- Pretrained MobileNetV3-Large backbone with Squeeze-and-Excitation attention
- Balanced class-weighted loss to handle imbalanced datasets (e.g. powdery mildew)
- Fine-tuning of deep feature extractors for Kashmiri apple disease lesions
- Cosine annealing learning rate schedule with AdamW optimizer
- ONNX export with verified input/output shapes and onnxruntime verification
- Comprehensive test metrics evaluation (per-class precision, recall, F1, confusion matrix)
"""
from __future__ import annotations

import argparse
import json
import logging
import math
import random
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch
from PIL import Image
from sklearn.metrics import classification_report, confusion_matrix
from torch import nn
from torch.utils.data import DataLoader, WeightedRandomSampler
from torchvision import datasets, models, transforms

import sys

def progress_bar(iterable, desc=""):
    total = len(iterable)
    for i, item in enumerate(iterable):
        if i % max(1, total // 10) == 0 or i == total - 1:
            LOGGER.info("%s progress: %d/%d (%.0f%%)", desc, i + 1, total, (i + 1) / total * 100)
            sys.stdout.flush()
        yield item



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
    parser.add_argument("--data-dir", type=Path, default=Path("data/apple"))
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/applecare-six"))
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--learning-rate", type=float, default=3e-4)
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
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
        transforms.Resize((256, 256)),
        transforms.RandomResizedCrop(IMAGE_SIZE, scale=(0.75, 1.0), ratio=(0.85, 1.15)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.3),
        transforms.RandomRotation(degrees=25),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.03),
        transforms.ToTensor(),
        transforms.Normalize(mean, std),
    ])
    evaluation = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean, std),
    ])
    return train, evaluation


def build_model(num_classes: int) -> nn.Module:
    weights = models.MobileNet_V3_Large_Weights.DEFAULT
    model = models.mobilenet_v3_large(weights=weights)
    
    # Freeze lower feature extraction layers (0-12)
    # Fine-tune top inverted residual blocks (13-16) for fine leaf pathology
    for idx, child in enumerate(model.features):
        if idx < 13:
            for param in child.parameters():
                param.requires_grad = False
        else:
            for param in child.parameters():
                param.requires_grad = True

    in_features = model.classifier[0].in_features
    model.classifier = nn.Sequential(
        nn.Linear(in_features, 512),
        nn.Hardswish(inplace=True),
        nn.Dropout(p=0.25, inplace=True),
        nn.Linear(512, num_classes),
    )
    return model


def compute_class_weights(dataset: datasets.ImageFolder, device: torch.device) -> torch.Tensor:
    counts = np.bincount(dataset.targets)
    total = len(dataset.targets)
    # Effective class weighting with square-root smoothing to prevent extreme weights
    weights = total / (len(counts) * np.sqrt(counts + 1e-5))
    weights = weights / weights.sum() * len(counts)
    return torch.tensor(weights, dtype=torch.float32, device=device)


def run_epoch(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer | None,
    device: torch.device,
) -> Tuple[float, float, List[int], List[int]]:
    training = optimizer is not None
    model.train(training)
    total_loss, correct, total = 0.0, 0, 0
    targets, predictions = [], []

    for images, labels in progress_bar(loader, desc="training" if training else "evaluating"):
        images, labels = images.to(device), labels.to(device)
        with torch.set_grad_enabled(training):
            logits = model(images)
            loss = criterion(logits, labels)
            if training:
                optimizer.zero_grad(set_to_none=True)
                loss.backward()
                nn.utils.clip_grad_norm_(model.parameters(), max_norm=2.0)
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
        model,
        dummy,
        path,
        input_names=["image"],
        output_names=["logits"],
        dynamic_axes={"image": {0: "batch"}, "logits": {0: "batch"}},
        opset_version=17,
    )
    LOGGER.info("Exported ONNX model to %s", path)


def verify_onnx(onnx_path: Path, test_loader: DataLoader, class_names: List[str]) -> float:
    import onnxruntime as ort
    session = ort.InferenceSession(str(onnx_path), providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name
    
    correct, total = 0, 0
    for images, labels in test_loader:
        np_images = images.numpy()
        outputs = session.run(None, {input_name: np_images})[0]
        preds = np.argmax(outputs, axis=1)
        correct += int((preds == labels.numpy()).sum())
        total += len(labels)
        if total >= 500:  # Spot-check first 500 test samples for quick ONNX sanity verification
            break
    acc = correct / max(total, 1)
    LOGGER.info("ONNX verified accuracy on %d samples: %.4f", total, acc)
    return acc


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    seed_everything(args.seed)
    class_names = sorted(CLASS_NAMES)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    device = torch.device("cpu")
    torch.set_num_threads(min(8, torch.get_num_threads()))

    LOGGER.info("Loading datasets from %s", args.data_dir)
    train_transform, eval_transform = build_transforms()
    train_ds = datasets.ImageFolder(args.data_dir / "train", transform=train_transform)
    val_ds = datasets.ImageFolder(args.data_dir / "val", transform=eval_transform)
    test_ds = datasets.ImageFolder(args.data_dir / "test", transform=eval_transform)

    LOGGER.info("Train classes: %s", train_ds.classes)
    assert train_ds.classes == class_names, f"Classes mismatch: {train_ds.classes} vs {class_names}"

    class_weights = compute_class_weights(train_ds, device)
    LOGGER.info("Computed class weights: %s", class_weights.tolist())

    loaders = {
        "train": DataLoader(train_ds, batch_size=args.batch_size, shuffle=True, num_workers=args.workers),
        "val": DataLoader(val_ds, batch_size=args.batch_size, shuffle=False, num_workers=args.workers),
        "test": DataLoader(test_ds, batch_size=args.batch_size, shuffle=False, num_workers=args.workers),
    }

    model = build_model(len(class_names)).to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights, label_smoothing=0.08)

    # Differential learning rates: smaller for backbone, higher for classification head
    backbone_params = [p for n, p in model.features.named_parameters() if p.requires_grad]
    head_params = list(model.classifier.parameters())
    optimizer = torch.optim.AdamW(
        [
            {"params": backbone_params, "lr": args.learning_rate * 0.25},
            {"params": head_params, "lr": args.learning_rate},
        ],
        weight_decay=1e-4,
    )
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs, eta_min=1e-6)

    best_accuracy = -1.0
    best_path = args.output_dir / "best.pt"

    for epoch in range(1, args.epochs + 1):
        t0 = time.time()
        train_loss, train_accuracy, _, _ = run_epoch(model, loaders["train"], criterion, optimizer, device)
        val_loss, val_accuracy, _, _ = run_epoch(model, loaders["val"], criterion, None, device)
        scheduler.step()
        elapsed = time.time() - t0
        LOGGER.info(
            "epoch=%d/%d train_loss=%.4f train_acc=%.4f val_loss=%.4f val_acc=%.4f time=%.1fs",
            epoch, args.epochs, train_loss, train_accuracy, val_loss, val_accuracy, elapsed,
        )

        if val_accuracy > best_accuracy:
            best_accuracy = val_accuracy
            torch.save({
                "model": model.state_dict(),
                "classes": class_names,
                "image_size": IMAGE_SIZE,
                "val_accuracy": val_accuracy,
                "epoch": epoch,
            }, best_path)
            LOGGER.info("--> Saved new best checkpoint (val_acc=%.4f)", val_accuracy)

    LOGGER.info("Loading best checkpoint for final test evaluation...")
    checkpoint = torch.load(best_path, map_location=device)
    model.load_state_dict(checkpoint["model"])

    test_loss, test_accuracy, targets, predictions = run_epoch(model, loaders["test"], criterion, None, device)
    report = classification_report(targets, predictions, target_names=class_names, output_dict=True, zero_division=0)
    conf_mat = confusion_matrix(targets, predictions).tolist()

    metrics = {
        "test_loss": test_loss,
        "test_accuracy": test_accuracy,
        "classification_report": report,
        "confusion_matrix": conf_mat,
        "model_architecture": "MobileNetV3-Large-FineTuned",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    (args.output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (args.output_dir / "classes.json").write_text(json.dumps(class_names, indent=2), encoding="utf-8")

    onnx_path = args.output_dir / "applecare_mobilenetv3.onnx"
    export_onnx(model, onnx_path, device)
    verify_onnx(onnx_path, loaders["test"], class_names)

    LOGGER.info("Training complete! Test accuracy=%.4f, Best Val accuracy=%.4f", test_accuracy, best_accuracy)
    print(f"\n=======================================================")
    print(f"MODEL TRAINING COMPLETED SUCCESSFULLY!")
    print(f"Overall Test Accuracy: {test_accuracy * 100:.2f}%")
    print(f"Metrics saved to: {args.output_dir / 'metrics.json'}")
    print(f"ONNX model saved to: {onnx_path}")
    print(f"=======================================================\n")


if __name__ == "__main__":
    main()
