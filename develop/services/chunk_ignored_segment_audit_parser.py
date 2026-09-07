"""Parser estricto de la auditoría semántica de segmentos ignorados."""

import json
from dataclasses import dataclass
from json import JSONDecodeError

from models.chunk_classification import (
    ClassifiedKnowledgeItem,
    ChunkKnowledgeKind,
)
from models.transcript_chunk import TranscriptChunk
from services.chunk_classification_parser import ChunkClassificationParser


@dataclass(frozen=True, slots=True)
class ChunkIgnoredSegmentAuditResult:
    recovered_items: tuple[ClassifiedKnowledgeItem, ...]
    confirmed_ignored_segment_ids: tuple[int, ...]


class ChunkIgnoredSegmentAuditParser:
    ROOT_FIELDS = {
        "items",
        "confirmed_ignored_segment_ids",
    }

    ITEM_FIELDS = {
        "kind",
        "description",
        "segment_ids",
    }

    def parse(
        self,
        response: str,
        chunk: TranscriptChunk,
        candidate_ids,
    ) -> ChunkIgnoredSegmentAuditResult:
        if not isinstance(chunk, TranscriptChunk):
            raise TypeError("chunk debe ser una instancia de TranscriptChunk.")

        candidates = self._normalize_candidate_ids(candidate_ids, chunk)
        data = self._load_json(self._clean_json_response(response))
        if not isinstance(data, dict):
            raise TypeError("La respuesta de auditoría debe contener un objeto JSON.")
        self._require_exact_fields(data, "root", self.ROOT_FIELDS)

        values = data["items"]
        if not isinstance(values, list):
            raise TypeError("El campo items debe ser una lista.")

        recovered_items = []
        recovered_ids: set[int] = set()
        for index, value in enumerate(values, start=1):
            if not isinstance(value, dict):
                raise TypeError(f"El campo items elemento #{index} debe ser un objeto.")
            self._require_exact_fields(value, f"items elemento #{index}", self.ITEM_FIELDS)
            kind = ChunkClassificationParser._parse_kind(value["kind"], index)
            description = ChunkClassificationParser._parse_description(
                value["description"], index
            )
            segment_ids = ChunkClassificationParser._parse_segment_ids(
                value["segment_ids"], index, chunk
            )
            unexpected = set(segment_ids) - candidates
            if unexpected:
                raise ValueError(
                    "La auditoría referencia IDs que no fueron enviados como "
                    "candidatos: " + ", ".join(str(item) for item in sorted(unexpected)) + "."
                )
            recovered_ids.update(segment_ids)
            recovered_items.append(
                ClassifiedKnowledgeItem(
                    kind=kind,
                    description=description,
                    segment_ids=segment_ids,
                )
            )

        confirmed = self._parse_confirmed_ids(
            data["confirmed_ignored_segment_ids"], candidates
        )
        confirmed_ids = set(confirmed)
        overlap = recovered_ids & confirmed_ids
        if overlap:
            raise ValueError(
                "La auditoría no puede recuperar y confirmar como ignorado "
                "el mismo ID: "
                + ", ".join(str(item) for item in sorted(overlap))
                + "."
            )

        accounted = recovered_ids | confirmed_ids
        missing = candidates - accounted
        if missing:
            raise ValueError(
                "La auditoría requiere cobertura completa de los candidatos; "
                "faltan IDs: "
                + ", ".join(str(item) for item in sorted(missing))
                + "."
            )

        return ChunkIgnoredSegmentAuditResult(
            recovered_items=tuple(recovered_items),
            confirmed_ignored_segment_ids=tuple(confirmed),
        )

    @staticmethod
    def _normalize_candidate_ids(candidate_ids, chunk: TranscriptChunk) -> set[int]:
        if not isinstance(candidate_ids, (list, tuple, set, frozenset)):
            raise TypeError("candidate_ids debe ser una colección de enteros.")
        normalized = list(candidate_ids)
        if any(
            not isinstance(value, int) or isinstance(value, bool)
            for value in normalized
        ):
            raise TypeError("candidate_ids debe contener únicamente enteros.")
        if len(set(normalized)) != len(normalized):
            raise ValueError("candidate_ids no puede contener duplicados.")
        valid_ids = set(range(len(chunk.segments)))
        unexpected = set(normalized) - valid_ids
        if unexpected:
            raise ValueError(
                "candidate_ids contiene segmentos inexistentes: "
                + ", ".join(str(item) for item in sorted(unexpected))
                + "."
            )
        return set(normalized)

    @staticmethod
    def _parse_confirmed_ids(values, candidates: set[int]) -> list[int]:
        if not isinstance(values, list):
            raise TypeError("El campo confirmed_ignored_segment_ids debe ser una lista.")
        parsed = []
        seen = set()
        for index, value in enumerate(values, start=1):
            if not isinstance(value, int) or isinstance(value, bool):
                raise TypeError(
                    "El campo confirmed_ignored_segment_ids elemento "
                    f"#{index} debe ser entero."
                )
            if value in seen:
                raise ValueError(
                    "El campo confirmed_ignored_segment_ids no puede contener "
                    "valores duplicados."
                )
            if value not in candidates:
                raise ValueError(
                    "La auditoría referencia IDs que no fueron enviados como "
                    "candidatos: "
                    f"{value}."
                )
            seen.add(value)
            parsed.append(value)
        return parsed

    @staticmethod
    def _clean_json_response(response: str) -> str:
        if not isinstance(response, str):
            raise TypeError("response debe ser una cadena.")
        clean = response.strip()
        first = clean.find("{")
        last = clean.rfind("}")
        if not clean or first < 0 or last < first:
            raise ValueError("La respuesta de auditoría no contiene un objeto JSON.")
        return clean[first:last + 1]

    @staticmethod
    def _load_json(response: str) -> dict:
        try:
            return json.loads(response)
        except JSONDecodeError as error:
            raise ValueError(
                "La respuesta de auditoría no contiene JSON válido. "
                f"Detalle: {error}"
            ) from error

    @staticmethod
    def _require_exact_fields(item: dict, field_name: str, required_fields: set[str]) -> None:
        actual = set(item)
        missing = required_fields - actual
        if missing:
            raise ValueError(
                f"El campo {field_name} no contiene los campos requeridos: "
                + ", ".join(sorted(missing))
            )
        unexpected = actual - required_fields
        if unexpected:
            raise ValueError(
                f"El campo {field_name} contiene campos no soportados: "
                + ", ".join(sorted(unexpected))
            )
