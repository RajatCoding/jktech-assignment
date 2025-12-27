from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    database_url: str
    open_router_api_key: str
    llm_model: str = "meta-llama/llama-3-8b-instruct"
    llm_base_url: str = "https://openrouter.ai/api/v1"  # Optional: for custom endpoints (e.g., Azure OpenAI)

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()


