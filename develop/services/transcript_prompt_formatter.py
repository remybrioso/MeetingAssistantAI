"""
transcript_prompt_formatter.py

Construye un Prompt de resumen a partir de un Transcript.
"""

import json
from pathlib import Path

from models.prompt import Prompt
from models.transcript import Transcript


class TranscriptPromptFormatter:
    """
    Convierte un Transcript en un Prompt listo para ser
    enviado al servicio de generación de resúmenes.
    """

    DEFAULT_TEMPLATE = Path(
        "prompts/summary_v1.md"
    )

    PROMPT_VERSION = "summary_v1"

    def __init__(
        self,
        template_file: Path | None = None,
    ):
        self.template_file = (
            template_file
            if template_file is not None
            else self.DEFAULT_TEMPLATE
        )

    def format(
        self,
        transcript: Transcript,
    ) -> Prompt:
        """
        Construye un Prompt a partir de un Transcript.
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

        placeholder = "{{TRANSCRIPT}}"

        if placeholder not in template:
            raise ValueError(
                "La plantilla no contiene el marcador "
                "{{TRANSCRIPT}}."
            )

        transcript_text = json.dumps(
            transcript.as_dict(),
            ensure_ascii=False,
            indent=4,
        )

        prompt_content = template.replace(
            placeholder,
            transcript_text,
        )

        return Prompt(
            content=prompt_content,
            version=self.PROMPT_VERSION,
        )