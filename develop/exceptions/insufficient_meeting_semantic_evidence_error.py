"""
insufficient_meeting_semantic_evidence_error.py

Resultado esperado cuando la extracción válida no encuentra
semántica suficiente de reunión.
"""

from exceptions.insufficient_meeting_evidence_error import (
    InsufficientMeetingEvidenceError,
)


class InsufficientMeetingSemanticEvidenceError(
    InsufficientMeetingEvidenceError
):
    """
    Indica que una transcripción estructuralmente válida produjo
    MeetingKnowledge sin contenido semántico de reunión.
    """

    def __init__(
        self,
        source_chunk_count: int,
        content_chunk_count: int,
    ) -> None:
        self.source_chunk_count = self._validate_count(
            value=source_chunk_count,
            field_name="source_chunk_count",
            minimum=1,
        )
        self.content_chunk_count = self._validate_count(
            value=content_chunk_count,
            field_name="content_chunk_count",
            minimum=0,
        )

        if self.content_chunk_count != 0:
            raise ValueError(
                "content_chunk_count debe ser cero para un "
                "resultado de evidencia semántica insuficiente."
            )

        super().__init__(
            "MeetingKnowledge no contiene conocimiento suficiente "
            "para generar un MeetingReport. "
            f"source_chunk_count={self.source_chunk_count}; "
            f"content_chunk_count={self.content_chunk_count}."
        )

    @staticmethod
    def _validate_count(
        value,
        field_name: str,
        minimum: int,
    ) -> int:
        if (
            not isinstance(
                value,
                int,
            )
            or isinstance(
                value,
                bool,
            )
        ):
            raise TypeError(
                f"{field_name} debe ser entero."
            )

        if value < minimum:
            raise ValueError(
                f"{field_name} debe ser mayor o igual que "
                f"{minimum}."
            )

        return value
