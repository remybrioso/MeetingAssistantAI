"""
evidence_backed_item.py

Base común para elementos de MeetingReport respaldados
por evidencia de la transcripción.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from models.meeting_report.evidence_reference import (
    EvidenceReference,
)


@dataclass(
    frozen=True,
    slots=True,
)
class EvidenceBackedItem(ABC):
    """
    Base abstracta para decisiones, acciones, riesgos
    y asuntos pendientes.

    Centraliza:
    - descripción;
    - referencias de evidencia;
    - normalización;
    - validación;
    - serialización común.
    """

    description: str
    evidence: list[EvidenceReference] = field(
        default_factory=list
    )

    def __post_init__(self) -> None:
        normalized_description = (
            self.description.strip()
        )

        if not normalized_description:
            raise ValueError(
                f"{type(self).__name__} description "
                "no puede estar vacío."
            )

        normalized_evidence = list(
            self.evidence
        )

        for reference in normalized_evidence:

            if not isinstance(
                reference,
                EvidenceReference,
            ):
                raise TypeError(
                    f"{type(self).__name__} evidence "
                    "solo admite instancias de "
                    "EvidenceReference."
                )

        object.__setattr__(
            self,
            "description",
            normalized_description,
        )

        object.__setattr__(
            self,
            "evidence",
            normalized_evidence,
        )

    def as_dict(self) -> dict:
        """
        Devuelve la representación serializable completa.
        """

        data = {
            "description": self.description,
            "evidence": [
                reference.as_dict()
                for reference in self.evidence
            ],
        }

        data.update(
            self._extra_fields()
        )

        return data

    @abstractmethod
    def _extra_fields(self) -> dict:
        """
        Devuelve los campos particulares de la entidad.

        Las clases concretas deben implementar este método.
        """