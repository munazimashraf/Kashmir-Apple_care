"""Plant image verification and inappropriate/non-plant image detection guard.

Ensures that uploaded images are genuinely plant/foliage leaves. If any non-plant
image is uploaded (people, faces, clothing, animals, vehicles, furniture,
electronics, documents, random objects, or inappropriate content), it flags
the image as inappropriate and prevents disease classification.
"""
from __future__ import annotations

import logging
from typing import Tuple, Dict, Any
import numpy as np
from PIL import Image

LOGGER = logging.getLogger("applecare.guard")

# ImageNet-1K indices corresponding to flora, plants, leaves, trees, vegetables, and fungi
PLANT_FLORA_IMAGENET_INDICES = {
    # Fungi / lichen / flora
    985,  # daisy
    986,  # yellow lady's slipper
    987,  # cardoon
    988,  # acorn
    989,  # ear, spike, capitulum (ear of corn / wheat)
    990,  # food market / grocery (often fruit/veggie)
    991,  # coral fungus
    992,  # agaric
    993,  # gyromitra
    994,  # stinkhorn
    995,  # earthstar
    996,  # hen-of-the-woods
    997,  # bolete
    998,  # ear (fungus)
    # Agricultural / vegetable / foliage
    936,  # head cabbage
    937,  # broccoli
    938,  # cauliflower
    939,  # zucchini
    940,  # spaghetti squash
    941,  # acorn squash
    942,  # butternut squash
    943,  # cucumber
    944,  # artichoke
    945,  # bell pepper
    946,  # cardoon
    947,  # mushroom
    948,  # Granny Smith apple
    949,  # strawberry
    950,  # orange
    951,  # lemon
    952,  # fig
    953,  # pineapple
    954,  # banana
    955,  # jackfruit
    956,  # custard apple
    957,  # pomegranate
    958,  # hay
    738,  # pot, flowerpot
    584,  # greenhouse
    301,  # leaf beetle
    306,  # rhinoceros beetle (on branch)
    314,  # cicada (on foliage)
    321,  # admiral (butterfly on leaf)
    322,  # ringlet (butterfly on leaf)
    323,  # monarch (butterfly on leaf)
    324,  # cabbage butterfly (on leaf)
    325,  # sulphur butterfly (on leaf)
    326,  # lycaenid (on leaf)
}

# ImageNet categories that explicitly indicate human beings, clothing, garments, and accessories
HUMAN_AND_CLOTHING_INDICES = {
    400, 411, 445, 452, 459, 474, 501, 515, 578, 608, 614, 617, 618, 636, 643,
    677, 697, 734, 824, 834, 838, 842, 869, 879, 887, 906, 823, 585, 629
}

# ImageNet categories that explicitly indicate non-plant man-made items, vehicles, electronics, or mammals
EXPLICIT_NON_PLANT_INDICES = {
    # Vehicles & transport
    404, 436, 466, 472, 484, 511, 547, 554, 565, 625, 627, 656, 670, 671, 705, 734, 751, 780, 814, 817, 829, 864, 867, 895, 914,
    # Electronics, office, screens
    487, 508, 523, 620, 664, 782, 851, 681, 722,
    # Furniture & indoor household
    532, 559, 765, 831, 857, 898, 423,
    # Domestic mammals / dogs / cats
    *range(151, 269), *range(281, 286), *range(365, 385),
}

_GUARD_MODEL = None
_PLANT_VERIFIER_SESSION = None


def get_plant_verifier():
    """Loads the dedicated neural PlantVillage verifier model (ONNX) if available."""
    global _PLANT_VERIFIER_SESSION
    if _PLANT_VERIFIER_SESSION is None:
        try:
            from pathlib import Path
            import onnxruntime as ort
            onnx_path = Path("backend/models/plant_verifier_mobilenetv3.onnx")
            if onnx_path.is_file():
                opts = ort.SessionOptions()
                opts.intra_op_num_threads = 2
                _PLANT_VERIFIER_SESSION = ort.InferenceSession(str(onnx_path), opts, providers=["CPUExecutionProvider"])
                LOGGER.info("Loaded PlantVerifier ONNX model from %s", onnx_path)
            else:
                _PLANT_VERIFIER_SESSION = False
        except Exception as exc:
            LOGGER.warning("Could not load PlantVerifier ONNX model: %s", exc)
            _PLANT_VERIFIER_SESSION = False
    return _PLANT_VERIFIER_SESSION if _PLANT_VERIFIER_SESSION is not False else None


