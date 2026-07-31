"""
summary_service.py
"""

from models.prompt import Prompt
from providers.ollama_provider import OllamaProvider
from services.response_parser import ResponseParser


class SummaryService:

    def __init__(
        self,
        provider=None,
        response_parser=None,
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

    def generate(
        self,
        prompt: Prompt,
    ):

        if not isinstance(
            prompt,
            Prompt,
        ):
            raise TypeError(
                "prompt debe ser una instancia de Prompt."
            )

        response = self.provider.generate(
            prompt.content
        )

        return self.response_parser.parse_summary(
            response=response,
            provider="ollama",
            model=self.provider.model,
            prompt_version=prompt.version,
        )