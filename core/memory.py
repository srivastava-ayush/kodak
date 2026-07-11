import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from config import DATA_DIR

MEMORY_FILE = DATA_DIR / "memory.json"


class Memory:
    def __init__(self):
        self.data = {}
        self._load()

    def _load(self):
        try:
            if MEMORY_FILE.exists():
                with open(MEMORY_FILE, "r") as f:
                    self.data = json.load(f)
        except Exception:
            self.data = {}

    def _save(self):
        try:
            with open(MEMORY_FILE, "w") as f:
                json.dump(self.data, f, indent=2)
        except Exception:
            pass

    def remember(self, key: str, value: str):
        self.data[key.lower()] = {
            "value": value,
            "timestamp": datetime.now().isoformat(),
        }
        self._save()

    def recall(self, key: str) -> Optional[str]:
        entry = self.data.get(key.lower())
        if entry:
            return entry.get("value")
        return None

    def forget(self, key: str) -> bool:
        if key.lower() in self.data:
            del self.data[key.lower()]
            self._save()
            return True
        return False

    def recall_all(self) -> dict:
        return {k: v["value"] for k, v in self.data.items()}

    def get_context(self) -> str:
        if not self.data:
            return ""
        lines = ["Memories:"]
        for key, entry in self.data.items():
            lines.append(f"- {key}: {entry['value']}")
        return "\n".join(lines)

    def handle_intent(self, action: str, params: dict) -> tuple:
        if action == "remember":
            key = params.get("key", "")
            value = params.get("value", "")
            if key and value:
                self.remember(key, value)
                return True, f"Remembered: {key} = {value}"
            return False, "What should I remember? Say 'remember that <key> is <value>'"
        elif action == "recall":
            key = params.get("key", "")
            if key:
                value = self.recall(key)
                if value:
                    return True, f"{key}: {value}"
                return False, f"I don't remember anything about {key}"
            return False, "What do you want me to recall?"
        elif action == "forget":
            key = params.get("key", "")
            if key:
                if self.forget(key):
                    return True, f"Forgot: {key}"
                return False, f"I don't remember {key}"
            return False, "What should I forget?"
        elif action == "list":
            all_mem = self.recall_all()
            if all_mem:
                lines = [f"{k}: {v}" for k, v in all_mem.items()]
                return True, "My memories:\n" + "\n".join(lines)
            return True, "I have no memories yet."
        return False, "Unknown memory action."
