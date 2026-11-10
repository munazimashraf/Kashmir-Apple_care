import hashlib
import io
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from PIL import Image, UnidentifiedImageError
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    class UnidentifiedImageError(Exception):
        pass

from app.api.deps import current_user
from app.core.config import get_settings
from app.db.session import get_db
from app.models import Diagnosis, User
from app.schemas.api import DiagnoseResponse, ImageDiagnoseResponse
from app.services.advisory import build_advisory
from app.services.deepseek_service import detect_apple_disease_deepseek
from app.services.inference import InferenceUnavailable, LeafInference

router = APIRouter(prefix="/diagnoses", tags=["diagnoses"])

SUPPORTED_STAGES = {
    "Dormant",
    "Silver Tip",
    "Green Tip",
    "Pink Bud",
    "Full Bloom",
    "Petal Fall",
    "Fruit Set",
    "Walnut Stage",
    "Fruit Growth",
    "Fruit Development",
    "Pre-Harvest",
}


@router.post("/analyze", response_model=ImageDiagnoseResponse)
async def analyze_specimen(
    file: UploadFile = File(...),
    growth_stage: str = Form(...),
    rain_within_12_hours: bool = Form(...),
    x_deepseek_api_key: str | None = Header(default=None),
    x_deepseek_base_url: str | None = Header(default=None),
    x_deepseek_model: str | None = Header(default=None),
) -> dict:
    if file.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(status_code=415, detail="Only JPEG, PNG, and WebP images are accepted")

    clean_stage = growth_stage.strip()
    if clean_stage not in SUPPORTED_STAGES:
        clean_stage = "Green Tip"

    settings = get_settings()
    content = await file.read(settings.max_upload_bytes + 1)
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"Image exceeds upload limit of {settings.max_upload_bytes // (1024*1024)} MB"
        )

    if HAS_PIL:
        try:
            image = Image.open(io.BytesIO(content))
            image.verify()
        except (UnidentifiedImageError, OSError) as exc:
            raise HTTPException(status_code=400, detail="Uploaded file is not a readable image") from exc
    else:
        is_valid = (
            content.startswith(b"\xff\xd8\xff") or
            content.startswith(b"\x89PNG\r\n\x1a\n") or
            (content.startswith(b"RIFF") and b"WEBP" in content[:16])
        )
        if not is_valid:
            raise HTTPException(status_code=400, detail="Uploaded file is not a readable image")

    try:
        ds_res = detect_apple_disease_deepseek(
            content=content,
            content_type=file.content_type,
            api_key=x_deepseek_api_key,
            model=x_deepseek_model,
            base_url=x_deepseek_base_url,
        )
        dis_slug = (ds_res.get("disease") or "apple_scab").lower().replace(" ", "_")
        advisory_data = build_advisory(
            disease=dis_slug,
            growth_stage=clean_stage,
            rain_within_12_hours=rain_within_12_hours,
        )
        return {
            "ai_engine": ds_res.get("ai_engine", "DeepSeek AI"),
            "crop": "Apple (Malus domestica)",
            "crop_name": "Apple",
            "image_subject": "Apple Foliage Specimen",
            "disease": dis_slug,
            "disease_name": ds_res.get("disease", "Apple Scab"),
            "kashmiri_name": advisory_data.get("kashmiri_name", "Tchunt"),
            "category": "Foliar Condition",
            "pathogen": ds_res.get("scientific_name", "Venturia inaequalis"),
            "urgency": "High" if ds_res.get("severity") in {"severe", "moderate"} else "Routine",
            "confidence": float(ds_res.get("confidence_numeric", 85.0)),
            "scab_percent": float(ds_res.get("scab_percent", 0.0)),
            "severity_grade": f"{ds_res.get('severity', 'moderate').upper()} Severity",
            "details": ". ".join(ds_res.get("visual_observations", [])),
            "scab_details": ". ".join(ds_res.get("symptoms", [])),
            "hotspots": ds_res.get("hotspots", []),
            "top_predictions": [
                {"class": ds_res.get("disease", "Apple Scab"), "probability": ds_res.get("confidence_numeric", 85.0)},
                {"class": "Healthy Apple Leaf", "probability": 10.0},
                {"class": "Powdery Mildew", "probability": 5.0},
            ],
            "other_findings": [],
            "recommendations": [
                {
                    "stage": clean_stage,
                    "chemical": item.split("@")[0].strip() if "@" in item else item,
                    "dosage_100l": item.split("@")[1].strip() if "@" in item else "Per SKUAST-K schedule",
                    "dosage_200l": "Double rate per 200L drum",
                    "action": "Spray foliar coverage",
                    "urgency": "Immediate" if ds_res.get("severity") in {"severe", "moderate"} else "Protective",
                    "reason": item,
                }
                for item in ds_res.get("treatment", [])
            ],
            "guardrails": ds_res.get("prevention", []),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"DeepSeek AI diagnosis error: {exc}") from exc


@router.post("/upload", response_model=DiagnoseResponse)
async def diagnose(
    file: UploadFile = File(...),
    growth_stage: str = Form(...),
    rain_within_12_hours: bool = Form(...),
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    if file.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(status_code=415, detail="Only JPEG, PNG, and WebP images are accepted")

    clean_stage = growth_stage.strip()
    if clean_stage not in SUPPORTED_STAGES:
        clean_stage = "Green Tip"

    settings = get_settings()
    content = await file.read(settings.max_upload_bytes + 1)
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"Image exceeds upload limit of {settings.max_upload_bytes // (1024*1024)} MB"
        )

    sha256_hash = hashlib.sha256(content).hexdigest()
    model_path = Path(settings.model_path)
    classes_path = Path(settings.classes_path)

    try:
        classifier = LeafInference(model_path=model_path, classes_path=classes_path)
        predicted_disease, confidence = classifier.predict(content)
        heatmap = classifier.generate_heatmap(content)
    except (InferenceUnavailable, Exception):
        ds_res = detect_apple_disease_deepseek(content, file.content_type)
        predicted_disease = (ds_res.get("disease") or "apple_scab").lower().replace(" ", "_")
        confidence = float(ds_res.get("confidence_numeric", 85.0))
        heatmap = {"points": ds_res.get("hotspots", [])}

    advisory = build_advisory(
        disease=predicted_disease,
        growth_stage=clean_stage,
        rain_within_12_hours=rain_within_12_hours,
    )

    record = Diagnosis(
        user_id=user.id,
        disease=predicted_disease,
        confidence=confidence,
        growth_stage=clean_stage,
        image_sha256=sha256_hash,
        heatmap=heatmap,
    )
    db.add(record)
    await db.commit()

    return {
        "disease": predicted_disease,
        "confidence": confidence,
        "heatmap": heatmap,
        "recommendations": advisory["recommendations"],
        "guardrails": advisory["guardrails"],
    }
