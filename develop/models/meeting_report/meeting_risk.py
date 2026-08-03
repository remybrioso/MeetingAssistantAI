"""
meeting_risk.py

Riesgo o bloqueo identificado durante una reunión.
"""

from dataclasses import dataclass

from models.meeting_report.evidence_backed_item import (
    EvidenceBackedItem,
)


@dataclass(
    frozen=True,
    slots=True,
)
class MeetingRisk(
    EvidenceBackedItem
):
    """
    Representa un riesgo, bloqueo o amenaza expresada
    durante una reunión.

    Attributes:
        description:
            Riesgo o bloqueo identificado.

        evidence:
            Referencias que respaldan el riesgo.

        impact:
            Consecuencia expresada durante la reunión.
            Será None cuando no exista evidencia suficiente.
    """

    impact: str | None = None

    def __post_init__(self) -> None:
        super().__post_init__()

        normalized_impact = (
            self.impact.strip()
            if self.impact is not None
            else None
        )

        object.__setattr__(
            self,
            "impact",
            normalized_impact or None,
        )

    def _extra_fields(self) -> dict:
        """
        Devuelve los campos particulares de MeetingRisk.
        """

        return {
            "impact": self.impact,
        }