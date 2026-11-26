import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

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
        self.classes_path = Path(settings.classes_path)
        self.ensemble_enabled = getattr(settings, "ensemble_enabled", True)
        self.ensemble_dir = Path(getattr(settings, "ensemble_dir", "artifacts/ensemble"))
        self.is_ensemble = False
        self.models: List[Dict[str, Any]] = []

        import onnxruntime as ort

        sess_options = ort.SessionOptions()
        sess_options.intra_op_num_threads = 4

        # 1. Try loading Tri-Model Deep Ensemble (ResNet-50 + VGG-16 + VGG-19)
        cfg_path = self.ensemble_dir / "ensemble_config.json"
        if not cfg_path.is_file():
            alt_path = Path("backend/models/ensemble_config.json")
            if alt_path.is_file():
                self.ensemble_dir = Path("backend/models")
                cfg_path = alt_path
        if self.ensemble_enabled and cfg_path.is_file():
            try:
                cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
                self.classes = cfg.get("classes", [])
                for m_spec in cfg.get("models", []):
                    m_file = self.ensemble_dir / m_spec["model_file"]
                    if m_file.is_file():
                        sess = ort.InferenceSession(str(m_file), sess_options, providers=["CPUExecutionProvider"])
                        inp_name = sess.get_inputs()[0].name
                        self.models.append({
                            "name": m_spec["name"],
                            "session": sess,
                            "input_name": inp_name,
                            "weight": float(m_spec.get("weight", 1.0)),
                        })
                if len(self.models) >= 2:
                    self.is_ensemble = True
                    LOGGER.info(
                        "Tri-Model Deep Ensemble loaded successfully with %d backbones: %s",
                        len(self.models),
                        [m["name"] for m in self.models],
                    )
            except Exception as exc:
                LOGGER.warning("Ensemble initialization failed (%s); falling back to single model.", exc)
                self.models.clear()
                self.is_ensemble = False

        # 2. Fallback to single ONNX model if ensemble unavailable
        if not self.is_ensemble:
            self.path = Path(settings.model_path)
            if not self.path.is_file():
                fallback = Path("artifacts/applecare-six/applecare_vgg19.onnx")
                if fallback.is_file():
                    self.path = fallback

            if not self.classes_path.is_file():
                fallback_cls = Path("artifacts/applecare-six/classes.json")
                if fallback_cls.is_file():
                    self.classes_path = fallback_cls

            if not self.path.is_file() or not self.classes_path.is_file():
                raise InferenceUnavailable("Trained ONNX model and classes.json are required.")

            try:
                self.session = ort.InferenceSession(str(self.path), sess_options, providers=["CPUExecutionProvider"])
                self.input_name = self.session.get_inputs()[0].name
                self.classes = json.loads(self.classes_path.read_text(encoding="utf-8"))
                LOGGER.info("Loaded single ONNX model from %s", self.path)
            except Exception as exc:
                raise InferenceUnavailable(f"Could not load ONNX inference session from {self.path}") from exc

    @staticmethod
    def _preprocess_tensor(img: Image.Image) -> np.ndarray:
        im_resized = img.convert("RGB").resize((224, 224))
        arr = np.asarray(im_resized, dtype=np.float32) / 255.0
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        arr = ((arr - mean) / std).astype(np.float32, copy=False)
        return np.transpose(arr, (2, 0, 1))[None, ...]

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

        # Step 2: Prepare inputs (full image + multi-scale leaf focus crop)
        tensor_full = self._preprocess_tensor(image)
        tensor_crop: Optional[np.ndarray] = None

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
                    tensor_crop = self._preprocess_tensor(crop)
        except Exception as exc:
            LOGGER.warning("Leaf bbox focus skipped: %s", exc)

        # Step 3: Run inference
        if self.is_ensemble:
            blended = np.zeros(len(self.classes), dtype=np.float32)
            total_w = 0.0
            breakdown: Dict[str, Any] = {}

            for m in self.models:
                logits_f = m["session"].run(None, {m["input_name"]: tensor_full})[0][0]
                shift_f = logits_f - np.max(logits_f)
                p_f = np.exp(shift_f) / np.sum(np.exp(shift_f))

                if tensor_crop is not None:
                    logits_c = m["session"].run(None, {m["input_name"]: tensor_crop})[0][0]
                    shift_c = logits_c - np.max(logits_c)
                    p_c = np.exp(shift_c) / np.sum(np.exp(shift_c))
                    p_m = 0.5 * p_f + 0.5 * p_c
                else:
                    p_m = p_f

                w = m["weight"]
                blended += w * p_m
                total_w += w

                top_m_idx = int(np.argmax(p_m))
                breakdown[m["name"]] = {
                    "disease": self.classes[top_m_idx],
                    "confidence": round(float(p_m[top_m_idx]), 4),
                    "weight": round(w, 2),
                }

            probabilities = blended / (total_w if total_w > 0 else 1.0)
            model_title = "Tri-Model Deep Ensemble (VGG-19 + VGG-16 + ResNet-50)"
            method_desc = "tri-model-deep-ensemble"
            area_desc = (
                f"Tri-Model Soft-Voting Ensemble (VGG-19 + VGG-16 + ResNet-50) "
                f"classified with {round(float(np.max(probabilities)) * 100, 1)}% confidence."
            )
        else:
            logits_f = self.session.run(None, {self.input_name: tensor_full})[0][0]
            shift_f = logits_f - np.max(logits_f)
            p_f = np.exp(shift_f) / np.sum(np.exp(shift_f))

            if tensor_crop is not None:
                logits_c = self.session.run(None, {self.input_name: tensor_crop})[0][0]
                shift_c = logits_c - np.max(logits_c)
                p_c = np.exp(shift_c) / np.sum(np.exp(shift_c))
                probabilities = 0.5 * p_f + 0.5 * p_c
            else:
                probabilities = p_f

            model_title = "VGG-19 Deep Neural Network"
            method_desc = "deep-feature-inference"
            top_single = int(np.argmax(probabilities))
            breakdown = {
                "VGG-19": {
                    "disease": self.classes[top_single],
                    "confidence": round(float(probabilities[top_single]), 4),
                    "weight": 1.0,
                }
            }
            area_desc = (
                f"Classified by VGG-19 Deep Neural Network with "
                f"{round(float(probabilities[top_single]) * 100, 1)}% confidence."
            )

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
            "model": model_title,
            "ensemble_breakdown": breakdown,
            "alternatives": [
                {
                    "disease": self.classes[int(item)],
                    "confidence": round(float(probabilities[int(item)]), 4),
                }
                for item in ranked
            ],
            "heatmap": {
                "method": method_desc,
                "area": area_desc,
            },
        }
