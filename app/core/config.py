from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    gemini_api_key: str | None = None

    database_url: str = "postgresql://postgres:postgres@localhost:5432/construction_ai"
    redis_url: str = "redis://localhost:6379"

    class Config:
        env_file = ".env"

settings = Settings()