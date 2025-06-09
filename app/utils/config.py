from pydantic_settings import BaseSettings
from typing import Optional

# Define a configuration class inheriting from Pydantic's BaseSettings.
# This class will automatically read environment variables and/or .env files
# to populate its attributes, providing a neat way to manage app configuration.
class Settings(BaseSettings):
    # URL for the database connection; defaulting to a local SQLite database file.
    database_url: str = "sqlite:///./helpdesk.db"
    
    # Base URL for the Ollama API (likely an LLM or AI model server endpoint).
    ollama_base_url: str = "http://localhost:11434"
    
    # Name or identifier of the Ollama model to be used.
    ollama_model: str = "qwen2.5:14b"
    
    # Directory path where Chroma vector database or embeddings will be persisted.
    chroma_persist_directory: str = "./chroma_db"
    
    # Optional API key for a search service (e.g., Google Custom Search or similar).
    # This is optional and can be None if not provided.
    search_api_key: Optional[str] = None
    
    # Optional search engine identifier for the search service.
    search_engine_id: Optional[str] = None
    
    # Logging level for the application (e.g., DEBUG, INFO, WARNING).
    log_level: str = "INFO"

    # Model configuration tells Pydantic to load environment variables
    # from a file named '.env' if it exists.
    model_config = {"env_file": ".env"}


# Instantiate the Settings class, loading configuration values immediately.
# This object can now be imported and used throughout the app to access config values.
settings = Settings()
