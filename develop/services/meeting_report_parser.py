"""
meeting_report_parser.py

Convierte una respuesta JSON de IA en un MeetingReport.
"""

import json
from json import JSONDecodeError

from models.artifacts.meeting_report import MeetingReport


class MeetingReportParser:
    """
    Convierte la respuesta textual de un proveedor de IA
    en un MeetingReport validado por el dominio.

    Esta primera versión procesa únicamente los campos
    principales del reporte. Las entidades anidadas se
    incorporarán en las siguientes tareas.
    """

    REQUIRED_FIELDS = {
        "title",
        "executive_summary",
        "key_points",
    }

    NESTED_FIELDS = {
        "topics",
        "decisions",
        "action_items",
        "risks",
        "pending_items",
        "participants",
    }

    def parse(
        self,
        response: str,
        provider: str,
        model: str,
        prompt_version: str,
    ) -> MeetingReport:
        """
        Convierte una respuesta JSON en MeetingReport.

        Raises:
            ValueError:
                Si la respuesta está vacía, no contiene
                JSON válido, carece de campos obligatorios
                o incluye secciones anidadas todavía no
                soportadas.

            TypeError:
                Si el objeto JSON principal no es un
                diccionario o si el dominio recibe tipos
                incorrectos.
        """

        clean_response = self._clean_json_response(
            response
        )

        data = self._load_json(
            clean_response
        )

        self._validate_root_object(
            data
        )

        self._validate_required_fields(
            data
        )

        self._validate_text_collections(
            data
        )

        self._validate_unsupported_nested_fields(
            data
        )

        return MeetingReport(
            artifact_type="meeting_report",
            provider=provider,
            model=model,
            prompt_version=prompt_version,
            title=data["title"],
            objective=data.get(
                "objective"
            ),
            executive_summary=data[
                "executive_summary"
            ],
            key_points=data["key_points"],
            topics=[],
            decisions=[],
            action_items=[],
            risks=[],
            pending_items=[],
            participants=[],
            conclusions=data.get(
                "conclusions",
                [],
            ),
        )

    @staticmethod
    def _load_json(
        clean_response: str,
    ):
        """
        Convierte el contenido limpio en datos Python.
        """

        try:
            return json.loads(
                clean_response
            )

        except JSONDecodeError as ex:
            raise ValueError(
                "La respuesta de IA no contiene JSON "
                f"válido. Detalle: {ex}"
            ) from ex

    @staticmethod
    def _validate_root_object(
        data,
    ) -> None:
        """
        Verifica que la raíz del JSON sea un objeto.
        """

        if not isinstance(
            data,
            dict,
        ):
            raise TypeError(
                "La respuesta de MeetingReport debe "
                "contener un objeto JSON."
            )

    def _validate_required_fields(
        self,
        data: dict,
    ) -> None:
        """
        Verifica la presencia de los campos obligatorios.
        """

        missing_fields = (
            self.REQUIRED_FIELDS.difference(
                data.keys()
            )
        )

        if missing_fields:
            raise ValueError(
                "La respuesta de MeetingReport no contiene "
                "los campos requeridos: "
                + ", ".join(
                    sorted(
                        missing_fields
                    )
                )
            )

    @staticmethod
    def _validate_text_collections(
        data: dict,
    ) -> None:
        """
        Verifica las colecciones textuales conocidas.

        La validación de sus elementos individuales
        corresponde a MeetingReport.
        """

        if not isinstance(
            data["key_points"],
            list,
        ):
            raise TypeError(
                "El campo key_points debe ser una lista."
            )

        conclusions = data.get(
            "conclusions",
            [],
        )

        if not isinstance(
            conclusions,
            list,
        ):
            raise TypeError(
                "El campo conclusions debe ser una lista."
            )

    def _validate_unsupported_nested_fields(
        self,
        data: dict,
    ) -> None:
        """
        Evita descartar silenciosamente entidades anidadas
        antes de que el parser pueda construirlas.
        """

        for field_name in sorted(
            self.NESTED_FIELDS
        ):
            if field_name not in data:
                continue

            value = data[field_name]

            if not isinstance(
                value,
                list,
            ):
                raise TypeError(
                    f"El campo {field_name} debe ser "
                    "una lista."
                )

            if value:
                raise ValueError(
                    f"El campo {field_name} todavía no "
                    "está soportado por "
                    "MeetingReportParser."
                )

    @staticmethod
    def _clean_json_response(
        response: str,
    ) -> str:
        """
        Extrae un objeto JSON de la respuesta textual.

        Tolera bloques Markdown y texto externo, pero exige
        que exista al menos un objeto delimitado por llaves.
        """

        if (
            not isinstance(
                response,
                str,
            )
            or not response.strip()
        ):
            raise ValueError(
                "La respuesta de IA está vacía."
            )

        cleaned = response.strip()

        if cleaned.startswith(
            "```json"
        ):
            cleaned = cleaned[
                len("```json"):
            ]

        elif cleaned.startswith(
            "```"
        ):
            cleaned = cleaned[3:]

        if cleaned.endswith(
            "```"
        ):
            cleaned = cleaned[:-3]

        cleaned = cleaned.strip()

        first_brace = cleaned.find(
            "{"
        )

        last_brace = cleaned.rfind(
            "}"
        )

        if (
            first_brace == -1
            or last_brace == -1
            or last_brace < first_brace
        ):
            raise ValueError(
                "No se encontró un objeto JSON en la "
                "respuesta de IA."
            )

        return cleaned[
            first_brace:last_brace + 1
        ]