# AppleCare Kashmir — AI Leaf Disease Diagnosis

Free-first, offline-capable disease diagnosis and advisory platform tailored for apple growers in Kashmir. Aligned with the official **SKUAST-K (Sher-e-Kashmir University of Agricultural Sciences and Technology of Kashmir)** annual apple spray schedule.

---

## 🌟 Key Features

1. **High-Accuracy Neural Classifier (98.04% Test Accuracy)**
   - Powered by a fine-tuned MobileNetV3-Large deep convolutional network with Squeeze-and-Excitation attention.
   - Trained on Kashmir indigenous and PlantVillage datasets across 6 apple leaf conditions:
     - Apple Scab (*Venturia inaequalis* / ژھوکھ)
     - Alternaria Leaf Blotch (*Alternaria mali* / ڈاگ)
     - Powdery Mildew (*Podosphaera leucotricha* / پھپھوند)
     - Black Rot & Canker (*Botryosphaeria obtusa* / سیاہی ڈاگ)
     - Cedar Apple Rust (*Gymnosporangium juniperi-virginianae* / زنگ ڈاگ)
     - Healthy Clean Foliage (*Malus domestica* / صحت مند پَن)
   - Exported to ONNX runtime for ultra-fast, lightweight inference (~15ms per image).

2. **Inappropriate / Non-Plant Image Guard**
   - Automatically detects and rejects non-plant images (vehicles, people, animals, electronics, documents, furniture, indoor scenes).
   - Prominently flags: `⚠️ Inappropriate Image: Not a Plant Leaf` and suppresses disease classification to avoid improper chemical spraying.

3. **Official SKUAST-Kashmir Integrated Pest Management (IPM) Advisory**
   - Stage-specific chemical recommendations (Green Tip, Pink Bud, Full Bloom, Petal Fall, Fruit Growth).
   - Commercial product names (Mancozeb 75 WP, Propineb 70 WP, Score 25 EC / Difenoconazole, Dodine 65 WP, Nativo 75 WG, Topas 10 EC).
   - Exact SKUAST-K recommended dosages per 100 Litres of water.
   - Cultural sanitation practices (5% Urea spray on post-harvest leaf litter, silver terminal removal, pruning wound Chaubattia paste sealing).
   - Pollinator shield: strictly prohibits chemical insecticide/acaricide spraying during Full Bloom.
   - Quality booster: foliar Calcium Chloride (3–4g/L) during Fruit Growth to prevent Bitter Pit in cold storage.

4. **Microclimate Weather Integration**
   - Live Open-Meteo GPS weather and 10 Kashmir apple districts selector (Pulwama, Sopore, Baramulla, Shopian, Srinagar, Anantnag, Kulgam, Kupwara, Budgam, Ganderbal).
   - Real-time 12-hour spray safety window (Dry Foliage Window vs. Rain Postponement Warning).

5. **Multi-lingual Audio Advisory**
   - Field voice synthesis in **Urdu (اردو)**, **Kashmiri (کٲشُرۍ)**, and **English** for orchard field teams.

---

## 📁 Repository Structure

```text
├── artifacts/
│   └── applecare-six/
│       ├── applecare_mobilenetv3.onnx   # Production ONNX model (98.04% accuracy)
│       ├── best.pt                     # PyTorch trained checkpoint
│       ├── classes.json                # Configured class labels
│       └── metrics.json                # Test evaluation report & confusion matrix
├── backend/
│   ├── app/
│   │   ├── api/                        # FastAPI endpoints (auth, diagnoses, weather, logs)
│   │   ├── core/                       # App configuration and settings
│   │   ├── db/                         # Database engine & session
│   │   ├── models/                     # SQLAlchemy ORM entities
│   │   ├── schemas/                    # Pydantic request/response schemas
│   │   └── services/
│   │       ├── advisory.py             # SKUAST-K Kashmir Spray Schedule engine
│   │       ├── inference.py            # ONNX leaf disease classifier
│   │       ├── plant_guard.py          # Plant verification & non-plant rejection
│   │       └── weather.py              # Weather integration
│   ├── tests/
│   │   └── test_api_and_guards.py      # Automated test suite (100% pass)
│   ├── Dockerfile
│   └── requirements.txt
├── data/
│   └── apple/                          # Train, val, test datasets
├── dist/                               # Production frontend build
├── index.html                          # Modern responsive web interface
├── ml/
│   ├── train_apple_model.py            # MobileNetV3-Large training & export pipeline
│   └── requirements.txt
├── mobile/                             # Flutter mobile client
└── docker-compose.yml
```

---

## 🚀 Running the Project

### 1. Web Frontend
To run the browser application:
```bash
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173). The interface supports drag-and-drop photo uploads, camera captures, and built-in interactive sample tests.

### 2. FastAPI Backend
```bash
PYTHONPATH=backend python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- Health Check: `GET http://127.0.0.1:8000/health`
- Diagnosis Endpoint: `POST http://127.0.0.1:8000/api/v1/diagnoses/upload`

### 3. Run Automated Tests
```bash
PYTHONPATH=backend pytest backend/tests/test_api_and_guards.py
```

### 4. Model Re-training & Export
```bash
PYTHONUNBUFFERED=1 python3 ml/train_apple_model.py --epochs 3 --batch-size 32
```
Outputs model metrics to `artifacts/applecare-six/metrics.json` and ONNX model to `artifacts/applecare-six/applecare_mobilenetv3.onnx`.

---

## 📊 Evaluation Metrics

| Disease Class | Precision | Recall | F1-Score | Support |
| :--- | :---: | :---: | :---: | :---: |
| **Alternaria Leaf Blotch** | 99.29% | 95.25% | 97.23% | 295 |
| **Apple Scab** | 94.61% | 96.61% | 95.60% | 236 |
| **Black Rot** | 96.89% | 96.89% | 96.89% | 225 |
| **Cedar Apple Rust** | 100.0% | 100.0% | 100.0% | 80 |
| **Healthy Leaf** | 99.17% | 99.72% | 99.45% | 721 |
| **Powdery Mildew** | 88.89% | 100.0% | 94.12% | 24 |
| **Overall Test Accuracy** | **98.04%** | **98.04%** | **98.04%** | **1,581** |

---

## ⚖️ Safety & SKUAST-K Guidelines

Advisories encode official SKUAST-K recommended fungicides, dosages per 100L water, rain wash-off postponement rules, and Full Bloom pollinator safeguards. Always consult a certified local Horticulture Development Officer (HDO) and inspect registered chemical packaging labels before operational application.
