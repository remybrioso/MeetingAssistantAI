"""
meeting_finalization_service.py

Caso de uso:
Finalizar una reunión.
"""

import time

import soundfile as sf

from models.audio_source import AudioSource
from models.processing_metrics import ProcessingMetrics

class MeetingFinalizationService:

    def __init__(
        self,
        transcript_service,
        transcript_storage_service,
        workspace_service,
        meeting_pipeline,
        bus=None,
    ):
        """
        Inicializa el servicio con todas sus dependencias.

        La composición de objetos pertenece exclusivamente
        al DependencyContainer.
        """

        self.bus = bus
        self.transcript_service = transcript_service
        self.storage_service = transcript_storage_service
        self.workspace_service = workspace_service
        self.meeting_pipeline = meeting_pipeline

        self._validate_dependencies()

    def _validate_dependencies(self) -> None:
        """
        Verifica que las dependencias obligatorias existan.
        """

        dependencies = {
                "transcript_service": self.transcript_service,
                "transcript_storage_service": self.storage_service,
                "workspace_service": self.workspace_service,
                "meeting_pipeline": self.meeting_pipeline,
            }

        missing = [
                name
                for name, service in dependencies.items()
                if service is None
            ]

        if missing:
                raise ValueError(
                    "Faltan dependencias obligatorias en "
                    "MeetingFinalizationService: "
                    + ", ".join(missing)
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

            audio_sources = self._build_audio_sources(
                recording_session
            )

            if not audio_sources:
                raise FileNotFoundError(
                    "No audio sources were found "
                    "for transcription."
                )

            transcript = (
                self.transcript_service
                .transcribe_sources(
                    audio_sources
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

            audio_duration = self._get_meeting_duration(
                recording_session,
                audio_sources
            )

            words_count = sum(
                len(segment.words)
                for segment in transcript.segments
            )

            metrics = ProcessingMetrics(
                audio_duration=audio_duration,
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

    @staticmethod
    def _build_audio_sources(
        recording_session,
    ) -> list[AudioSource]:
        """
        Construye las fuentes disponibles para transcripción.

        Una pista ausente no impide procesar las demás.
        """

        configured_sources = (
            (
                recording_session.mic_file,
                "LOCAL",
            ),
            (
                recording_session.system_file,
                "REMOTE",
            ),
        )

        return [
            AudioSource(
                file=audio_file,
                speaker=speaker,
            )
            for audio_file, speaker in configured_sources
            if audio_file is not None
            and audio_file.is_file()
        ]

    @staticmethod
    def _get_meeting_duration(
        recording_session,
        audio_sources: list[AudioSource],
    ) -> float:
        """
        Obtiene la duración completa de la reunión.

        Utiliza meeting.wav cuando está disponible. Como
        respaldo, toma la mayor duración entre las pistas
        individuales, ya que fueron grabadas simultáneamente.
        """

        meeting_file = recording_session.meeting_file

        if (
            meeting_file is not None
            and meeting_file.is_file()
        ):
            return sf.info(
                str(meeting_file)
            ).duration

        return max(
            sf.info(
                str(source.file)
            ).duration
            for source in audio_sources
        )
