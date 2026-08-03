"""
decision.py

Decisión explícita identificada durante una reunión.
"""

from dataclasses import dataclass

from models.meeting_report.evidence_backed_item import (
    EvidenceBackedItem,
)


@dataclass(
    frozen=True,
    slots=True,
)
class Decision(
    EvidenceBackedItem
):
    """
    Representa una decisión explícita respaldada
    por evidencia de la transcripción.

    Attributes:
        description:
            Decisión adoptada.

        evidence:
            Referencias que respaldan la decisión.

        rationale:
            Justificación expresada durante la reunión.
            Será None cuando no exista evidencia suficiente.
    """

    rationale: str | None = None

    def __post_init__(self) -> None:
        super().__post_init__()

        normalized_rationale = (
            self.rationale.strip()
            if self.rationale is not None
            else None
        )

        object.__setattr__(
            self,
            "rationale",
            normalized_rationale or None,
        )

    def _extra_fields(self) -> dict:
        """
        Devuelve los campos particulares de Decision.
        """

        return {
            "rationale": self.rationale,
        }