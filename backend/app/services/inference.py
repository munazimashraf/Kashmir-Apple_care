import io
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from app.core.config import get_settings


class InferenceUnavailable(RuntimeError):
    pass


DISEASE_INFO = {
    "apple_scab": ("Apple Scab", "Venturia inaequalis"),
    "alternaria_leaf_blotch": ("Alternaria Leaf Blotch", "Alternaria alternata"),
    "powdery_mildew": ("Powdery Mildew", "Podosphaera leucotricha"),
    "black_rot": ("Black Rot", "Botryosphaeria obtusa"),
    "cedar_apple_rust": ("Cedar Apple Rust", "Gymnosporangium juniperi-virginianae"),
    "healthy": ("Healthy Apple Leaf", "Malus domestica"),
}


class LeafInference:
    def __init__(self, model_path: Path | None = None, classes_path: Path | None = None) -> None:
        settings = get_settings()
        self.path = model_path or Path(settings.model_path)
        classes_file = classes_path or Path(settings.classes_path)
        if not self.path.is_file() or not classes_file.is_file():
            raise InferenceUnavailable("Trained ONNX model and classes.json are required.")
        try:
            import onnxruntime as ort
            self.session = ort.InferenceSession(str(self.path), providers=["CPUExecutionProvider"])
        except Exception as exc:
            raise InferenceUnavailable("Could not load ONNX inference session.") from exc
        self.classes = json.loads(classes_file.read_text(encoding="utf-8"))
        self.input_name = self.session.get_inputs()[0].name

    def predict(self, content: bytes | Image.Image) -> dict[str, Any]:
        image = Image.open(io.BytesIO(content)) if isinstance(content, bytes) else content
        image = image.convert("RGB").resize((224, 224))
        array = np.asarray(image, dtype=np.float32) / 255.0
        array = (array - np.array([0.485, 0.456, 0.406])) / np.array([0.229, 0.224, 0.225])
        logits = self.session.run(
            None,
            {self.input_name: np.transpose(array, (2, 0, 1))[None, ...]},
        )[0][0]
        probabilities = np.exp(logits - np.max(logits))
        probabilities /= probabilities.sum()
        ranked = np.argsort(probabilities)[::-1]
        index = int(ranked[0])
        disease = self.classes[index]
        confidence = float(probabilities[index]) * 100
        return {
            "disease": disease,
            "disease_name": DISEASE_INFO.get(disease, (disease, "Unidentified"))[0],
            "scientific_name": DISEASE_INFO.get(disease, (disease, "Unidentified"))[1],
            "confidence": confidence,
            "confidence_label": "high" if confidence >= 85 else "medium" if confidence >= 60 else "low",
            "severity": "none" if disease == "healthy" else "moderate",
            "top_predictions": [
                {
                    "class": DISEASE_INFO.get(self.classes[i], (self.classes[i], ""))[0],
                    "slug": self.classes[i],
                    "probability": float(probabilities[i]) * 100,
                }
                for i in ranked[:3]
            ],
            "heatmap": {
                "method": "vgg19-classification",
                "area": "Whole specimen; localization is not available from this export.",
            },
        }


@lru_cache(maxsize=1)
def get_classifier() -> LeafInference:
    return LeafInference()
