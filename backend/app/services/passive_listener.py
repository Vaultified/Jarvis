import pvporcupine
import sounddevice as sd
import numpy as np
import webrtcvad
import queue
import threading
import time
import os
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PassiveListener:
    def __init__(self, keyword="jarvis", sensitivity=0.7, silence_timeout=1.5, sample_rate=16000):
        self.keyword = keyword
        self.sensitivity = sensitivity
        self.silence_timeout = silence_timeout
        self.sample_rate = sample_rate
        self.vad = webrtcvad.Vad(2)
        self.audio_queue = queue.Queue(maxsize=1)
        self.listening = False
        self._stop_event = threading.Event()
        self._thread = None
        self._processing = False
        self._current_audio = []
        self._audio_buffer = queue.Queue()

        # Initialize Porcupine
        key = os.getenv("porcupine_access_key")
        if not key:
            raise ValueError("porcupine_access_key environment variable is not set")
        print(f"Picovoice Access Key: {key[:5]}...")  # Only print first 5 chars for security
        self.porcupine = pvporcupine.create(
            access_key=key,
            keywords=[self.keyword],
            sensitivities=[self.sensitivity]
        )

    def _audio_callback(self, indata, frames, time, status):
        """Callback for audio input stream."""
        if status:
            print(f"Audio callback status: {status}")
        if not self._stop_event.is_set():
            self._audio_buffer.put(indata.copy())

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1.0)
        self.porcupine.delete()

    def _run(self):
        try:
            with sd.InputStream(
                samplerate=self.porcupine.sample_rate,
                channels=1,
                callback=self._audio_callback,
                dtype=np.int16,
                blocksize=self.porcupine.frame_length
            ) as stream:
                print("PassiveListener: Listening for wake word...")
                while not self._stop_event.is_set():
                    try:
                        # Get audio data from the buffer
                        audio_chunk = self._audio_buffer.get(timeout=0.1)
                        if audio_chunk is None:
                            continue

                        # Process with Porcupine
                        pcm16 = audio_chunk.flatten().astype(np.int16)
                        keyword_index = self.porcupine.process(pcm16)

                        if keyword_index >= 0:
                            print("Wake word detected!")
                            self._record_until_silence()
                    except queue.Empty:
                        continue
                    except Exception as e:
                        print(f"Error processing audio chunk: {e}")
                        continue

        except Exception as e:
            print(f"Error in passive listener thread: {e}")
            traceback.print_exc()
    
    def _record_until_silence(self):
        if self._processing:
            return
            
        self._processing = True
        self.listening = True
        self._current_audio = []  # Reset audio buffer
        silence_start = None
        vad_frame_ms = 30
        vad_frame_bytes = int(self.sample_rate * vad_frame_ms / 1000) * 2

        print("PassiveListener: Recording after wake word...")
        try:
            while not self._stop_event.is_set():
                try:
                    audio_chunk = self._audio_buffer.get(timeout=0.1)
                    if audio_chunk is None:
                        continue

                    self._current_audio.append(audio_chunk)
                    
                    if len(self._current_audio) * audio_chunk.size >= vad_frame_bytes:
                        # Get the last frame for VAD
                        vad_chunk = self._current_audio[-1].flatten().astype(np.int16)
                        is_speech = self.vad.is_speech(vad_chunk.tobytes(), self.sample_rate)

                        if is_speech:
                            silence_start = None
                        else:
                            if silence_start is None:
                                silence_start = time.time()
                            elif time.time() - silence_start > self.silence_timeout:
                                print("PassiveListener: Silence detected, stopping recording.")
                                break

                except queue.Empty:
                    continue

            # Combine all recorded audio
            if self._current_audio:
                full_audio = np.concatenate(self._current_audio)
                audio_bytes = full_audio.flatten().astype(np.int16).tobytes()
                
                # Clear the queue before putting new audio
                while not self.audio_queue.empty():
                    try:
                        self.audio_queue.get_nowait()
                    except queue.Empty:
                        break

                if len(audio_bytes) > 0:
                    print(f"Putting {len(audio_bytes)} bytes of audio onto queue.")
                    self.audio_queue.put(audio_bytes, timeout=1.0)
                else:
                    print("No audio recorded to put onto queue.")

        except Exception as e:
            print(f"Error during recording: {e}")
            traceback.print_exc()
        finally:
            self.listening = False
            self._processing = False
            self._current_audio = []

    def get_audio(self, timeout=5):
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None