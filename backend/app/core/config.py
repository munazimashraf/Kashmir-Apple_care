from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", "../.env"), extra="ignore")
    app_name: str = "Kashmir Apple Care API"
    environment: str = "production"
    database_url: str = Field(
        default="sqlite:///./applecare.db",
        validation_alias="DATABASE_URL",
    )
    jwt_secret: str = Field(
        default="kashmir-apple-care-secure-jwt-secret-key-2026",
        validation_alias="JWT_SECRET",
    )
    jwt_expire_minutes: int = 60 * 24
    openweather_api_key: str = Field(
        default="development-unused",
        validation_alias="OPENWEATHER_API_KEY",
    )
    allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://localhost:8000,http://127.0.0.1:8000,*"
    model_path: str = "artifacts/applecare/applecare_mobilenetv3.onnx"
    classes_path: str = "artifacts/applecare/classes.json"
    max_upload_bytes: int = 15 * 1024 * 1024

    # DeepSeek AI Multimodal Engine
    deepseek_api_key: str | None = Field(default=None, validation_alias="DEEPSEEK_API_KEY")
    deepseek_base_url: str = Field(default="https://api.deepseek.com", validation_alias="DEEPSEEK_BASE_URL")
    deepseek_model: str = Field(default="deepseek-flash", validation_alias="DEEPSEEK_MODEL")

    @property
    def cors_origins(self) -> list[str]:
        origins = [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]
        if "*" in origins:
            return ["*"]
        return origins


@lru_cache
def get_settings() -> Settings:
    return Settings()
