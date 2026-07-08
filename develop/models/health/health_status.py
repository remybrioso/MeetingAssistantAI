"""
health_status.py

Representa el estado de un servicio externo.
"""

from dataclasses import dataclass, field


@dataclass
class HealthStatus:

    available: bool

    service: str

    message: str

    models: list[str] = field(default_factory=list)

    def as_dict(self):

        return {
            "service": self.service,
            "available": self.available,
            "message": self.message,
            "models": self.models
        }