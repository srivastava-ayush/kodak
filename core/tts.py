import subprocess
import tempfile
import threading
import wave
import os
import platform
from pathlib import Path

from config import VOICE_DIR, DEFAULT_VOICE, SYSTEM

if SYSTEM == "Windows":
    import winsound


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
                self._speak_native(text)
        except Exception:
            self._speak_native(text)
        finally:
            self._playing = False

    def _speak_piper(self, text):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            wav_path = f.name
        try:
            with wave.open(wav_path, "wb") as wav_file:
                self.voice.synthesize_wav(text, wav_file)
            self._play_wav(wav_path)
        finally:
            os.unlink(wav_path)

    def _play_wav(self, wav_path):
        if SYSTEM == "Darwin":
            subprocess.run(["afplay", wav_path], capture_output=True)
        elif SYSTEM == "Windows":
            subprocess.run(["powershell", "-c", f'(New-Object Media.SoundPlayer "{wav_path}").PlaySync()'], capture_output=True)
        else:
            for cmd in ["aplay", "paplay", "play"]:
                if subprocess.run([cmd, wav_path], capture_output=True).returncode == 0:
                    return

    def _speak_native(self, text):
        if SYSTEM == "Darwin":
            subprocess.run(["say", text], capture_output=True)
        elif SYSTEM == "Windows":
            subprocess.run(["powershell", "-c", f"Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{text}')"], capture_output=True)
        else:
            subprocess.run(["espeak", text], capture_output=True)

    def stop(self):
        self._stop_event.set()
        self._playing = False

    def is_playing(self):
        return self._playing
