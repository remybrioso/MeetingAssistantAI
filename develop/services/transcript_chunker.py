"""
transcript_chunker.py

Divide un Transcript en bloques contiguos y trazables.
"""

from models.transcript import Transcript
from models.transcript_chunk import TranscriptChunk


class TranscriptChunker:
    """
    Segmenta reuniones largas sin cortar Segment.

    Usa cantidad de palabras como límite principal. No aplica
    solapamiento: cada Segment aparece exactamente una vez.
    """

    DEFAULT_MAX_WORDS = 1200

    def __init__(self, max_words: int = DEFAULT_MAX_WORDS) -> None:
        if not isinstance(max_words, int):
            raise TypeError("max_words debe ser entero.")
        if max_words <= 0:
            raise ValueError("max_words debe ser mayor que cero.")
        self.max_words = max_words

    def chunk(self, transcript: Transcript) -> list[TranscriptChunk]:
        """
        Divide un Transcript preservando orden y segmentos completos.

        Si un Segment individual excede max_words, se conserva
        completo dentro de un chunk propio.
        """

        if not isinstance(transcript, Transcript):
            raise TypeError(
                "transcript debe ser una instancia de Transcript."
            )

        if not transcript.segments:
            return []

        chunks: list[TranscriptChunk] = []
        current_segments = []
        current_words = 0

        for segment in transcript.segments:
            segment_words = len(segment.text.split())

            if (
                current_segments
                and current_words + segment_words > self.max_words
            ):
                chunks.append(
                    TranscriptChunk(
                        index=len(chunks),
                        segments=current_segments,
                    )
                )
                current_segments = []
                current_words = 0

            current_segments.append(segment)
            current_words += segment_words

        if current_segments:
            chunks.append(
                TranscriptChunk(
                    index=len(chunks),
                    segments=current_segments,
                )
            )

        return chunks
