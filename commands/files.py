import os
import shutil
from pathlib import Path
from typing import Tuple


class FileCommands:
    def __init__(self):
        self.cwd = Path.cwd()

    def create_file(self, filename: str) -> Tuple[bool, str]:
        path = Path(filename)
        try:
            path.touch()
            return True, f"Created file: {filename}"
        except Exception as e:
            return False, f"Failed to create file: {e}"

    def create_directory(self, dirname: str) -> Tuple[bool, str]:
        path = Path(dirname)
        try:
            path.mkdir(parents=True, exist_ok=True)
            return True, f"Created directory: {dirname}"
        except Exception as e:
            return False, f"Failed to create directory: {e}"

    def delete_file(self, filename: str) -> Tuple[bool, str]:
        path = Path(filename)
        try:
            if path.is_file():
                path.unlink()
                return True, f"Deleted file: {filename}"
            elif path.is_dir():
                shutil.rmtree(path)
                return True, f"Deleted directory: {filename}"
            else:
                return False, f"File not found: {filename}"
        except Exception as e:
            return False, f"Failed to delete: {e}"

    def move_file(self, source: str, destination: str) -> Tuple[bool, str]:
        try:
            shutil.move(source, destination)
            return True, f"Moved {source} to {destination}"
        except Exception as e:
            return False, f"Failed to move: {e}"

    def copy_file(self, source: str, destination: str) -> Tuple[bool, str]:
        try:
            src = Path(source)
            if src.is_file():
                shutil.copy2(source, destination)
            elif src.is_dir():
                shutil.copytree(source, destination)
            return True, f"Copied {source} to {destination}"
        except Exception as e:
            return False, f"Failed to copy: {e}"

    def list_files(self, path: str = ".") -> Tuple[bool, str]:
        try:
            items = list(Path(path).iterdir())
            items.sort(key=lambda x: (x.is_file(), x.name))
            lines = []
            for item in items:
                prefix = "d" if item.is_dir() else "-"
                lines.append(f"{prefix} {item.name}")
            return True, "\n".join(lines) if lines else "Directory is empty"
        except Exception as e:
            return False, f"Failed to list files: {e}"

    def find_file(self, pattern: str, search_path: str = ".") -> Tuple[bool, str]:
        try:
            matches = list(Path(search_path).rglob(f"*{pattern}*"))
            if matches:
                results = [str(m) for m in matches[:20]]
                return True, "Found:\n" + "\n".join(results)
            return False, f"No files matching '{pattern}' found"
        except Exception as e:
            return False, f"Failed to search: {e}"

    def handle_intent(self, action: str, params: dict) -> Tuple[bool, str]:
        if action == "create":
            name = params.get("name", "")
            is_dir = params.get("is_dir", False)
            if is_dir:
                return self.create_directory(name)
            return self.create_file(name)
        elif action == "delete":
            return self.delete_file(params.get("name", ""))
        elif action == "move":
            return self.move_file(params.get("source", ""), params.get("dest", ""))
        elif action == "copy":
            return self.copy_file(params.get("source", ""), params.get("dest", ""))
        elif action == "list":
            return self.list_files(params.get("path", "."))
        elif action == "find":
            return self.find_file(params.get("pattern", ""), params.get("path", "."))
        return False, f"Unknown file action: {action}"
