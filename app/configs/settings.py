from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # database
    DB_PATH: str = "data/nutrilens.duckdb"
    READ_ONLY: bool = True

    # requests
    ALLOWED_ORIGINS: list[str] = ["*"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()