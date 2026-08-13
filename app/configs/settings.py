from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    # database
    DB_PATH: str = str(BASE_DIR / "app" / "data" / "nutrilens.duckdb")
    READ_ONLY: bool = True

    # requests
    ALLOWED_ORIGINS: list[str] = ["*"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()