"""
whisper_models.py

Modelos internos del proveedor Whisper.
"""

from dataclasses import dataclass, field


@dataclass
class WhisperWord:

    start: float
    end: float
    text: str
    probability: float | None = None

    def as_dict(self):

        return {
            "start": self.start,
            "end": self.end,
            "text": self.text,
            "probability": self.probability,
        }


@dataclass
class WhisperSegment:

    start: float
    end: float
    text: str
    words: list[WhisperWord] = field(default_factory=list)

    def as_dict(self):

        return {
            "start": self.start,
            "end": self.end,
            "text": self.text,
            "words": [
                word.as_dict()
                for word in self.words
            ],
        }


@dataclass
class WhisperResult:

    language: str
    segments: list[WhisperSegment] = field(default_factory=list)

    def as_dict(self):

        return {
            "language": self.language,
            "segments": [
                segment.as_dict()
                for segment in self.segments
            ],
        }