# Kashmir Apple Care 🍏
### OpenRouter Free Multimodal Vision AI & SKUAST-K Orchard Pathology Platform

**Kashmir Apple Care** is a production plant pathology intelligence system powered by **OpenRouter Free Vision AI** (`qwen/qwen-2.5-vl-72b-instruct:free`, `meta-llama/llama-3.2-11b-vision-instruct:free`, `google/gemini-2.0-flash-exp:free`) engineered for orchardists, agronomists, and researchers across Jammu & Kashmir and agricultural belts worldwide.

The platform integrates OpenRouter multimodal vision diagnostics to identify apple foliar diseases and other conditions, returning certified structured JSON results paired with official **SKUAST-K (Sher-e-Kashmir University of Agricultural Sciences & Technology of Kashmir)** chemical prescriptions, dual 100L and 200L drum dosages, and live environmental micro-climate guardrails.

---

## 🌟 OpenRouter Vision AI Capabilities

### 1. Dedicated Disease Detection Endpoint: `POST /api/disease/detect`
- **OpenRouter Endpoint**: `https://openrouter.ai/api/v1/chat/completions`
- **Supported Vision Models**:
  - `qwen/qwen-2.5-vl-72b-instruct:free` (Default, 72B Multimodal Vision at zero cost)
  - `meta-llama/llama-3.2-11b-vision-instruct:free`
  - `google/gemini-2.0-flash-exp:free`
- **Covered Apple Conditions**:
  - Apple Scab (*Venturia inaequalis*)
  - Cedar Apple Rust (*Gymnosporangium juniperi-virginianae*)
  - Powdery Mildew (*Podosphaera leucotricha*)
  - Marssonina Leaf Blotch (*Marssonina coronaria*)
  - Alternaria Leaf Spot (*Alternaria alternata f. sp. mali*)
  - Black Rot (*Botryosphaeria obtusa*)
  - Healthy Apple Leaf (*Normal foliar tissue*)
  - Unknown Disease (*Unclear or non-apple specimen flagged for expert review*)

### 2. Strict Structured JSON Output Schema
```json
{
  "disease": "Apple Scab",
  "scientific_name": "Venturia inaequalis",
  "confidence": "medium",
  "severity": "moderate",
  "symptoms": [
    "Velvety olive-green to dark brown lesions on foliar surface",
    "Foliar distortion and puckering along lesion margins"
  ],
  "visual_observations": [
    "Multiple discrete circular to irregular fungal spots distributed across upper foliage surface",
    "Active conidial margins indicating ongoing sporulation"
  ],
  "treatment": [
    "Apply protectant fungicide: Mancozeb 75 WP @ 300g/100L water (600g per 200L tractor drum) before rain",
    "Systemic curative intervention: Difenoconazole 25 EC @ 30ml/100L water within 72 hours of primary infection"
  ],
  "prevention": [
    "Prune orchard canopy during dormancy to promote 360° airflow and rapid foliage drying",
    "Rake, compost, or flail-mow fallen autumn leaves to eliminate overwintering fungal pseudothecia"
  ],
  "expert_consultation": true
}
```

### 3. Accuracy & Guardrails
- **No Fabricated Confidence Scores**: Returns calibrated levels: `high`, `medium`, `low`, or `uncertain`.
- **Unclear Image Flagging**: If the specimen cannot be diagnosed with certainty, returns `"disease": "Unknown Disease"`, `"confidence": "uncertain"`, and `"expert_consultation": true`.
- **Separation of Concerns**: Visual observations are strictly segregated from agronomic treatment guidance.
- **Database History Logging**: Authenticated diagnoses are automatically persisted to the existing SQLite `diagnoses` table.

---

## ⚙️ Configuration & Environment Variables

Configure OpenRouter API credentials in `.env` (or pass via request headers `x-openrouter-api-key` and `x-openrouter-model`):

```env
# OpenRouter API Configuration
OPENROUTER_API_KEY=sk-or-v1-your-openrouter-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=qwen/qwen-2.5-vl-72b-instruct:free
```

