"""Application configuration from environment variables."""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


_BACKEND_DIR = Path(__file__).resolve().parents[1]
_PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    secret_key: str = "dev-secret-key-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    database_url: str = "sqlite+aiosqlite:///./plant_disease.db"
    model_path: str = str(_PROJECT_ROOT / "model" / "saved_models" / "best_model.h5")
    class_labels_path: str = str(_PROJECT_ROOT / "model" / "saved_models" / "class_labels.json")
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    admin_email: str = "admin@plantcare.local"
    admin_password: str = "admin123"
    uploads_dir: str = "uploads"
    processed_dir: str = "processed"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
