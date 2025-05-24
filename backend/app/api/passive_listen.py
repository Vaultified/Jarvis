from fastapi import APIRouter, HTTPException, BackgroundTasks
from ..services.passive_listener import PassiveListener
import tempfile
import whisper
import numpy as np
import os
from queue import Empty
import traceback
import asyncio
from concurrent.futures import ThreadPoolExecutor

router = APIRouter()
listener = PassiveListener()
executor = ThreadPoolExecutor(max_workers=2)  # Limit concurrent processing

# Load Whisper model once at startup
whisper_model = whisper.load_model("base")

async def process_audio(audio_data: bytes, sample_rate: int) -> str:
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
            tmpfile_path = tmpfile.name
            import soundfile as sf
            sf.write(tmpfile_path, np.frombuffer(audio_data, dtype=np.int16), sample_rate)

        # Run transcription in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            executor,
            lambda: whisper_model.transcribe(tmpfile_path)
        )

        os.remove(tmpfile_path)
        return result["text"].strip()
    except Exception as e:
        if 'tmpfile_path' in locals() and os.path.exists(tmpfile_path):
            os.remove(tmpfile_path)
        raise e

@router.post("/passive-listen")
async def passive_listen():
    try:
        if not listener._thread or not listener._thread.is_alive():
            print("Listener thread not active, starting.")
            listener.start()
        else:
            print("Listener thread already active.")

        print("Waiting for wake word and speech (via queue)...")
        audio = listener.get_audio(timeout=5)  # Reduced timeout

        if not audio:
            print("Error: get_audio returned None (queue empty after timeout?)")
            raise ValueError("No audio captured or retrieved from listener queue.")

        print(f"Received {len(audio)} bytes of audio from queue, transcribing...")
        
        # Process audio asynchronously
        text = await process_audio(audio, listener.sample_rate)
        print(f"Transcription Result: {text}")

        return {"text": text}

    except Empty:
        print("Error in /passive-listen: Queue timeout - No audio received after wake word and speech.")
        raise HTTPException(status_code=408, detail="Timeout waiting for speech after wake word.")
    except ValueError as ve:
        print(f"Error in /passive-listen: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print("Error in /passive-listen endpoint:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))