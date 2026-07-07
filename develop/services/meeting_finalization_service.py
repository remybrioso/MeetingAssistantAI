"""
meeting_finalization_service.py

Caso de uso:
Finalizar una reunión.
"""
import time
import soundfile as sf

from models.processing_metrics import ProcessingMetrics
from services.transcript_service import TranscriptService
from services.transcript_storage_service import TranscriptStorageService


class MeetingFinalizationService:

    def __init__(self, bus=None):

        self.bus = bus

        self.transcript_service = TranscriptService()

        self.storage_service = TranscriptStorageService()

    def finalize(self, recording_session):

        try:
            start_time = time.time()
            if self.bus:
                self.bus.emit("meeting_processing_started")

            if self.bus:
                self.bus.emit("meeting_transcribing")

            transcription_start = time.time()

            transcript = self.transcript_service.transcribe_microphone(
                recording_session
            )

            transcription_time = time.time() - transcription_start

            if self.bus:
                self.bus.emit("meeting_saving")

            output_file = (
                recording_session.session_dir /
                "transcript.json"
            )

            save_start = time.time()

            self.storage_service.save(
                transcript,
                output_file
            )

            save_time = time.time() - save_start

            audio_info = sf.info(
                str(recording_session.mic_file)
            )

            words_count = sum(
                len(segment.words)
                for segment in transcript.segments
            )

            metrics = ProcessingMetrics(
                audio_duration=audio_info.duration,
                transcription_time=transcription_time,
                save_time=save_time,
                total_time=time.time() - start_time,
                segments=len(transcript.segments),
                words=words_count,
                language="es"
            )

            metrics_file = (
                recording_session.session_dir /
                "processing_metrics.json"
            )

            self.storage_service.save_json(
                metrics,
                metrics_file
            )

            if self.bus:
                self.bus.emit(
                    "meeting_processing_completed",
                    recording_session
                )

            return transcript

        except Exception as ex:

            if self.bus:
                self.bus.emit(
                    "meeting_processing_failed",
                    str(ex)
                )

            raise