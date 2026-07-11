import subprocess
from typing import Tuple

from config import SYSTEM, MEDIA_PLAYER


class MediaCommands:
    def __init__(self):
        self.player = MEDIA_PLAYER

    def _run_cmd(self, cmd: list, timeout: int = 10) -> Tuple[bool, str]:
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout
            )
            if result.returncode == 0:
                return True, result.stdout.strip() if result.stdout else "Done"
            return False, result.stderr.strip() if result.stderr else "Failed"
        except FileNotFoundError:
            return False, f"Command not found: {cmd[0]}"
        except Exception as e:
            return False, str(e)

    def play(self) -> Tuple[bool, str]:
        if SYSTEM == "Darwin":
            return self._run_cmd(["osascript", "-e", "tell application \"System Events\" to key code 16 using {command down}"])
        elif SYSTEM == "Windows":
            return self._run_cmd(["powershell", "-c", "(New-Object -ComObject WScript.Shell}).SendKeys('{MediaPlayPause}')"])
        elif self.player == "playerctl":
            return self._run_cmd(["playerctl", "play"])
        return False, "No media player available"

    def pause(self) -> Tuple[bool, str]:
        if SYSTEM == "Darwin":
            return self._run_cmd(["osascript", "-e", "tell application \"System Events\" to key code 16 using {command down}"])
        elif SYSTEM == "Windows":
            return self._run_cmd(["powershell", "-c", "(New-Object -ComObject WScript.Shell}).SendKeys('{MediaPlayPause}')"])
        elif self.player == "playerctl":
            return self._run_cmd(["playerctl", "pause"])
        return False, "No media player available"

    def toggle(self) -> Tuple[bool, str]:
        if SYSTEM == "Darwin":
            return self._run_cmd(["osascript", "-e", "tell application \"System Events\" to key code 16 using {command down}"])
        elif SYSTEM == "Windows":
            return self._run_cmd(["powershell", "-c", "(New-Object -ComObject WScript.Shell}).SendKeys('{MediaPlayPause}')"])
        elif self.player == "playerctl":
            return self._run_cmd(["playerctl", "play-pause"])
        return False, "No media player available"

    def next_track(self) -> Tuple[bool, str]:
        if SYSTEM == "Darwin":
            return self._run_cmd(["osascript", "-e", "tell application \"System Events\" to key code 17 using {command down}"])
        elif SYSTEM == "Windows":
            return self._run_cmd(["powershell", "-c", "(New-Object -ComObject WScript.Shell}).SendKeys('{MediaNextTrack}')"])
        elif self.player == "playerctl":
            return self._run_cmd(["playerctl", "next"])
        return False, "No media player available"

    def previous_track(self) -> Tuple[bool, str]:
        if SYSTEM == "Darwin":
            return self._run_cmd(["osascript", "-e", "tell application \"System Events\" to key code 20 using {command down}"])
        elif SYSTEM == "Windows":
            return self._run_cmd(["powershell", "-c", "(New-Object -ComObject WScript.Shell}).SendKeys('{MediaPrevTrack}')"])
        elif self.player == "playerctl":
            return self._run_cmd(["playerctl", "previous"])
        return False, "No media player available"

    def volume_up(self, amount: int = 10) -> Tuple[bool, str]:
        if SYSTEM == "Darwin":
            return self._run_cmd(["osascript", "-e", "set volume output volume (output volume of (get volume settings) + 10)"])
        elif SYSTEM == "Windows":
            return self._run_cmd(["powershell", "-c", "$wshShell = New-Object -ComObject WScript.Shell; 1..10 | ForEach-Object {$wshShell.SendKeys([char]175)}"])
        else:
            return self._run_cmd(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"+{amount}%"])

    def volume_down(self, amount: int = 10) -> Tuple[bool, str]:
        if SYSTEM == "Darwin":
            return self._run_cmd(["osascript", "-e", "set volume output volume (output volume of (get volume settings) - 10)"])
        elif SYSTEM == "Windows":
            return self._run_cmd(["powershell", "-c", "$wshShell = New-Object -ComObject WScript.Shell; 1..10 | ForEach-Object {$wshShell.SendKeys([char]174)}"])
        else:
            return self._run_cmd(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"-{amount}%"])

    def mute(self) -> Tuple[bool, str]:
        if SYSTEM == "Darwin":
            return self._run_cmd(["osascript", "-e", "set volume output muted not (output muted of (get volume settings))"])
        elif SYSTEM == "Windows":
            return self._run_cmd(["powershell", "-c", "(New-Object -ComObject WScript.Shell}).SendKeys('{VolumeMute}')"])
        else:
            return self._run_cmd(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"])

    def get_status(self) -> Tuple[bool, str]:
        if self.player == "playerctl":
            return self._run_cmd(["playerctl", "status"])
        return True, "Unknown"

    def get_current(self) -> Tuple[bool, str]:
        if self.player == "playerctl":
            return self._run_cmd(["playerctl", "metadata", "--format", "{{artist}} - {{title}}"])
        return True, "No track info available"

    def handle_intent(self, action: str, params: dict) -> Tuple[bool, str]:
        handlers = {
            "play": self.play,
            "pause": self.pause,
            "toggle": self.toggle,
            "next": self.next_track,
            "previous": self.previous_track,
            "volume_up": lambda: self.volume_up(params.get("amount", 10)),
            "volume_down": lambda: self.volume_down(params.get("amount", 10)),
            "mute": self.mute,
            "status": self.get_status,
            "current": self.get_current,
        }
        handler = handlers.get(action)
        if handler:
            return handler()
        return False, f"Unknown media action: {action}"
