import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App settings
    app_name: str = "AI Story Generator"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database settings
    database_url: str = "sqlite:///./stories.db"
    
    # OpenAI settings
    openai_api_key: str = ""
    openai_model: str = "gpt-3.5-turbo"
    max_tokens: int = 1000
    temperature: float = 0.7
    
    # Security
    secret_key: str = "your-super-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()