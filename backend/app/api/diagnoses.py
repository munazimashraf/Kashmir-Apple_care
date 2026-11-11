import hashlib
import io
import logging
from typing import Optional
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import optional_current_user
from app.core.config import get_settings
from app.db.session import get_db
from app.models import Diagnosis, User
from app.schemas.api import DiagnoseResponse
from app.services.advisory import build_advisory
from app.services.inference import InferenceUnavailable, LeafInference

LOGGER = logging.getLogger("applecare.api.diagnoses")
router = APIRouter(prefix="/diagnoses", tags=["diagnoses"])


@router.post("/upload", response_model=DiagnoseResponse)
async def diagnose(
    file: UploadFile = File(...),
    growth_stage: str = Form("Green Tip"),
    variety: str = Form("Red Delicious"),
    root_type: str = Form("Seedling (Standard Vigorous)"),
    rain_within_12_hours: bool = Form(False),
    user: Optional[User] = Depends(optional_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    if file.content_type not in {"image/jpeg", "image/png", "image/webp", "image/jpg", "application/octet-stream"}:
        raise HTTPException(status_code=415, detail="Only JPEG, PNG, and WebP images are accepted")

    content = await file.read(get_settings().max_upload_bytes + 1)
    if len(content) > get_settings().max_upload_bytes:
        raise HTTPException(status_code=413, detail="Image exceeds the 10MB upload limit")

    try:
        image = Image.open(io.BytesIO(content))
        image.verify()
        image = Image.open(io.BytesIO(content)).convert("RGB")
    except (UnidentifiedImageError, OSError) as exc:
        raise HTTPException(status_code=400, detail="Uploaded file is not a readable image") from exc

    try:
        result = LeafInference().predict(image)
    except InferenceUnavailable as exc:
        LOGGER.error("Inference unavailable: %s", exc)
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    # Inappropriate or non-plant image handling
    if result.get("inappropriate"):
        return {
            **result,
            "disease_common": "Inappropriate Image (Not a Plant)",
            "disease_scientific": "Out of domain",
            "kashmiri_name": "Ghair Muta'aliq Tasveer",
            "recommendations": [],
            "cultural_measures": [
                "Please photograph a real apple leaf in good lighting.",
                "Ensure the camera is focused on the leaf surface showing visible veins or symptoms.",
                "Do not upload people, animals, vehicles, documents, or indoor items.",
            ],
            "guardrails": [
                "⚠️ INAPPROPRIATE IMAGE: The system detected that this photo is not a plant or foliage.",
                "SKUAST-K advisory is strictly reserved for apple leaf pathologies.",
                "Please upload a genuine apple leaf photo to get diagnostic guidance.",
            ],
        }

    # Generate full SKUAST-K Advisory
    advisory = build_advisory(
        result["disease"] if not result["uncertain"] else "__uncertain__",
        growth_stage,
        rain_within_12_hours,
        variety=variety,
        root_type=root_type,
    )

    # Save to history if an authenticated user session is active
    if user is not None:
        try:
            diagnosis = Diagnosis(
                user_id=user.id,
                disease=result["disease"],
                confidence=result["confidence"],
                growth_stage=growth_stage,
                image_sha256=hashlib.sha256(content).hexdigest(),
                heatmap=result["heatmap"],
            )
            db.add(diagnosis)
            await db.commit()
        except Exception as exc:
            LOGGER.warning("Could not persist diagnosis record: %s", exc)

    return {**result, **advisory}
