"""
meeting_knowledge_prompt_formatter.py

Construye un Prompt versionado para consolidar MeetingKnowledge
en un MeetingReport global.
"""

import json
import re
from pathlib import Path

from models.meeting_knowledge import MeetingKnowledge
from models.prompt import Prompt


class MeetingKnowledgePromptFormatter:
    """
    Convierte MeetingKnowledge en un Prompt de consolidación.

    El formatter preserva toda la estructura intermedia y no
    realiza deduplicación, resumen ni interpretación.
    """

    DEFAULT_CONTRACT = "meeting_report_consolidation_v1"

    CONTRACTS_DIRECTORY = Path(
        "prompts"
    )

    KNOWLEDGE_PLACEHOLDER = (
        "{{MEETING_KNOWLEDGE}}"
    )

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

        self.template_file = (
            self._resolve_template_file(
                contract=self.contract,
                template_file=template_file,
            )
        )

    def format(
        self,
        meeting_knowledge: MeetingKnowledge,
    ) -> Prompt:
        """
        Construye el Prompt global a partir de MeetingKnowledge.
        """

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

        knowledge_text = json.dumps(
            meeting_knowledge.as_dict(),
            ensure_ascii=False,
            indent=4,
        )

        prompt_content = template.replace(
            self.KNOWLEDGE_PLACEHOLDER,
            knowledge_text,
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
            cls.KNOWLEDGE_PLACEHOLDER
        )

        if placeholder_count == 0:
            raise ValueError(
                "La plantilla no contiene el marcador "
                "{{MEETING_KNOWLEDGE}}."
            )

        if placeholder_count > 1:
            raise ValueError(
                "La plantilla contiene más de una "
                "ocurrencia del marcador "
                "{{MEETING_KNOWLEDGE}}."
            )
