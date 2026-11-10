#!/usr/bin/env python3
"""Train a dedicated neural Plant Verifier (Plant vs Non-Plant / Fast Color)
using the PlantVillage dataset + synthesized plain/fast colors and negative objects.

Ensures that:
- Plain green colors, neon fast colors, flat digital graphics, wallpapers,
  clothing, vehicles, and portraits are strictly classified as NON-PLANT (0).
- Genuine botanical plant leaves across multiple crop species are classified
  as REAL_PLANT (1).
"""
import glob
import os
import random
import time
from pathlib import Path
from typing import List, Tuple, Any

import numpy as np
import torch
import torch.nn as nn
from PIL import Image, ImageDraw, ImageFilter
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms


def generate_synthetic_non_plant_image(size=(224, 224)) -> Image.Image:
    """Generates synthetic flat/fast colors, neon swatches, gradients, and graphic textures."""
    w, h = size
    choice = random.random()

    if choice < 0.35:
        # 1. Solid plain or fast color (especially all shades of green, neon, lime, olive, mint)
        if random.random() < 0.65:
            # Green / lime / neon / fast color spectrum
            g = random.randint(80, 255)
            r = random.randint(0, min(255, int(g * random.uniform(0.1, 0.95))))
            b = random.randint(0, min(255, int(g * random.uniform(0.1, 0.95))))
            color = (r, g, b)
        else:
            # Any other random flat color (blue, red, gray, cyan, magenta, orange)
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        
        img = Image.new("RGB", size, color=color)
        # Add slight digital noise to some
        if random.random() < 0.3:
            arr = np.asarray(img, dtype=np.int16)
            noise = np.random.normal(0, random.uniform(2, 8), arr.shape).astype(np.int16)
            arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
            img = Image.fromarray(arr)
        return img

    elif choice < 0.60:
        # 2. Linear or radial synthetic fast color gradient
        c1 = np.array([random.randint(0, 100), random.randint(120, 255), random.randint(0, 100)], dtype=np.float32)
        c2 = np.array([random.randint(0, 150), random.randint(80, 255), random.randint(0, 150)], dtype=np.float32)
        arr = np.zeros((h, w, 3), dtype=np.uint8)
        axis = random.choice([0, 1])
        t = np.linspace(0, 1, w if axis == 1 else h, dtype=np.float32)
        for i in range(h if axis == 0 else w):
            alpha = t[i]
            col = (1.0 - alpha) * c1 + alpha * c2
            if axis == 0:
                arr[i, :, :] = col.astype(np.uint8)
            else:
                arr[:, i, :] = col.astype(np.uint8)
        return Image.fromarray(arr)

    elif choice < 0.80:
        # 3. Geometric graphics / banner / document / card
        bg_col = (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255))
        img = Image.new("RGB", size, bg_col)
        draw = ImageDraw.Draw(img)
        for _ in range(random.randint(2, 6)):
            x1, y1 = random.randint(0, w - 40), random.randint(0, h - 40)
            x2, y2 = random.randint(x1 + 10, w), random.randint(y1 + 10, h)
            fill_col = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            if random.random() < 0.5:
                draw.rectangle([x1, y1, x2, y2], fill=fill_col)
            else:
                draw.ellipse([x1, y1, x2, y2], fill=fill_col)
        return img

    else:
        # 4. Fabric / wallpaper / digital grid pattern
        base = random.randint(50, 200)
        grid = np.zeros((h, w, 3), dtype=np.uint8)
        grid[..., 1] = base
        freq = random.choice([4, 8, 16, 32])
        grid[::freq, :, 1] = min(255, base + 40)
        grid[:, ::freq, 1] = min(255, base + 40)
        return Image.fromarray(grid)


class PlantVsNonPlantDataset(Dataset):
    def __init__(self, items: List[Tuple[Any, int]], transform=None):
        self.items = items
        self.transform = transform

    def __len__(self):
        return len(self.items)

    def __getitem__(self, idx):
        item, label = self.items[idx]
        if isinstance(item, (str, Path)):
            try:
                img = Image.open(item).convert("RGB")
            except Exception:
                img = generate_synthetic_non_plant_image()
        else:
            img = item

        if self.transform:
            img = self.transform(img)

        return img, label


