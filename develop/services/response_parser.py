"""
response_parser.py

Convierte respuestas JSON de IA en objetos del dominio.
"""

import json

from models.artifacts.summary import Summary


class ResponseParser:

    def parse_summary(
        self,
        response: str,
        provider: str,
        model: str,
        prompt_version: str
    ) -> Summary:

        data = json.loads(response)

        return Summary(
            artifact_type="summary",
            provider=provider,
            model=model,
            prompt_version=prompt_version,
            title=data["title"],
            executive_summary=data["executive_summary"],
            key_points=data["key_points"]
        )