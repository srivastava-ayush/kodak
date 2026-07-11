import subprocess
import shutil
from typing import Tuple

from config import SYSTEM


class PackageCommands:
    def __init__(self):
        self.sudo = "sudo" if SYSTEM != "Windows" else ""
        self._detect_pm()

    def _detect_pm(self):
        if SYSTEM == "Darwin":
            self.pm = "brew"
            self.sudo = ""
        elif SYSTEM == "Windows":
            self.pm = "winget"
            self.sudo = ""
        elif shutil.which("yay"):
            self.pm = "yay"
        elif shutil.which("paru"):
            self.pm = "paru"
        elif shutil.which("pacman"):
            self.pm = "pacman"
        elif shutil.which("apt"):
            self.pm = "apt"
        elif shutil.which("dnf"):
            self.pm = "dnf"
        else:
            self.pm = None

    def _run(self, cmd: list, timeout: int = 60) -> Tuple[bool, str]:
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout
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
        if not self.pm:
            return False, "No package manager found"
        if self.pm in ("pacman", "yay", "paru"):
            cmd = f"{self.sudo} {self.pm} -S --noconfirm {package}".split()
        elif self.pm == "apt":
            cmd = f"{self.sudo} apt install -y {package}".split()
        elif self.pm == "dnf":
            cmd = f"{self.sudo} dnf install -y {package}".split()
        elif self.pm == "brew":
            cmd = ["brew", "install", package]
        elif self.pm == "winget":
            cmd = ["winget", "install", package]
        else:
            return False, f"Unsupported package manager: {self.pm}"
        return self._run(cmd, timeout=120)

    def remove(self, package: str) -> Tuple[bool, str]:
        if not self.pm:
            return False, "No package manager found"
        if self.pm in ("pacman", "yay", "paru"):
            cmd = f"{self.sudo} {self.pm} -R --noconfirm {package}".split()
        elif self.pm == "apt":
            cmd = f"{self.sudo} apt remove -y {package}".split()
        elif self.pm == "dnf":
            cmd = f"{self.sudo} dnf remove -y {package}".split()
        elif self.pm == "brew":
            cmd = ["brew", "uninstall", package]
        elif self.pm == "winget":
            cmd = ["winget", "uninstall", package]
        else:
            return False, f"Unsupported package manager: {self.pm}"
        return self._run(cmd)

    def search(self, query: str) -> Tuple[bool, str]:
        if not self.pm:
            return False, "No package manager found"
        if self.pm in ("pacman", "yay", "paru"):
            cmd = [self.pm, "-Ss", query]
        elif self.pm == "apt":
            cmd = ["apt", "search", query]
        elif self.pm == "dnf":
            cmd = ["dnf", "search", query]
        elif self.pm == "brew":
            cmd = ["brew", "search", query]
        elif self.pm == "winget":
            cmd = ["winget", "search", query]
        else:
            return False, f"Unsupported package manager: {self.pm}"
        return self._run(cmd)

    def list_installed(self) -> Tuple[bool, str]:
        if not self.pm:
            return False, "No package manager found"
        if self.pm in ("pacman", "yay", "paru"):
            result = self._run([self.pm, "-Q"])
            if result[0]:
                count = len(result[1].strip().split("\n"))
                return True, f"Installed packages: {count}"
            return result
        elif self.pm == "apt":
            result = self._run(["apt", "--installed"])
            if result[0]:
                count = len([l for l in result[1].strip().split("\n") if l.strip()])
                return True, f"Installed packages: {count}"
            return result
        elif self.pm == "brew":
            result = self._run(["brew", "list"])
            if result[0]:
                count = len(result[1].strip().split("\n"))
                return True, f"Installed packages: {count}"
            return result
        elif self.pm == "winget":
            return self._run(["winget", "list"])
        return False, "Not implemented"

    def update_system(self) -> Tuple[bool, str]:
        if not self.pm:
            return False, "No package manager found"
        if self.pm in ("pacman", "yay", "paru"):
            cmd = f"{self.sudo} {self.pm} -Syu --noconfirm".split()
        elif self.pm == "apt":
            cmd = f"{self.sudo} apt update && {self.sudo} apt upgrade -y".split()
        elif self.pm == "dnf":
            cmd = f"{self.sudo} dnf upgrade -y".split()
        elif self.pm == "brew":
            cmd = ["brew", "upgrade"]
        elif self.pm == "winget":
            cmd = ["winget", "upgrade", "--all"]
        else:
            return False, f"Unsupported package manager: {self.pm}"
        return self._run(cmd, timeout=300)

    def get_info(self, package: str) -> Tuple[bool, str]:
        if not self.pm:
            return False, "No package manager found"
        if self.pm in ("pacman", "yay", "paru"):
            return self._run([self.pm, "-Qi", package])
        elif self.pm == "apt":
            return self._run(["apt", "show", package])
        elif self.pm == "brew":
            return self._run(["brew", "info", package])
        elif self.pm == "winget":
            return self._run(["winget", "show", package])
        return False, "Not implemented"

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
