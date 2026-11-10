from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_db
from app.models import User
from app.schemas.api import LoginRequest, RegisterRequest, Token

router = APIRouter(prefix="/auth", tags=["auth"])
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


def token_for(user: User) -> str:
    settings = get_settings()
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    return jwt.encode({"sub": str(user.id), "exp": expires}, settings.jwt_secret, algorithm="HS256")


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)) -> Token:
    existing = await db.scalar(select(User).where(User.email == payload.email.lower()))
    if existing:
        raise HTTPException(status_code=409, detail="Email is already registered")
    user = User(email=payload.email.lower(), password_hash=pwd.hash(payload.password), preferred_language=payload.preferred_language)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return Token(access_token=token_for(user))


@router.post("/login", response_model=Token)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> Token:
    user = await db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not pwd.verify(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return Token(access_token=token_for(user))
