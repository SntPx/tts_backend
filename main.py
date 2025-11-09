from fastapi import FastAPI
from pathlib import PosixPath

# -- API info --
API_INFO = {
    "NAME": "tts_backend",
    "AUTHOR": "Christophe 'SntPx' RIVIÈRE",
    "VERSION": "0.1",
}

# -- Config --
AUDIO_FILES_DIR = 'audio_files'
DEFAULT_LANG = 'us'
DEFAULT_FMT = "ogg"

app = FastAPI()


@app.get('/')
async def root():
    return {
        "message": f"{API_INFO['NAME']} v{API_INFO['VERSION']}"
    }


@app.get('/audio/{audio_hash}')
async def get_audio(audio_hash: str):
    lang = DEFAULT_LANG
    pass


@app.get('/audio/{audio_hash}/{lang_code}/{fmt}')
async def get_audio(audio_hash: str, lang_code: str, fmt: str):
    f_path = PosixPath(AUDIO_FILES_DIR, lang_code, '.'.join([audio_hash, fmt]))
    return {"location": f_path}
