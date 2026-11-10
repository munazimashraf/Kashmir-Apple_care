import hashlib
import io

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
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
from app.services.inference import InferenceUnavailable, get_classifier

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
        result = get_classifier().predict(content)
        dis_slug = result["disease"]
        advisory_data = build_advisory(
            disease=dis_slug,
            growth_stage=clean_stage,
            rain_within_12_hours=rain_within_12_hours,
        )
        return {
            "ai_engine": "Local VGG19 trained on supplied apple leaf datasets",
            "crop": "Apple (Malus domestica)",
            "crop_name": "Apple",
            "image_subject": "Apple Foliage Specimen",
            "disease": dis_slug,
            "disease_name": result["disease_name"],
            "kashmiri_name": advisory_data.get("kashmiri_name", "Tchunt"),
            "category": "Foliar Condition",
            "pathogen": result["scientific_name"],
            "urgency": "High" if result["severity"] == "moderate" else "Routine",
            "confidence": result["confidence"],
            "scab_percent": result["confidence"] if dis_slug == "apple_scab" else 0.0,
            "severity_grade": f"{result['severity'].upper()} Severity",
            "details": f"Classification produced by the local VGG19 model with {result['confidence']:.1f}% confidence.",
            "scab_details": f"Predicted class: {result['disease_name']}.",
            "hotspots": [],
            "top_predictions": result["top_predictions"],
            "other_findings": [],
            "recommendations": advisory_data.get("recommendations", []),
            "guardrails": advisory_data.get("guardrails", []),
        }
    except Exception as exc:
        if isinstance(exc, InferenceUnavailable):
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        raise HTTPException(status_code=500, detail=f"Local VGG19 diagnosis error: {exc}") from exc


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
    try:
        result = get_classifier().predict(content)
        predicted_disease = result["disease"]
        confidence = result["confidence"]
        heatmap = result["heatmap"]
    except InferenceUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

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
