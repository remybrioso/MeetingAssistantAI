"""
transcript_chunk.py

Modelo de dominio para representar un bloque contiguo de
una transcripción.
"""

from dataclasses import dataclass, field

from models.transcript import Segment


@dataclass
class TranscriptChunk:
    """Bloque ordenado y trazable de segmentos completos."""

    index: int
    segments: list[Segment] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.index, int):
            raise TypeError("TranscriptChunk index debe ser entero.")
        if self.index < 0:
            raise ValueError("TranscriptChunk index no puede ser negativo.")
        if not isinstance(self.segments, list):
            raise TypeError("TranscriptChunk segments debe ser una lista.")
        if not self.segments:
            raise ValueError(
                "TranscriptChunk debe contener al menos un segmento."
            )
        if not all(isinstance(segment, Segment) for segment in self.segments):
            raise TypeError(
                "TranscriptChunk solo puede contener instancias de Segment."
            )

    @property
    def start(self) -> float:
        return self.segments[0].start

    @property
    def end(self) -> float:
        return self.segments[-1].end

    @property
    def duration(self) -> float:
        return max(0.0, self.end - self.start)

    @property
    def word_count(self) -> int:
        return sum(
            len(segment.text.split())
            for segment in self.segments
            if segment.text.strip()
        )

    @property
    def character_count(self) -> int:
        return sum(len(segment.text) for segment in self.segments)

    def as_dict(self) -> dict:
        return {
            "index": self.index,
            "start": self.start,
            "end": self.end,
            "segments": [
                segment.as_dict()
                for segment in self.segments
            ],
        }
