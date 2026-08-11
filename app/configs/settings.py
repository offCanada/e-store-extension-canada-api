from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_PATH: str = "data/nutrilens.duckdb"
    READ_ONLY: bool = True

    class Config:
        env_file = ".env"

settings = Settings()