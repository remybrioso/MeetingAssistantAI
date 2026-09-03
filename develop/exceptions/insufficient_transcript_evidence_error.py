"""
insufficient_transcript_evidence_error.py

Excepción de dominio lanzada cuando una transcripción
no contiene evidencia suficiente para generar una minuta.
"""

from exceptions.insufficient_meeting_evidence_error import (
    InsufficientMeetingEvidenceError,
)


class InsufficientTranscriptEvidenceError(
    InsufficientMeetingEvidenceError
):
    """
    Indica que la transcripción no contiene evidencia
    suficiente para continuar el Knowledge Pipeline.
    """
