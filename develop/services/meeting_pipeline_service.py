"""
meeting_pipeline_service.py

Orquestador del Knowledge Pipeline.
"""

import json

from exceptions.insufficient_transcript_evidence_error import (
    InsufficientTranscriptEvidenceError,
)
from services.transcript_analyzer import TranscriptAnalyzer
from services.transcript_storage_service import (
    TranscriptStorageService,
)
from services.transcript_validator import TranscriptValidator


class MeetingPipelineService:
    """
    Ejecuta el Knowledge Pipeline de una reunión.

    Mantiene compatibilidad temporal con el argumento
    histórico `validator`, utilizado como SummaryValidator.
    """

    def __init__(
        self,
        summary_service,
        validator=None,
        storage_service=None,
        markdown_exporter=None,
        transcript_storage_service=None,
        transcript_analyzer=None,
        transcript_validator=None,
        summary_validator=None,
    ):
        self.summary_service = summary_service

        self.transcript_storage_service = (
            transcript_storage_service
            or TranscriptStorageService()
        )

        self.transcript_analyzer = (
            transcript_analyzer
            or TranscriptAnalyzer()
        )

        self.transcript_validator = (
            transcript_validator
            or TranscriptValidator()
        )

        # Compatibilidad temporal con:
        # validator=SummaryValidator()
        self.summary_validator = (
            summary_validator
            or validator
        )

        self.storage_service = storage_service
        self.markdown_exporter = markdown_exporter

        self._validate_dependencies()

    def process(
        self,
        recording_session,
    ):
        """
        Ejecuta el Knowledge Pipeline completo.

        Returns:
            Summary:
                Resumen validado y persistido.

        Raises:
            InsufficientTranscriptEvidenceError:
                Si el transcript no contiene evidencia
                suficiente.

            ValueError:
                Si el Summary generado no cumple las
                reglas de validación.
        """

        workspace = recording_session.workspace

        transcript = self.transcript_storage_service.load(
            workspace.transcript_json
        )

        analysis = self.transcript_analyzer.analyze(
            transcript
        )

        transcript_valid, transcript_errors = (
            self.transcript_validator.validate(
                analysis
            )
        )

        if not transcript_valid:
            raise InsufficientTranscriptEvidenceError(
                "; ".join(transcript_errors)
            )

        transcript_text = (
            self._serialize_transcript(
                transcript
            )
        )

        summary = self.summary_service.generate(
            transcript_text
        )

        summary_valid, summary_errors = (
            self.summary_validator.validate(
                summary
            )
        )

        if not summary_valid:
            raise ValueError(
                "Summary inválido: "
                + "; ".join(summary_errors)
            )

        self.storage_service.save(
            summary,
            workspace.summary_json,
        )

        self.markdown_exporter.export(
            summary,
            workspace.summary_markdown,
        )

        return summary

    @staticmethod
    def _serialize_transcript(
        transcript,
    ) -> str:
        """
        Convierte el Transcript en la representación textual
        enviada al SummaryService.

        Esta responsabilidad será extraída a un componente
        especializado en una tarea posterior.
        """

        return json.dumps(
            transcript.as_dict(),
            ensure_ascii=False,
            indent=4,
        )

    def _validate_dependencies(self) -> None:
        """
        Verifica las dependencias obligatorias del pipeline.
        """

        missing_dependencies = []

        if self.summary_service is None:
            missing_dependencies.append(
                "summary_service"
            )

        if self.summary_validator is None:
            missing_dependencies.append(
                "summary_validator"
            )

        if self.storage_service is None:
            missing_dependencies.append(
                "storage_service"
            )

        if self.markdown_exporter is None:
            missing_dependencies.append(
                "markdown_exporter"
            )

        if missing_dependencies:
            raise ValueError(
                "Faltan dependencias obligatorias en "
                "MeetingPipelineService: "
                + ", ".join(missing_dependencies)
            )