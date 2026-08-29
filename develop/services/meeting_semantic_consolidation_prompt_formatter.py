"""
meeting_semantic_consolidation_prompt_formatter.py

Construye el Prompt compacto para la consolidación semántica global
de MeetingKnowledge mediante referencias a items fuente.
"""

import json
import re
from pathlib import Path

from application.runtime_paths import RuntimePaths
from models.meeting_knowledge import MeetingKnowledge
from models.prompt import Prompt


class MeetingSemanticConsolidationPromptFormatter:

    DEFAULT_CONTRACT = (
        "meeting_semantic_consolidation_v1"
    )
    CONTRACTS_DIRECTORY = (
        RuntimePaths.resolve()
        .prompts_directory
    )
    CATALOG_PLACEHOLDER = (
        "{{SOURCE_CATALOG}}"
    )
    CONTRACT_NAME_PATTERN = re.compile(
        r"^[A-Za-z0-9][A-Za-z0-9_-]*$"
    )
    SECTION_KIND_PAIRS = (
        ("topics", "topic"),
        ("decisions", "decision"),
        ("action_items", "action"),
        ("risks", "risk"),
        ("pending_items", "pending"),
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
        meeting_knowledge: MeetingKnowledge,
    ) -> Prompt:
        if not isinstance(
            meeting_knowledge,
            MeetingKnowledge,
        ):
            raise TypeError(
                "meeting_knowledge debe ser una instancia "
                "de MeetingKnowledge."
            )

        template = self.template_file.read_text(
            encoding="utf-8"
        )
        self._validate_template(
            template
        )

        catalog = self.build_catalog(
            meeting_knowledge
        )

        serialized_catalog = json.dumps(
            catalog,
            ensure_ascii=False,
            separators=(
                ",",
                ":",
            ),
        )

        return Prompt(
            content=template.replace(
                self.CATALOG_PLACEHOLDER,
                serialized_catalog,
            ),
            version=self.contract,
        )

    @classmethod
    def build_catalog(
        cls,
        meeting_knowledge: MeetingKnowledge,
    ) -> list[dict]:
        if not isinstance(
            meeting_knowledge,
            MeetingKnowledge,
        ):
            raise TypeError(
                "meeting_knowledge debe ser una instancia "
                "de MeetingKnowledge."
            )

        catalog: list[dict] = []

        for chunk in meeting_knowledge.chunks:
            for section_name, kind in (
                cls.SECTION_KIND_PAIRS
            ):
                items = getattr(
                    chunk,
                    section_name,
                )

                for item_index, item in enumerate(
                    items
                ):
                    entry = {
                        "kind": kind,
                        "chunk_index": (
                            chunk.chunk_index
                        ),
                        "item_index": item_index,
                        "text": cls._item_text(
                            kind=kind,
                            item=item,
                        ),
                    }

                    if kind == "action":
                        entry.update(
                            cls._action_metadata(
                                item
                            )
                        )

                    catalog.append(
                        entry
                    )

        return catalog

    @staticmethod
    def _item_text(
        kind: str,
        item,
    ) -> str:
        if kind == "topic":
            if item.title == item.summary:
                return item.summary

            return (
                f"{item.title}. "
                f"{item.summary}"
            )

        return item.description

    @staticmethod
    def _action_metadata(
        item,
    ) -> dict:
        return {
            "owner": (
                item.owner.display_name
                if item.owner is not None
                else None
            ),
            "due_date": (
                item.due_date.isoformat()
                if item.due_date is not None
                else None
            ),
            "status": item.status.value,
        }

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
            cls.CATALOG_PLACEHOLDER
        )

        if placeholder_count == 0:
            raise ValueError(
                "La plantilla no contiene el marcador "
                "{{SOURCE_CATALOG}}."
            )

        if placeholder_count > 1:
            raise ValueError(
                "La plantilla contiene más de una "
                "ocurrencia del marcador "
                "{{SOURCE_CATALOG}}."
            )
