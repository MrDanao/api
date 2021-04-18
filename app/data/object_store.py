from minio import Minio

from core.config import config


engine = Minio(
    endpoint=config.minio_host,
    access_key=config.minio_user,
    secret_key=config.minio_pass,
    secure=config.minio_secure
)
