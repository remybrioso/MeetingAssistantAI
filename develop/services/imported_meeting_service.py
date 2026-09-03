"""
imported_meeting_service.py

Caso de uso para importar y procesar
una reunión existente en formato WAV.
"""

import shutil
import time
from pathlib import Path

import soundfile as sf

from models.processing_metrics import ProcessingMetrics
from models.recording_session import RecordingSession
from services.transcript_storage_service import (
    TranscriptStorageService
)
from models.audio_source import AudioSource


class ImportedMeetingService:

    def __init__(
        self,
        workspace_service,
        transcript_service,
        transcript_storage_service,
        meeting_pipeline,
        meetings_root: Path,
        ):

        if not isinstance(
            meetings_root,
            Path,
        ):
            raise TypeError(
                "meetings_root debe ser una instancia "
                "de Path."
            )

        if not meetings_root.is_absolute():
            raise ValueError(
                "meetings_root debe ser una ruta absoluta."
            )

        self.workspace_service = workspace_service
        self.transcript_service = transcript_service
        self.transcript_storage_service = transcript_storage_service
        self.meeting_pipeline = meeting_pipeline
        self.meetings_root = meetings_root

        self.transcript_storage = (
            transcript_storage_service
        )

    def import_wav(
        self,
        source_file: Path
    ) -> RecordingSession:

        source_file = Path(source_file)

        self._validate_source(source_file)

        total_start = time.time()

        session = RecordingSession(
            base_output_dir=str(
                self.meetings_root
            ),
            session_prefix="meeting_imported"
        )

        workspace = self.workspace_service.create(
            session.session_dir
        )

        session.workspace = workspace

        shutil.copy2(
            source_file,
            workspace.meeting_audio
        )

        # TranscriptService utiliza mic_file.
        # En reuniones importadas, Reunion.wav
        # representa el audio completo.
        session.mic_file = workspace.meeting_audio
        session.meeting_file = workspace.meeting_audio

        transcription_start = time.time()

        transcript = (
            self.transcript_service
            .transcribe_sources(
                [
                    AudioSource(
                        file=workspace.meeting_audio,
                        speaker="IMPORTED",
                    )
                ]
            )
        )

        transcription_time = (
            time.time() - transcription_start
        )

        save_start = time.time()

        self.transcript_storage.save(
            transcript,
            workspace.transcript_json
        )

        save_time = time.time() - save_start

        audio_info = sf.info(
            str(workspace.meeting_audio)
        )

        words_count = sum(
            len(segment.words)
            for segment in transcript.segments
        )

        metrics = ProcessingMetrics(
            audio_duration=audio_info.duration,
            transcription_time=transcription_time,
            save_time=save_time,
            total_time=time.time() - total_start,
            segments=len(transcript.segments),
            words=words_count,
            language="es"
        )

        self.transcript_storage.save_json(
            metrics,
            workspace.processing_metrics_json
        )

        self.meeting_pipeline.process(session)

        return session

    @staticmethod
    def _validate_source(
        source_file: Path
    ) -> None:

        if not source_file.exists():
            raise FileNotFoundError(
                f"No existe el archivo: {source_file}"
            )

        if not source_file.is_file():
            raise ValueError(
                "La ruta seleccionada no es un archivo."
            )

        if source_file.suffix.lower() != ".wav":
            raise ValueError(
                "AI-011A solamente admite archivos WAV."
            )

        if source_file.stat().st_size == 0:
            raise ValueError(
                "El archivo WAV está vacío."
            )

        try:
            audio_info = sf.info(
                str(source_file)
            )

        except Exception as ex:
            raise ValueError(
                "No se pudo leer el archivo WAV."
            ) from ex

        if audio_info.duration <= 0:
            raise ValueError(
                "El archivo WAV no contiene audio válido."
            )
