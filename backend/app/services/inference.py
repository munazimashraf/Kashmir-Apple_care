import json
import logging
from pathlib import Path
from typing import Any, Dict

import numpy as np
from PIL import Image

from app.core.config import get_settings
from app.services.plant_guard import check_is_plant

LOGGER = logging.getLogger("applecare.inference")


class InferenceUnavailable(RuntimeError):
    pass


class LeafInference:
    MIN_CONFIDENCE = 0.45

    def __init__(self) -> None:
        settings = get_settings()
        self.path = Path(settings.model_path)
        classes_path = Path(settings.classes_path)
        
        # Fallback to applecare_mobilenetv3.onnx if default not found
        if not self.path.is_file():
            fallback = Path("artifacts/applecare-six/applecare_mobilenetv3.onnx")
            if fallback.is_file():
                self.path = fallback

        if not classes_path.is_file():
            fallback_cls = Path("artifacts/applecare-six/classes.json")
            if fallback_cls.is_file():
                classes_path = fallback_cls

        if not self.path.is_file() or not classes_path.is_file():
            raise InferenceUnavailable("Trained ONNX model and classes.json are required.")

        try:
            import onnxruntime as ort
            # Optimize inference session options for CPU execution
            sess_options = ort.SessionOptions()
            sess_options.intra_op_num_threads = 4
            self.session = ort.InferenceSession(str(self.path), sess_options, providers=["CPUExecutionProvider"])
        except Exception as exc:
            raise InferenceUnavailable(f"Could not load ONNX inference session from {self.path}") from exc

        self.classes = json.loads(classes_path.read_text(encoding="utf-8"))
        self.input_name = self.session.get_inputs()[0].name

    def predict(self, image: Image.Image) -> Dict[str, Any]:
        """Classifies the leaf image, with automatic guard against non-plant / inappropriate images."""
        # Step 1: Plant verification guard
        is_plant, guard_reason, guard_details = check_is_plant(image)
        if not is_plant:
            LOGGER.warning("Inappropriate non-plant image uploaded: %s (details: %s)", guard_reason, guard_details)
            return {
                "is_plant": False,
                "inappropriate": True,
                "disease": "Inappropriate Image (Not a Plant)",
                "confidence": 0.0,
                "uncertain": True,
                "alternatives": [],
                "error": f"Inappropriate image: {guard_reason} Please upload a clear photo of an apple leaf.",
                "guard_details": guard_details,
                "heatmap": {
                    "method": "plant-guard-rejection",
                    "area": "No disease activation: image does not contain plant foliage.",
                },
            }

        # Step 2: Normalization and ONNX inference (with multi-scale leaf focus)
        def _get_probs(img: Image.Image) -> np.ndarray:
            im_resized = img.convert("RGB").resize((224, 224))
            arr = np.asarray(im_resized, dtype=np.float32) / 255.0
            mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
            std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
            arr = ((arr - mean) / std).astype(np.float32, copy=False)
            tensor = np.transpose(arr, (2, 0, 1))[None, ...]
            logits = self.session.run(None, {self.input_name: tensor})[0][0]
            shift_logits = logits - np.max(logits)
            p = np.exp(shift_logits)
            return p / p.sum()

        p_full = _get_probs(image)
        
        # Test-time leaf bounding-box focus (handles farmer hands, orchard backgrounds)
        try:
            rgb = image.convert("RGB")
            w, h = rgb.size
            small = rgb.resize((128, 128))
            arr_s = np.asarray(small, dtype=np.float32) / 255.0
            r, g, b = arr_s[..., 0], arr_s[..., 1], arr_s[..., 2]
            green_mask = (g > r * 0.92) & (g > b * 1.05) & (g > 0.12)
            yellow_brown_mask = (r > 0.20) & (g > 0.18) & (b < 0.45) & (r + g > 1.8 * b)
            saturation = np.maximum(r, np.maximum(g, b)) - np.minimum(r, np.minimum(g, b))
            necrotic_mask = (r < 0.45) & (g < 0.42) & (b < 0.30) & (r > b) & (saturation > 0.03)
            leaf_mask = green_mask | yellow_brown_mask | necrotic_mask
            y_indices, x_indices = np.where(leaf_mask)
            if len(y_indices) > 50:
                ymin = int(np.percentile(y_indices, 2) / 128.0 * h)
                ymax = int(np.percentile(y_indices, 98) / 128.0 * h)
                xmin = int(np.percentile(x_indices, 2) / 128.0 * w)
                xmax = int(np.percentile(x_indices, 98) / 128.0 * w)
                if (xmax - xmin) > 64 and (ymax - ymin) > 64:
                    crop = rgb.crop((max(0, xmin), max(0, ymin), min(w, xmax), min(h, ymax)))
                    p_crop = _get_probs(crop)
                    probabilities = 0.5 * p_full + 0.5 * p_crop
                else:
                    probabilities = p_full
            else:
                probabilities = p_full
        except Exception as exc:
            LOGGER.warning("Leaf bbox focus skipped: %s", exc)
            probabilities = p_full
        
        index = int(np.argmax(probabilities))
        confidence = float(probabilities[index])
        ranked = np.argsort(probabilities)[::-1][:3]
        
        uncertain = confidence < self.MIN_CONFIDENCE

        return {
            "is_plant": True,
            "inappropriate": False,
            "disease": self.classes[index],
            "confidence": round(confidence, 4),
            "uncertain": uncertain,
            "alternatives": [
                {
                    "disease": self.classes[int(item)],
                    "confidence": round(float(probabilities[int(item)]), 4),
                }
                for item in ranked
            ],
            "heatmap": {
                "method": "deep-feature-inference",
                "area": f"Classified by MobileNetV3-Large with {round(confidence * 100, 1)}% confidence.",
            },
        }