*Note: The frontend never exposes your backend API key. Users can either store their own free OpenRouter key in their browser localStorage or utilize the backend environment key or built-in offline engine.*

---

## 🧪 Testing the OpenRouter Integration

Run the automated verification suite to test multimodal image analysis and schema validation:

```bash
# In KASHMIR APPLE CARE directory
python test_openrouter.py
```

---

## 🚀 How to Run

### Option 1: Full Stack (Frontend + FastAPI Backend)
Double-click **`start_all.bat`**.
- Web Client: **`http://localhost:5173`**
- FastAPI Backend: **`http://localhost:8000`** (Swagger docs at **`http://localhost:8000/docs`**)

### Option 2: Backend Only
Double-click **`start_backend.bat`**.

### Option 3: Frontend Only
Double-click **`start_frontend.bat`**.

---

## 🌟 Qwen 2.5-VL Multimodal AI Capabilities

### 1. Powered by Qwen 2.5-VL Multimodal Vision
- **Flexible Qwen Engine Integration**:
  - **OpenRouter Free Tier**: `qwen/qwen-2.5-vl-72b-instruct:free`
  - **Alibaba Cloud DashScope**: `qwen-vl-max`, `qwen2.5-vl-72b-instruct`
  - **Local Ollama / vLLM**: `http://localhost:11434/v1` (`ollama run qwen2.5-vl`)
  - **Built-in Qwen Expert Engine**: Operates instantly with zero external API keys or offline in the field.
- **Universal Disease & Fungus Detection**:
  - **Fungal Ascomycetes**: Apple Scab (*Venturia inaequalis*), Powdery Mildew (*Podosphaera / Erysiphales*), Alternaria Blotch & Early Blight (*Alternaria mali / solani*), Anthracnose (*Colletotrichum*), Gray Mold (*Botrytis cinerea*), Septoria Leaf Spot, Black Rot (*Botryosphaeria / Guignardia*), Marssonina Blotch.
  - **Fungal Basidiomycetes**: Foliar Rusts & Cedar Apple Rust (*Pucciniales / Gymnosporangium / Puccinia sorghi*).
  - **Oomycetes (Water Molds)**: Tomato & Potato Late Blight (*Phytophthora infestans*), Grape Downy Mildew (*Plasmopara viticola*), Cucurbit Downy Mildew.
  - **Bacterial Pathogens**: Bacterial Spot (*Xanthomonas*), Fire Blight (*Erwinia amylovora*), Bacterial Cankers (*Pseudomonas*).
  - **Acarina Pests**: European Red Mite (*Panonychus ulmi*), Two-Spotted Spider Mite (*Tetranychus urticae*).
  - **Physiological Disorders**: Bitter Pit (Calcium Deficiency), Corking, Chlorosis.
  - **Healthy Crop Foliage**: High-accuracy baseline for healthy plant canopies.
- **Top-5 Neural Probability Ranking**: Displays sorted class probabilities with visual distribution bars.
- **Dynamic Lesion Centroid Pinpointing**: Automatically detects lesion centers and renders coordinate rings (`L1`, `L2`, ...) over active conidial colonies directly on the specimen canvas.
- **Agronomic Severity Indexing**: Quantifies tissue surface infection percentage into standardized agronomic grades (Grade 0: Healthy to Grade 4: Epidemic).

### 2. Dual Spray Drum Agronomic Calculations
- **Field-Calibrated Trade Brands**: Formulations with commercial trade names used in Kashmir (*Indofil M-45*, *Antracol 70 WP*, *Score 25 EC*, *Syllit 65 WP*, *Contaf 5 EC*, *Topas 10 EC*, *Ridomil Gold 68 WG*, *Curzate M-8*, *Nativo 75 WG*, *Maiden 5.45 EC*, *Oberon 22.9 SC*, *Calcium Chloride 77%*).
- **Dual Dosage Breakdown**: Formulated for both **per 100L water** and **per standard 200L Kashmir Tractor / Power Sprayer Drum**.
- **Rainfastness & Pre-Harvest Intervals**: Specifies exact drying hours before rain and safe harvest wait days (PHI).

