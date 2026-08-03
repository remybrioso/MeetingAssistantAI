"""
evidence_reference.py

Referencia trazable a un fragmento de la transcripción.
"""

from dataclasses import dataclass


@dataclass(
    frozen=True,
    slots=True,
)
class EvidenceReference:
    """
    Identifica el segmento de la transcripción que respalda
    una afirmación incluida en un MeetingReport.

    Attributes:
        speaker:
            Identificador lógico del hablante.

        start:
            Tiempo inicial del fragmento, en segundos.

        end:
            Tiempo final del fragmento, en segundos.

        excerpt:
            Texto breve extraído de la transcripción.
    """

    speaker: str
    start: float
    end: float
    excerpt: str

    def __post_init__(self) -> None:
        normalized_speaker = self.speaker.strip()
        normalized_excerpt = self.excerpt.strip()

        if not normalized_speaker:
            raise ValueError(
                "EvidenceReference speaker no puede "
                "estar vacío."
            )

        if self.start < 0:
            raise ValueError(
                "EvidenceReference start no puede "
                "ser negativo."
            )

        if self.end < self.start:
            raise ValueError(
                "EvidenceReference end no puede ser "
                "menor que start."
            )

        if not normalized_excerpt:
            raise ValueError(
                "EvidenceReference excerpt no puede "
                "estar vacío."
            )

        object.__setattr__(
            self,
            "speaker",
            normalized_speaker,
        )

        object.__setattr__(
            self,
            "excerpt",
            normalized_excerpt,
        )

    def as_dict(self) -> dict:
        """
        Devuelve una representación serializable.
        """

        return {
            "speaker": self.speaker,
            "start": self.start,
            "end": self.end,
            "excerpt": self.excerpt,
        }