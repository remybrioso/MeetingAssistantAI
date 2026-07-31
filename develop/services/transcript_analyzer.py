"""
transcript_analyzer.py

Analiza un Transcript y produce un TranscriptAnalysis.
"""

from models.transcript import Transcript
from models.transcript_analysis import TranscriptAnalysis


class TranscriptAnalyzer:

    def analyze(
        self,
        transcript: Transcript,
    ) -> TranscriptAnalysis:

        total_segments = len(
            transcript.segments
        )

        total_words = 0
        total_characters = 0
        empty_segments = 0

        speakers = set()

        max_end = 0.0

        for segment in transcript.segments:

            speakers.add(
                segment.speaker
            )

            text = segment.text.strip()

            if not text:
                empty_segments += 1
            else:
                total_words += len(
                    text.split()
                )

                total_characters += len(
                    text
                )

            if segment.end > max_end:
                max_end = segment.end

        return TranscriptAnalysis(
            total_segments=total_segments,
            total_words=total_words,
            total_characters=total_characters,
            total_duration=max_end,
            unique_speakers=len(speakers),
            empty_segments=empty_segments,
        )