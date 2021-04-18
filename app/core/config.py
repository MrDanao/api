import os
from functools import lru_cache
from typing import Dict

from pydantic import BaseSettings


class Config(BaseSettings):
    env: str = os.environ['ENV']
    api_user: str = os.environ['API_USER']
    api_pass: str = os.environ['API_PASS']
    api_secret_key: str = os.environ['API_SECRET_KEY']
    mongo_host: str = os.environ['MONGO_HOST']
    mongo_user: str = os.environ['MONGO_INITDB_ROOT_USERNAME']
    mongo_pass: str = os.environ['MONGO_INITDB_ROOT_PASSWORD']
    mongo_db: str = os.environ['MONGO_DB']
    minio_host: str = os.environ['MINIO_HOST']
    minio_user: str = os.environ['MINIO_ROOT_USER']
    minio_pass: str = os.environ['MINIO_ROOT_PASSWORD']
    minio_secure: bool = os.environ['MINIO_SECURE']
    allowed_ctypes: Dict[str, set] = {
        'audio': {'audio/mpeg', 'audio/mp4', 'audio/x-m4a'},
        'image': {'image/png', 'image/jpeg'}
    }
    token_algorithm: str = 'HS256'
    token_duration: int = 15


@lru_cache()
def get_config():
    return Config()


config = get_config()
