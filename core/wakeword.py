import queue
import threading
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
        if status:
            pass
        self.audio_queue.put(indata.copy())

    def start(self):
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
            self.stream.stop()
            self.stream.close()

    def listen(self, callback):
        self.start()
        try:
            while self.running:
                try:
                    audio_frame = self.audio_queue.get(timeout=0.1)
                    pcm = audio_frame.flatten().astype(np.int16)
                    prediction = self.model.predict(pcm)
                    score = prediction.get(WAKE_WORD, 0)
                    if score > WAKE_WORD_THRESHOLD:
                        callback()
                except queue.Empty:
                    continue
        finally:
            self.stop()

    def listen_once(self):
        event = threading.Event()

        def on_detected():
            event.set()

        self.start()
        try:
            while not event.is_set():
                try:
                    audio_frame = self.audio_queue.get(timeout=0.1)
                    pcm = audio_frame.flatten().astype(np.int16)
                    prediction = self.model.predict(pcm)
                    score = prediction.get(WAKE_WORD, 0)
                    if score > WAKE_WORD_THRESHOLD:
                        return True
                except queue.Empty:
                    continue
        finally:
            self.stop()
        return False
