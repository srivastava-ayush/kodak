import subprocess
import tempfile
import threading
import os
from pathlib import Path

from config import TTS_ENGINE, PIPER_MODEL, PIPER_BIN, TTS_STREAMING


class TextToSpeech:
    def __init__(self):
        self.engine = TTS_ENGINE
        self._check_piper()
        self._playing = False
        self._stop_event = threading.Event()

    def _check_piper(self):
        try:
            subprocess.run([PIPER_BIN, "--help"], capture_output=True, timeout=5)
            self.piper_available = True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            self.piper_available = False
            self.engine = "espeak"

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
            if self.engine == "piper" and self.piper_available:
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
            process = subprocess.Popen(
                [PIPER_BIN, "--model", PIPER_MODEL, "--output_file", wav_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            process.communicate(input=text.encode())
            subprocess.run(["aplay", wav_path], capture_output=True)
        finally:
            if os.path.exists(wav_path):
                os.unlink(wav_path)

    def _speak_espeak(self, text):
        subprocess.run(["espeak", text], capture_output=True)

    def stop(self):
        self._stop_event.set()
        self._playing = False

    def is_playing(self):
        return self._playing
