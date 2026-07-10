# kodak - Jarvis Desktop AI Assistant [TUI / Voice]

A voice-controlled AI assistant inspired by J.A.R.V.I.S. that listens for a wake word, detects intent, and executes commands on your Arch Linux system.

## Features

- **Wake Word Detection**: Always listens for "hey jarvis" using openwakeword (free, no API key)
- **Speech-to-Text**: Transcribes speech using faster-whisper
- **Intent Detection**: Uses local LLM (Ollama/llama3) to understand user intent
- **Command Execution**: Executes shell commands with user confirmation
- **Safety**: Automatically rejects dangerous commands (rm -rf, mkfs, etc.)
- **Text-to-Speech**: Responds using piper (fast, natural) or espeak (fallback)
- **Beautiful TUI**: Rich terminal interface with status indicators

## Architecture

```
kodak2/
├── main.py              # Entry point with TUI
├── config.py            # Configuration
├── core/
│   ├── engine.py        # Main orchestrator
│   ├── wakeword.py      # Wake word detection (openwakeword)
│   ├── stt.py           # Speech-to-text (faster-whisper)
│   ├── tts.py           # Text-to-speech (piper)
│   ├── llm.py           # LLM client (ollama)
│   ├── intent.py        # Intent detection & command generation
│   └── executor.py      # Command execution with confirmation
├── commands/
│   ├── apps.py          # App launching
│   ├── files.py         # File operations
│   ├── system.py        # System info
│   ├── packages.py      # Package management (pacman)
│   └── media.py         # Media control (playerctl)
└── utils/
    └── audio.py         # Audio utilities (beeps, sounds)
```

## Prerequisites

- Python 3.10+
- Ollama installed and running with llama3 model
- Arch Linux (for pacman commands)
- Microphone access
- Audio output (speakers/headphones)

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd kodak2
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install openwakeword faster-whisper piper-tts rich sounddevice numpy requests scipy
   ```

4. **Install system dependencies (Arch Linux):**
   ```bash
   sudo pacman -S espeak-ng playerctl alsa-utils
   ```

5. **Install Ollama and pull llama3 model:**
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ollama pull llama3
   ```

6. **Start Ollama service:**
   ```bash
   ollama serve
   ```

## Usage

### Starting the Assistant

```bash
python main.py
```

### Interaction Methods

1. **Voice Input (Wake Word)**:
   - Say "hey jarvis" to activate
   - Speak your command
   - Confirm with voice ("yes"/"no") or keyboard (y/n)

2. **Text Input**:
   - Type commands directly in the TUI
   - Press Enter to execute

### Commands

#### App Launching
- "open firefox" / "open browser"
- "open code" / "open vscode"
- "open files" / "open file manager"
- "open terminal"
- "open spotify"

#### File Operations
- "create file test.txt"
- "create directory projects"
- "delete file old.txt"
- "move file.txt to backup/"
- "copy file.txt to backup/"
- "list files"
- "find file main.py"

#### System Info
- "what time is it"
- "what's the date"
- "cpu usage"
- "memory usage"
- "disk usage"
- "network info"
- "system info"
- "show processes"

#### Package Management
- "install neovim"
- "remove firefox"
- "search python"
- "list installed packages"
- "update system"

#### Media Control
- "play"
- "pause"
- "next track"
- "previous track"
- "volume up"
- "volume down"
- "mute"

### TUI Commands

- `history` or `h` - Show conversation history
- `status` or `s` - Show current status
- `clear` or `cls` - Clear screen
- `exit` or `quit` or `q` - Shutdown

## Configuration

Edit `config.py` to customize:

```python
# Wake word
WAKE_WORD = "hey jarvis"
WAKE_WORD_THRESHOLD = 0.5

# Audio
SAMPLE_RATE = 16000
RECORD_DURATION = 4

# LLM
LLM_MODEL = "llama3"

# TTS
TTS_ENGINE = "piper"  # or "espeak"

# Security
CONFIRM_BEFORE_EXECUTE = True
REJECT_DANGEROUS_COMMANDS = True
```

## Safety Features

The following commands are **automatically rejected**:
- `rm -rf /` or `rm -rf ~`
- `mkfs.*` (format disk)
- `dd if=...`
- `chmod -R 777 /`
- `shutdown`, `reboot`, `halt`, `poweroff`
- Commands modifying `/etc/passwd` or `/etc/shadow`

## Data Storage

- **Logs**: `~/.kodak2/logs/`
- **Command History**: `~/.kodak2/command_history.json`
- **Preferences**: `~/.kodak2/preferences.json`

## Troubleshooting

### Wake Word Not Detecting
- Ensure microphone is working: `arecord -d 3 test.wav`
- Adjust threshold in `config.py`: `WAKE_WORD_THRESHOLD = 0.5`
- Check openwakeword models are downloaded

### No Audio Output
- Check speakers: `speaker-test -t wav`
- Verify piper is installed: `piper --help`
- Fallback to espeak: Set `TTS_ENGINE = "espeak"` in config

### LLM Not Responding
- Ensure Ollama is running: `curl http://localhost:11434/api/tags`
- Check model is pulled: `ollama list`
- Verify model name in config: `LLM_MODEL = "llama3"`

### Command Execution Fails
- Check permissions for sudo commands
- Verify packages are installed (playerctl, etc.)
- Check logs in `~/.kodak2/logs/`

## License

This project is open source and available under the MIT License.
