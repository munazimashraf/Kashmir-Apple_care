from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import current_user
from app.db.session import get_db
from app.models import SprayLog, User
from app.schemas.api import SprayLogCreate

router = APIRouter(prefix="/spray-logs", tags=["spray logs"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_log(payload: SprayLogCreate, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)) -> dict:
    log = SprayLog(user_id=user.id, **payload.model_dump())
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return {"id": str(log.id), "status": "recorded"}


@router.get("")
async def list_logs(user: User = Depends(current_user), db: AsyncSession = Depends(get_db)) -> list[dict]:
    result = await db.scalars(select(SprayLog).where(SprayLog.user_id == user.id).order_by(SprayLog.sprayed_at.desc()))
    return [{"id": str(log.id), "orchard_id": str(log.orchard_id) if log.orchard_id else None, "product": log.product, "dosage": log.dosage, "sprayed_at": log.sprayed_at.isoformat(), "notes": log.notes} for log in result]
