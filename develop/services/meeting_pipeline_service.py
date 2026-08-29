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
    - generación del MeetingReport;
    - entrega de todos los artefactos derivados.

    La generación pertenece al ArtifactGenerator recibido.
    La persistencia y exportación pertenecen al servicio
    especializado de entrega.
    """

    def __init__(
        self,
        artifact_generator,
        artifact_delivery_service,
        transcript_storage_service=None,
        transcript_analyzer=None,
        transcript_validator=None,
    ) -> None:
        self.artifact_generator = artifact_generator

        self.artifact_delivery_service = (
            artifact_delivery_service
        )

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
            MeetingReport generado, validado y entregado.

        Raises:
            InsufficientTranscriptEvidenceError:
                Si el Transcript no contiene evidencia
                suficiente para continuar.

            También propaga cualquier error producido por
            generación o entrega de artefactos.
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

        self.artifact_delivery_service.deliver(
            report=artifact,
            workspace=workspace,
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

        if self.artifact_delivery_service is None:
            missing_dependencies.append(
                "artifact_delivery_service"
            )

        if missing_dependencies:
            raise ValueError(
                "Faltan dependencias obligatorias en "
                "MeetingPipelineService: "
                + ", ".join(
                    missing_dependencies
                )
            )
