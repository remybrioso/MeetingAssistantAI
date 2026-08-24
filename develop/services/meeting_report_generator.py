"""
meeting_report_generator.py

Generador de MeetingReport a partir de un Transcript.
"""

from models.artifacts.meeting_report import MeetingReport
from models.prompt import Prompt
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
    - realizar un segundo intento correctivo si el primero
      falla por contenido inválido;
    - validar su calidad semántica;
    - devolver únicamente un artefacto válido.

    No realiza persistencia ni exportación.
    """

    CONTRACT = "meeting_report_v1"
    MAX_GENERATION_ATTEMPTS = 2

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

        El primer intento utiliza el Prompt original.

        Si el contenido producido no puede convertirse en
        MeetingReport o no supera la validación semántica,
        el segundo intento añade instrucciones correctivas
        concretas al mismo Prompt.

        Los errores de infraestructura del proveedor no se
        capturan aquí y continúan propagándose.

        Raises:
            TypeError:
                Si transcript no es una instancia de
                Transcript.

            ValueError:
                Si ambos intentos producen contenido
                inválido.
        """

        if not isinstance(
            transcript,
            Transcript,
        ):
            raise TypeError(
                "transcript debe ser una instancia "
                "de Transcript."
            )

        base_prompt = self.prompt_formatter.format(
            transcript
        )

        current_prompt = base_prompt
        last_errors: list[str] = []

        for attempt in range(
            1,
            self.MAX_GENERATION_ATTEMPTS + 1,
        ):
            try:
                report = (
                    self.meeting_report_service.generate(
                        current_prompt
                    )
                )
            except ValueError as ex:
                last_errors = [
                    str(ex)
                ]

                if (
                    attempt
                    < self.MAX_GENERATION_ATTEMPTS
                ):
                    current_prompt = (
                        self._build_corrective_prompt(
                            base_prompt=base_prompt,
                            errors=last_errors,
                        )
                    )

                continue

            valid, errors = self.validator.validate(
                report
            )

            if valid:
                return report

            last_errors = errors

            if (
                attempt
                < self.MAX_GENERATION_ATTEMPTS
            ):
                current_prompt = (
                    self._build_corrective_prompt(
                        base_prompt=base_prompt,
                        errors=last_errors,
                    )
                )

        raise ValueError(
            "MeetingReport inválido: "
            + "; ".join(
                last_errors
            )
        )

    @staticmethod
    def _build_corrective_prompt(
        base_prompt: Prompt,
        errors: list[str],
    ) -> Prompt:
        """
        Construye el Prompt del segundo intento.

        Conserva íntegramente el contrato y la transcripción
        originales, pero añade feedback explícito sobre los
        defectos detectados en la generación anterior.
        """

        if not isinstance(
            base_prompt,
            Prompt,
        ):
            raise TypeError(
                "base_prompt debe ser una instancia "
                "de Prompt."
            )

        error_text = "\n".join(
            f"- {error}"
            for error in errors
        )

        correction = f"""

INSTRUCCIONES CORRECTIVAS PARA ESTE NUEVO INTENTO

La generación anterior fue rechazada por los siguientes
problemas:

{error_text}

Genera nuevamente TODO el documento desde cero.

Reglas obligatorias para este intento:

- No devuelvas cadenas vacías en campos obligatorios.
- El campo title debe contener un título descriptivo y
  específico de la reunión.
- executive_summary debe explicar de forma suficiente lo
  tratado en la reunión.
- key_points debe contener al menos un punto relevante.
- No inventes hechos que no estén respaldados por la
  transcripción.
- Si una sección opcional no tiene información suficiente,
  utiliza una lista vacía en lugar de crear objetos vacíos.
- Respeta exactamente el JSON Schema solicitado.
- Devuelve únicamente el objeto JSON estructurado requerido.
"""

        return Prompt(
            content=(
                base_prompt.content
                + correction
            ),
            version=base_prompt.version,
        )
