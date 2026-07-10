import subprocess
from typing import Tuple


class PackageCommands:
    def __init__(self):
        self.pacman = "pacman"
        self.sudo = "sudo"

    def _run(self, cmd: list, timeout: int = 60) -> Tuple[bool, str]:
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            output = result.stdout + result.stderr
            if result.returncode == 0:
                return True, output.strip()
            return False, output.strip()
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)

    def install(self, package: str) -> Tuple[bool, str]:
        return self._run([self.sudo, self.pacman, "-S", "--noconfirm", package], timeout=120)

    def remove(self, package: str) -> Tuple[bool, str]:
        return self._run([self.sudo, self.pacman, "-R", "--noconfirm", package])

    def search(self, query: str) -> Tuple[bool, str]:
        return self._run([self.pacman, "-Ss", query])

    def list_installed(self) -> Tuple[bool, str]:
        result = self._run([self.pacman, "-Q"])
        if result[0]:
            packages = result[1].strip().split("\n")
            return True, f"Installed packages: {len(packages)}"
        return result

    def update_system(self) -> Tuple[bool, str]:
        return self._run([self.sudo, self.pacman, "-Syu", "--noconfirm"], timeout=300)

    def get_info(self, package: str) -> Tuple[bool, str]:
        return self._run([self.pacman, "-Qi", package])

    def handle_intent(self, action: str, params: dict) -> Tuple[bool, str]:
        package = params.get("package", "")
        if action == "install":
            if not package:
                return False, "No package specified"
            return self.install(package)
        elif action == "remove":
            if not package:
                return False, "No package specified"
            return self.remove(package)
        elif action == "search":
            query = params.get("query", package)
            if not query:
                return False, "No search query specified"
            return self.search(query)
        elif action == "list":
            return self.list_installed()
        elif action == "update":
            return self.update_system()
        elif action == "info":
            if not package:
                return False, "No package specified"
            return self.get_info(package)
        return False, f"Unknown package action: {action}"