def predict_plant_verifier(image: Image.Image) -> Tuple[bool, float]:
    """Evaluates image with the PlantVillage-trained neural verifier."""
    session = get_plant_verifier()
    if session is None:
        return True, 1.0  # Fallback if model not yet loaded

    try:
        im = image.convert("RGB").resize((224, 224))
        arr = np.asarray(im, dtype=np.float32) / 255.0
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        arr = ((arr - mean) / std).astype(np.float32, copy=False)
        tensor = np.transpose(arr, (2, 0, 1))[None, ...]

        input_name = session.get_inputs()[0].name
        logits = session.run(None, {input_name: tensor})[0][0]
        shift = logits - np.max(logits)
        probs = np.exp(shift) / np.sum(np.exp(shift))
        p_plant = float(probs[1])
        return (p_plant >= 0.50), p_plant
    except Exception as exc:
        LOGGER.warning("PlantVerifier inference failed: %s", exc)
        return True, 1.0


def analyze_botanical_texture_and_flatness(image: Image.Image) -> Dict[str, Any]:
    """Analyzes spatial frequency, discrete Laplacian variance, local tile variance,
    and synthetic saturation to detect flat plain colors, neon fast colors, and digital graphics.

    Authentic leaves have veins, stomata, margins, and natural chlorophyll gradients.
    Plain colors or artificial 'fast' colors have near-zero texture and unnatural saturation.
    """
    rgb_img = image.convert("RGB").resize((160, 160))
    arr = np.asarray(rgb_img, dtype=np.float32)
    gray = 0.299 * arr[..., 0] + 0.587 * arr[..., 1] + 0.114 * arr[..., 2]

    # 1. Discrete 2nd-order Laplacian variance (measures leaf vein & surface micro-texture)
    lap = -4 * gray[1:-1, 1:-1] + gray[:-2, 1:-1] + gray[2:, 1:-1] + gray[1:-1, :-2] + gray[1:-1, 2:]
    lap_var = float(np.var(lap))

    # 2. Local 16x16 micro-tile variance (detects uniform blocks / absence of vein networks)
    tiles = []
    h, w = gray.shape
    for i in range(0, h - 16, 16):
        for j in range(0, w - 16, 16):
            tiles.append(np.std(gray[i:i + 16, j:j + 16]))
    tile_std_mean = float(np.mean(tiles)) if tiles else 0.0
    tile_std_max = float(np.max(tiles)) if tiles else 0.0

    # 3. Spatial gradient energy
    dx = np.abs(gray[:, 1:] - gray[:, :-1])
    dy = np.abs(gray[1:, :] - gray[:-1, :])
    grad_mean = float(np.mean(dx) + np.mean(dy))

    # 4. Color variance across RGB
    color_std = float(np.mean([np.std(arr[..., c]) for c in range(3)]))

    # 5. Synthetic fast / neon color detection (HSV)
    r, g, b = arr[..., 0] / 255.0, arr[..., 1] / 255.0, arr[..., 2] / 255.0
    max_c = np.maximum(r, np.maximum(g, b))
    min_c = np.minimum(r, np.minimum(g, b))
    sat = np.where(max_c > 0.01, (max_c - min_c) / (max_c + 1e-6), 0.0)
    mean_sat = float(np.mean(sat))
    mean_val = float(np.mean(max_c))

    # A. Plain flat color: near-zero Laplacian variance, tile standard deviation, or gradient
    avg_r, avg_g, avg_b = float(np.mean(arr[..., 0])), float(np.mean(arr[..., 1])), float(np.mean(arr[..., 2]))
    mean_color = np.array([avg_r, avg_g, avg_b], dtype=np.float32)
    dist_from_mean = np.sqrt(np.sum((arr - mean_color) ** 2, axis=-1))
    uniform_ratio = float(np.mean(dist_from_mean < 15.0))
    is_uniform_swatch = uniform_ratio > 0.85

    is_plain_color = (
        (lap_var < 28.0 and tile_std_mean < 3.5)
        or color_std < 10.0
        or is_uniform_swatch
    )

    # B. Synthetic fast/neon color: high artificial saturation with lack of natural leaf vein texture
    is_synthetic_fast_color = (
        mean_sat > 0.65 and (lap_var < 80.0 or tile_std_mean < 6.0)
    )

    # C. Unnatural green dominance without chlorophyll balance (e.g. pure phosphor green RGB(0,255,0))
    is_unnatural_green = (
        avg_g > 1.8 * (avg_r + 2.0) and avg_g > 1.8 * (avg_b + 2.0) and mean_sat > 0.55 and lap_var < 90.0
    )

    return {
        "lap_var": round(lap_var, 2),
        "tile_std_mean": round(tile_std_mean, 2),
        "tile_std_max": round(tile_std_max, 2),
        "grad_mean": round(grad_mean, 2),
        "color_std": round(color_std, 2),
        "mean_sat": round(mean_sat, 2),
        "mean_val": round(mean_val, 2),
        "uniform_ratio": round(uniform_ratio, 2),
        "is_plain_color": is_plain_color,
        "is_synthetic_fast_color": is_synthetic_fast_color,
        "is_unnatural_green": is_unnatural_green,
        "is_uniform_swatch": is_uniform_swatch,
    }


