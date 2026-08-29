"""
output_schema_loader.py

Carga contratos JSON Schema versionados utilizados
para restringir la salida de los proveedores de IA.
"""

import json
import re
from json import JSONDecodeError
from pathlib import Path

from application.runtime_paths import RuntimePaths


class OutputSchemaLoader:
    """
    Resuelve y carga un JSON Schema a partir del nombre
    versionado de un contrato.

    Los schemas de aplicación viven en:

        <resource_root>/prompts/schemas/<contract>.json

    El loader no conoce Summary, MeetingReport ni ningún
    otro artefacto concreto.
    """

    DEFAULT_SCHEMAS_DIRECTORY = (
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
                "schemas_directory debe ser una instancia "
                "de Path o None."
            )

        self.schemas_directory = (
            schemas_directory
            if schemas_directory is not None
            else self.DEFAULT_SCHEMAS_DIRECTORY
        )

    def load(
        self,
        contract: str,
    ) -> dict:
        """
        Carga el JSON Schema asociado a un contrato.

        Raises:
            TypeError:
                Si contract no es una cadena.

            ValueError:
                Si el nombre del contrato es inválido,
                el archivo no contiene JSON válido o
                la raíz del schema no es un objeto.

            FileNotFoundError:
                Si no existe el schema solicitado.
        """

        normalized_contract = (
            self._validate_contract(
                contract
            )
        )

        schema_file = (
            self.schemas_directory
            / f"{normalized_contract}.json"
        )

        raw_schema = schema_file.read_text(
            encoding="utf-8"
        )

        try:
            schema = json.loads(
                raw_schema
            )

        except JSONDecodeError as ex:
            raise ValueError(
                "El schema del contrato "
                f"{normalized_contract} no contiene "
                f"JSON válido. Detalle: {ex}"
            ) from ex

        if not isinstance(
            schema,
            dict,
        ):
            raise ValueError(
                "El schema del contrato "
                f"{normalized_contract} debe contener "
                "un objeto JSON en la raíz."
            )

        return schema

    @classmethod
    def _validate_contract(
        cls,
        contract: str,
    ) -> str:
        """
        Valida y normaliza el nombre lógico del contrato.
        """

        if not isinstance(
            contract,
            str,
        ):
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
