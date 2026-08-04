"""
meeting_report.py

Artefacto maestro que representa la minuta estructurada
de una reunión.
"""

from dataclasses import dataclass, field
from typing import TypeVar

from models.artifacts.artifact import Artifact
from models.meeting_report import (
    ActionItem,
    Decision,
    MeetingRisk,
    MeetingTopic,
    Participant,
    PendingItem,
)


ItemType = TypeVar("ItemType")


@dataclass
class MeetingReport(Artifact):
    """
    Representa una minuta profesional estructurada.

    MeetingReport conserva únicamente objetos del dominio.
    La conversión desde diccionarios pertenece al parser.

    Attributes:
        title:
            Título identificativo de la reunión.

        objective:
            Objetivo expresado o claramente respaldado
            por la transcripción.

        executive_summary:
            Resumen ejecutivo de la reunión.

        key_points:
            Puntos principales respaldados por el contenido.

        topics:
            Temas relevantes tratados.

        decisions:
            Decisiones explícitas.

        action_items:
            Acciones o compromisos identificados.

        risks:
            Riesgos o bloqueos mencionados.

        pending_items:
            Asuntos que quedaron abiertos.

        participants:
            Participantes identificados o mencionados.

        conclusions:
            Conclusiones expresadas durante la reunión.
    """

    title: str = ""
    objective: str | None = None
    executive_summary: str = ""

    key_points: list[str] = field(
        default_factory=list
    )

    topics: list[MeetingTopic] = field(
        default_factory=list
    )

    decisions: list[Decision] = field(
        default_factory=list
    )

    action_items: list[ActionItem] = field(
        default_factory=list
    )

    risks: list[MeetingRisk] = field(
        default_factory=list
    )

    pending_items: list[PendingItem] = field(
        default_factory=list
    )

    participants: list[Participant] = field(
        default_factory=list
    )

    conclusions: list[str] = field(
        default_factory=list
    )

    def __post_init__(self) -> None:
        """
        Normaliza y valida el contenido del reporte.
        """

        self.title = self._normalize_required_text(
            value=self.title,
            field_name="title",
        )

        self.objective = self._normalize_optional_text(
            self.objective
        )

        self.executive_summary = (
            self._normalize_required_text(
                value=self.executive_summary,
                field_name="executive_summary",
            )
        )

        self.key_points = self._normalize_text_collection(
            values=self.key_points,
            field_name="key_points",
            require_items=True,
        )

        self.conclusions = (
            self._normalize_text_collection(
                values=self.conclusions,
                field_name="conclusions",
                require_items=False,
            )
        )

        self.topics = self._validate_collection(
            values=self.topics,
            expected_type=MeetingTopic,
            field_name="topics",
        )

        self.decisions = self._validate_collection(
            values=self.decisions,
            expected_type=Decision,
            field_name="decisions",
        )

        self.action_items = self._validate_collection(
            values=self.action_items,
            expected_type=ActionItem,
            field_name="action_items",
        )

        self.risks = self._validate_collection(
            values=self.risks,
            expected_type=MeetingRisk,
            field_name="risks",
        )

        self.pending_items = self._validate_collection(
            values=self.pending_items,
            expected_type=PendingItem,
            field_name="pending_items",
        )

        self.participants = self._validate_collection(
            values=self.participants,
            expected_type=Participant,
            field_name="participants",
        )

    @staticmethod
    def _normalize_required_text(
        value: str,
        field_name: str,
    ) -> str:
        """
        Normaliza una cadena obligatoria.
        """

        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                f"MeetingReport {field_name} "
                "debe ser una cadena."
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"MeetingReport {field_name} "
                "no puede estar vacío."
            )

        return normalized

    @staticmethod
    def _normalize_optional_text(
        value: str | None,
    ) -> str | None:
        """
        Normaliza una cadena opcional.

        Las cadenas vacías se convierten en None.
        """

        if value is None:
            return None

        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                "MeetingReport objective debe ser "
                "una cadena o None."
            )

        normalized = value.strip()

        return normalized or None

    @staticmethod
    def _normalize_text_collection(
        values: list[str],
        field_name: str,
        require_items: bool,
    ) -> list[str]:
        """
        Normaliza una colección de cadenas.

        Se crea una copia defensiva y se rechazan elementos
        que no sean cadenas o estén vacíos.
        """

        if not isinstance(
            values,
            list,
        ):
            raise TypeError(
                f"MeetingReport {field_name} "
                "debe ser una lista."
            )

        normalized_values: list[str] = []

        for index, value in enumerate(
            values,
            start=1,
        ):
            if not isinstance(
                value,
                str,
            ):
                raise TypeError(
                    f"MeetingReport {field_name} "
                    f"elemento #{index} debe ser "
                    "una cadena."
                )

            normalized = value.strip()

            if not normalized:
                raise ValueError(
                    f"MeetingReport {field_name} "
                    f"elemento #{index} no puede "
                    "estar vacío."
                )

            normalized_values.append(
                normalized
            )

        if (
            require_items
            and not normalized_values
        ):
            raise ValueError(
                f"MeetingReport {field_name} "
                "debe contener al menos un elemento."
            )

        return normalized_values

    @staticmethod
    def _validate_collection(
        values: list[ItemType],
        expected_type: type[ItemType],
        field_name: str,
    ) -> list[ItemType]:
        """
        Valida y copia una colección de objetos del dominio.
        """

        if not isinstance(
            values,
            list,
        ):
            raise TypeError(
                f"MeetingReport {field_name} "
                "debe ser una lista."
            )

        normalized_values = list(
            values
        )

        for index, value in enumerate(
            normalized_values,
            start=1,
        ):
            if not isinstance(
                value,
                expected_type,
            ):
                raise TypeError(
                    f"MeetingReport {field_name} "
                    f"elemento #{index} debe ser "
                    f"una instancia de "
                    f"{expected_type.__name__}."
                )

        return normalized_values

    def as_dict(self) -> dict:
        """
        Devuelve la representación completa y serializable.
        """

        data = super().as_dict()

        data.update(
            {
                "title": self.title,
                "objective": self.objective,
                "executive_summary": (
                    self.executive_summary
                ),
                "key_points": list(
                    self.key_points
                ),
                "topics": [
                    topic.as_dict()
                    for topic in self.topics
                ],
                "decisions": [
                    decision.as_dict()
                    for decision in self.decisions
                ],
                "action_items": [
                    action_item.as_dict()
                    for action_item
                    in self.action_items
                ],
                "risks": [
                    risk.as_dict()
                    for risk in self.risks
                ],
                "pending_items": [
                    pending_item.as_dict()
                    for pending_item
                    in self.pending_items
                ],
                "participants": [
                    participant.as_dict()
                    for participant
                    in self.participants
                ],
                "conclusions": list(
                    self.conclusions
                ),
            }
        )

        return data