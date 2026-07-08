"""
ollama_health_service.py
"""

import requests


class OllamaHealthService:

    def __init__(self):

        self.url = "http://localhost:11434/api/tags"

    def check(self):

        try:

            response = requests.get(
                self.url,
                timeout=3
            )

            response.raise_for_status()

            data = response.json()

            models = []

            for model in data.get("models", []):

                models.append(
                    model["name"]
                )

            return {
                "available": True,
                "models": models,
                "message": "Ollama disponible."
            }

        except Exception as ex:

            return {
                "available": False,
                "models": [],
                "message": str(ex)
            }