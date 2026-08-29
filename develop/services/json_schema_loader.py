"""
json_schema_loader.py

Carga contratos JSON Schema versionados para salidas
estructuradas de proveedores de IA.
"""

import json
import re
from json import JSONDecodeError
from pathlib import Path

from application.runtime_paths import RuntimePaths


class JsonSchemaLoader:
    """Carga un JSON Schema a partir de un contrato versionado."""

    DEFAULT_DIRECTORY = (
        RuntimePaths.resolve()
        .schemas_directory
    )

    CONTRACT_NAME_PATTERN = re.compile(
        r"^[A-Za-z0-9][A-Za-z0-9_-]*$"
    )

    def __init__(
        self,
        schemas_directory: Path | None = None,
    ) -> None:
        if (
            schemas_directory is not None
            and not isinstance(
                schemas_directory,
                Path,
            )
        ):
            raise TypeError(
                "schemas_directory debe ser una "
                "instancia de Path o None."
            )

        self.schemas_directory = (
            schemas_directory
            if schemas_directory is not None
            else self.DEFAULT_DIRECTORY
        )

    def load(self, contract: str) -> dict:
        normalized_contract = self._validate_contract(
            contract
        )

        schema_file = (
            self.schemas_directory
            / f"{normalized_contract}.json"
        )

        schema_text = schema_file.read_text(
            encoding="utf-8"
        )

        try:
            schema = json.loads(schema_text)
        except JSONDecodeError as ex:
            raise ValueError(
                "El schema del contrato "
                f"{normalized_contract} no contiene "
                "JSON válido. "
                f"Detalle: {ex}"
            ) from ex

        if not isinstance(schema, dict):
            raise TypeError(
                "El schema del contrato "
                f"{normalized_contract} debe contener "
                "un objeto JSON en la raíz."
            )

        if not schema:
            raise ValueError(
                "El schema del contrato "
                f"{normalized_contract} está vacío."
            )

        return schema

    @classmethod
    def _validate_contract(
        cls,
        contract: str,
    ) -> str:
        if not isinstance(contract, str):
            raise TypeError(
                "contract debe ser una cadena."
            )

        normalized_contract = contract.strip()

        if not normalized_contract:
            raise ValueError(
                "contract no puede estar vacío."
            )

        if not cls.CONTRACT_NAME_PATTERN.fullmatch(
            normalized_contract
        ):
            raise ValueError(
                "contract contiene caracteres no "
                "permitidos."
            )

        return normalized_contract
