import json
import re
from typing import Optional, Dict, Any

from .llm import LLMClient

INTENT_PROMPT = """You are an AI assistant that detects user intent and generates appropriate shell commands for Arch Linux.

Analyze the user's request and respond with a JSON object containing:
- "intent": The category of intent (app, file, system, package, media, query, unknown)
- "action": The specific action to take
- "params": Object with relevant parameters
- "command": The shell command to execute (if applicable), or null
- "response": A natural language response to speak back to the user
- "confidence": Your confidence level (0.0 to 1.0)

Examples:
User: "open firefox"
Response: {"intent": "app", "action": "launch", "params": {"app": "firefox"}, "command": "firefox &", "response": "Opening Firefox", "confidence": 0.95}

User: "what time is it"
Response: {"intent": "system", "action": "time", "params": {}, "command": "date '+%H:%M'", "response": "Let me check the time", "confidence": 0.9}

User: "how much disk space do I have"
Response: {"intent": "system", "action": "disk_usage", "params": {}, "command": "df -h /", "response": "Checking disk usage", "confidence": 0.9}

User: "install neovim"
Response: {"intent": "package", "action": "install", "params": {"package": "neovim"}, "command": "sudo pacman -S neovim", "response": "Installing neovim", "confidence": 0.95}

User: "play music"
Response: {"intent": "media", "action": "play", "params": {}, "command": "playerctl play", "response": "Playing music", "confidence": 0.8}

User: "list files in current directory"
Response: {"intent": "file", "action": "list", "params": {"path": "."}, "command": "ls -la", "response": "Listing files", "confidence": 0.9}

User: "what is the weather"
Response: {"intent": "query", "action": "weather", "params": {}, "command": null, "response": "I cannot check the weather yet, but I can help with other tasks", "confidence": 0.3}

User: "create a new python project"
Response: {"intent": "file", "action": "create_project", "params": {"type": "python"}, "command": "mkdir -p src && touch src/main.py src/requirements.txt", "response": "Creating Python project structure", "confidence": 0.85}

Respond only with valid JSON. No additional text."""

SYSTEM_PROMPT = """You are Jarvis, a helpful AI desktop assistant running on Arch Linux.
You detect user intent and generate appropriate shell commands.
Always respond with valid JSON only. No markdown, no code blocks, just raw JSON."""


class Intent:
    def __init__(self, data: Dict[str, Any]):
        self.intent = data.get("intent", "unknown")
        self.action = data.get("action", "unknown")
        self.params = data.get("params", {})
        self.command = data.get("command")
        self.response = data.get("response", "I'm not sure how to help with that")
        self.confidence = data.get("confidence", 0.0)

    def has_command(self) -> bool:
        return self.command is not None and self.command.strip() != ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent": self.intent,
            "action": self.action,
            "params": self.params,
            "command": self.command,
            "response": self.response,
            "confidence": self.confidence,
        }


class IntentDetector:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def detect(self, user_input: str) -> Intent:
        prompt = f"{INTENT_PROMPT}\n\nUser: \"{user_input}\"\nResponse:"
        raw_response = self.llm.generate(prompt, system=SYSTEM_PROMPT)
        return self._parse_response(raw_response)

    def detect_stream(self, user_input: str):
        prompt = f"{INTENT_PROMPT}\n\nUser: \"{user_input}\"\nResponse:"
        for chunk in self.llm.generate_stream(prompt, system=SYSTEM_PROMPT):
            yield chunk

    def _parse_response(self, raw_response: str) -> Intent:
        try:
            cleaned = raw_response.strip()
            if cleaned.startswith("```"):
                lines = cleaned.split("\n")
                lines = [l for l in lines if not l.startswith("```")]
                cleaned = "\n".join(lines)
            data = json.loads(cleaned)
            return Intent(data)
        except (json.JSONDecodeError, KeyError):
            return Intent({
                "intent": "unknown",
                "action": "unknown",
                "params": {},
                "command": None,
                "response": "I had trouble understanding that. Could you rephrase?",
                "confidence": 0.0,
            })
