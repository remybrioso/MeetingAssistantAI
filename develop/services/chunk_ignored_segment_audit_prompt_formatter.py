"""Construye el prompt versionado para auditar IDs ignorados por J1."""

import json
from pathlib import Path

from application.runtime_paths import RuntimePaths
from models.prompt import Prompt
from models.transcript_chunk import TranscriptChunk


class ChunkIgnoredSegmentAuditPromptFormatter:
    DEFAULT_CONTRACT = "chunk_ignored_segment_audit_v1"
    SEGMENTS_PLACEHOLDER = "{{CANDIDATE_SEGMENTS}}"

    def __init__(self, template_file: Path | None = None) -> None:
        if template_file is not None and not isinstance(template_file, Path):
            raise TypeError("template_file debe ser una instancia de Path o None.")
        self.template_file = (
            template_file
            if template_file is not None
            else RuntimePaths.resolve().prompts_directory
            / f"{self.DEFAULT_CONTRACT}.md"
        )

    def format(
        self,
        chunk: TranscriptChunk,
        candidate_ignored_segment_ids,
    ) -> Prompt:
        if not isinstance(chunk, TranscriptChunk):
            raise TypeError("chunk debe ser una instancia de TranscriptChunk.")
        if not isinstance(candidate_ignored_segment_ids, (list, tuple)):
            raise TypeError(
                "candidate_ignored_segment_ids debe ser una lista o tupla."
            )
        candidate_ids = list(candidate_ignored_segment_ids)
        if any(
            not isinstance(value, int) or isinstance(value, bool)
            for value in candidate_ids
        ):
            raise TypeError("candidate_ignored_segment_ids debe contener enteros.")
        if len(set(candidate_ids)) != len(candidate_ids):
            raise ValueError("candidate_ignored_segment_ids no puede contener duplicados.")
        valid_ids = set(range(len(chunk.segments)))
        unexpected = set(candidate_ids) - valid_ids
        if unexpected:
            raise ValueError(
                "candidate_ignored_segment_ids contiene IDs inexistentes: "
                + ", ".join(str(item) for item in sorted(unexpected))
                + "."
            )

        template = self.template_file.read_text(encoding="utf-8")
        if template.count(self.SEGMENTS_PLACEHOLDER) != 1:
            raise ValueError(
                "La plantilla debe contener exactamente un marcador "
                + self.SEGMENTS_PLACEHOLDER
                + "."
            )

        candidate_set = set(candidate_ids)
        payload = {
            "candidate_segment_ids": candidate_ids,
            "segments": [
                {"segment_id": index, "text": segment.text}
                for index, segment in enumerate(chunk.segments)
                if index in candidate_set
            ],
        }
        content = template.replace(
            self.SEGMENTS_PLACEHOLDER,
            json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        )
        return Prompt(content=content, version=self.DEFAULT_CONTRACT)
