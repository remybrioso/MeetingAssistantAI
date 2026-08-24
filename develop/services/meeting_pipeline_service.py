"""
meeting_pipeline_service.py

Orquestador principal del Knowledge Pipeline.
"""

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

    El pipeline coordina:

    - carga del Transcript;
    - análisis de evidencia;
    - validación del Transcript;
    - generación del artefacto principal;
    - persistencia estructurada;
    - exportación documental.

    La lógica propia del artefacto pertenece al
    ArtifactGenerator recibido.
    """

    def __init__(
        self,
        artifact_generator,
        storage_service,
        markdown_exporter,
        transcript_storage_service=None,
        transcript_analyzer=None,
        transcript_validator=None,
    ) -> None:
        self.artifact_generator = artifact_generator

        self.storage_service = storage_service

        self.markdown_exporter = markdown_exporter

        self.transcript_storage_service = (
            transcript_storage_service
            if transcript_storage_service is not None
            else TranscriptStorageService()
        )

        self.transcript_analyzer = (
            transcript_analyzer
            if transcript_analyzer is not None
            else TranscriptAnalyzer()
        )

        self.transcript_validator = (
            transcript_validator
            if transcript_validator is not None
            else TranscriptValidator()
        )

        self._validate_dependencies()

    def process(
        self,
        recording_session,
    ):
        """
        Ejecuta el Knowledge Pipeline completo.

        Returns:
            Artefacto de dominio generado, validado,
            persistido y exportado.

        Raises:
            InsufficientTranscriptEvidenceError:
                Si el Transcript no contiene evidencia
                suficiente para continuar.

            También propaga cualquier error producido por
            ArtifactGenerator, almacenamiento o exportación.
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
                "; ".join(
                    transcript_errors
                )
            )

        artifact = self.artifact_generator.generate(
            transcript
        )

        self.storage_service.save(
            artifact,
            workspace.meeting_report_json,
        )

        self.markdown_exporter.export(
            artifact,
            workspace.meeting_report_markdown,
        )

        return artifact

    def _validate_dependencies(
        self,
    ) -> None:
        """
        Verifica las dependencias obligatorias del pipeline.
        """

        missing_dependencies = []

        if self.artifact_generator is None:
            missing_dependencies.append(
                "artifact_generator"
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
                + ", ".join(
                    missing_dependencies
                )
            )