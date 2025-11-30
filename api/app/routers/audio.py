from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models import Audio
from app.schemas import AudioResponse
from app.db_init import get_db

router = APIRouter(prefix="/audio", tags=["Audio"])


@router.get("/{audio_id}", response_model=AudioResponse)
def get_audio(audio_id: str, db: Session = Depends(get_db)):

    audio = db.query(Audio).filter(Audio.id == audio_id).first()

    if not audio:
        raise HTTPException(status_code=404, detail="Audio not found")

    return audio
