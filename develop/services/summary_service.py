"""
summary_service.py

Genera Summary a partir de Transcript.
"""

import json
from pathlib import Path

from models.artifacts.summary import Summary
from providers.ollama_provider import OllamaProvider


class SummaryService:

    def __init__(self):

        self.provider = OllamaProvider()

    def generate_from_transcript(
        self,
        transcript_file: Path
    ) -> Summary:

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

        response = self.provider.generate(prompt)

        data = json.loads(response)

        return Summary(
            artifact_type="summary",
            provider="ollama",
            model=self.provider.model,
            prompt_version="summary_v1",
            title=data["title"],
            executive_summary=data["executive_summary"],
            key_points=data["key_points"]
        )