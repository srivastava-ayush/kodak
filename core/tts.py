import subprocess
import tempfile
import threading
import wave
import os
from pathlib import Path

from config import BASE_DIR

VOICE_DIR = BASE_DIR / "voices"
DEFAULT_VOICE = VOICE_DIR / "en_US-lessac-medium.onnx"


class TextToSpeech:
    def __init__(self):
        self._playing = False
        self._stop_event = threading.Event()
        self.voice = None
        self._load_voice()

    def _load_voice(self):
        try:
            from piper import PiperVoice
            if DEFAULT_VOICE.exists():
                self.voice = PiperVoice.load(str(DEFAULT_VOICE))
            else:
                self.voice = None
        except Exception:
            self.voice = None

    def speak(self, text, blocking=True):
        if not text:
            return
        self._stop_event.clear()
        self._playing = True
        if blocking:
            self._speak_sync(text)
        else:
            thread = threading.Thread(target=self._speak_sync, args=(text,), daemon=True)
            thread.start()

    def _speak_sync(self, text):
        try:
            if self.voice:
                self._speak_piper(text)
            else:
                self._speak_espeak(text)
        except Exception:
            self._speak_espeak(text)
        finally:
            self._playing = False

    def _speak_piper(self, text):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            wav_path = f.name
        try:
            with wave.open(wav_path, "wb") as wav_file:
                self.voice.synthesize_wav(text, wav_file)
            subprocess.run(["aplay", wav_path], capture_output=True)
        finally:
            os.unlink(wav_path)

    def _speak_espeak(self, text):
        subprocess.run(["espeak", text], capture_output=True)

    def stop(self):
        self._stop_event.set()
        self._playing = False

    def is_playing(self):
        return self._playing