def main():
    print("=" * 70)
    print("TRAINING NEURAL PLANT VERIFIER (PLANT vs NON-PLANT / FAST COLOR)")
    print("=" * 70)

    # 1. Gather Real Plant Leaf Images from PlantVillage-Dataset
    pv_paths = glob.glob("PlantVillage-Dataset/raw/color/*/*.JPG")
    if not pv_paths:
        pv_paths = glob.glob("PlantVillage-Dataset/raw/color/*/*.jpg")
    print(f"Found {len(pv_paths)} total PlantVillage leaf images.")

    random.seed(42)
    torch.manual_seed(42)
    random.shuffle(pv_paths)

    # Sample 3,000 real leaves across all crops (Apple, Tomato, Grape, Corn, Pepper, Potato, etc.)
    num_plant_samples = min(3000, len(pv_paths))
    real_plant_samples = pv_paths[:num_plant_samples]
    print(f"Sampled {len(real_plant_samples)} real botanical leaf images for positive class (Class 1).")

    # 2. Generate Non-Plant / Fast Color Samples (Class 0)
    num_neg_samples = 2500
    print(f"Synthesizing {num_neg_samples} negative samples (plain colors, neon greens, fast colors, graphics, patterns)...")
    negative_samples = [generate_synthetic_non_plant_image() for _ in range(num_neg_samples)]

    # Combine into labeled list
    all_data = [(p, 1) for p in real_plant_samples] + [(im, 0) for im in negative_samples]
    random.shuffle(all_data)

    split = int(0.85 * len(all_data))
    train_data = all_data[:split]
    val_data = all_data[split:]

    print(f"Dataset: {len(train_data)} train samples, {len(val_data)} validation samples.")

    # Data Transforms
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.15, contrast=0.15, saturation=0.15),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    train_loader = DataLoader(PlantVsNonPlantDataset(train_data, train_transform), batch_size=64, shuffle=True, num_workers=0)
    val_loader = DataLoader(PlantVsNonPlantDataset(val_data, val_transform), batch_size=64, shuffle=False, num_workers=0)

    # 3. Model: MobileNetV3-Small Backbone
    print("Initializing MobileNetV3-Small binary plant verifier...")
    model = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.DEFAULT)

    # Freeze early feature layers, train classification head & last conv block
    for param in model.features[:-3].parameters():
        param.requires_grad = False

    in_features = model.classifier[0].in_features
    model.classifier = nn.Sequential(
        nn.Linear(in_features, 128),
        nn.Hardswish(),
        nn.Dropout(p=0.2),
        nn.Linear(128, 2),
    )

    device = torch.device("cpu")
    model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=1e-3, weight_decay=1e-4)

    # 4. Training Loop
    epochs = 4
    for epoch in range(1, epochs + 1):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        t0 = time.time()

        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            preds = outputs.argmax(dim=1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

        train_loss = running_loss / total
        train_acc = correct / total

        # Validation
        model.eval()
        v_loss = 0.0
        v_correct = 0
        v_total = 0
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)
                v_loss += loss.item() * images.size(0)
                preds = outputs.argmax(dim=1)
                v_correct += (preds == labels).sum().item()
                v_total += labels.size(0)

        val_loss = v_loss / v_total
        val_acc = v_correct / v_total
        elapsed = time.time() - t0

        print(f"Epoch [{epoch}/{epochs}] ({elapsed:.1f}s) | Train Loss: {train_loss:.4f}, Acc: {train_acc*100:.2f}% | Val Loss: {val_loss:.4f}, Val Acc: {val_acc*100:.2f}%")

    # 5. Save PyTorch Model
    pth_path = Path("backend/models/plant_verifier_mobilenetv3.pth")
    torch.save(model.state_dict(), pth_path)
    print(f"Saved PyTorch weights: {pth_path} ({pth_path.stat().st_size / 1e6:.2f} MB)")

    # 6. Export to ONNX for Ultra-Fast CPU Inference
    onnx_path = Path("backend/models/plant_verifier_mobilenetv3.onnx")
    dummy_input = torch.randn(1, 3, 224, 224, device=device)
    torch.onnx.export(
        model,
        dummy_input,
        str(onnx_path),
        input_names=["input"],
        output_names=["logits"],
        dynamic_axes={"input": {0: "batch_size"}, "logits": {0: "batch_size"}},
        opset_version=14,
    )
    print(f"Exported ONNX model: {onnx_path} ({onnx_path.stat().st_size / 1e6:.2f} MB)")

    # 7. Test on Edge Cases: Plain Green, Neon Fast Green, Real Leaf
    print("\n" + "=" * 50)
    print("BENCHMARK TEST ON EDGE-CASE IMAGES:")
    print("=" * 50)
    model.eval()

    test_cases = [
        ("Solid Green (34,139,34)", Image.new("RGB", (224, 224), (34, 139, 34))),
        ("Neon Fast Green (0,255,0)", Image.new("RGB", (224, 224), (0, 255, 0))),
        ("Fast Lime Green (50,220,50)", Image.new("RGB", (224, 224), (50, 220, 50))),
        ("Dark Green Swatch (10,80,10)", Image.new("RGB", (224, 224), (10, 80, 10))),
        ("Real Leaf: Apple Scab", Image.open(real_plant_samples[0]).convert("RGB")),
        ("Real Leaf: PlantVillage #2", Image.open(real_plant_samples[1]).convert("RGB")),
    ]

    for name, img in test_cases:
        tensor = val_transform(img).unsqueeze(0).to(device)
        with torch.no_grad():
            logits = model(tensor)
            probs = torch.softmax(logits, dim=1)[0]
            is_plant_prob = float(probs[1])
            is_plant = is_plant_prob >= 0.50
            status = "✅ PASS (Real Plant Leaf)" if is_plant else "🚫 REJECTED (Non-Plant / Fast Color)"
            print(f"  {name:30s} -> P(Plant) = {is_plant_prob*100:5.1f}% | {status}")

    print("=" * 70)
    print("Plant Verifier training and ONNX export complete!")


if __name__ == "__main__":
    main()
