"""
Configuration settings for the AI Viva Voce Examiner
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from the project root .env file
# This ensures .env is found regardless of which directory the script runs from
project_root = Path(__file__).parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

# Debug: Print confirmation that .env was loaded
print(f"📁 Loading .env from: {env_path}")
print(f"🔑 GOOGLE_API_KEY loaded: {'Yes' if os.getenv('GOOGLE_API_KEY') else 'No'}")

class Settings(BaseSettings):
    """Application settings"""
    
    # API Keys
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    
    # LLM Provider
    llm_provider: str = os.getenv("LLM_PROVIDER", "gemini")
    
    # Embedding Model
    embedding_model: str = os.getenv(
        "EMBEDDING_MODEL", 
        "sentence-transformers/all-MiniLM-L6-v2"
    )
    
    # Voice Settings
    voice_enabled: bool = os.getenv("VOICE_ENABLED", "true").lower() == "true"
    tts_provider: str = os.getenv("TTS_PROVIDER", "gtts")
    
    # Server Settings
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # Paths
    base_dir: Path = Path(__file__).parent.parent
    upload_dir: Path = base_dir / "uploads"
    vector_db_dir: Path = base_dir / "vector_db"
    audio_dir: Path = base_dir / "audio"
    
    # RAG Settings
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_retrieval: int = 5
    
    # Evaluation Weights
    semantic_weight: float = 0.6
    keyword_weight: float = 0.4
    
    class Config:
        env_file = ".env"
        extra = "allow"

    def ensure_directories(self):
        """Create necessary directories if they don't exist"""
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.vector_db_dir.mkdir(parents=True, exist_ok=True)
        self.audio_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
settings.ensure_directories()
