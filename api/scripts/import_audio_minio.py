import os
from io import BytesIO
import hashlib
from minio import Minio
from sqlalchemy.orm import Session
from app.db_init import engine
from app.models import Base, Audio
from app.config import settings
from pydub import AudioSegment
import pathlib

# --- MinIO and DB configuration ---
minio_client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_SECURE in [True, "True", "true", "1"],
)

bucket = settings.MINIO_BUCKET
if not minio_client.bucket_exists(bucket):
    minio_client.make_bucket(bucket)

# Create tables if they do not exist
Base.metadata.create_all(bind=engine)

# Session DB
from sqlalchemy.orm import sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# --- Utilitarian functions ---
def compute_sha1(file_path):
    h = hashlib.sha1()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def get_audio_duration(file_path):
    try:
        audio = AudioSegment.from_file(file_path)
        return len(audio) / 1000.0  # duration in seconds
    except:
        return None


def upload_to_minio(file_path, country, file_name):
    ext = file_path.split(".")[-1]
    object_key = f"{country}/{file_name}.{ext}"
    with open(file_path, "rb") as f:
        data = BytesIO(f.read())
    minio_client.put_object(
        bucket_name=bucket,
        object_name=object_key,
        data=data,
        length=len(data.getvalue()),
        content_type=f"audio/{ext}"
    )
    return object_key, len(data.getvalue()), f"audio/{ext}"


# --- Main Import ---
def import_audio_folder(root_dir):
    db: Session = SessionLocal()

    for country in os.listdir(root_dir):
        country_dir = os.path.join(root_dir, country)
        if not os.path.isdir(country_dir):
            continue

        for filename in os.listdir(country_dir):
            file_path = os.path.join(country_dir, filename)
            if not os.path.isfile(file_path):
                continue

            sha1 = pathlib.Path(file_path).stem
            existing = db.query(Audio).filter(Audio.id == sha1).first()
            if existing:
                print(f"⏭️  Already present : {file_path}")
                continue

            duration = get_audio_duration(file_path)
            minio_key, size_bytes, content_type = upload_to_minio(file_path, country, sha1)

            audio_entry = Audio(
                id=sha1,
                country=country,
                filename=filename,
                minio_key=minio_key,
                content_type=content_type,
                duration=duration,
                size_bytes=size_bytes,
                owner=None
            )
            db.add(audio_entry)
            print(f"✅ Added : {file_path} -> {minio_key}")

    db.commit()
    db.close()
    print("Finished importing.")


if __name__ == "__main__":
    ROOT_AUDIO_DIR = "/app/audio_files"
    import_audio_folder(ROOT_AUDIO_DIR)
