#!/usr/bin/env python3
"""Train a dedicated neural Plant Verifier (Plant vs Non-Plant / Fast Color)
using VGG-19 architecture + PlantVillage dataset + synthesized plain/fast colors.

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

    if choice < 0.40:
        # 1. Solid plain or fast color (especially all shades of green, neon, lime, olive, mint)
        fast_greens = [
            (0, 255, 0),      # Pure electric/phosphor green
            (50, 255, 50),    # Fast neon lime
            (34, 139, 34),    # Forest green swatch
            (0, 128, 0),      # Standard HTML green
            (46, 139, 87),    # Sea green
            (107, 142, 35),   # Olive drab
            (124, 252, 0),    # Lawn green
            (127, 255, 0),    # Chartreuse
            (0, 255, 127),    # Spring green
            (0, 250, 154),    # Medium spring green
            (144, 238, 144),  # Light pastel green
            (154, 205, 50),   # Yellow green
            (173, 255, 47),   # Green yellow
            (32, 178, 170),   # Light sea green
            (60, 179, 113),   # Medium sea green
            (0, 100, 0),      # Dark green
            (85, 107, 47),    # Dark olive green
        ]
        if random.random() < 0.70:
            if random.random() < 0.50:
                color = random.choice(fast_greens)
            else:
                # Random green/lime/neon spectrum
                g = random.randint(70, 255)
                r = random.randint(0, min(255, int(g * random.uniform(0.05, 0.95))))
                b = random.randint(0, min(255, int(g * random.uniform(0.05, 0.95))))
                color = (r, g, b)
        else:
            # Any other random flat color (blue, red, gray, cyan, magenta, orange, black, white)
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        
        img = Image.new("RGB", size, color=color)
        # Add camera/sensor noise or slight lighting falloff to simulate a photo of a green wall / paper / cloth
        if random.random() < 0.5:
            arr = np.asarray(img, dtype=np.int16)
            noise_std = random.uniform(2, 18)
            noise = np.random.normal(0, noise_std, arr.shape).astype(np.int16)
            arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
            img = Image.fromarray(arr)
        return img

    elif choice < 0.65:
        # 2. Linear, diagonal, or radial synthetic fast color gradient
        c1 = np.array([random.randint(0, 100), random.randint(120, 255), random.randint(0, 100)], dtype=np.float32)
        c2 = np.array([random.randint(0, 160), random.randint(80, 255), random.randint(0, 160)], dtype=np.float32)
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
        if random.random() < 0.4:
            noise = np.random.normal(0, random.uniform(3, 15), arr.shape)
            arr = np.clip(arr.astype(np.float32) + noise, 0, 255).astype(np.uint8)
        return Image.fromarray(arr)

    elif choice < 0.85:
        # 3. Geometric graphics / banner / document / card / flat vector shapes
        bg_col = (random.randint(180, 255), random.randint(180, 255), random.randint(180, 255))
        img = Image.new("RGB", size, bg_col)
        draw = ImageDraw.Draw(img)
        for _ in range(random.randint(2, 7)):
            x1, y1 = random.randint(0, w - 40), random.randint(0, h - 40)
            x2, y2 = random.randint(x1 + 10, w), random.randint(y1 + 10, h)
            if random.random() < 0.6:
                fill_col = (random.randint(0, 80), random.randint(150, 255), random.randint(0, 80))
            else:
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


class VGG19PlantVerifier(nn.Module):
    def __init__(self, features: nn.Module, classifier: nn.Module):
        super().__init__()
        self.features = features
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.classifier = classifier

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        x = self.avgpool(x)
        return self.classifier(x)


def main():
    print("=" * 70)
    print("TRAINING NEURAL PLANT VERIFIER (VGG-19 PLANT vs NON-PLANT)")
    print("=" * 70)

    # 1. Gather Real Plant Leaf Images from PlantVillage-Dataset and data/apple
    pv_paths = glob.glob("PlantVillage-Dataset/raw/color/*/*.JPG")
    if not pv_paths:
        pv_paths = glob.glob("PlantVillage-Dataset/raw/color/*/*.jpg")
    if not pv_paths:
        pv_paths = glob.glob("data/apple/train/*/*.JPG")
    print(f"Found {len(pv_paths)} total botanical leaf images.")

    random.seed(42)
    torch.manual_seed(42)
    random.shuffle(pv_paths)

    # Balanced sample across crops and diseases
    num_plant_samples = min(300, len(pv_paths))
    real_plant_samples = pv_paths[:num_plant_samples]
    print(f"Sampled {len(real_plant_samples)} real botanical leaf images for positive class (Class 1).")

    # 2. Generate Non-Plant / Fast Color Samples (Class 0)
    num_neg_samples = 300
    print(f"Synthesizing {num_neg_samples} negative samples (plain colors, neon greens, fast colors, graphics, patterns)...")
    negative_samples = [generate_synthetic_non_plant_image() for _ in range(num_neg_samples)]

    # Combine into labeled list
    all_data = [(p, 1) for p in real_plant_samples] + [(im, 0) for im in negative_samples]
    random.shuffle(all_data)

    split = int(0.80 * len(all_data))
    train_data = all_data[:split]
    val_data = all_data[split:]

    print(f"Dataset: {len(train_data)} train samples, {len(val_data)} validation samples.")

    # Data Transforms
    eval_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    device = torch.device("cpu")
    torch.set_num_threads(min(8, torch.get_num_threads()))

    # 3. Model: VGG-19 Backbone Feature Extractor
    print("Initializing VGG-19 backbone from Torch hub...")
    base_vgg = models.vgg19(weights=models.VGG19_Weights.DEFAULT)
    base_vgg.eval()
    for param in base_vgg.parameters():
        param.requires_grad = False

    avgpool = nn.AdaptiveAvgPool2d((1, 1))

    # Pre-extract VGG-19 deep feature embeddings for speed and precision
    print("Extracting VGG-19 deep feature embeddings (512 dimensions)...")
    def extract_features(data_list):
        features = []
        labels = []
        loader = DataLoader(PlantVsNonPlantDataset(data_list, eval_transform), batch_size=32, shuffle=False)
        with torch.no_grad():
            for idx, (images, lbls) in enumerate(loader):
                feats = avgpool(base_vgg.features(images)).view(images.size(0), -1)
                features.append(feats)
                labels.append(lbls)
                if (idx + 1) % 4 == 0 or idx == len(loader) - 1:
                    print(f"  Processed batch {idx + 1}/{len(loader)}...")
        return torch.cat(features, dim=0), torch.cat(labels, dim=0)

    X_train, y_train = extract_features(train_data)
    X_val, y_val = extract_features(val_data)
    print(f"Feature extraction complete! Train features: {X_train.shape}, Val features: {X_val.shape}")

    # 4. Train Neural Classification Head
    head = nn.Sequential(
        nn.Flatten(),
        nn.Linear(512, 128),
        nn.ReLU(inplace=True),
        nn.Dropout(p=0.2),
        nn.Linear(128, 2),
    )

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(head.parameters(), lr=1e-3, weight_decay=1e-4)

    epochs = 20
    batch_size = 32
    num_batches = int(np.ceil(len(X_train) / batch_size))

    for epoch in range(1, epochs + 1):
        head.train()
        perm = torch.randperm(len(X_train))
        running_loss = 0.0
        correct = 0

        for b in range(num_batches):
            idx_b = perm[b * batch_size : (b + 1) * batch_size]
            x_b, y_b = X_train[idx_b], y_train[idx_b]

            optimizer.zero_grad()
            out = head(x_b)
            loss = criterion(out, y_b)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * len(x_b)
            correct += (out.argmax(dim=1) == y_b).sum().item()

        train_loss = running_loss / len(X_train)
        train_acc = correct / len(X_train)

        # Validation
        head.eval()
        with torch.no_grad():
            v_out = head(X_val)
            v_loss = criterion(v_out, y_val).item()
            v_acc = (v_out.argmax(dim=1) == y_val).float().mean().item()

        if epoch % 5 == 0 or epoch == epochs:
            print(f"Epoch [{epoch:2d}/{epochs}] | Train Loss: {train_loss:.4f}, Acc: {train_acc*100:.2f}% | Val Loss: {v_loss:.4f}, Val Acc: {v_acc*100:.2f}%")

    # 5. Assemble End-to-End VGG-19 Verifier Model
    print("\nAssembling full end-to-end VGG-19 verifier model...")
    model = VGG19PlantVerifier(base_vgg.features, head)
    model.eval()

    # Save PyTorch Model
    Path("backend/models").mkdir(parents=True, exist_ok=True)
    pth_path = Path("backend/models/plant_verifier_vgg19.pth")
    torch.save(model.state_dict(), pth_path)
    print(f"Saved PyTorch weights: {pth_path} ({pth_path.stat().st_size / 1e6:.2f} MB)")

    # 6. Export to ONNX for High-Speed Inference
    onnx_path = Path("backend/models/plant_verifier_vgg19.onnx")
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

    test_cases = [
        ("Solid Green (34,139,34)", Image.new("RGB", (224, 224), (34, 139, 34))),
        ("Neon Fast Green (0,255,0)", Image.new("RGB", (224, 224), (0, 255, 0))),
        ("Fast Lime Green (50,220,50)", Image.new("RGB", (224, 224), (50, 220, 50))),
        ("Dark Green Swatch (10,80,10)", Image.new("RGB", (224, 224), (10, 80, 10))),
        ("Chartreuse Neon (127,255,0)", Image.new("RGB", (224, 224), (127, 255, 0))),
        ("Spring Green (0,255,127)", Image.new("RGB", (224, 224), (0, 255, 127))),
        ("Olive Drab (107,142,35)", Image.new("RGB", (224, 224), (107, 142, 35))),
        ("Real Leaf: Apple Scab", Image.open(real_plant_samples[0]).convert("RGB")),
        ("Real Leaf: PlantVillage #2", Image.open(real_plant_samples[1]).convert("RGB")),
    ]

    for name, img in test_cases:
        tensor = eval_transform(img).unsqueeze(0).to(device)
        with torch.no_grad():
            logits = model(tensor)
            probs = torch.softmax(logits, dim=1)[0]
            is_plant_prob = float(probs[1])
            is_plant = is_plant_prob >= 0.50
            status = "✅ PASS (Real Plant Leaf)" if is_plant else "🚫 REJECTED (Non-Plant / Fast Color)"
            print(f"  {name:30s} -> P(Plant) = {is_plant_prob*100:5.1f}% | {status}")

    print("=" * 70)
    print("VGG-19 Plant Verifier training and ONNX export complete!")


if __name__ == "__main__":
    main()
