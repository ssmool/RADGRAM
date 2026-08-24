import os
import hashlib
import requests

class AssetCacheManager:
    """Gerencia o cache local de mídias e assets para otimizar tempo e APIs."""
    
    CACHE_DIR = os.path.join("assets", ".cache")

    @classmethod
    def _ensure_cache_dir(cls):
        os.makedirs(cls.CACHE_DIR, exist_ok=True)

    @classmethod
    def get_hash_path(cls, key: str, extension: str = "png") -> str:
        cls._ensure_cache_dir()
        hash_key = hashlib.md5(key.encode("utf-8")).hexdigest()
        return os.path.join(cls.CACHE_DIR, f"{hash_key}.{extension}")

    @classmethod
    def exists(cls, key: str, extension: str = "png") -> bool:
        return os.path.exists(cls.get_hash_path(key, extension))

    @classmethod
    def save_bytes(cls, key: str, data: bytes, extension: str = "png") -> str:
        filepath = cls.get_hash_path(key, extension)
        with open(filepath, "wb") as f:
            f.write(data)
        return filepath