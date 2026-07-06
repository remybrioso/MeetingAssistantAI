"""
transcript_service.py

Servicio que orquesta la transcripción de una sesión.
"""

from builders.transcript_builder import TranscriptBuilder
from providers.whisper.whisper_provider import WhisperProvider


class TranscriptService:

    def __init__(self):

        self.provider = WhisperProvider()
        self.builder = TranscriptBuilder()

    def transcribe_microphone(self, recording_session):

        whisper_result = self.provider.transcribe(
            str(recording_session.mic_file)
        )

        raw_segments = []

        for segment in whisper_result.segments:

            raw_segments.append(
                {
                    "start": segment.start,
                    "end": segment.end,
                    "speaker": "LOCAL",
                    "text": segment.text,
                    "words": [
                        {
                            "start": word.start,
                            "end": word.end,
                            "text": word.text,
                            "confidence": word.probability,
                        }
                        for word in segment.words
                    ],
                }
            )

        return self.builder.from_segments(raw_segments)