"""
ollama_health_service.py

Adaptador de compatibilidad para código antiguo.

El diagnóstico oficial se encuentra ahora
en OllamaProvider.health().
"""

from providers.ollama_provider import OllamaProvider


class OllamaHealthService:

    def __init__(self, provider=None):

        self.provider = (
            provider or OllamaProvider()
        )

    def check(self):

        health = self.provider.health()

        return {
            "available": health.connected,
            "model_found": health.model_found,
            "model": health.model,
            "models": health.available_models,
            "response_time_ms": (
                health.response_time_ms
            ),
            "message": health.message,
            "error": health.error,
        }