def get_guard_model():
    global _GUARD_MODEL
    if _GUARD_MODEL is None:
        try:
            import torch
            from torchvision import models
            model = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.DEFAULT)
            model.eval()
            _GUARD_MODEL = model
            LOGGER.info("Initialized PlantGuard ImageNet verification model.")
        except Exception as exc:
            LOGGER.warning("Could not load ImageNet guard model: %s. Using visual heuristics.", exc)
            _GUARD_MODEL = False
    return _GUARD_MODEL if _GUARD_MODEL is not False else None


def analyze_human_skin_ratio(image: Image.Image) -> float:
    """Calculates percentage of pixels matching human skin tones using standard RGB/HSV rules."""
    rgb_img = image.convert("RGB").resize((128, 128))
    arr = np.asarray(rgb_img, dtype=np.float32) / 255.0
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]

    # Peer et al. / Kovac et al. skin detection in RGB:
    # R > 0.35, G > 0.15, B > 0.10, R > G, G > B, (R - G) > 0.05, (R - B) > 0.10
    skin_mask = (
        (r > 0.35) & (g > 0.15) & (b > 0.10) &
        (r > g) & (g > b) & ((r - g) > 0.05) & ((r - b) > 0.10) &
        (np.maximum(r, np.maximum(g, b)) - np.minimum(r, np.minimum(g, b)) > 0.06)
    )
    return float(np.mean(skin_mask))


