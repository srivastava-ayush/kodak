import subprocess
import tempfile
import os
from pathlib import Path


class AudioUtils:
    @staticmethod
    def play_beep(frequency: int = 800, duration: int = 0.15):
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                wav_path = f.name
            subprocess.run(
                [
                    "python3", "-c",
                    f"""
import struct, wave
freq = {frequency}
duration = {duration}
sample_rate = 16000
samples = int(sample_rate * duration)
with wave.open('{wav_path}', 'w') as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(sample_rate)
    for i in range(samples):
        t = i / sample_rate
        value = int(32767 * 0.5 * (1 if (2 * 3.14159 * freq * t) % (2 * 3.14159) < 3.14159 else -1))
        w.writeframes(struct.pack('<h', value))
""",
                ],
                capture_output=True,
            )
            subprocess.run(["aplay", wav_path], capture_output=True)
            os.unlink(wav_path)
        except Exception:
            pass

    @staticmethod
    def play_wake_sound():
        AudioUtils.play_beep(frequency=1000, duration=0.1)

    @staticmethod
    def play_confirm_sound():
        AudioUtils.play_beep(frequency=1200, duration=0.08)

    @staticmethod
    def play_deny_sound():
        AudioUtils.play_beep(frequency=400, duration=0.2)

    @staticmethod
    def play_error_sound():
        AudioUtils.play_beep(frequency=300, duration=0.3)
