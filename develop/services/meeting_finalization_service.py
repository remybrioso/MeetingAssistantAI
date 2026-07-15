"""
meeting_finalization_service.py

Caso de uso:
Finalizar una reunión.
"""

import time

import soundfile as sf

from models.processing_metrics import ProcessingMetrics
from services.artifact_storage_service import ArtifactStorageService
from services.meeting_pipeline_service import MeetingPipelineService
from services.summary_markdown_exporter import SummaryMarkdownExporter
from services.summary_service import SummaryService
from services.transcript_service import TranscriptService
from services.transcript_storage_service import TranscriptStorageService
from services.validators.summary_validator import SummaryValidator
from services.workspace_service import WorkspaceService


class MeetingFinalizationService:

    def __init__(self, bus=None):

        self.bus = bus

        self.transcript_service = TranscriptService()
        self.storage_service = TranscriptStorageService()
        self.workspace_service = WorkspaceService()

        self.meeting_pipeline = MeetingPipelineService(
            summary_service=SummaryService(),
            validator=SummaryValidator(),
            storage_service=ArtifactStorageService(),
            markdown_exporter=SummaryMarkdownExporter()
        )

    def finalize(self, recording_session):

        try:
            start_time = time.time()

            if self.bus:
                self.bus.emit(
                    "meeting_processing_started"
                )

            workspace = recording_session.workspace

            # Compatibilidad con sesiones antiguas o pruebas
            # que todavía no tengan Workspace asociado.
            if workspace is None:

                workspace = self.workspace_service.create(
                    recording_session.session_dir
                )

                recording_session.attach_workspace(
                    workspace
                )

            if self.bus:
                self.bus.emit(
                    "meeting_transcribing"
                )

            transcription_start = time.time()

            transcript = (
                self.transcript_service
                .transcribe_microphone(
                    recording_session
                )
            )

            transcription_time = (
                time.time() - transcription_start
            )

            if self.bus:
                self.bus.emit(
                    "meeting_saving"
                )

            save_start = time.time()

            self.storage_service.save(
                transcript,
                workspace.transcript_json
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

            self.storage_service.save_json(
                metrics,
                workspace.processing_metrics_json
            )

            self.meeting_pipeline.process(
                recording_session
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