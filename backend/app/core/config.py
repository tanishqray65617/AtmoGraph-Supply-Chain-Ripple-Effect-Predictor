from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "AtmoGraph Risk Intelligence API"
    APP_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    
    # Neo4j Settings
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "atmograph_secret_2026"
    NEO4J_DATABASE: str = "neo4j"
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["*"]
    
    # NLP
    NLP_MODEL: str = "en_core_web_sm"

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()

