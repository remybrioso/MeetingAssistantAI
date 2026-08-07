"""
meeting_report_service.py

Servicio de generación del artefacto MeetingReport.
"""

from models.artifacts.meeting_report import MeetingReport
from models.prompt import Prompt
from providers.ollama_provider import OllamaProvider
from services.meeting_report_parser import (
    MeetingReportParser,
)
from services.output_schema_loader import (
    OutputSchemaLoader,
)


class MeetingReportService:
    """
    Genera un MeetingReport estructurado mediante un
    proveedor de IA.

    Responsabilidades:

    - recibir un Prompt ya construido;
    - cargar el JSON Schema correspondiente a su versión;
    - solicitar generación estructurada al proveedor;
    - convertir la respuesta en MeetingReport mediante
      MeetingReportParser.

    No realiza validación semántica, persistencia,
    construcción del Prompt ni exportación.
    """

    PROVIDER_NAME = "ollama"

    def __init__(
        self,
        provider=None,
        response_parser=None,
        schema_loader=None,
    ) -> None:
        self.provider = (
            provider
            if provider is not None
            else OllamaProvider()
        )

        self.response_parser = (
            response_parser
            if response_parser is not None
            else MeetingReportParser()
        )

        self.schema_loader = (
            schema_loader
            if schema_loader is not None
            else OutputSchemaLoader()
        )

    def generate(
        self,
        prompt: Prompt,
    ) -> MeetingReport:
        """
        Genera un MeetingReport utilizando el contrato
        estructural asociado a la versión del Prompt.

        Args:
            prompt:
                Prompt completo y versionado.

        Returns:
            MeetingReport:
                Artefacto de dominio construido por
                MeetingReportParser.

        Raises:
            TypeError:
                Si prompt no es una instancia de Prompt.

            FileNotFoundError:
                Si no existe el JSON Schema asociado a
                prompt.version.

            ValueError:
                Si el proveedor o el parser detectan una
                respuesta inválida.
        """

        if not isinstance(
            prompt,
            Prompt,
        ):
            raise TypeError(
                "prompt debe ser una instancia de Prompt."
            )

        output_schema = self.schema_loader.load(
            prompt.version
        )

        response = self.provider.generate(
            prompt.content,
            output_schema=output_schema,
        )

        return self.response_parser.parse(
            response=response,
            provider=self.PROVIDER_NAME,
            model=self.provider.model,
            prompt_version=prompt.version,
        )