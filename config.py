import os
from pathlib import Path

class Config:
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2:3b")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
    
    VECTOR_STORE_PATH = Path("./chroma_db")
    
    MAX_SEARCH_RESULTS = 5
    MAX_CONTENT_LENGTH = 5000
    
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'es': 'Spanish', 
        'fr': 'French',
        'sw': 'Swahili',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'zh': 'Chinese',
        'ja': 'Japanese',
        'ar': 'Arabic',
        'hi': 'Hindi'
    }