"""
insufficient_meeting_evidence_error.py

Excepción base para resultados esperados de evidencia insuficiente.
"""


class InsufficientMeetingEvidenceError(Exception):
    """
    Marca un resultado de dominio esperado en el que no puede
    producirse un reporte por falta de evidencia suficiente.

    Los subtipos conservan los detalles técnicos del motivo. La
    presentación de mensajes al usuario pertenece a la capa GUI.
    """
