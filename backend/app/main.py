import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api import auth, diagnoses, disease, logs, orchards, weather
from app.core.config import get_settings
from app.db.session import init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("applecare.api")
limiter = Limiter(key_func=get_remote_address, default_limits=["120/minute"])


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Starting Kashmir Apple Care API with DeepSeek AI Engine")
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as exc:
        logger.warning(f"Database auto-init notice: {exc}")
    yield
    logger.info("Stopping Kashmir Apple Care API")


app = FastAPI(
    title=get_settings().app_name,
    version="2.0.0",
    description="Kashmir Apple Care AI Orchard Disease Diagnostic & SKUAST-K Advisory Platform",
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

cors_origins = get_settings().cors_origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if cors_origins == ["*"] else cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DeepSeek Apple Disease Detection Endpoints
app.include_router(disease.router, prefix="/api/disease", tags=["DeepSeek Apple Disease Detection"])
app.include_router(disease.router, prefix="/api/v1/disease", tags=["DeepSeek Apple Disease Detection"])

app.include_router(auth.router, prefix="/api/v1")
app.include_router(diagnoses.router, prefix="/api/v1")
app.include_router(orchards.router, prefix="/api/v1")
app.include_router(weather.router, prefix="/api/v1")
app.include_router(logs.router, prefix="/api/v1")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "app": "Kashmir Apple Care API", "version": "2.0.0"}


@app.get("/api/v1/status")
async def api_status() -> dict[str, object]:
    settings = get_settings()
    has_key = bool(settings.deepseek_api_key)
    model = settings.deepseek_model
    return {
        "status": "ready",
        "app_name": settings.app_name,
        "ai_engine": f"DeepSeek AI ({model})",
        "has_deepseek_key": has_key,
        "keyless": not has_key,
        "database": "sqlite" if "sqlite" in settings.database_url else "postgresql",
    }
