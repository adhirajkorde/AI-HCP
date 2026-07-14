import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./crm_fallback.db"
    JWT_SECRET: str = "42898b0f8dcdcb2bdeff5a73e4b09e20a9a1473fa58a436573c71ea407cbe07d"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    GROQ_API_KEY: str = ""
    DEFAULT_MODEL: str = "gemma2-9b-it"
    ALTERNATIVE_MODEL: str = "llama-3.3-70b-versatile"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
