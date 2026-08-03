"""
pending_item.py

Asunto pendiente o no resuelto identificado
durante una reunión.
"""

from dataclasses import dataclass

from models.meeting_report.evidence_backed_item import (
    EvidenceBackedItem,
)


@dataclass(
    frozen=True,
    slots=True,
)
class PendingItem(
    EvidenceBackedItem
):
    """
    Representa un asunto que quedó abierto o pendiente
    de resolución durante una reunión.

    Hereda:
        description:
            Descripción del asunto pendiente.

        evidence:
            Referencias de la transcripción que respaldan
            su inclusión en el reporte.
    """

    def _extra_fields(self) -> dict:
        """
        PendingItem no añade campos particulares.
        """

        return {}