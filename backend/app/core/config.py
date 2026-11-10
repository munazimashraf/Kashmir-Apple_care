from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_name: str = "AppleCare Kashmir API"
    environment: str = "production"
    database_url: str = Field("sqlite+aiosqlite:///./applecare.db", validation_alias="DATABASE_URL")
    jwt_secret: str = Field("local-development-secret-change-before-deploy", validation_alias="JWT_SECRET")
    jwt_expire_minutes: int = 60 * 24
    openweather_api_key: str = Field("", validation_alias="OPENWEATHER_API_KEY")
    allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    model_path: str = "artifacts/applecare-six/applecare_mobilenetv3.onnx"
    classes_path: str = "artifacts/applecare-six/classes.json"
    max_upload_bytes: int = 10 * 1024 * 1024

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
