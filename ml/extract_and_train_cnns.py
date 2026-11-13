"""Step 1: Deep Feature Extraction and Training for VGG-16, VGG-19, and ResNet-50.

Extracts deep convolutional embeddings from pretrained backbones and trains
classification heads for Kashmiri apple diseases.
Saves all extracted features and CNN probability distributions to artifacts/ensemble/extracted_features.npz
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import random
import time
from pathlib import Path
from typing import Dict, List, Tuple, Any

import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from torchvision import models, transforms

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
LOGGER = logging.getLogger("applecare.cnn_extractor")

CLASSES = [
    "alternaria_leaf_blotch",
    "apple_scab",
    "black_rot",
    "cedar_apple_rust",
    "healthy",
    "powdery_mildew",
]


def seed_everything(seed: int = 42) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)


def get_stratified_subset(
    data_dir: Path,
    samples_per_class: int,
    seed: int = 42,
) -> List[Tuple[Path, int]]:
    rng = random.Random(seed)
    selected = []
    for class_idx, class_name in enumerate(sorted(CLASSES)):
        class_dir = data_dir / class_name
        if not class_dir.exists():
            continue
        all_imgs = sorted([
            p for p in class_dir.iterdir()
            if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"} and not p.name.startswith(".")
        ])
        rng.shuffle(all_imgs)
        chosen = all_imgs[:samples_per_class]
        for img_path in chosen:
            selected.append((img_path, class_idx))
    return selected


class PreloadedDataset(torch.utils.data.Dataset):
    def __init__(self, samples: List[Tuple[Path, int]], transform: transforms.Compose):
        self.samples = samples
        self.transform = transform

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        path, label = self.samples[idx]
        with Image.open(path) as img:
            img = img.convert("RGB")
            tensor = self.transform(img)
        return tensor, label


def build_feature_extractors() -> Tuple[nn.Module, nn.Module, nn.Module]:
    LOGGER.info("Loading pretrained backbones: ResNet-50, VGG-16, VGG-19...")
    r50 = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
    r50_extractor = nn.Sequential(*list(r50.children())[:-1], nn.Flatten()).eval()

    v16 = models.vgg16(weights=models.VGG16_Weights.DEFAULT)
    v16_extractor = nn.Sequential(v16.features, nn.AdaptiveAvgPool2d((1, 1)), nn.Flatten()).eval()

    v19 = models.vgg19(weights=models.VGG19_Weights.DEFAULT)
    v19_extractor = nn.Sequential(v19.features, nn.AdaptiveAvgPool2d((1, 1)), nn.Flatten()).eval()

    return r50_extractor, v16_extractor, v19_extractor


def extract_all_features(
    loader: torch.utils.data.DataLoader,
    r50_net: nn.Module,
    v16_net: nn.Module,
    v19_net: nn.Module,
    desc: str = "dataset",
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    feats_r50, feats_v16, feats_v19, labels_list = [], [], [], []
    total_batches = len(loader)

    LOGGER.info("Extracting features for %s (%d batches)...", desc, total_batches)
    t0 = time.time()

    with torch.no_grad():
        for b_idx, (imgs, lbls) in enumerate(loader):
            f_r50 = r50_net(imgs).cpu().numpy()
            f_v16 = v16_net(imgs).cpu().numpy()
            f_v19 = v19_net(imgs).cpu().numpy()

            feats_r50.append(f_r50)
            feats_v16.append(f_v16)
            feats_v19.append(f_v19)
            labels_list.append(lbls.numpy())

            if (b_idx + 1) % max(1, total_batches // 4) == 0 or b_idx == total_batches - 1:
                elapsed = time.time() - t0
                LOGGER.info("  [%s] batch %d/%d (%.1f%%) in %.1fs", desc, b_idx + 1, total_batches, (b_idx + 1) / total_batches * 100, elapsed)

    X_r50 = np.concatenate(feats_r50, axis=0)
    X_v16 = np.concatenate(feats_v16, axis=0)
    X_v19 = np.concatenate(feats_v19, axis=0)
    y = np.concatenate(labels_list, axis=0)

    LOGGER.info("Extracted %s: ResNet-50=%s, VGG-16=%s, VGG-19=%s, Targets=%s", desc, X_r50.shape, X_v16.shape, X_v19.shape, y.shape)
    return X_r50, X_v16, X_v19, y


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data/apple"))
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/ensemble"))
    parser.add_argument("--train-per-class", type=int, default=35)
    parser.add_argument("--val-per-class", type=int, default=12)
    parser.add_argument("--test-per-class", type=int, default=18)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    seed_everything(args.seed)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    # 1. Stratified sampling
    train_samples = get_stratified_subset(args.data_dir / "train", args.train_per_class, seed=args.seed)
    val_samples = get_stratified_subset(args.data_dir / "val", args.val_per_class, seed=args.seed)
    test_samples = get_stratified_subset(args.data_dir / "test", args.test_per_class, seed=args.seed)

    LOGGER.info("Stratified samples: train=%d, val=%d, test=%d", len(train_samples), len(val_samples), len(test_samples))

    # DataLoaders (workers=0 for macOS sandbox safety)
    train_loader = torch.utils.data.DataLoader(PreloadedDataset(train_samples, transform), batch_size=32, shuffle=False, num_workers=0)
    val_loader = torch.utils.data.DataLoader(PreloadedDataset(val_samples, transform), batch_size=32, shuffle=False, num_workers=0)
    test_loader = torch.utils.data.DataLoader(PreloadedDataset(test_samples, transform), batch_size=32, shuffle=False, num_workers=0)

    # 2. Extract deep features
    r50_net, v16_net, v19_net = build_feature_extractors()
    X_train_r50, X_train_v16, X_train_v19, y_train = extract_all_features(train_loader, r50_net, v16_net, v19_net, "train")
    X_val_r50, X_val_v16, X_val_v19, y_val = extract_all_features(val_loader, r50_net, v16_net, v19_net, "val")
    X_test_r50, X_test_v16, X_test_v19, y_test = extract_all_features(test_loader, r50_net, v16_net, v19_net, "test")

    # 3. Train VGG-16 Classifier
    LOGGER.info("Training VGG-16 Classifier Head...")
    clf_v16 = LogisticRegression(C=1.0, max_iter=1000, random_state=args.seed, solver="lbfgs")
    t0 = time.time()
    clf_v16.fit(X_train_v16, y_train)
    p_train_v16 = clf_v16.predict_proba(X_train_v16)
    p_val_v16 = clf_v16.predict_proba(X_val_v16)
    t_inf = time.time()
    p_test_v16 = clf_v16.predict_proba(X_test_v16)
    v16_lat_ms = (time.time() - t_inf) / len(X_test_v16) * 1000.0

    # 4. Train VGG-19 Classifier
    LOGGER.info("Training VGG-19 Classifier Head...")
    clf_v19 = LogisticRegression(C=1.0, max_iter=1000, random_state=args.seed, solver="lbfgs")
    clf_v19.fit(X_train_v19, y_train)
    p_train_v19 = clf_v19.predict_proba(X_train_v19)
    p_val_v19 = clf_v19.predict_proba(X_val_v19)
    t_inf = time.time()
    p_test_v19 = clf_v19.predict_proba(X_test_v19)
    v19_lat_ms = (time.time() - t_inf) / len(X_test_v19) * 1000.0

    # 5. Train ResNet-50 Classifier
    LOGGER.info("Training ResNet-50 Classifier Head...")
    clf_r50 = LogisticRegression(C=1.0, max_iter=1000, random_state=args.seed, solver="lbfgs")
    clf_r50.fit(X_train_r50, y_train)
    p_train_r50 = clf_r50.predict_proba(X_train_r50)
    p_val_r50 = clf_r50.predict_proba(X_val_r50)
    t_inf = time.time()
    p_test_r50 = clf_r50.predict_proba(X_test_r50)
    r50_lat_ms = (time.time() - t_inf) / len(X_test_r50) * 1000.0

    # Save all features & probabilities to NPZ
    npz_path = args.output_dir / "extracted_features.npz"
    np.savez_compressed(
        npz_path,
        X_train_r50=X_train_r50, X_train_v16=X_train_v16, X_train_v19=X_train_v19, y_train=y_train,
        X_val_r50=X_val_r50, X_val_v16=X_val_v16, X_val_v19=X_val_v19, y_val=y_val,
        X_test_r50=X_test_r50, X_test_v16=X_test_v16, X_test_v19=X_test_v19, y_test=y_test,
        p_train_r50=p_train_r50, p_train_v16=p_train_v16, p_train_v19=p_train_v19,
        p_val_r50=p_val_r50, p_val_v16=p_val_v16, p_val_v19=p_val_v19,
        p_test_r50=p_test_r50, p_test_v16=p_test_v16, p_test_v19=p_test_v19,
    )
    LOGGER.info("Saved extracted features and CNN probabilities to %s", npz_path)

    # Save CNN info
    cnn_info = {
        "classes": CLASSES,
        "latencies_ms": {
            "VGG-16": v16_lat_ms,
            "VGG-19": v19_lat_ms,
            "ResNet-50": r50_lat_ms,
        },
    }
    (args.output_dir / "cnn_info.json").write_text(json.dumps(cnn_info, indent=2), encoding="utf-8")
    LOGGER.info("Stage 1 CNN Extraction Completed Successfully!")


if __name__ == "__main__":
    main()
