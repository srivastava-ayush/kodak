import os
import platform
import shutil
from pathlib import Path

SYSTEM = platform.system()

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

VOICE_DIR = BASE_DIR / "voices"
DEFAULT_VOICE = VOICE_DIR / "en_US-lessac-medium.onnx"

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
    r"del\s+/[sfq]",
    r"rmdir\s+/[sq]",
]


def _detect_audio_player():
    if SYSTEM == "Darwin":
        return "afplay"
    if SYSTEM == "Windows":
        return "powershell"
    for cmd in ["aplay", "paplay", "play"]:
        if shutil.which(cmd):
            return cmd
    return None


def _detect_media_player():
    if SYSTEM == "Darwin":
        return "osascript"
    if SYSTEM == "Windows":
        return "powershell"
    if shutil.which("playerctl"):
        return "playerctl"
    return None


AUDIO_PLAYER = _detect_audio_player()
MEDIA_PLAYER = _detect_media_player()

APP_ALIASES = {
    "browser": ["firefox", "chromium", "google-chrome", "brave", "brave-browser", "vivaldi", "opera", "safari", "msedge"],
    "code": ["code", "vscode"],
    "files": ["nautilus", "thunar", "dolphin", "pcmanfm", "finder", "explorer"],
    "terminal": ["kitty", "alacritty", "terminator", "gnome-terminal", "konsole", "iterm2", "wt", "windowsterminal"],
    "spotify": ["spotify"],
    "editor": ["nvim", "vim", "nano", "gedit", "kate", "notepad", "notepad++"],
    "calculator": ["gnome-calculator", "kcalc", "qalculate-gtk", "calculator"],
    "settings": ["gnome-control-center", "xfce4-settings-manager", "x-app-settings"],
    "screenshot": ["gnome-screenshot", "flameshot", "scrot", "screencapture"],
}

if SYSTEM == "Linux":
    DANGEROUS_PATTERNS.extend([
        r"mkfs\.",
        r"dd\s+if=",
        r"/dev/sd",
    ])
elif SYSTEM == "Darwin":
    DANGEROUS_PATTERNS.extend([
        r"diskutil\s+erase",
        r"rm\s+-rf\s+/System",
        r"rm\s+-rf\s+/Library",
    ])
elif SYSTEM == "Windows":
    DANGEROUS_PATTERNS.extend([
        r"Format\s+[A-Z]:",
        r"Remove-Item\s+-Recurse\s+[A-Z]:\\\\",
    ])
