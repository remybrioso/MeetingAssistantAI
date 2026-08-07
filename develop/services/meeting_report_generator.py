"""
meeting_report_generator.py

Generador de MeetingReport a partir de un Transcript.
"""

from models.artifacts.meeting_report import MeetingReport
from models.transcript import Transcript
from services.artifact_generator import ArtifactGenerator
from services.meeting_report_service import (
    MeetingReportService,
)
from services.transcript_prompt_formatter import (
    TranscriptPromptFormatter,
)
from services.validators.meeting_report_validator import (
    MeetingReportValidator,
)


class MeetingReportGenerator(
    ArtifactGenerator
):
    """
    Orquesta la generación completa de un MeetingReport.

    Responsabilidades:

    - recibir un Transcript;
    - construir el Prompt usando meeting_report_v1;
    - generar el MeetingReport;
    - validar su calidad semántica;
    - devolver únicamente un artefacto válido.

    No realiza persistencia ni exportación.
    """

    CONTRACT = "meeting_report_v1"

    def __init__(
        self,
        prompt_formatter=None,
        meeting_report_service=None,
        validator=None,
    ) -> None:
        self.prompt_formatter = (
            prompt_formatter
            if prompt_formatter is not None
            else TranscriptPromptFormatter(
                contract=self.CONTRACT
            )
        )

        self.meeting_report_service = (
            meeting_report_service
            if meeting_report_service is not None
            else MeetingReportService()
        )

        self.validator = (
            validator
            if validator is not None
            else MeetingReportValidator()
        )

    def generate(
        self,
        transcript: Transcript,
    ) -> MeetingReport:
        """
        Genera y valida un MeetingReport.

        Raises:
            TypeError:
                Si transcript no es una instancia de
                Transcript.

            ValueError:
                Si el MeetingReport generado no supera la
                validación semántica.

            También propaga errores del formatter, proveedor,
            schema loader y parser.
        """

        if not isinstance(
            transcript,
            Transcript,
        ):
            raise TypeError(
                "transcript debe ser una instancia "
                "de Transcript."
            )

        prompt = self.prompt_formatter.format(
            transcript
        )

        report = (
            self.meeting_report_service.generate(
                prompt
            )
        )

        valid, errors = self.validator.validate(
            report
        )

        if not valid:
            raise ValueError(
                "MeetingReport inválido: "
                + "; ".join(
                    errors
                )
            )

        return report