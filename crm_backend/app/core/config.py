import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./crm_fallback_v2.db"
    JWT_SECRET: str = "42898b0f8dcdcb2bdeff5a73e4b09e20a9a1473fa58a436573c71ea407cbe07d"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    GROQ_API_KEY: str = ""
    DEFAULT_MODEL: str = "gemma2-9b-it"
    ALTERNATIVE_MODEL: str = "llama-3.3-70b-versatile"

    N8N_WEBHOOK_URL: str = ""
    REDIS_URL: str = ""
    EMAIL_HOST: str = ""
    EMAIL_PORT: int = 587
    EMAIL_USERNAME: str = ""
    EMAIL_PASSWORD: str = ""
    EMAIL_FROM: str = ""

    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET: str = ""

    OPENAI_API_KEY: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
