"""Construye el único pase de reparación de cobertura de J1."""

import json
from pathlib import Path

from application.runtime_paths import RuntimePaths
from models.prompt import Prompt
from models.transcript_chunk import TranscriptChunk


class ChunkClassificationRepairPromptFormatter:
    DEFAULT_CONTRACT = "chunk_classification_repair_v1"
    CONTEXT_PLACEHOLDER = "{{REPAIR_CONTEXT}}"

    def __init__(self, template_file: Path | None = None) -> None:
        if template_file is not None and not isinstance(template_file, Path):
            raise TypeError("template_file debe ser una instancia de Path o None.")
        self.template_file = (
            template_file if template_file is not None
            else RuntimePaths.resolve().prompts_directory
            / f"{self.DEFAULT_CONTRACT}.md"
        )

    def format(
        self,
        chunk: TranscriptChunk,
        invalid_response: str,
        coverage_error: str,
    ) -> Prompt:
        if not isinstance(chunk, TranscriptChunk):
            raise TypeError("chunk debe ser una instancia de TranscriptChunk.")
        for name, value in (
            ("invalid_response", invalid_response),
            ("coverage_error", coverage_error),
        ):
            if not isinstance(value, str):
                raise TypeError(f"{name} debe ser una cadena.")
            if not value.strip():
                raise ValueError(f"{name} no puede estar vacío.")

        template = self.template_file.read_text(encoding="utf-8")
        if template.count(self.CONTEXT_PLACEHOLDER) != 1:
            raise ValueError(
                "La plantilla debe contener exactamente un marcador "
                + self.CONTEXT_PLACEHOLDER + "."
            )

        # Una sola sustitución: el contenido del usuario nunca es una plantilla.
        context = json.dumps(
            {
                "segments": [
                    {"segment_id": index, "text": segment.text}
                    for index, segment in enumerate(chunk.segments)
                ],
                "valid_segment_ids": list(range(len(chunk.segments))),
                "invalid_response": invalid_response,
                "coverage_error": coverage_error,
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )
        return Prompt(
            content=template.replace(self.CONTEXT_PLACEHOLDER, context),
            version=self.DEFAULT_CONTRACT,
        )
