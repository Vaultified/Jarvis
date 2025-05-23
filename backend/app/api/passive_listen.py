from fastapi import APIRouter, HTTPException
from ..services.passive_listener import PassiveListener
import tempfile
import whisper
import numpy as np
import os
from queue import Empty
import traceback

router = APIRouter()
listener = PassiveListener()

@router.post("/passive-listen")
async def passive_listen():
    try:
        if not listener._thread or not listener._thread.is_alive():
            print("Listener thread not active, starting.")
            listener.start()
        else:
            print("Listener thread already active.")

        print("Waiting for wake word and speech (via queue)...")
        audio = listener.get_audio(timeout=75)

        if not audio:
            print("Error: get_audio returned None (queue empty after timeout?)")
            raise ValueError("No audio captured or retrieved from listener queue.")

        print(f"Received {len(audio)} bytes of audio from queue, transcribing...")

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
            tmpfile_path = tmpfile.name
            import soundfile as sf
            sf.write(tmpfile_path, np.frombuffer(audio, dtype=np.int16), listener.sample_rate)
        print(f"Audio saved to {tmpfile_path} for transcription.")

        model = whisper.load_model("base")
        result = model.transcribe(tmpfile_path)
        print(f"Transcription Result: {result['text']}")

        os.remove(tmpfile_path)

        return {"text": result["text"].strip()}

    except Empty:
        print("Error in /passive-listen: Queue timeout - No audio received after wake word and speech.")
        raise HTTPException(status_code=500, detail="Timeout waiting for speech after wake word.")
    except ValueError as ve:
        print(f"Error in /passive-listen: {ve}")
        raise HTTPException(status_code=500, detail=str(ve))
    except Exception as e:
        print("Error in /passive-listen endpoint:", e)
        traceback.print_exc()
        if 'tmpfile_path' in locals() and os.path.exists(tmpfile_path):
            os.remove(tmpfile_path)
        raise HTTPException(status_code=500, detail=str(e))