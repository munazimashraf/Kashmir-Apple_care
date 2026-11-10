import json
from pathlib import Path
from typing import Any

from PIL import Image

from app.core.config import get_settings


class InferenceUnavailable(RuntimeError):
    pass


class LeafInference:
    def __init__(self) -> None:
        settings = get_settings()
        self.path = Path(settings.model_path)
        classes_path = Path(settings.classes_path)
        if not self.path.is_file() or not classes_path.is_file():
            raise InferenceUnavailable("Trained ONNX model and classes.json are required.")
        try:
            import onnxruntime as ort
            self.session = ort.InferenceSession(str(self.path), providers=["CPUExecutionProvider"])
        except Exception as exc:
            raise InferenceUnavailable("Could not load ONNX inference session.") from exc
        self.classes = json.loads(classes_path.read_text(encoding="utf-8"))
        self.input_name = self.session.get_inputs()[0].name

    def predict(self, image: Image.Image) -> dict[str, Any]:
        import numpy as np

        image = image.convert("RGB").resize((224, 224))
        array = np.asarray(image, dtype=np.float32) / 255.0
        array = (array - np.array([0.485, 0.456, 0.406])) / np.array([0.229, 0.224, 0.225])
        logits = self.session.run(None, {self.input_name: np.transpose(array, (2, 0, 1))[None, ...]})[0][0]
        probabilities = np.exp(logits - np.max(logits))
        probabilities /= probabilities.sum()
        index = int(np.argmax(probabilities))
        return {"disease": self.classes[index], "confidence": float(probabilities[index]), "heatmap": {"method": "model-inference", "area": "Grad-CAM requires a model export with feature maps; cloud result is classified without fabricated activation."}}
