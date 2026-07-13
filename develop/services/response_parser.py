"""
response_parser.py

Convierte respuestas JSON de IA en objetos del dominio.
"""

import json
from json import JSONDecodeError

from models.artifacts.summary import Summary


class ResponseParser:

    def parse_summary(
        self,
        response: str,
        provider: str,
        model: str,
        prompt_version: str
    ) -> Summary:

        clean_response = self._clean_json_response(
            response
        )

        try:
            data = json.loads(clean_response)

        except JSONDecodeError as ex:
            raise ValueError(
                "La respuesta de IA no contiene JSON válido. "
                f"Detalle: {ex}"
            ) from ex

        required_fields = {
            "title",
            "executive_summary",
            "key_points"
        }

        missing_fields = required_fields.difference(
            data.keys()
        )

        if missing_fields:
            raise ValueError(
                "La respuesta de IA no contiene los campos "
                f"requeridos: {', '.join(sorted(missing_fields))}"
            )

        if not isinstance(data["key_points"], list):
            raise ValueError(
                "El campo key_points debe ser una lista."
            )

        return Summary(
            artifact_type="summary",
            provider=provider,
            model=model,
            prompt_version=prompt_version,
            title=str(data["title"]).strip(),
            executive_summary=str(
                data["executive_summary"]
            ).strip(),
            key_points=[
                str(point).strip()
                for point in data["key_points"]
                if str(point).strip()
            ]
        )

    @staticmethod
    def _clean_json_response(response: str) -> str:

        if not response or not response.strip():
            raise ValueError(
                "La respuesta de IA está vacía."
            )

        cleaned = response.strip()

        if cleaned.startswith("```json"):
            cleaned = cleaned[len("```json"):]

        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]

        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]

        cleaned = cleaned.strip()

        first_brace = cleaned.find("{")
        last_brace = cleaned.rfind("}")

        if first_brace == -1 or last_brace == -1:
            raise ValueError(
                "No se encontró un objeto JSON en la respuesta de IA."
            )

        return cleaned[first_brace:last_brace + 1]