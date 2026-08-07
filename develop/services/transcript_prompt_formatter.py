"""
transcript_prompt_formatter.py

Construye un Prompt versionado a partir de un Transcript
y un contrato de salida para el proveedor de IA.
"""

import json
import re
from pathlib import Path

from models.prompt import Prompt
from models.transcript import Transcript


class TranscriptPromptFormatter:
    """
    Convierte un Transcript en un Prompt listo para ser
    enviado a un proveedor de IA.

    El formatter no conoce tipos concretos de artefactos.
    Recibe el nombre de un contrato versionado y resuelve
    automáticamente su plantilla desde:

        prompts/<contract>.md

    Para pruebas unitarias también permite inyectar una
    plantilla mediante template_file.
    """

    DEFAULT_CONTRACT = "summary_v1"

    CONTRACTS_DIRECTORY = Path(
        "prompts"
    )

    TRANSCRIPT_PLACEHOLDER = "{{TRANSCRIPT}}"

    CONTRACT_NAME_PATTERN = re.compile(
        r"^[A-Za-z0-9][A-Za-z0-9_-]*$"
    )

    def __init__(
        self,
        contract: str = DEFAULT_CONTRACT,
        template_file: Path | None = None,
    ) -> None:
        """
        Inicializa el formatter.

        Args:
            contract:
                Nombre versionado del contrato, sin extensión.

                Ejemplos:

                    summary_v1
                    meeting_report_v1

            template_file:
                Ruta opcional para sustituir la resolución
                automática de la plantilla.

                Está pensada principalmente para pruebas.

        Raises:
            TypeError:
                Si contract no es una cadena o template_file
                no es Path ni None.

            ValueError:
                Si contract está vacío o contiene caracteres
                no permitidos.
        """

        self.contract = self._validate_contract(
            contract
        )

        self.template_file = (
            self._resolve_template_file(
                contract=self.contract,
                template_file=template_file,
            )
        )

    def format(
        self,
        transcript: Transcript,
    ) -> Prompt:
        """
        Construye un Prompt a partir de un Transcript.

        Raises:
            TypeError:
                Si transcript no es una instancia de
                Transcript.

            FileNotFoundError:
                Si la plantilla del contrato no existe.

            ValueError:
                Si la plantilla no contiene exactamente una
                ocurrencia de {{TRANSCRIPT}}.
        """

        if not isinstance(
            transcript,
            Transcript,
        ):
            raise TypeError(
                "transcript debe ser una instancia "
                "de Transcript."
            )

        template = self.template_file.read_text(
            encoding="utf-8"
        )

        self._validate_template(
            template
        )

        transcript_text = json.dumps(
            transcript.as_dict(),
            ensure_ascii=False,
            indent=4,
        )

        prompt_content = template.replace(
            self.TRANSCRIPT_PLACEHOLDER,
            transcript_text,
        )

        return Prompt(
            content=prompt_content,
            version=self.contract,
        )

    @classmethod
    def _validate_contract(
        cls,
        contract: str,
    ) -> str:
        """
        Valida el nombre lógico de un contrato.

        El contrato no incluye carpeta ni extensión.
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

    @classmethod
    def _resolve_template_file(
        cls,
        contract: str,
        template_file: Path | None,
    ) -> Path:
        """
        Resuelve la plantilla correspondiente al contrato.
        """

        if template_file is None:
            return (
                cls.CONTRACTS_DIRECTORY
                / f"{contract}.md"
            )

        if not isinstance(
            template_file,
            Path,
        ):
            raise TypeError(
                "template_file debe ser una instancia "
                "de Path o None."
            )

        return template_file

    @classmethod
    def _validate_template(
        cls,
        template: str,
    ) -> None:
        """
        Verifica el contrato de inyección del Transcript.

        La plantilla debe contener exactamente una
        ocurrencia de {{TRANSCRIPT}}.
        """

        placeholder_count = template.count(
            cls.TRANSCRIPT_PLACEHOLDER
        )

        if placeholder_count == 0:
            raise ValueError(
                "La plantilla no contiene el marcador "
                "{{TRANSCRIPT}}."
            )

        if placeholder_count > 1:
            raise ValueError(
                "La plantilla contiene más de una "
                "ocurrencia del marcador "
                "{{TRANSCRIPT}}."
            )