import queue
import time
import numpy as np
import sounddevice as sd
from openwakeword.model import Model

from config import WAKE_WORD, WAKE_WORD_THRESHOLD, SAMPLE_RATE


class WakeWordDetector:
    def __init__(self):
        self.audio_queue = queue.Queue()
        self.running = False
        self.stream = None
        self.model = None
        self._load_model()

    def _load_model(self):
        self.model = Model()

    def _audio_callback(self, indata, frames, time_info, status):
        if not self.running:
            return
        self.audio_queue.put(indata.copy())

    def start(self):
        self.audio_queue = queue.Queue()
        self.running = True
        self.stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16",
            callback=self._audio_callback,
            blocksize=int(SAMPLE_RATE * 0.08),
        )
        self.stream.start()

    def stop(self):
        self.running = False
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
            self.stream = None
        time.sleep(0.2)

    def listen(self, callback):
        self.start()
        try:
            while self.running:
                try:
                    audio_frame = self.audio_queue.get(timeout=0.1)
                    if not self.running:
                        return
                    pcm = audio_frame.flatten().astype(np.int16)
                    prediction = self.model.predict(pcm)
                    score = prediction.get(WAKE_WORD, 0)
                    if score > WAKE_WORD_THRESHOLD:
                        self.stop()
                        time.sleep(0.3)
                        callback()
                        return
                except queue.Empty:
                    continue
        finally:
            self.stop()
