from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sounddevice as sd
import numpy as np
import tempfile
import whisper
import traceback

router = APIRouter()

class ListenResponse(BaseModel):
    text: str

@router.post("/listen", response_model=ListenResponse)
async def listen():
    try:
        duration = 5  # seconds
        samplerate = 16000
        print("Recording...")
        audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
        sd.wait()
        print("Recording finished.")

        # Save to temp WAV file
        with tempfile.NamedTemporaryFile(suffix=".wav") as tmpfile:
            from scipy.io.wavfile import write
            write(tmpfile.name, samplerate, audio)
            model = whisper.load_model("base")
            result = model.transcribe(tmpfile.name)
            return {"text": result["text"].strip()}
    except Exception as e:
        print("Error in /listen endpoint:", e)
        traceback.print_exc()  # This will print the full traceback to your terminal
        raise HTTPException(status_code=500, detail=str(e))