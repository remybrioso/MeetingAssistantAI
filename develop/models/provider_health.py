"""
provider_health.py

Resultado técnico del diagnóstico
de un proveedor de inteligencia artificial.
"""

from dataclasses import dataclass, field


@dataclass
class ProviderHealth:

    provider: str
    connected: bool
    model_found: bool
    model: str
    response_time_ms: float | None = None
    available_models: list[str] = field(
        default_factory=list
    )
    message: str = ""
    error: str | None = None

    @property
    def is_healthy(self) -> bool:

        return (
            self.connected
            and self.model_found
        )

    def as_dict(self) -> dict:

        return {
            "provider": self.provider,
            "connected": self.connected,
            "model_found": self.model_found,
            "model": self.model,
            "response_time_ms": self.response_time_ms,
            "available_models": self.available_models,
            "message": self.message,
            "error": self.error,
        }