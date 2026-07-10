import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = Path(os.path.expanduser("~/.kodak2"))
LOG_DIR = DATA_DIR / "logs"
HISTORY_FILE = DATA_DIR / "command_history.json"
PREFERENCES_FILE = DATA_DIR / "preferences.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

WAKE_WORD = "hey_jarvis"
WAKE_WORD_THRESHOLD = 0.5

SAMPLE_RATE = 16000
RECORD_DURATION = 4
CHANNELS = 1
AUDIO_FILE = BASE_DIR / "input.wav"

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_STREAM_URL = "http://localhost:11434/api/generate"
LLM_MODEL = "gemma3:4b"

WHISPER_MODEL = "small"

TTS_ENGINE = "piper"
PIPER_MODEL = "en_US-lessac-medium"
PIPER_BIN = "piper"
TTS_STREAMING = True

CONFIRM_BEFORE_EXECUTE = True
REJECT_DANGEROUS_COMMANDS = True
LOG_COMMANDS = True

STORE_COMMAND_HISTORY = True
STORE_USER_PREFERENCES = True
MAX_HISTORY_SIZE = 100

DANGEROUS_PATTERNS = [
    r"rm\s+-rf\s+/",
    r"rm\s+-rf\s+~",
    r"rm\s+-rf\s+\*",
    r"mkfs\.",
    r"dd\s+if=",
    r"chmod\s+-R\s+777\s+/",
    r"mv\s+.*\s+/\s*$",
    r">\s*/dev/sd",
    r"shutdown",
    r"reboot",
    r"halt",
    r"poweroff",
    r"init\s+[06]",
    r"killall",
    r"pkill\s+-9",
    r"/etc/passwd",
    r"/etc/shadow",
    r"format\s+[a-z]:",
]

APP_ALIASES = {
    "browser": ["firefox", "chromium", "google-chrome", "brave", "brave-browser", "vivaldi", "opera"],
    "code": ["code", "vscode"],
    "files": ["nautilus", "thunar", "dolphin", "pcmanfm"],
    "terminal": ["kitty", "alacritty", "terminator", "gnome-terminal", "konsole"],
    "spotify": ["spotify"],
    "editor": ["nvim", "vim", "nano", "gedit", "kate"],
    "calculator": ["gnome-calculator", "kcalc", "qalculate-gtk"],
    "settings": ["gnome-control-center", "xfce4-settings-manager"],
    "screenshot": ["gnome-screenshot", "flameshot", "scrot"],
}

MEDIA_PLAYER = "playerctl"
