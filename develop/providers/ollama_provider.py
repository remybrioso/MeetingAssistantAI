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

        summary_schema = {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string"
                },
                "executive_summary": {
                    "type": "string"
                },
                "key_points": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "minItems": 3,
                    "maxItems": 5
                }
            },
            "required": [
                "title",
                "executive_summary",
                "key_points"
            ]
        }

        response = requests.post(
            self.url,
            json={
                "model": self.model,
                "prompt": prompt,
                "format": summary_schema,
                "stream": False,
                "think": False,
                "options": {
                    "temperature": 0.1,
                    "num_ctx": 8192
                }
            },
            timeout=180
        )

        response.raise_for_status()

        payload = response.json()

        generated_text = payload.get(
            "response",
            ""
        ).strip()

        if not generated_text:
            raise ValueError(
                "Ollama devolvió una respuesta vacía."
            )

        return generated_text