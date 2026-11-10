import hashlib
import io
import logging
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from PIL import Image, UnidentifiedImageError
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

from app.api.deps import optional_current_user
from app.core.config import get_settings
from app.db.session import get_db
from app.models.entities import Diagnosis, User
from app.schemas.api import AppleDiseaseDetectResponse
from app.services.advisory import build_advisory
from app.services.inference import InferenceUnavailable, get_classifier

logger = logging.getLogger("applecare.disease_api")

router = APIRouter()


@router.post("/detect", response_model=AppleDiseaseDetectResponse)
async def detect_disease(
    file: UploadFile = File(...),
    user: User | None = Depends(optional_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Local VGG19 Apple Disease Detection.
    Receives an apple foliage image and classifies it using the trained model,
    and returns verified structured JSON adhering strictly to:
    {
      "disease": str,
      "scientific_name": str,
      "confidence": "high"|"medium"|"low"|"uncertain",
      "severity": "none"|"mild"|"moderate"|"severe",
      "symptoms": list[str],
      "visual_observations": list[str],
      "treatment": list[str],
      "prevention": list[str],
      "expert_consultation": bool
    }
    """
    # 1. Format Validation
    if file.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(
            status_code=415,
            detail="Unsupported image format. Please upload a JPEG, PNG, or WebP image."
        )

    # 2. Size Validation
    settings = get_settings()
    content = await file.read(settings.max_upload_bytes + 1)
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"Image exceeds upload limit of {settings.max_upload_bytes // (1024 * 1024)} MB."
        )

    # 3. Image Integrity Verification
    if HAS_PIL:
        try:
            pil_img = Image.open(io.BytesIO(content))
            pil_img.verify()
        except (UnidentifiedImageError, OSError) as exc:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is not a valid or readable image."
            ) from exc
    else:
        is_valid_header = (
            content.startswith(b"\xff\xd8\xff") or
            content.startswith(b"\x89PNG\r\n\x1a\n") or
            (content.startswith(b"RIFF") and b"WEBP" in content[:16])
        )
        if not is_valid_header:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file header is not a valid JPEG, PNG, or WebP image."
            )

    # 4. Local model analysis
    try:
        prediction = get_classifier().predict(content)
        advisory = build_advisory(
            disease=prediction["disease"],
            growth_stage="Green Tip",
            rain_within_12_hours=False,
        )
        result = {
            "disease": prediction["disease_name"],
            "scientific_name": prediction["scientific_name"],
            "confidence": prediction["confidence_label"],
            "severity": prediction["severity"],
            "symptoms": [f"Model prediction: {prediction['disease_name']}."],
            "visual_observations": [
                f"Local VGG19 classifier confidence: {prediction['confidence']:.1f}%.",
            ],
            "treatment": [
                f"{item['trade_name']}: {item['dosage_100l']}"
                for item in advisory["recommendations"]
            ],
            "prevention": advisory["guardrails"],
            "expert_consultation": prediction["confidence"] < 60,
            "ai_engine": "Local VGG19 trained on supplied apple leaf datasets",
            "hotspots": [],
            "confidence_numeric": prediction["confidence"],
            "scab_percent": prediction["confidence"] if prediction["disease"] == "apple_scab" else 0.0,
        }
    except InferenceUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Local model detection error: %s", exc)
        raise HTTPException(
            status_code=500,
            detail=f"Local VGG19 detection failed: {exc}"
        ) from exc

    # 5. Database Integration (Save to existing database history when user is authenticated)
    if user:
        try:
            sha256_hash = hashlib.sha256(content).hexdigest()
            record = Diagnosis(
                user_id=user.id,
                disease=result["disease"],
                confidence=float(result.get("confidence_numeric", 90.0)),
                growth_stage="Vegetative",
                image_sha256=sha256_hash,
                heatmap={
                    "scientific_name": result["scientific_name"],
                    "confidence_str": result["confidence"],
                    "severity": result["severity"],
                    "symptoms": result["symptoms"],
                    "visual_observations": result["visual_observations"],
                    "treatment": result["treatment"],
                    "prevention": result["prevention"],
                    "expert_consultation": result["expert_consultation"],
                    "ai_engine": result.get("ai_engine"),
                }
            )
            db.add(record)
            await db.commit()
            logger.info("Diagnosis history record saved for user: %s", user.id)
        except Exception as db_err:
            logger.warning("Could not persist diagnosis to database: %s", db_err)

    return result
