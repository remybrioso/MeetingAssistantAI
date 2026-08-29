"""
meeting_report_narrative_prompt_formatter.py

Construye el Prompt compacto para la etapa global G2 a partir de
MeetingSemanticConsolidation.
"""

import json
import re
from pathlib import Path

from models.meeting_semantic_consolidation import (
    MeetingSemanticConsolidation,
)
from models.prompt import Prompt


class MeetingReportNarrativePromptFormatter:
    """
    Serializa solo item_id + kind + description.

    G2 no recibe evidencia ni metadata operacional. Toda esa
    información permanece bajo control del sistema.
    """

    DEFAULT_CONTRACT = (
        "meeting_report_narrative_v1"
    )

    CONTRACTS_DIRECTORY = Path(
        "prompts"
    )

    ITEMS_PLACEHOLDER = (
        "{{CONSOLIDATED_ITEMS}}"
    )

    CONTRACT_NAME_PATTERN = re.compile(
        r"^[A-Za-z0-9][A-Za-z0-9_-]*$"
    )

    def __init__(
        self,
        contract: str = DEFAULT_CONTRACT,
        template_file: Path | None = None,
    ) -> None:
        self.contract = (
            self._validate_contract(
                contract
            )
        )

        self.template_file = (
            self._resolve_template_file(
                contract=self.contract,
                template_file=template_file,
            )
        )

    def format(
        self,
        semantic_consolidation: MeetingSemanticConsolidation,
    ) -> Prompt:
        if not isinstance(
            semantic_consolidation,
            MeetingSemanticConsolidation,
        ):
            raise TypeError(
                "semantic_consolidation debe ser una instancia "
                "de MeetingSemanticConsolidation."
            )

        if not semantic_consolidation.has_content:
            raise ValueError(
                "semantic_consolidation no contiene items "
                "suficientes para redactar narrativa."
            )

        template = self.template_file.read_text(
            encoding="utf-8"
        )

        self._validate_template(
            template
        )

        catalog = self.build_catalog(
            semantic_consolidation
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
                self.ITEMS_PLACEHOLDER,
                serialized_catalog,
            ),
            version=self.contract,
        )

    @staticmethod
    def build_catalog(
        semantic_consolidation: MeetingSemanticConsolidation,
    ) -> list[dict]:
        if not isinstance(
            semantic_consolidation,
            MeetingSemanticConsolidation,
        ):
            raise TypeError(
                "semantic_consolidation debe ser una instancia "
                "de MeetingSemanticConsolidation."
            )

        return [
            {
                "item_id": item_id,
                "kind": item.kind.value,
                "description": (
                    item.description
                ),
            }
            for item_id, item in enumerate(
                semantic_consolidation.items
            )
        ]

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

        normalized_contract = (
            contract.strip()
        )

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
            cls.ITEMS_PLACEHOLDER
        )

        if placeholder_count == 0:
            raise ValueError(
                "La plantilla no contiene el marcador "
                "{{CONSOLIDATED_ITEMS}}."
            )

        if placeholder_count > 1:
            raise ValueError(
                "La plantilla contiene más de una ocurrencia "
                "del marcador {{CONSOLIDATED_ITEMS}}."
            )
