"""
transcript.py

Modelo de dominio para representar una transcripción.
"""

from dataclasses import dataclass, field


@dataclass
class Segment:

    start: float
    end: float
    speaker: str
    text: str

    def as_dict(self):

        return {
            "start": self.start,
            "end": self.end,
            "speaker": self.speaker,
            "text": self.text,
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