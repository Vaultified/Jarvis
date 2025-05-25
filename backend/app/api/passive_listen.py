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
            # Give the listener a moment to initialize
            await asyncio.sleep(0.5)
        else:
            print("Listener thread already active.")

        print("Waiting for wake word and speech (via queue)...")
        audio = listener.get_audio(timeout=5)  # Reduced timeout

        if not audio:
            print("No audio captured within timeout period.")
            return {
                "status": "waiting",
                "message": "Listening for wake word...",
                "text": ""
            }

        if len(audio) < 1024:  # Minimum audio length check
            print(f"Audio too short ({len(audio)} bytes)")
            return {
                "status": "too_short",
                "message": "Audio captured was too short to process.",
                "text": ""
            }

        print(f"Received {len(audio)} bytes of audio from queue, transcribing...")
        
        # Process audio asynchronously
        text = await process_audio(audio, listener.sample_rate)
        print(f"Transcription Result: {text}")

        if not text.strip():
            return {
                "status": "no_speech",
                "message": "No speech detected in the audio.",
                "text": ""
            }

        return {
            "status": "success",
            "message": "Successfully transcribed speech.",
            "text": text
        }

    except Empty:
        print("Queue timeout - No audio received after wake word and speech.")
        return {
            "status": "timeout",
            "message": "Timeout waiting for speech after wake word.",
            "text": ""
        }
    except Exception as e:
        print("Error in /passive-listen endpoint:", e)
        traceback.print_exc()
        return {
            "status": "error",
            "message": f"An error occurred: {str(e)}",
            "text": ""
        }