import os
import requests
import logging
from app.llm.base import LLMClient
from app.llm.errors import LLMProviderError

logger = logging.getLogger(__name__)

class OllamaClient(LLMClient):
    def __init__(self):
        self.host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct-q4_K_M")

    def generate(self, prompt: str, temperature: float = 0.3, max_tokens: int = 512, meta: dict | None = None) -> str:
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            if meta and meta.get("json_mode"):
                payload["format"] = "json"

            response = requests.post(f"{self.host}/api/generate", json=payload, timeout=120)
            response.raise_for_status()
            
            return response.json().get("response", "")

        except requests.exceptions.RequestException as e:
            raise LLMProviderError(f"Ollama Connection Error: {e}")
        except Exception as e:
            raise LLMProviderError(f"Ollama Error: {e}")
