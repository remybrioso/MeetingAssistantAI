"""
summary_service.py

Genera Summary a partir de Transcript.
"""

from pathlib import Path

from providers.ollama_provider import OllamaProvider
from services.response_parser import ResponseParser


class SummaryService:

    def __init__(self):
        self.provider = OllamaProvider()
        self.response_parser = ResponseParser()

    def generate_from_transcript(
        self,
        transcript_file: Path
    ):

        transcript_text = transcript_file.read_text(
            encoding="utf-8"
        )

        prompt_template = Path(
            "prompts/summary_v1.md"
        ).read_text(
            encoding="utf-8"
        )

        prompt = prompt_template.replace(
            "{{TRANSCRIPT}}",
            transcript_text
        )

        response = self.provider.generate(
            prompt
        )

        return self.response_parser.parse_summary(
            response=response,
            provider="ollama",
            model=self.provider.model,
            prompt_version="summary_v1"
        )