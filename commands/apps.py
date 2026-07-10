import subprocess
import shutil
from typing import Optional, Tuple

from config import APP_ALIASES


class AppCommands:
    def __init__(self):
        self.aliases = APP_ALIASES

    def find_executable(self, name: str) -> Optional[str]:
        if shutil.which(name):
            return name
        for alias_name, executables in self.aliases.items():
            if name.lower() == alias_name.lower():
                for exe in executables:
                    if shutil.which(exe):
                        return exe
        for executables in self.aliases.values():
            for exe in executables:
                if name.lower() in exe.lower() or exe.lower() in name.lower():
                    if shutil.which(exe):
                        return exe
        return None

    def launch(self, app_name: str) -> Tuple[bool, str]:
        exe = self.find_executable(app_name)
        if exe:
            try:
                subprocess.Popen([exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True, f"Launched {exe}"
            except Exception as e:
                return False, f"Failed to launch {exe}: {e}"
        return False, f"Could not find application: {app_name}"

    def handle_intent(self, params: dict) -> Tuple[bool, str]:
        app_name = params.get("app", "")
        if not app_name:
            return False, "No application specified"
        return self.launch(app_name)
