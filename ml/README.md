# Training the real leaf model

Use the PlantVillage apple images plus Kashmir field images arranged in `train`,
`val`, and `test` folders. Each split must contain the seven class directories
listed in `train_apple_model.py`. Keep field images in the validation/test
splits to measure domain shift instead of reporting only laboratory accuracy.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r ml/requirements.txt
python ml/train_apple_model.py --data-dir data/apple --output-dir artifacts/applecare
```

The script writes a checkpoint, `metrics.json`, `classes.json`, and an ONNX
model. For mobile export:

```bash
pip install -r ml/requirements-tflite.txt
python ml/train_apple_model.py --data-dir data/apple --output-dir artifacts/applecare
```

The training script invokes `onnx2tf` and TensorFlow's converter and writes a
quantized `applecare_mobilenetv3.tflite`. Copy that model and `classes.json`
into the Flutter app's assets after reviewing test metrics and validating
representative Kashmir field images.
