import requests
from typing import Generator, Optional

from config import OLLAMA_URL, OLLAMA_STREAM_URL, LLM_MODEL


class LLMClient:
    def __init__(self, model=LLM_MODEL):
        self.model = model
        self.url = OLLAMA_URL
        self.stream_url = OLLAMA_STREAM_URL

    def generate(self, prompt: str, system: Optional[str] = None) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        if system:
            payload["system"] = system
        try:
            res = requests.post(self.url, json=payload, timeout=120)
            res.raise_for_status()
            data = res.json()
            return data.get("response", "")
        except requests.RequestException:
            return ""

    def generate_stream(self, prompt: str, system: Optional[str] = None) -> Generator[str, None, None]:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
        }
        if system:
            payload["system"] = system
        try:
            with requests.post(self.stream_url, json=payload, stream=True, timeout=120) as res:
                res.raise_for_status()
                for line in res.iter_lines():
                    if line:
                        import json
                        data = json.loads(line)
                        chunk = data.get("response", "")
                        if chunk:
                            yield chunk
                        if data.get("done", False):
                            break
        except requests.RequestException:
            yield ""

    def is_available(self) -> bool:
        try:
            res = requests.get("http://localhost:11434/api/tags", timeout=5)
            return res.status_code == 200
        except requests.RequestException:
            return False
