"""
ollama_provider.py

Proveedor local de IA usando Ollama.
"""

import requests

from providers.ai_provider import AIProvider


class OllamaProvider(AIProvider):

    def __init__(
        self,
        model: str = "qwen2.5:3b",
        url: str = "http://localhost:11434/api/generate"
    ):

        self.model = model
        self.url = url

    def generate(self, prompt: str) -> str:

        response = requests.post(
            self.url,
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        return data["response"]