"""
summary_service.py

Genera Summary a partir de contenido textual.
"""

from pathlib import Path

from providers.ollama_provider import OllamaProvider
from services.response_parser import ResponseParser


class SummaryService:
    """
    Genera una minuta utilizando contenido textual
    previamente preparado por el Knowledge Pipeline.

    No carga transcripciones desde el sistema de archivos.
    """

    DEFAULT_PROMPT_FILE = Path(
        "prompts/summary_v1.md"
    )

    PROMPT_VERSION = "summary_v1"

    def __init__(
        self,
        provider=None,
        response_parser=None,
        prompt_file: Path | None = None,
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

        self.prompt_file = (
            prompt_file
            if prompt_file is not None
            else self.DEFAULT_PROMPT_FILE
        )

    def generate(
        self,
        transcript_text: str,
    ):
        """
        Genera un Summary a partir del contenido textual
        de una transcripción.

        Args:
            transcript_text:
                Representación textual preparada por el
                Knowledge Pipeline.

        Returns:
            Summary:
                Minuta estructurada generada por el proveedor.

        Raises:
            TypeError:
                Si transcript_text no es una cadena.

            ValueError:
                Si transcript_text está vacío.
        """

        if not isinstance(
            transcript_text,
            str,
        ):
            raise TypeError(
                "transcript_text debe ser una cadena."
            )

        if not transcript_text.strip():
            raise ValueError(
                "transcript_text no puede estar vacío."
            )

        prompt_template = self.prompt_file.read_text(
            encoding="utf-8"
        )

        prompt = prompt_template.replace(
            "{{TRANSCRIPT}}",
            transcript_text,
        )

        response = self.provider.generate(
            prompt
        )

        return self.response_parser.parse_summary(
            response=response,
            provider="ollama",
            model=self.provider.model,
            prompt_version=self.PROMPT_VERSION,
        )