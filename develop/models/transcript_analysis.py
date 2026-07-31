"""
transcript_analysis.py

Resultado del análisis de un Transcript.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TranscriptAnalysis:
    """
    Contiene métricas derivadas de un Transcript.

    No realiza cálculos.
    No toma decisiones.
    Solo representa el resultado del análisis.
    """

    total_segments: int
    total_words: int
    total_characters: int
    total_duration: float

    unique_speakers: int
    empty_segments: int