"""
meeting_report_consolidation_service.py

Consolida MeetingKnowledge en un MeetingReport global mediante
un proveedor de IA con salida estructurada.
"""

from models.artifacts.meeting_report import MeetingReport
from models.meeting_knowledge import MeetingKnowledge
from models.prompt import Prompt
from providers.ollama_provider import OllamaProvider
from services.json_schema_loader import JsonSchemaLoader
from services.meeting_report_parser import MeetingReportParser
from services.validators.meeting_report_grounding_validator import (
    MeetingReportGroundingValidator,
)
from services.validators.meeting_report_validator import (
    MeetingReportValidator,
)


class MeetingReportConsolidationService:
    """
    Genera un MeetingReport global desde MeetingKnowledge.

    Responsabilidades:
    - exigir el contrato de prompt de consolidación;
    - usar el schema estructural estable de MeetingReport;
    - solicitar una única generación al proveedor;
    - convertir la respuesta al dominio MeetingReport;
    - validar grounding contra MeetingKnowledge;
    - validar calidad semántica/documental.

    No divide transcripts, no extrae ChunkKnowledge, no persiste
    artefactos y no realiza reintentos.
    """

    PROMPT_CONTRACT = "meeting_report_consolidation_v1"
    OUTPUT_SCHEMA_CONTRACT = "meeting_report_v1"
    PROVIDER_NAME = "ollama"

    def __init__(
        self,
        provider=None,
        parser=None,
        schema_loader=None,
        grounding_validator=None,
        report_validator=None,
    ) -> None:
        self.provider = provider if provider is not None else OllamaProvider()
        self.parser = parser if parser is not None else MeetingReportParser()
        self.schema_loader = (
            schema_loader if schema_loader is not None else JsonSchemaLoader()
        )
        self.grounding_validator = (
            grounding_validator
            if grounding_validator is not None
            else MeetingReportGroundingValidator()
        )
        self.report_validator = (
            report_validator
            if report_validator is not None
            else MeetingReportValidator()
        )

    def generate(
        self,
        prompt: Prompt,
        meeting_knowledge: MeetingKnowledge,
    ) -> MeetingReport:
        """
        Genera y valida un MeetingReport consolidado.

        Errores HTTP, timeouts y demás fallos del proveedor se
        propagan sin ser ocultados. Los reintentos pertenecen a
        una capa de orquestación superior.
        """

        if not isinstance(prompt, Prompt):
            raise TypeError(
                "prompt debe ser una instancia de Prompt."
            )

        if not isinstance(meeting_knowledge, MeetingKnowledge):
            raise TypeError(
                "meeting_knowledge debe ser una instancia "
                "de MeetingKnowledge."
            )

        if prompt.version != self.PROMPT_CONTRACT:
            raise ValueError(
                "MeetingReportConsolidationService requiere "
                "el contrato "
                f"{self.PROMPT_CONTRACT}. "
                f"Recibido: {prompt.version}."
            )

        if not meeting_knowledge.has_content:
            raise ValueError(
                "MeetingKnowledge no contiene conocimiento "
                "suficiente para consolidar un MeetingReport."
            )

        output_schema = self.schema_loader.load(
            self.OUTPUT_SCHEMA_CONTRACT
        )

        response = self.provider.generate(
            prompt.content,
            output_schema,
        )

        report = self.parser.parse(
            response=response,
            provider=self.PROVIDER_NAME,
            model=self.provider.model,
            prompt_version=prompt.version,
        )

        grounded, grounding_errors = (
            self.grounding_validator.validate(
                report=report,
                meeting_knowledge=meeting_knowledge,
            )
        )

        if not grounded:
            raise ValueError(
                "MeetingReport sin grounding válido: "
                + "; ".join(grounding_errors)
            )

        valid, validation_errors = self.report_validator.validate(
            report
        )

        if not valid:
            raise ValueError(
                "MeetingReport consolidado inválido: "
                + "; ".join(validation_errors)
            )

        return report
