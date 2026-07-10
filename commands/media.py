import subprocess
from typing import Tuple

from config import MEDIA_PLAYER


class MediaCommands:
    def __init__(self):
        self.player = MEDIA_PLAYER

    def _run_playerctl(self, command: str) -> Tuple[bool, str]:
        try:
            result = subprocess.run(
                [self.player, command],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return True, result.stdout.strip() if result.stdout else f"Executed: {command}"
            return False, result.stderr.strip() if result.stderr else f"Failed: {command}"
        except FileNotFoundError:
            return False, "playerctl not found. Install with: sudo pacman -S playerctl"
        except Exception as e:
            return False, str(e)

    def _run_pactl(self, args: list) -> Tuple[bool, str]:
        try:
            result = subprocess.run(
                ["pactl"] + args,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return True, result.stdout.strip() if result.stdout else "Done"
            return False, result.stderr.strip() if result.stderr else "Failed"
        except FileNotFoundError:
            return False, "pactl not found"
        except Exception as e:
            return False, str(e)

    def play(self) -> Tuple[bool, str]:
        return self._run_playerctl("play")

    def pause(self) -> Tuple[bool, str]:
        return self._run_playerctl("pause")

    def toggle(self) -> Tuple[bool, str]:
        return self._run_playerctl("play-pause")

    def next_track(self) -> Tuple[bool, str]:
        return self._run_playerctl("next")

    def previous_track(self) -> Tuple[bool, str]:
        return self._run_playerctl("previous")

    def volume_up(self, amount: int = 10) -> Tuple[bool, str]:
        return self._run_pactl(
            ["set-sink-volume", "@DEFAULT_SINK@", f"+{amount}%"]
        )

    def volume_down(self, amount: int = 10) -> Tuple[bool, str]:
        return self._run_pactl(
            ["set-sink-volume", "@DEFAULT_SINK@", f"-{amount}%"]
        )

    def mute(self) -> Tuple[bool, str]:
        return self._run_pactl(
            ["set-sink-mute", "@DEFAULT_SINK@", "toggle"]
        )

    def get_status(self) -> Tuple[bool, str]:
        try:
            result = subprocess.run(
                [self.player, "status"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return True, result.stdout.strip() if result.stdout else "Unknown"
        except Exception:
            return False, "Could not get media status"

    def get_current(self) -> Tuple[bool, str]:
        try:
            result = subprocess.run(
                [self.player, "metadata", "--format", "{{artist}} - {{title}}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.stdout.strip():
                return True, result.stdout.strip()
            return True, "No track playing"
        except Exception:
            return False, "Could not get current track"

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
