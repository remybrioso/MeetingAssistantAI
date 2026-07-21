"""
artifact.py

Clase base para todos los artefactos generados por IA.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class Artifact:

    artifact_type: str

    provider: str

    model: str

    prompt_version: str

    created_at: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )

    def as_dict(self):

        return {
            "artifact_type": self.artifact_type,
            "provider": self.provider,
            "model": self.model,
            "prompt_version": self.prompt_version,
            "created_at": self.created_at.isoformat()
        }