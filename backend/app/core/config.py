from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API Keys
    OPENAI_API_KEY: str = ""
    
    # Model paths
    llama_cpp_path: str = "../llama.cpp/main"
    model_path: str = "models/llama-2-7b-chat.gguf"  # Using the existing model file
    
    # Google OAuth2
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/auth/callback"
    
    class Config:
        env_file = ".env"
        case_sensitive = False  # This allows for case-insensitive matching
        extra = "ignore"  # This will ignore extra fields like pythonpath

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings() 