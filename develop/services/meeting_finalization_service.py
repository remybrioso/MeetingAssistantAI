"""
meeting_finalization_service.py

Caso de uso:
Finalizar una reunión.
"""

from services.transcript_service import TranscriptService
from services.transcript_storage_service import TranscriptStorageService


class MeetingFinalizationService:

    def __init__(self, bus=None):

        self.bus = bus

        self.transcript_service = TranscriptService()

        self.storage_service = TranscriptStorageService()

    def finalize(self, recording_session):

        transcript = self.transcript_service.transcribe_microphone(
            recording_session
        )

        output_file = (
            recording_session.session_dir /
            "transcript.json"
        )

        self.storage_service.save(
            transcript,
            output_file
        )

        if self.bus:

            self.bus.emit(
                "meeting_processing_completed",
                recording_session
            )

        return transcript