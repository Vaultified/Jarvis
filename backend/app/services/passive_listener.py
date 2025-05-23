import pvporcupine
import sounddevice as sd
import numpy as np
import webrtcvad
import queue
import threading
import time
import os
import traceback

class PassiveListener:
    def __init__(self, keyword="jarvis", sensitivity=0.7, silence_timeout=2.0, sample_rate=16000):
        self.keyword = keyword
        self.sensitivity = sensitivity
        self.silence_timeout = silence_timeout
        self.sample_rate = sample_rate
        self.vad = webrtcvad.Vad(2)
        self.audio_queue = queue.Queue()
        self.listening = False
        self._stop_event = threading.Event()
        self._thread = None

        # Initialize Porcupine
        key = os.getenv("PORCUPINE_ACCESS_KEY")
        self.porcupine = pvporcupine.create(access_key=key,keywords=[self.keyword], sensitivities=[self.sensitivity])

    def start(self):
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join()
        self.porcupine.delete()

    def _run(self):
        with sd.RawInputStream(samplerate=self.porcupine.sample_rate, blocksize=512, dtype='int16', channels=1) as stream:
            print("PassiveListener: Listening for wake word...")
            while not self._stop_event.is_set():
                pcm = stream.read(512)[0]
                pcm16 = np.frombuffer(pcm, dtype=np.int16)
                keyword_index = self.porcupine.process(pcm16)
                if keyword_index >= 0:
                    print("Wake word detected!")
                    self._record_until_silence(stream)
    
    def _record_until_silence(self, stream):
        self.listening = True
        audio_frames = []
        silence_start = None
        vad_frame_ms = 30
        vad_frame_bytes = int(self.sample_rate * vad_frame_ms / 1000) * 2  # 16-bit audio

        print("PassiveListener: Recording after wake word...")
        while not self._stop_event.is_set():
            try:
                # Use a smaller block size for reading to check silence more frequently
                pcm = stream.read(int(self.sample_rate * 0.1 / 1000) * 2)[0] # Read ~10ms blocks
                audio_frames.append(pcm)

                # Process in VAD frame chunks (e.g., 30ms)
                if len(b"".join(audio_frames)) >= vad_frame_bytes:
                    vad_chunk = b"".join(audio_frames)[-vad_frame_bytes:] # Process the last chunk
                    is_speech = self.vad.is_speech(vad_chunk, self.sample_rate)

                    if is_speech:
                        silence_start = None
                    else:
                        if silence_start is None:
                            silence_start = time.time()
                        elif time.time() - silence_start > self.silence_timeout:
                            print("PassiveListener: Silence detected, stopping recording.")
                            break # Exit the recording loop
            except Exception as e:
                print(f"Error during recording: {e}")
                traceback.print_exc()
                break # Exit on error

        self.listening = False
        # Put the full recorded audio onto the queue AFTER the loop finishes
        full_audio = b"".join(audio_frames)
        if full_audio:
            print(f"Putting {len(full_audio)} bytes of audio onto queue.")
            self.audio_queue.put(full_audio)
        else:
            print("No audio recorded to put onto queue.")

    def get_audio(self, timeout=10):
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None