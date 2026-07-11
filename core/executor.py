import subprocess
import re
import json
import logging
from datetime import datetime
from typing import Tuple

from config import (
    CONFIRM_BEFORE_EXECUTE,
    REJECT_DANGEROUS_COMMANDS,
    LOG_COMMANDS,
    LOG_DIR,
    DANGEROUS_PATTERNS,
    HISTORY_FILE,
    MAX_HISTORY_SIZE,
)

from .stt import SpeechToText
from .tts import TextToSpeech


class CommandExecutor:
    def __init__(self, stt: SpeechToText, tts: TextToSpeech):
        self.stt = stt
        self.tts = tts
        self.history = self._load_history()
        self._setup_logging()

    def _setup_logging(self):
        if LOG_COMMANDS:
            log_file = LOG_DIR / f"commands_{datetime.now().strftime('%Y%m%d')}.log"
            logging.basicConfig(
                filename=str(log_file),
                level=logging.INFO,
                format="%(asctime)s - %(message)s",
            )

    def _load_history(self) -> list:
        try:
            if HISTORY_FILE.exists():
                with open(HISTORY_FILE, "r") as f:
                    return json.load(f)
        except Exception:
            pass
        return []

    def _save_history(self):
        try:
            with open(HISTORY_FILE, "w") as f:
                json.dump(self.history[-MAX_HISTORY_SIZE:], f, indent=2)
        except Exception:
            pass

    def is_dangerous(self, command: str) -> bool:
        if not REJECT_DANGEROUS_COMMANDS:
            return False
        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return True
        return False

    def ask_confirmation(self, command: str, stt: bool = True) -> bool:
        prompt = f"Boss, can I execute this command? {command}"
        self.tts.speak(prompt)

        if stt:
            try:
                print("  Say 'yes' or 'no'...")
                response = self.stt.record_and_transcribe(duration=3)
                response = response.lower().strip()
                if any(word in response for word in ["yes", "yeah", "yep", "yup", "sure", "do it", "go ahead", "execute"]):
                    return True
                if any(word in response for word in ["no", "nope", "nah", "cancel", "stop", "don't"]):
                    return False
            except Exception:
                pass

        try:
            keyboard_response = input("  Or type y/n: ").strip().lower()
            return keyboard_response in ["y", "yes"]
        except (EOFError, KeyboardInterrupt):
            return False

    def execute_command(self, command: str, confirm: bool = True) -> Tuple[bool, str]:
        if self.is_dangerous(command):
            msg = "Boss, I can't execute that - it's too dangerous!"
            self.tts.speak(msg)
            return False, msg

        if confirm and CONFIRM_BEFORE_EXECUTE:
            if not self.ask_confirmation(command):
                msg = "Command cancelled."
                return False, msg

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
            )
            output = result.stdout + result.stderr
            success = result.returncode == 0

            self._log_command(command, success, output)
            self._add_to_history(command, success, output)

            return success, output.strip() if output else ("Command executed" if success else "Command failed")
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, f"Error: {e}"

    def _log_command(self, command: str, success: bool, output: str):
        if LOG_COMMANDS:
            status = "SUCCESS" if success else "FAILED"
            logging.info(f"[{status}] {command}")
            if output:
                logging.info(f"  Output: {output[:500]}")

    def _add_to_history(self, command: str, success: bool, output: str):
        entry = {
            "command": command,
            "success": success,
            "output": output[:500] if output else "",
            "timestamp": datetime.now().isoformat(),
        }
        self.history.append(entry)
        self._save_history()

    def get_history(self, limit: int = 10) -> list:
        return self.history[-limit:]

    def clear_history(self):
        self.history = []
        self._save_history()
