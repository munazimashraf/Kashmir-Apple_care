from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.db.base import Base

settings = get_settings()

connect_args = {}
if "sqlite" in settings.database_url:
    connect_args = {"check_same_thread": False}

db_url = settings.database_url
if db_url.startswith("sqlite:///"):
    db_url = db_url.replace("sqlite:///", "sqlite+aiosqlite:///")
elif db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(
    db_url,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=False,
)

SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_db() -> None:
    """Initialize database tables if they do not exist."""
    # Ensure all models are registered on Base.metadata
    import app.models.entities  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session
