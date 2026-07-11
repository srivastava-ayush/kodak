import sounddevice as sd
import scipy.io.wavfile as wav
from faster_whisper import WhisperModel

from config import WHISPER_MODEL, SAMPLE_RATE, RECORD_DURATION, AUDIO_FILE, CHANNELS


class SpeechToText:
    def __init__(self):
        self.model = WhisperModel(WHISPER_MODEL)

    def record_audio(self, duration=RECORD_DURATION):
        fs = SAMPLE_RATE
        sd.stop()
        audio = sd.rec(int(duration * fs), samplerate=fs, channels=CHANNELS)
        sd.wait()
        wav.write(str(AUDIO_FILE), fs, audio)
        return AUDIO_FILE

    def transcribe(self, audio_file=None):
        if audio_file is None:
            audio_file = AUDIO_FILE
        segments, _ = self.model.transcribe(str(audio_file))
        text = " ".join([seg.text for seg in segments])
        return text.strip()

    def record_and_transcribe(self, duration=RECORD_DURATION):
        audio_file = self.record_audio(duration)
        return self.transcribe(audio_file)
