from minio import Minio
from urllib.parse import urlparse, urlunparse
from app.config import settings
from datetime import timedelta


minio_client = Minio(settings.MINIO_ENDPOINT, access_key=settings.MINIO_ACCESS_KEY,
                     secret_key=settings.MINIO_SECRET_KEY, secure=False)


def get_public_url(audio_hash):
    if settings.ENV == "dev":
        return f'{settings.PROTOCOL}{settings.MINIO_ENDPOINT}/{settings.MINIO_BUCKET}/{audio_hash}'

    url = minio_client.get_presigned_url(
        "GET",
        bucket_name=settings.MINIO_BUCKET,
        object_name=audio_hash,
        expires=timedelta(seconds=settings.URL_TTL)
    )

    parsed = urlparse(url)
    final_url = urlunparse(parsed._replace(netloc=settings.MINIO_HOST))

    return final_url
