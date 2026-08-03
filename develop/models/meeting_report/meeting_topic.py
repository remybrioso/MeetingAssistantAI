"""
meeting_topic.py

Tema relevante tratado durante una reunión.
"""

from dataclasses import dataclass, field

from models.meeting_report.evidence_reference import (
    EvidenceReference,
)


@dataclass(
    frozen=True,
    slots=True,
)
class MeetingTopic:
    """
    Representa un tema relevante tratado en la reunión.

    La ausencia de evidencia enlazada es válida durante
    la primera versión del MeetingReport.
    """

    title: str
    summary: str
    evidence: list[EvidenceReference] = field(
        default_factory=list
    )

    def __post_init__(self) -> None:
        normalized_title = self.title.strip()
        normalized_summary = self.summary.strip()

        if not normalized_title:
            raise ValueError(
                "MeetingTopic title no puede estar vacío."
            )

        if not normalized_summary:
            raise ValueError(
                "MeetingTopic summary no puede estar vacío."
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
                    "MeetingTopic evidence solo admite "
                    "instancias de EvidenceReference."
                )

        object.__setattr__(
            self,
            "title",
            normalized_title,
        )

        object.__setattr__(
            self,
            "summary",
            normalized_summary,
        )

        object.__setattr__(
            self,
            "evidence",
            normalized_evidence,
        )

    def as_dict(self) -> dict:
        """
        Devuelve una representación serializable.
        """

        return {
            "title": self.title,
            "summary": self.summary,
            "evidence": [
                reference.as_dict()
                for reference in self.evidence
            ],
        }