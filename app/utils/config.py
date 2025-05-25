from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    database_url: str = "sqlite:///./helpdesk.db"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:14b"
    chroma_persist_directory: str = "./chroma_db"
    search_api_key: Optional[str] = None
    search_engine_id: Optional[str] = None
    log_level: str = "INFO"

    model_config = {"env_file": ".env"}


settings = Settings()