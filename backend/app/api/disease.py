import hashlib
import io
import logging
from typing import Any

from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile
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
from app.services.deepseek_service import detect_apple_disease_deepseek

logger = logging.getLogger("applecare.disease_api")

router = APIRouter()


@router.post("/detect", response_model=AppleDiseaseDetectResponse)
async def detect_disease(
    file: UploadFile = File(...),
    x_deepseek_api_key: str | None = Header(default=None),
    x_deepseek_model: str | None = Header(default=None),
    user: User | None = Depends(optional_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    AI-powered Apple Disease Detection using DeepSeek AI.
    Receives an apple foliage or fruit image, sends to DeepSeek multimodal API,
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

    # 4. DeepSeek AI Analysis
    try:
        result = detect_apple_disease_deepseek(
            content=content,
            content_type=file.content_type or "image/jpeg",
            api_key=x_deepseek_api_key,
            model=x_deepseek_model,
        )
    except Exception as exc:
        logger.error("DeepSeek detection error: %s", exc)
        raise HTTPException(
            status_code=500,
            detail=f"DeepSeek vision detection failed: {exc}"
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
