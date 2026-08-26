"""
chunk_prompt_formatter.py

Construye un Prompt versionado a partir de un TranscriptChunk.
"""

import json
import re
from pathlib import Path

from models.prompt import Prompt
from models.transcript_chunk import TranscriptChunk


class ChunkPromptFormatter:
    """Convierte un TranscriptChunk en un Prompt de extracción."""

    DEFAULT_CONTRACT = "chunk_knowledge_v1"
    CONTRACTS_DIRECTORY = Path("prompts")
    CHUNK_PLACEHOLDER = "{{CHUNK}}"
    CONTRACT_NAME_PATTERN = re.compile(
        r"^[A-Za-z0-9][A-Za-z0-9_-]*$"
    )

    def __init__(
        self,
        contract: str = DEFAULT_CONTRACT,
        template_file: Path | None = None,
    ) -> None:
        self.contract = self._validate_contract(
            contract
        )
        self.template_file = self._resolve_template_file(
            contract=self.contract,
            template_file=template_file,
        )

    def format(
        self,
        chunk: TranscriptChunk,
    ) -> Prompt:
        if not isinstance(
            chunk,
            TranscriptChunk,
        ):
            raise TypeError(
                "chunk debe ser una instancia "
                "de TranscriptChunk."
            )

        template = self.template_file.read_text(
            encoding="utf-8"
        )
        self._validate_template(
            template
        )

        chunk_text = json.dumps(
            chunk.as_dict(),
            ensure_ascii=False,
            indent=4,
        )

        return Prompt(
            content=template.replace(
                self.CHUNK_PLACEHOLDER,
                chunk_text,
            ),
            version=self.contract,
        )

    @classmethod
    def _validate_contract(
        cls,
        contract: str,
    ) -> str:
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
        placeholder_count = template.count(
            cls.CHUNK_PLACEHOLDER
        )

        if placeholder_count == 0:
            raise ValueError(
                "La plantilla no contiene el marcador "
                "{{CHUNK}}."
            )

        if placeholder_count > 1:
            raise ValueError(
                "La plantilla contiene más de una "
                "ocurrencia del marcador "
                "{{CHUNK}}."
            )
