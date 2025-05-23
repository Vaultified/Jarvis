from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import subprocess

router = APIRouter()

class SpeakRequest(BaseModel):
    text: str

@router.post("/speak")
async def speak(request: SpeakRequest):
    try:
        # Use macOS 'say' command to speak the text
        subprocess.Popen(["say", request.text])
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 