def analyze_skin_and_foliage(image: Image.Image) -> Tuple[float, float, float, float]:
    """Calculates overall and central skin and foliage color ratios.
    
    Returns:
        (total_skin, total_foliage, center_skin, center_foliage)
    """
    rgb_img = image.convert("RGB").resize((128, 128))
    arr = np.asarray(rgb_img, dtype=np.float32) / 255.0
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]

    # Peer & Kovac RGB skin tone rules:
    skin_mask = (
        (r > 0.35) & (g > 0.15) & (b > 0.10) &
        (r > g) & (g > b) & ((r - g) > 0.05) & ((r - b) > 0.10) &
        (np.maximum(r, np.maximum(g, b)) - np.minimum(r, np.minimum(g, b)) > 0.06)
    )

    # 1. Green chlorophyll dominance: Green channel is greater than blue and red
    green_mask = (g > r * 0.95) & (g > b * 1.1) & (g > 0.15)

    # 2. Yellow/brown/chlorotic/autumnal diseased leaf tissue
    yellow_brown_mask = (r > 0.25) & (g > 0.20) & (b < 0.45) & (r + g > 2.0 * b) & (np.abs(r - g) < 0.35)

    # 3. Dark necrotic lesion spots (scab, rot): require brown hue and saturation
    saturation = np.maximum(r, np.maximum(g, b)) - np.minimum(r, np.minimum(g, b))
    necrotic_mask = (r < 0.40) & (g < 0.38) & (b < 0.25) & (r > b) & (g >= b) & (saturation > 0.04)

    foliage_mask = green_mask | yellow_brown_mask | necrotic_mask

    total_skin = float(np.mean(skin_mask))
    total_foliage = float(np.mean(foliage_mask))

    # Center crop: central 50% width and height (coordinates 32:96 in 128x128)
    center_skin = float(np.mean(skin_mask[32:96, 32:96]))
    center_foliage = float(np.mean(foliage_mask[32:96, 32:96]))

    return total_skin, total_foliage, center_skin, center_foliage


