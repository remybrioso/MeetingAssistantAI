"""
participant.py

Participante identificado o mencionado durante una reunión.
"""

from dataclasses import dataclass


@dataclass(
    frozen=True,
    slots=True,
)
class Participant:
    """
    Representa una identidad real o lógica asociada
    a una reunión.

    Todos los atributos son opcionales porque una fuente
    de audio puede conocerse sin que exista evidencia
    suficiente para determinar nombre o función.
    """

    name: str | None = None
    speaker: str | None = None
    role: str | None = None

    def __post_init__(self) -> None:
        normalized_name = self._normalize_optional(
            self.name
        )

        normalized_speaker = self._normalize_optional(
            self.speaker
        )

        normalized_role = self._normalize_optional(
            self.role
        )

        if (
            normalized_name is None
            and normalized_speaker is None
            and normalized_role is None
        ):
            raise ValueError(
                "Participant requiere al menos un dato "
                "identificable."
            )

        object.__setattr__(
            self,
            "name",
            normalized_name,
        )

        object.__setattr__(
            self,
            "speaker",
            normalized_speaker,
        )

        object.__setattr__(
            self,
            "role",
            normalized_role,
        )

    @staticmethod
    def _normalize_optional(
        value: str | None,
    ) -> str | None:
        """
        Convierte cadenas vacías en None y elimina
        espacios externos.
        """

        if value is None:
            return None

        normalized = value.strip()

        return normalized or None

    def as_dict(self) -> dict:
        """
        Devuelve una representación serializable.
        """

        return {
            "name": self.name,
            "speaker": self.speaker,
            "role": self.role,
        }