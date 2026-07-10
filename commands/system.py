import platform
import subprocess
import os
from typing import Tuple


class SystemCommands:
    def __init__(self):
        pass

    def get_time(self) -> Tuple[bool, str]:
        from datetime import datetime
        now = datetime.now()
        return True, now.strftime("%H:%M")

    def get_date(self) -> Tuple[bool, str]:
        from datetime import datetime
        now = datetime.now()
        return True, now.strftime("%A, %B %d, %Y")

    def get_cpu_usage(self) -> Tuple[bool, str]:
        try:
            result = subprocess.run(
                ["grep", "cpu", "/proc/stat"],
                capture_output=True, text=True, timeout=5
            )
            parts = result.stdout.split()
            if len(parts) >= 5:
                idle = int(parts[4])
                total = sum(int(x) for x in parts[1:5])
                usage = round((1 - idle / total) * 100, 1)
                return True, f"CPU usage: {usage}%"
            return False, "Could not parse CPU info"
        except Exception as e:
            return False, f"Failed to get CPU usage: {e}"

    def get_memory_usage(self) -> Tuple[bool, str]:
        try:
            result = subprocess.run(
                ["free", "-h"],
                capture_output=True, text=True, timeout=5
            )
            lines = result.stdout.strip().split("\n")
            if len(lines) >= 2:
                parts = lines[1].split()
                return True, f"Memory: {parts[2]} used / {parts[1]} total ({parts[2]})"
            return False, "Could not parse memory info"
        except Exception as e:
            return False, f"Failed to get memory usage: {e}"

    def get_disk_usage(self) -> Tuple[bool, str]:
        try:
            result = subprocess.run(
                ["df", "-h", "/"],
                capture_output=True, text=True, timeout=5
            )
            lines = result.stdout.strip().split("\n")
            if len(lines) >= 2:
                parts = lines[1].split()
                return True, f"Disk: {parts[2]} used / {parts[1]} total ({parts[4]})"
            return False, "Could not parse disk info"
        except Exception as e:
            return False, f"Failed to get disk usage: {e}"

    def get_network_info(self) -> Tuple[bool, str]:
        try:
            result = subprocess.run(
                ["ip", "addr", "show"],
                capture_output=True, text=True, timeout=5
            )
            lines = result.stdout.strip().split("\n")
            interfaces = []
            current = None
            for line in lines:
                if line.startswith("inet "):
                    parts = line.split()
                    if len(parts) >= 2 and current:
                        interfaces.append(f"{current}: {parts[1]}")
                elif ":" in line and not line.startswith(" "):
                    current = line.split(":")[1].strip()
            if interfaces:
                return True, "Network:\n" + "\n".join(interfaces)
            return True, "No network interfaces found"
        except Exception as e:
            return False, f"Failed to get network info: {e}"

    def get_system_info(self) -> Tuple[bool, str]:
        try:
            info = {
                "OS": f"{platform.system()} {platform.release()}",
                "Machine": platform.machine(),
                "Python": platform.python_version(),
                "Hostname": platform.node(),
            }
            lines = [f"{k}: {v}" for k, v in info.items()]
            return True, "System Info:\n" + "\n".join(lines)
        except Exception as e:
            return False, f"Failed to get system info: {e}"

    def get_running_processes(self) -> Tuple[bool, str]:
        try:
            result = subprocess.run(
                ["ps", "aux", "--sort=-pcpu"],
                capture_output=True, text=True, timeout=5
            )
            lines = result.stdout.strip().split("\n")
            if len(lines) > 6:
                return True, "Top processes:\n" + "\n".join(lines[:6])
            return True, result.stdout
        except Exception as e:
            return False, f"Failed to get processes: {e}"

    def handle_intent(self, action: str, params: dict) -> Tuple[bool, str]:
        handlers = {
            "time": self.get_time,
            "date": self.get_date,
            "cpu_usage": self.get_cpu_usage,
            "memory_usage": self.get_memory_usage,
            "disk_usage": self.get_disk_usage,
            "network_info": self.get_network_info,
            "system_info": self.get_system_info,
            "processes": self.get_running_processes,
        }
        handler = handlers.get(action)
        if handler:
            return handler()
        return False, f"Unknown system action: {action}"