def check_is_plant(image: Image.Image) -> Tuple[bool, str, Dict[str, Any]]:
    """Evaluates whether the uploaded image is a real plant leaf or an inappropriate / non-plant image.
    
    Strictly rejects:
    - Plain green colors, neon fast colors, flat digital graphics, and uniform swatches.
    - Human beings, portraits, selfies, and clothing.
    - Vehicles, electronics, animals, furniture, and indoor scenes.
    - Non-plant images without botanical leaf texture.
    
    Supports authentic field conditions where growers hold leaves in hand or on palm.
    
    Returns:
        (is_plant: bool, reason: str, details: dict)
    """
    # Step 0: Botanical Texture & Flatness Physics Guard
    texture = analyze_botanical_texture_and_flatness(image)
    
    total_skin, total_foliage, center_skin, center_foliage = analyze_skin_and_foliage(image)

    # A genuine leaf held in hand or photographed on palm will dominate the central frame
    is_center_leaf = (
        (center_foliage >= 0.40 and center_skin < 0.20)
        or (center_foliage >= 0.60 and center_skin < 0.30)
    )

    # Neural Plant Verifier (Trained on PlantVillage dataset + negative fast colors)
    is_real_plant_neural, p_plant_neural = predict_plant_verifier(image)

    # ImageNet category verification
    guard_model = get_guard_model()
    imagenet_top1_idx = None
    imagenet_top1_prob = 0.0
    top_indices = []
    top_probs = []
    is_flora_top = False
    has_clothing_top = False

    if guard_model is not None:
        try:
            import torch
            from torchvision import transforms
            preprocess = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])
            tensor = preprocess(image.convert("RGB")).unsqueeze(0)
            with torch.no_grad():
                logits = guard_model(tensor)
                probs = torch.softmax(logits, dim=1)[0]
                topk = torch.topk(probs, k=5)
                top_indices = topk.indices.tolist()
                top_probs = [float(x) for x in topk.values.tolist()]

                imagenet_top1_idx = top_indices[0]
                imagenet_top1_prob = top_probs[0]

                # Check flora matches in top 3
                is_flora_top = any(idx in PLANT_FLORA_IMAGENET_INDICES for idx in top_indices[:3])
                # Check human clothing matches in top 5 with significant probability (>= 0.08)
                has_clothing_top = any(
                    (idx in HUMAN_AND_CLOTHING_INDICES and prob >= 0.08)
                    for idx, prob in zip(top_indices[:5], top_probs[:5])
                )
        except Exception as exc:
            LOGGER.warning("ImageNet inference failed: %s", exc)

    details = {
        "skin_ratio": round(total_skin, 4),
        "foliage_color_ratio": round(total_foliage, 4),
        "center_skin_ratio": round(center_skin, 4),
        "center_foliage_ratio": round(center_foliage, 4),
        "is_center_leaf": is_center_leaf,
        "lap_var": texture["lap_var"],
        "tile_std_mean": texture["tile_std_mean"],
        "color_std": texture["color_std"],
        "mean_sat": texture["mean_sat"],
        "p_plant_verifier": round(p_plant_neural, 4),
        "imagenet_top1_idx": imagenet_top1_idx,
        "imagenet_top1_prob": round(imagenet_top1_prob, 4),
        "is_flora_top": is_flora_top,
        "has_clothing_top": has_clothing_top,
    }

    # REJECTION RULE 1: Plain / Solid / Uniform Flat Color Check
    if texture["is_plain_color"] or texture["is_uniform_swatch"]:
        LOGGER.info("Plain/flat color detected: %s", texture)
        return False, "Inappropriate image: Plain or uniform color detected. The image lacks organic leaf veins, cellular texture, and botanical structure. Please photograph an actual plant leaf.", details

    # REJECTION RULE 2: Synthetic Fast / Neon Color Check
    if texture["is_synthetic_fast_color"] or texture["is_unnatural_green"]:
        LOGGER.info("Synthetic fast/neon color detected: %s", texture)
        return False, "Inappropriate image: Synthetic fast/neon color detected. Natural plant leaves have organic chlorophyll pigmentation and surface micro-texture. Please photograph an actual plant leaf in natural light.", details

    # REJECTION RULE 3: Neural Plant Verifier Rejection
    if not is_real_plant_neural:
        LOGGER.info("Neural Plant Verifier rejected non-plant: p_plant=%.4f", p_plant_neural)
        return False, "Inappropriate image: Neural verification determined this image is not a genuine plant leaf. Please upload a clear photo of an apple leaf.", details

    # REJECTION RULE 4: Human Subject / Portrait / Selfie / Clothes
    if not is_center_leaf:
        # High skin in center = person face/neck/torso
        if center_skin > 0.25:
            LOGGER.info("Human subject detected in center: center_skin=%.3f", center_skin)
            return False, "Human subject / person detected in the photo. Please photograph a plant leaf instead.", details

        # High overall skin tone with no leaf in center = person or bare hand
        if total_skin > 0.15 and center_foliage < 0.35:
            LOGGER.info("Human subject / person detected: skin=%.3f, center_foliage=%.3f", total_skin, center_foliage)
            return False, "Human subject / person detected in the photo. Please photograph a plant leaf instead.", details

        # Human clothing / garment detected (e.g. stole, shirt, coat, robe, vestment)
        if has_clothing_top and not is_flora_top and center_foliage < 0.45:
            LOGGER.info("Clothing/person detected: indices=%s", top_indices)
            return False, "Clothing or person detected. Please upload an apple leaf photo.", details

    # REJECTION RULE 5: Explicit Non-Plant Objects (vehicles, electronics, furniture, domestic animals)
    is_explicit_non_plant = (
        imagenet_top1_idx in EXPLICIT_NON_PLANT_INDICES
        or any(idx in EXPLICIT_NON_PLANT_INDICES for idx in top_indices[:2])
    )
    if guard_model is not None and is_explicit_non_plant and not is_flora_top and center_foliage < 0.30:
        LOGGER.info("Explicit non-plant object detected: top1=%s, prob=%.3f", imagenet_top1_idx, imagenet_top1_prob)
        return False, "Inappropriate image: Non-plant object detected (vehicle/electronics/animal/indoor object).", details

    # REJECTION RULE 6: Insufficient Foliage Coloration (< 8% overall and < 8% in center)
    if total_foliage < 0.08 and center_foliage < 0.08:
        LOGGER.info("Foliage color check failed: foliage=%.3f, center_foliage=%.3f", total_foliage, center_foliage)
        return False, "No plant leaf or foliage coloration detected in the image.", details

    # Passed plant verification
    return True, "Valid plant leaf detected.", details
