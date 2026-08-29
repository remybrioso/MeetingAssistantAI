"""
decisions_artifact.py

Artefacto estructurado derivado de MeetingReport que contiene
las decisiones identificadas en una reunión.
"""

from dataclasses import dataclass, field
from datetime import datetime

from models.artifacts.artifact import Artifact
from models.meeting_report import Decision


@dataclass
class DecisionsArtifact(Artifact):
    """
    Vista estructurada e independiente de las decisiones de un
    MeetingReport ya validado.

    No genera ni reinterpreta contenido. Conserva la procedencia
    del reporte fuente mediante metadata del modelo y timestamp.
    """

    meeting_title: str = ""
    source_report_created_at: datetime | None = None
    items: list[Decision] = field(
        default_factory=list
    )

    def __post_init__(self) -> None:
        if not isinstance(
            self.meeting_title,
            str,
        ):
            raise TypeError(
                "DecisionsArtifact meeting_title "
                "debe ser una cadena."
            )

        normalized_title = (
            self.meeting_title.strip()
        )

        if not normalized_title:
            raise ValueError(
                "DecisionsArtifact meeting_title "
                "no puede estar vacío."
            )

        self.meeting_title = (
            normalized_title
        )

        if not isinstance(
            self.source_report_created_at,
            datetime,
        ):
            raise TypeError(
                "DecisionsArtifact "
                "source_report_created_at debe ser "
                "una instancia de datetime."
            )

        if not isinstance(
            self.items,
            list,
        ):
            raise TypeError(
                "DecisionsArtifact items "
                "debe ser una lista."
            )

        normalized_items = list(
            self.items
        )

        for index, item in enumerate(
            normalized_items,
            start=1,
        ):
            if not isinstance(
                item,
                Decision,
            ):
                raise TypeError(
                    "DecisionsArtifact items "
                    f"elemento #{index} debe ser "
                    "una instancia de Decision."
                )

        self.items = normalized_items

    def as_dict(self) -> dict:
        data = super().as_dict()

        data.update(
            {
                "meeting_title": (
                    self.meeting_title
                ),
                "source_report_created_at": (
                    self.source_report_created_at
                    .isoformat()
                ),
                "items": [
                    item.as_dict()
                    for item in self.items
                ],
            }
        )

        return data
