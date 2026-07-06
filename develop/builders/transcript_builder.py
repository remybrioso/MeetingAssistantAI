"""
transcript_builder.py

Convierte datos externos en modelos Transcript.
"""

from models.transcript import Transcript, Segment, Word


class TranscriptBuilder:

    def from_segments(self, raw_segments: list[dict]) -> Transcript:

        transcript = Transcript()

        for item in raw_segments:

            words = [
                Word(
                    start=word["start"],
                    end=word["end"],
                    text=word["text"],
                    confidence=word.get("confidence")
                )
                for word in item.get("words", [])
            ]

            segment = Segment(
                start=item["start"],
                end=item["end"],
                speaker=item.get("speaker", "UNKNOWN"),
                text=item["text"],
                words=words
            )

            transcript.add_segment(segment)

        return transcript