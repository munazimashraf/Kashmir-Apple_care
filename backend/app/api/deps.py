from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_db
from app.models import User

security = HTTPBearer()
security_optional = HTTPBearer(auto_error=False)


async def current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: AsyncSession = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(credentials.credentials, get_settings().jwt_secret, algorithms=["HS256"])
        user_id = UUID(payload["sub"])
    except (JWTError, KeyError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="Invalid access token") from exc
    user = await db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


async def optional_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_optional),
    db: AsyncSession = Depends(get_db)
) -> User | None:
    if not credentials:
        return None
    try:
        payload = jwt.decode(credentials.credentials, get_settings().jwt_secret, algorithms=["HS256"])
        user_id = UUID(payload["sub"])
        user = await db.scalar(select(User).where(User.id == user_id))
        return user
    except Exception:
        return None
