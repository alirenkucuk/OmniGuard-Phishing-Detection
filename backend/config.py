import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Centralized configuration for the FastAPI backend.
    Can be overridden by environment variables (e.g., export THRESHOLD=0.9).
    """
    PROJECT_NAME: str = "OmniGuard API"
    API_VERSION: str = "1.0.0"
    
    # Model settings
    MODEL_WEIGHTS_PATH: str = os.getenv("MODEL_PATH", "../ml_core/saved_models/omniguard_best.pth")
    TABULAR_FEATURE_DIM: int = 10
    DECISION_THRESHOLD: float = 0.85
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"

# Create a global settings object to import across the backend
settings = Settings()