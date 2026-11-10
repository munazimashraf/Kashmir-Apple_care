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
    
    Supports real-world agricultural photography where farmers hold leaves in their hands or on their palms.
    
    Returns:
        (is_plant: bool, reason: str, details: dict)
    """
    total_skin, total_foliage, center_skin, center_foliage = analyze_skin_and_foliage(image)

    # A genuine leaf held in hand or photographed on palm will dominate the central frame
    is_center_leaf = (
        (center_foliage >= 0.40 and center_skin < 0.20)
        or (center_foliage >= 0.60 and center_skin < 0.30)
    )

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
        "imagenet_top1_idx": imagenet_top1_idx,
        "imagenet_top1_prob": round(imagenet_top1_prob, 4),
        "is_flora_top": is_flora_top,
        "has_clothing_top": has_clothing_top,
    }

    # Case 1: If NOT a dominant center leaf, verify it is not a human subject/portrait/clothing
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

    # Case 2: Explicit non-plant objects (vehicles, electronics, furniture, domestic animals)
    is_explicit_non_plant = (
        imagenet_top1_idx in EXPLICIT_NON_PLANT_INDICES
        or any(idx in EXPLICIT_NON_PLANT_INDICES for idx in top_indices[:2])
    )
    if guard_model is not None and is_explicit_non_plant and not is_flora_top and center_foliage < 0.30:
        LOGGER.info("Explicit non-plant object detected: top1=%s, prob=%.3f", imagenet_top1_idx, imagenet_top1_prob)
        return False, "Inappropriate image: Non-plant object detected (vehicle/electronics/animal/indoor object).", details

    # Case 3: Insufficient foliage coloration (< 8% overall and < 8% in center)
    if total_foliage < 0.08 and center_foliage < 0.08:
        LOGGER.info("Foliage color check failed: foliage=%.3f, center_foliage=%.3f", total_foliage, center_foliage)
        return False, "No plant leaf or foliage coloration detected in the image.", details

    # Passed plant verification
    return True, "Valid plant leaf detected.", details
