# Machine Learning Models & Ensemble Learning

This directory contains the training, feature extraction, and ensembling pipelines for Kashmiri apple leaf disease classification.

## Supported Architectures & Ensembles

1. **VGG-16** (138.4M parameters): Deep sequential convolutional network with 16 weight layers.
2. **VGG-19** (143.7M parameters): 19-layer sequential convolutional hierarchy with rich high-level texture representations.
3. **ResNet-50** (25.6M parameters): 50-layer deep residual highway network with identity skip-connections.
4. **XGBoost (Standalone)** (0.5M parameters): Gradient Boosted Decision Trees trained directly on 3,072-dimensional multi-backbone deep feature embeddings (`[ResNet50, VGG16, VGG19]`).
5. **Hard-Voting Ensemble**: Majority consensus voting across discrete model predictions.
6. **Soft-Voting Ensemble**: Validation-calibrated Bayesian probability averaging.
7. **Stacking Ensemble (XGBoost Meta-Learner)**: Level-0 base CNN models generate posterior probability vectors; a Level-1 XGBoost classifier learns the non-linear decision boundaries.

---

## Performance Comparison (Kashmiri Apple Diseases)

Evaluated on stratified test samples across all 6 Kashmiri apple conditions (*Alternaria Leaf Blotch, Apple Scab (Tchoke), Black Rot, Cedar Apple Rust, Healthy, Powdery Mildew*):

| Model / Ensemble Architecture | Accuracy | Macro Precision | Macro Recall | Macro F1-Score | Parameter Count |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **VGG-16** | 90.74% | 91.49% | 90.74% | 90.76% | 138.4 M |
| **VGG-19** | 79.63% | 79.23% | 79.63% | 78.80% | 143.7 M |
| **ResNet-50** | 93.52% | 93.64% | 93.52% | 93.49% | 25.6 M |
| **XGBoost (Standalone)** | 85.19% | 85.34% | 85.19% | 84.97% | 0.5 M |
| **Hard-Voting Ensemble** | 89.81% | 89.80% | 89.81% | 89.76% | 308.0 M |
| **Soft-Voting Ensemble** | 90.74% | 91.03% | 90.74% | 90.75% | 308.0 M |
| **Stacking Ensemble (XGBoost Meta-Learner)** | **93.52%** | **94.44%** | **93.52%** | **93.67%** | **308.1 M** |

### Per-Class F1-Scores for Stacking Ensemble
- **Alternaria Leaf Blotch**: 94.12% F1 (100% Precision)
- **Apple Scab (Tchoke)**: 94.12% F1 (100% Precision)
- **Black Rot**: 92.31% F1 (100% Recall)
- **Cedar Apple Rust**: 97.14% F1 (100% Precision)
- **Healthy Foliage**: 87.18% F1 (94.44% Recall)
- **Powdery Mildew**: 97.14% F1 (100% Precision)

---

## Running the Ensemble Pipeline

```bash
# 1. Install dependencies
pip install -r ml/requirements.txt

# 2. Run two-stage orchestrated pipeline
python ml/train_and_evaluate_ensemble.py
```

Outputs are automatically saved to `artifacts/ensemble/`:
- `performance_comparison.json`: Comprehensive precision, recall, F1, and latency metrics.
- `confusion_matrices.json`: Complete 6x6 confusion matrices for every model.
- `xgboost_standalone.json`: Trained standalone XGBoost model.
- `xgboost_stacker.json`: Trained Level-1 XGBoost meta-learner.
