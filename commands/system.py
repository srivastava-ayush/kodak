import platform
import subprocess
import os
from typing import Tuple

from config import SYSTEM


class SystemCommands:
    def __init__(self):
        pass

    def _run(self, cmd, timeout=5) -> Tuple[bool, str]:
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout
            )
            output = result.stdout.strip()
            if result.returncode == 0 and output:
                return True, output
            return False, output or "Command returned no output"
        except Exception as e:
            return False, str(e)

    def get_time(self) -> Tuple[bool, str]:
        from datetime import datetime
        return True, datetime.now().strftime("%H:%M")

    def get_date(self) -> Tuple[bool, str]:
        from datetime import datetime
        return True, datetime.now().strftime("%A, %B %d, %Y")

    def get_cpu_usage(self) -> Tuple[bool, str]:
        if SYSTEM == "Darwin":
            return self._run(["top", "-l", "1", "-n", "0"])
        elif SYSTEM == "Windows":
            return self._run(["powershell", "-c", "Get-Counter '\\Processor(_Total)\\% Processor Time' | Select-Object -ExpandProperty CounterSamples | Select-Object CookedValue"])
        else:
            try:
                with open("/proc/stat") as f:
                    parts = f.readline().split()
                idle, total = int(parts[4]), sum(int(x) for x in parts[1:5])
                usage = round((1 - idle / total) * 100, 1)
                return True, f"CPU usage: {usage}%"
            except Exception:
                return self._run(["top", "-bn1"])

    def get_memory_usage(self) -> Tuple[bool, str]:
        if SYSTEM == "Darwin":
            return self._run(["vm_stat"])
        elif SYSTEM == "Windows":
            return self._run(["powershell", "-c", "Get-CimInstance Win32_OperatingSystem | Select-Object TotalVisibleMemorySize,FreePhysicalMemory"])
        else:
            return self._run(["free", "-h"])

    def get_disk_usage(self) -> Tuple[bool, str]:
        if SYSTEM == "Windows":
            return self._run(["powershell", "-c", "Get-PSDrive C | Select-Object Used,Free"])
        else:
            path = "/" if SYSTEM == "Linux" else "/"
            return self._run(["df", "-h", path])

    def get_network_info(self) -> Tuple[bool, str]:
        if SYSTEM == "Darwin":
            return self._run(["ifconfig"])
        elif SYSTEM == "Windows":
            return self._run(["ipconfig"])
        else:
            return self._run(["ip", "addr", "show"])

    def get_system_info(self) -> Tuple[bool, str]:
        info = {
            "OS": f"{platform.system()} {platform.release()}",
            "Machine": platform.machine(),
            "Python": platform.python_version(),
            "Hostname": platform.node(),
        }
        lines = [f"{k}: {v}" for k, v in info.items()]
        return True, "System Info:\n" + "\n".join(lines)

    def get_running_processes(self) -> Tuple[bool, str]:
        if SYSTEM == "Darwin":
            return self._run(["ps", "aux", "--sort=-pcpu"])
        elif SYSTEM == "Windows":
            return self._run(["powershell", "-c", "Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 Name,CPU,WorkingSet"])
        else:
            return self._run(["ps", "aux", "--sort=-pcpu"])

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
