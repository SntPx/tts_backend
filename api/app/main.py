from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from minio import Minio
from io import BytesIO
from . import models, crud, schemas, auth, config
from .db_init import init_db, get_db
from app.routers.audio import router as audio_router

settings = config.settings
init_db()

minio_client = Minio(settings.MINIO_ENDPOINT, access_key=settings.MINIO_ACCESS_KEY,
                     secret_key=settings.MINIO_SECRET_KEY, secure=False)

if not minio_client.bucket_exists(settings.MINIO_BUCKET):
    minio_client.make_bucket(settings.MINIO_BUCKET)

app = FastAPI()


@app.post('/token')
def token(username: str):
    return {"access_token": auth.create_access_token(username)}


@app.post('/audio/upload')
async def upload_audio(file: UploadFile = File(...), db=Depends(get_db), user=Depends(auth.get_current_user)):
    import uuid
    key = f"{uuid.uuid4()}_{file.filename}"
    data = await file.read()
    data = BytesIO(data)
    minio_client.put_object(settings.MINIO_BUCKET, key, data, len(data.getvalue()), content_type=file.content_type)
    audio = schemas.AudioCreate(key=key, filename=file.filename, content_type=file.content_type,
                                size_bytes=len(data.getvalue()), owner=user)
    return crud.create_audio(db, audio)


@app.get('/audios')
def list_audios(db=Depends(get_db), user=Depends(auth.get_current_user)):
    return crud.list_audios(db)


app.include_router(audio_router)