### 3. Smart Field Guardrails
- **12-Hour Rain Postponement Warning**: Integrates live GPS geolocation with Kashmir district selectors to alert against spraying prior to rain events.
- **Honeybee Pollinator Shield**: Enforces strict prohibition of synthetic chemical insecticides during **Full Bloom** to protect pollinators essential for fruit set.
- **Bitter Pit Calcium Booster**: Prompts foliar Calcium Chloride 77% sprays (3–4g/L) during Fruit Growth and Walnut stages.

### 4. Alibaba Qwen AI Login Prompt & Specimen Upload Flow
- **Automatic Login & Connect Prompt on Photo Upload**:
  - When an orchardist or researcher uploads a photo (via file picker, drag & drop, or camera viewfinder), if unauthenticated, the system automatically presents the **Alibaba Qwen AI Login & Connect Prompt**.
  - Direct quick-links to obtain API keys:
    - 🔗 **Alibaba Cloud Model Studio (Official Bailian Console)**: `https://bailian.console.alibabacloud.com` / `https://dashscope.console.aliyun.com` (Model: `qwen-vl-max`, `qwen2.5-vl-72b-instruct`)
    - 🔗 **Free OpenRouter Qwen Tier**: `https://openrouter.ai/keys` (Model: `qwen/qwen-2.5-vl-72b-instruct:free`)
  - **Single-Click Authentication**: "Sign In & Scan Specimen with Qwen AI" stores credentials locally and seamlessly executes the upload.
  - **Zero-Block Guest Mode**: "Continue in Guest Mode (Offline Qwen Engine)" allows instant scanning and testing with the built-in offline Qwen engine without requiring any key.
  - **Account Status Indicator**: Top navigation pill displays real-time connection status (`🟢 Alibaba Qwen AI: Connected (sk-...)`, `🟡 Qwen AI: Guest Mode`, or `⚪ Connect Alibaba Qwen AI`) with instant account switching and sign-out.

### 5. Labeled Kashmir Apple Care Pathology Dashboard
- When Qwen AI completes the multimodal scan, the results are meticulously labeled across the system:
  - **Engine Badge**: Labeled with exact model used (`Alibaba Cloud DashScope (qwen-vl-max)` or `Alibaba Qwen 2.5-VL`).
  - **Host Crop & Taxonomy**: Host plant identification + binomial pathogen classification (*Venturia inaequalis*, etc.) + Kashmiri local name (*چھچ / کۄل چَھچ*).
  - **Hotspot Overlay Rings**: High-precision conidial lesion markers (`L1`, `L2`, ...) projected directly onto the specimen canvas.
  - **Top-5 Probability Ranking**: Neural probability distribution bars for primary diagnosis and differentials.
  - **Tissue Colonization & Clinical Grade**: Scab surface area percentage mapped to standardized clinical grades.
  - **Microscopic Diagnostic Notes**: Qwen AI's visual reasoning, lesion margins, and conidial felt texture observations.
  - **SKUAST-K Chemical Prescriptions**: Kashmiri trade formulations (*Score 25 EC*, *Indofil M-45*, *Syllit 65 WP*, etc.) with dual **100L Water** & **200L Tractor Drum** calibrations.
  - **Environmental Guardrails**: Live 12-hour rainfastness weather warning, Honeybee pollinator shield during Full Bloom, and pre-harvest intervals (PHI).
  - **Multilingual Audio Advisor**: Voice advisory read in Kashmiri, Urdu, and English.
  - **Official Diagnostic Report**: Exportable agronomic certificate ready for printing or copying.

---

## 🚀 Quick Launch Guide

### Option 1: Web Interface Only (Fastest)
Double-click **`start_frontend.bat`** (or run `npx vite`).
Open: **`http://localhost:5173`**

### Option 2: Full Stack (Frontend + FastAPI Backend)
Double-click **`start_all.bat`**.
- Web Client: **`http://localhost:5173`**
- FastAPI Backend API: **`http://localhost:8000`** (Interactive OpenAPI docs at **`http://localhost:8000/docs`**)

### Option 3: Backend API Only
Double-click **`start_backend.bat`**.
API endpoint: **`http://localhost:8000`**
