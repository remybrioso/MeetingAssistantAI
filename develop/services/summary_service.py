"""
summary_service.py

Servicio de generación del artefacto Summary.
"""

from models.prompt import Prompt
from providers.ollama_provider import OllamaProvider
from services.output_schema_loader import (
    OutputSchemaLoader,
)
from services.response_parser import ResponseParser


class SummaryService:

    def __init__(
        self,
        provider=None,
        response_parser=None,
        schema_loader=None,
    ):
        self.provider = (
            provider
            if provider is not None
            else OllamaProvider()
        )

        self.response_parser = (
            response_parser
            if response_parser is not None
            else ResponseParser()
        )

        self.schema_loader = (
            schema_loader
            if schema_loader is not None
            else OutputSchemaLoader()
        )

    def generate(
        self,
        prompt: Prompt,
    ):
        """
        Genera un Summary utilizando el schema asociado
        a la versión del Prompt.
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

        return self.response_parser.parse_summary(
            response=response,
            provider="ollama",
            model=self.provider.model,
            prompt_version=prompt.version,
        )