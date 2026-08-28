"""
chunk_classification_parser.py

Convierte la salida JSON de clasificación de un TranscriptChunk
en ChunkClassification.
"""

import json
from json import JSONDecodeError

from models.chunk_classification import (
    ChunkClassification,
    ChunkKnowledgeKind,
    ClassifiedKnowledgeItem,
)
from models.transcript_chunk import TranscriptChunk


class ChunkClassificationParser:
    """
    Parser estricto de la primera etapa de extracción.

    El LLM solo controla kind, description y segment_ids.
    La procedencia del chunk es propiedad del sistema.
    """

    ROOT_FIELDS = {
        "items",
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
    ) -> ChunkClassification:
        if not isinstance(
            chunk,
            TranscriptChunk,
        ):
            raise TypeError(
                "chunk debe ser una instancia de TranscriptChunk."
            )

        clean_response = self._clean_json_response(
            response
        )
        data = self._load_json(
            clean_response
        )

        self._validate_root_object(
            data
        )
        self._require_exact_fields(
            field_name="root",
            item=data,
            required_fields=self.ROOT_FIELDS,
        )

        items = self._parse_items(
            values=data["items"],
            chunk=chunk,
        )

        return ChunkClassification(
            chunk_index=chunk.index,
            start=chunk.start,
            end=chunk.end,
            items=items,
        )

    def _parse_items(
        self,
        values,
        chunk: TranscriptChunk,
    ) -> list[ClassifiedKnowledgeItem]:
        if not isinstance(
            values,
            list,
        ):
            raise TypeError(
                "El campo items debe ser una lista."
            )

        parsed_items: list[ClassifiedKnowledgeItem] = []

        for index, value in enumerate(
            values,
            start=1,
        ):
            if not isinstance(
                value,
                dict,
            ):
                raise TypeError(
                    "El campo items elemento "
                    f"#{index} debe ser un objeto."
                )

            self._require_exact_fields(
                field_name=f"items elemento #{index}",
                item=value,
                required_fields=self.ITEM_FIELDS,
            )

            kind = self._parse_kind(
                value=value["kind"],
                item_index=index,
            )
            description = self._parse_description(
                value=value["description"],
                item_index=index,
            )
            segment_ids = self._parse_segment_ids(
                values=value["segment_ids"],
                item_index=index,
                chunk=chunk,
            )

            parsed_items.append(
                ClassifiedKnowledgeItem(
                    kind=kind,
                    description=description,
                    segment_ids=segment_ids,
                )
            )

        return parsed_items

    @staticmethod
    def _parse_kind(
        value,
        item_index: int,
    ) -> ChunkKnowledgeKind:
        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                "El campo items elemento "
                f"#{item_index} kind debe ser una cadena."
            )

        try:
            return ChunkKnowledgeKind.from_value(
                value
            )
        except ValueError as ex:
            raise ValueError(
                "El campo items elemento "
                f"#{item_index} kind no contiene un valor válido."
            ) from ex

    @staticmethod
    def _parse_description(
        value,
        item_index: int,
    ) -> str:
        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                "El campo items elemento "
                f"#{item_index} description debe ser una cadena."
            )

        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError(
                "El campo items elemento "
                f"#{item_index} description no puede estar vacío."
            )

        return normalized_value

    @staticmethod
    def _parse_segment_ids(
        values,
        item_index: int,
        chunk: TranscriptChunk,
    ) -> list[int]:
        if not isinstance(
            values,
            list,
        ):
            raise TypeError(
                "El campo items elemento "
                f"#{item_index} segment_ids debe ser una lista."
            )

        if not values:
            raise ValueError(
                "El campo items elemento "
                f"#{item_index} requiere al menos un segment_id."
            )

        parsed_ids: list[int] = []
        seen_ids: set[int] = set()
        maximum_id = len(
            chunk.segments
        ) - 1

        for segment_index, segment_id in enumerate(
            values,
            start=1,
        ):
            if (
                not isinstance(
                    segment_id,
                    int,
                )
                or isinstance(
                    segment_id,
                    bool,
                )
            ):
                raise TypeError(
                    "El campo items elemento "
                    f"#{item_index} segment_ids elemento "
                    f"#{segment_index} debe ser entero."
                )

            if (
                segment_id < 0
                or segment_id > maximum_id
            ):
                raise ValueError(
                    "El campo items elemento "
                    f"#{item_index} segment_ids elemento "
                    f"#{segment_index} referencia un segmento "
                    "inexistente del chunk."
                )

            if segment_id in seen_ids:
                raise ValueError(
                    "El campo items elemento "
                    f"#{item_index} segment_ids no puede contener "
                    "valores duplicados."
                )

            seen_ids.add(
                segment_id
            )
            parsed_ids.append(
                segment_id
            )

        return parsed_ids

    @staticmethod
    def _load_json(
        clean_response: str,
    ) -> dict:
        try:
            return json.loads(
                clean_response
            )
        except JSONDecodeError as ex:
            raise ValueError(
                "La respuesta de ChunkClassification no contiene "
                f"JSON válido. Detalle: {ex}"
            ) from ex

    @staticmethod
    def _validate_root_object(
        data,
    ) -> None:
        if not isinstance(
            data,
            dict,
        ):
            raise TypeError(
                "La respuesta de ChunkClassification debe "
                "contener un objeto JSON."
            )

    @staticmethod
    def _require_exact_fields(
        field_name: str,
        item: dict,
        required_fields: set[str],
    ) -> None:
        actual_fields = set(
            item.keys()
        )

        missing_fields = required_fields.difference(
            actual_fields
        )

        if missing_fields:
            raise ValueError(
                f"El campo {field_name} no contiene los campos "
                "requeridos: "
                + ", ".join(
                    sorted(
                        missing_fields
                    )
                )
            )

        unexpected_fields = actual_fields.difference(
            required_fields
        )

        if unexpected_fields:
            raise ValueError(
                f"El campo {field_name} contiene campos no "
                "soportados: "
                + ", ".join(
                    sorted(
                        unexpected_fields
                    )
                )
            )

    @staticmethod
    def _clean_json_response(
        response: str,
    ) -> str:
        if not isinstance(
            response,
            str,
        ):
            raise TypeError(
                "response debe ser una cadena."
            )

        clean_response = response.strip()

        if not clean_response:
            raise ValueError(
                "La respuesta de ChunkClassification está vacía."
            )

        first_brace = clean_response.find(
            "{"
        )
        last_brace = clean_response.rfind(
            "}"
        )

        if (
            first_brace == -1
            or last_brace == -1
            or last_brace < first_brace
        ):
            raise ValueError(
                "La respuesta de ChunkClassification no contiene "
                "un objeto JSON."
            )

        return clean_response[
            first_brace:
            last_brace + 1
        ]
