"""
chunk_action_metadata_prompt_formatter.py

Construye un Prompt batch para enriquecer todas las acciones
clasificadas dentro de un TranscriptChunk.
"""

import json
import re
from pathlib import Path

from models.chunk_classification import (
    ChunkClassification,
    ChunkKnowledgeKind,
)
from models.prompt import Prompt
from models.transcript_chunk import TranscriptChunk


class ChunkActionMetadataPromptFormatter:
    """
    Envía en una sola solicitud todas las acciones del chunk.

    Cada acción incluye únicamente:
    - item_index del ChunkClassification;
    - description;
    - segment_id + text de su evidencia.

    No envía speaker ni timestamps.
    """

    DEFAULT_CONTRACT = "chunk_action_metadata_v1"
    CONTRACTS_DIRECTORY = Path(
        "prompts"
    )
    ACTIONS_PLACEHOLDER = "{{ACTIONS}}"
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
        classification: ChunkClassification,
        chunk: TranscriptChunk,
    ) -> Prompt:
        if not isinstance(
            classification,
            ChunkClassification,
        ):
            raise TypeError(
                "classification debe ser una instancia de "
                "ChunkClassification."
            )

        if not isinstance(
            chunk,
            TranscriptChunk,
        ):
            raise TypeError(
                "chunk debe ser una instancia de TranscriptChunk."
            )

        self._validate_classification_source(
            classification=classification,
            chunk=chunk,
        )

        action_payload = self._build_action_payload(
            classification=classification,
            chunk=chunk,
        )

        if not action_payload:
            raise ValueError(
                "classification no contiene acciones para "
                "enriquecer."
            )

        template = self.template_file.read_text(
            encoding="utf-8"
        )
        self._validate_template(
            template
        )

        serialized_actions = json.dumps(
            action_payload,
            ensure_ascii=False,
            separators=(
                ",",
                ":",
            ),
        )

        return Prompt(
            content=template.replace(
                self.ACTIONS_PLACEHOLDER,
                serialized_actions,
            ),
            version=self.contract,
        )

    @staticmethod
    def _build_action_payload(
        classification: ChunkClassification,
        chunk: TranscriptChunk,
    ) -> list[dict]:
        payload: list[dict] = []

        for item_index, item in enumerate(
            classification.items
        ):
            if (
                item.kind
                is not ChunkKnowledgeKind.ACTION
            ):
                continue

            source_segments = []

            for segment_id in item.segment_ids:
                if (
                    segment_id < 0
                    or segment_id
                    >= len(
                        chunk.segments
                    )
                ):
                    raise ValueError(
                        "La clasificación contiene un "
                        "segment_id inexistente del chunk."
                    )

                segment = chunk.segments[
                    segment_id
                ]

                source_segments.append(
                    {
                        "segment_id": segment_id,
                        "text": segment.text,
                    }
                )

            payload.append(
                {
                    "item_index": item_index,
                    "description": item.description,
                    "segments": source_segments,
                }
            )

        return payload

    @staticmethod
    def _validate_classification_source(
        classification: ChunkClassification,
        chunk: TranscriptChunk,
    ) -> None:
        tolerance = 0.001

        if classification.chunk_index != chunk.index:
            raise ValueError(
                "classification y chunk no pertenecen al mismo "
                "chunk_index."
            )

        if (
            abs(
                classification.start
                - chunk.start
            )
            > tolerance
            or abs(
                classification.end
                - chunk.end
            )
            > tolerance
        ):
            raise ValueError(
                "classification y chunk no comparten el mismo "
                "rango temporal."
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
                "contract contiene caracteres no permitidos."
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
                "template_file debe ser una instancia de Path "
                "o None."
            )

        return template_file

    @classmethod
    def _validate_template(
        cls,
        template: str,
    ) -> None:
        placeholder_count = template.count(
            cls.ACTIONS_PLACEHOLDER
        )

        if placeholder_count == 0:
            raise ValueError(
                "La plantilla no contiene el marcador "
                "{{ACTIONS}}."
            )

        if placeholder_count > 1:
            raise ValueError(
                "La plantilla contiene más de una ocurrencia "
                "del marcador {{ACTIONS}}."
            )
