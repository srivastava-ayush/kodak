from .wakeword import WakeWordDetector
from .stt import SpeechToText
from .tts import TextToSpeech
from .llm import LLMClient
from .intent import IntentDetector
from .executor import CommandExecutor
from .memory import Memory

from commands.apps import AppCommands
from commands.files import FileCommands
from commands.system import SystemCommands
from commands.packages import PackageCommands
from commands.media import MediaCommands

from utils.audio import AudioUtils


class AssistantEngine:
    def __init__(self, callback=None):
        self.callback = callback

        self.wakeword = WakeWordDetector()
        self.stt = SpeechToText()
        self.tts = TextToSpeech()
        self.llm = LLMClient()
        self.memory = Memory()
        self.intent_detector = IntentDetector(self.llm, self.memory)
        self.executor = CommandExecutor(self.stt, self.tts)

        self.apps = AppCommands()
        self.files = FileCommands()
        self.system = SystemCommands()
        self.packages = PackageCommands()
        self.media = MediaCommands()

        self._status = "idle"

    def set_status(self, status: str):
        self._status = status
        if self.callback:
            self.callback("status", status)

    def on_wake_word(self):
        self.set_status("listening")

    def process_input(self, text: str) -> str:
        self.set_status("thinking")
        intent = self.intent_detector.detect(text)
        response = self._handle_intent(intent)
        return response

    def _handle_intent(self, intent) -> str:
        intent_type = intent.intent
        action = intent.action
        params = intent.params
        command = intent.command

        success = False
        output = ""

        if intent_type == "memory":
            success, output = self.memory.handle_intent(action, params)
        elif intent_type == "app":
            success, output = self.apps.handle_intent(params)
        elif intent_type == "file":
            success, output = self.files.handle_intent(action, params)
        elif intent_type == "system":
            success, output = self.system.handle_intent(action, params)
        elif intent_type == "package":
            success, output = self.packages.handle_intent(action, params)
        elif intent_type == "media":
            success, output = self.media.handle_intent(action, params)
        elif command:
            self.set_status("executing")
            success, output = self.executor.execute_command(command)
        else:
            return intent.response

        if success:
            if output:
                return f"{intent.response}. {output}"
            return intent.response
        else:
            return f"{intent.response}. Error: {output}" if output else f"{intent.response}. Command failed."

    def run_interactive(self, text: str) -> str:
        response = self.process_input(text)
        self.tts.speak(response, blocking=True)
        return response

    def listen_loop(self):
        self.set_status("waiting")
        self.wakeword.listen(self.on_wake_word)

    def speak(self, text: str):
        self.tts.speak(text, blocking=False)

    def stop(self):
        self.wakeword.stop()
        self.tts.stop()
