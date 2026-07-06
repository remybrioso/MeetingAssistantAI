"""
transcript.py

Modelo de dominio para representar una transcripción.
"""

from dataclasses import dataclass, field


@dataclass
class Word:

    start: float
    end: float
    text: str
    confidence: float | None = None

    def as_dict(self):

        return {
            "start": self.start,
            "end": self.end,
            "text": self.text,
            "confidence": self.confidence,
        }


@dataclass
class Segment:

    start: float
    end: float
    speaker: str
    text: str
    words: list[Word] = field(default_factory=list)

    def as_dict(self):

        return {
            "start": self.start,
            "end": self.end,
            "speaker": self.speaker,
            "text": self.text,
            "words": [
                word.as_dict()
                for word in self.words
            ],
        }


@dataclass
class Transcript:

    segments: list[Segment] = field(default_factory=list)

    def add_segment(self, segment: Segment):

        self.segments.append(segment)

    def as_dict(self):

        return {
            "segments": [
                segment.as_dict()
                for segment in self.segments
            ]
        }