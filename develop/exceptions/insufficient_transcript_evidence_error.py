"""
insufficient_transcript_evidence_error.py

Excepción de dominio lanzada cuando una transcripción
no contiene evidencia suficiente para generar una minuta.
"""


class InsufficientTranscriptEvidenceError(Exception):
    """
    Indica que la transcripción no contiene evidencia
    suficiente para continuar el Knowledge Pipeline.
    """