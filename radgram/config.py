import os
from dataclasses import dataclass

@dataclass
class RADCAMConfig:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    RADGRAM_API_URL: str = os.getenv("RADGRAM_API_URL", "http://localhost:8000")
    CACHE_DIR: str = os.path.join("assets", ".cache")
    DEFAULT_MODEL: str = "gemini-1.5-flash"
    DEFAULT_FPS: float = 30.0

config = RADCAMConfig()