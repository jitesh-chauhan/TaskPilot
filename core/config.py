from pathlib import Path

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    JWT_SECRET_KEY: str
    MONGO_URI: str
    DB_NAME: str

    class Config:
        env_file = f"{BASE_DIR}/.env"
        env_file_encoding = "utf-8"


settings = Settings()
