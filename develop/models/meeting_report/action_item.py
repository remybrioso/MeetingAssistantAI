"""
action_item.py

Acción o compromiso identificado durante una reunión.
"""

from dataclasses import dataclass
from datetime import date

from models.meeting_report.evidence_backed_item import (
    EvidenceBackedItem,
)
from models.meeting_report.value_objects.action_owner import (
    ActionOwner,
)
from models.meeting_report.value_objects.action_status import (
    ActionStatus,
)


@dataclass(
    frozen=True,
    slots=True,
)
class ActionItem(
    EvidenceBackedItem
):
    """
    Representa una acción concreta identificada durante
    una reunión.

    Attributes:
        description:
            Trabajo o compromiso que debe realizarse.

        evidence:
            Referencias que respaldan la acción.

        owner:
            Persona, equipo o área responsable.
            Será None cuando no exista evidencia suficiente.

        due_date:
            Fecha límite normalizada.
            Será None cuando no exista una fecha explícita
            y verificable.

        status:
            Estado controlado de la acción.
    """

    owner: ActionOwner | str | None = None
    due_date: date | None = None
    status: ActionStatus | str = ActionStatus.UNKNOWN

    def __post_init__(self) -> None:
        super().__post_init__()

        normalized_owner = self._normalize_owner(
            self.owner
        )

        normalized_due_date = self._normalize_due_date(
            self.due_date
        )

        normalized_status = ActionStatus.from_value(
            self.status
        )

        object.__setattr__(
            self,
            "owner",
            normalized_owner,
        )

        object.__setattr__(
            self,
            "due_date",
            normalized_due_date,
        )

        object.__setattr__(
            self,
            "status",
            normalized_status,
        )

    @staticmethod
    def _normalize_owner(
        owner: ActionOwner | str | None,
    ) -> ActionOwner | None:
        """
        Convierte un responsable textual en ActionOwner.
        """

        if owner is None:
            return None

        return ActionOwner.from_value(
            owner
        )

    @staticmethod
    def _normalize_due_date(
        due_date: date | None,
    ) -> date | None:
        """
        Verifica que la fecha límite sea date o None.

        No se aceptan cadenas ambiguas dentro del dominio.
        El parser futuro será responsable de normalizar
        fechas explícitas antes de crear ActionItem.
        """

        if due_date is None:
            return None

        if not isinstance(
            due_date,
            date,
        ):
            raise TypeError(
                "ActionItem due_date debe ser una fecha "
                "o None."
            )

        return due_date

    def _extra_fields(self) -> dict:
        """
        Devuelve los campos particulares de ActionItem.
        """

        return {
            "owner": (
                self.owner.as_dict()
                if self.owner is not None
                else None
            ),
            "due_date": (
                self.due_date.isoformat()
                if self.due_date is not None
                else None
            ),
            "status": self.status.value,
        }