from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import current_user
from app.db.session import get_db
from app.models import Orchard, User
from app.schemas.api import OrchardCreate, OrchardResponse

router = APIRouter(prefix="/orchards", tags=["orchards"])


@router.post("", response_model=OrchardResponse, status_code=status.HTTP_201_CREATED)
async def create_orchard(payload: OrchardCreate, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)) -> Orchard:
    orchard = Orchard(owner_id=user.id, **payload.model_dump())
    db.add(orchard)
    await db.commit()
    await db.refresh(orchard)
    return orchard


@router.get("", response_model=list[OrchardResponse])
async def list_orchards(user: User = Depends(current_user), db: AsyncSession = Depends(get_db)) -> list[Orchard]:
    result = await db.scalars(select(Orchard).where(Orchard.owner_id == user.id).order_by(Orchard.name))
    return list(result)
