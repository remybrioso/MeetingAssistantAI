"""
chunk_action_metadata_parser.py

Convierte una respuesta JSON batch de metadatos de acciones
en ChunkActionMetadata.
"""

import json
from datetime import date
from json import JSONDecodeError

from models.chunk_action_metadata import (
    ActionMetadataEntry,
    ChunkActionMetadata,
)
from models.chunk_classification import (
    ChunkClassification,
    ChunkKnowledgeKind,
)
from models.meeting_report import (
    ActionOwner,
    ActionStatus,
)
from models.transcript_chunk import TranscriptChunk


class ChunkActionMetadataParser:
    """
    Parser estricto de la segunda etapa.

    La respuesta debe contener exactamente una entrada por cada
    acción de ChunkClassification y ninguna entrada adicional.
    """

    ROOT_FIELDS = {
        "actions",
    }

    ACTION_FIELDS = {
        "item_index",
        "owner",
        "due_date",
        "status",
    }

    def parse(
        self,
        response: str,
        classification: ChunkClassification,
        chunk: TranscriptChunk,
    ) -> ChunkActionMetadata:
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

        expected_indices = self._action_item_indices(
            classification
        )

        entries = self._parse_actions(
            values=data["actions"],
            classification=classification,
            chunk=chunk,
            expected_indices=expected_indices,
        )

        returned_indices = {
            entry.classification_item_index
            for entry in entries
        }

        if returned_indices != expected_indices:
            missing_indices = (
                expected_indices
                - returned_indices
            )

            if missing_indices:
                raise ValueError(
                    "La respuesta de metadatos de acciones no "
                    "contiene todas las acciones requeridas. "
                    "Faltan item_index: "
                    + ", ".join(
                        str(value)
                        for value in sorted(
                            missing_indices
                        )
                    )
                )

            unexpected_indices = (
                returned_indices
                - expected_indices
            )

            raise ValueError(
                "La respuesta de metadatos de acciones contiene "
                "item_index inesperados: "
                + ", ".join(
                    str(value)
                    for value in sorted(
                        unexpected_indices
                    )
                )
            )

        return ChunkActionMetadata(
            chunk_index=chunk.index,
            entries=entries,
        )

    def _parse_actions(
        self,
        values,
        classification: ChunkClassification,
        chunk: TranscriptChunk,
        expected_indices: set[int],
    ) -> list[ActionMetadataEntry]:
        if not isinstance(
            values,
            list,
        ):
            raise TypeError(
                "El campo actions debe ser una lista."
            )

        entries: list[ActionMetadataEntry] = []
        seen_indices: set[int] = set()

        for action_index, value in enumerate(
            values,
            start=1,
        ):
            if not isinstance(
                value,
                dict,
            ):
                raise TypeError(
                    "El campo actions elemento "
                    f"#{action_index} debe ser un objeto."
                )

            self._require_exact_fields(
                field_name=(
                    f"actions elemento #{action_index}"
                ),
                item=value,
                required_fields=self.ACTION_FIELDS,
            )

            item_index = self._parse_item_index(
                value=value["item_index"],
                action_index=action_index,
                classification=classification,
                expected_indices=expected_indices,
            )

            if item_index in seen_indices:
                raise ValueError(
                    "El campo actions no puede contener "
                    f"item_index duplicado: {item_index}."
                )

            seen_indices.add(
                item_index
            )

            source_item = classification.items[
                item_index
            ]

            owner = self._parse_owner(
                value=value["owner"],
                action_index=action_index,
                source_item=source_item,
                chunk=chunk,
            )
            due_date = self._parse_due_date(
                value=value["due_date"],
                action_index=action_index,
            )
            status = self._parse_status(
                value=value["status"],
                action_index=action_index,
            )

            entries.append(
                ActionMetadataEntry(
                    classification_item_index=item_index,
                    owner=owner,
                    due_date=due_date,
                    status=status,
                )
            )

        return entries

    @staticmethod
    def _parse_item_index(
        value,
        action_index: int,
        classification: ChunkClassification,
        expected_indices: set[int],
    ) -> int:
        if (
            not isinstance(
                value,
                int,
            )
            or isinstance(
                value,
                bool,
            )
        ):
            raise TypeError(
                "El campo actions elemento "
                f"#{action_index} item_index debe ser entero."
            )

        if (
            value < 0
            or value >= len(
                classification.items
            )
        ):
            raise ValueError(
                "El campo actions elemento "
                f"#{action_index} item_index referencia un item "
                "inexistente de ChunkClassification."
            )

        if value not in expected_indices:
            raise ValueError(
                "El campo actions elemento "
                f"#{action_index} item_index no referencia una "
                "acción clasificada."
            )

        return value

    def _parse_owner(
        self,
        value,
        action_index: int,
        source_item,
        chunk: TranscriptChunk,
    ) -> ActionOwner | None:
        if value is None:
            return None

        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                "El campo actions elemento "
                f"#{action_index} owner debe ser una cadena "
                "o null."
            )

        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError(
                "El campo actions elemento "
                f"#{action_index} owner no puede estar vacío."
            )

        if not self._owner_is_grounded(
            owner=normalized_value,
            segment_ids=source_item.segment_ids,
            chunk=chunk,
        ):
            raise ValueError(
                "El campo actions elemento "
                f"#{action_index} owner no aparece de forma "
                "literal en los segmentos que respaldan la acción."
            )

        return ActionOwner(
            display_name=normalized_value
        )

    @staticmethod
    def _owner_is_grounded(
        owner: str,
        segment_ids: list[int],
        chunk: TranscriptChunk,
    ) -> bool:
        normalized_owner = (
            " ".join(
                owner.split()
            )
            .casefold()
        )

        for segment_id in segment_ids:
            if (
                segment_id < 0
                or segment_id >= len(
                    chunk.segments
                )
            ):
                raise ValueError(
                    "La clasificación contiene un segment_id "
                    "inexistente del chunk."
                )

            normalized_text = (
                " ".join(
                    chunk.segments[
                        segment_id
                    ].text.split()
                )
                .casefold()
            )

            if normalized_owner in normalized_text:
                return True

        return False

    @staticmethod
    def _parse_due_date(
        value,
        action_index: int,
    ) -> date | None:
        if value is None:
            return None

        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                "El campo actions elemento "
                f"#{action_index} due_date debe ser una cadena "
                "ISO o null."
            )

        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError(
                "El campo actions elemento "
                f"#{action_index} due_date no puede estar vacío."
            )

        try:
            return date.fromisoformat(
                normalized_value
            )
        except ValueError as ex:
            raise ValueError(
                "El campo actions elemento "
                f"#{action_index} due_date debe usar formato "
                "YYYY-MM-DD."
            ) from ex

    @staticmethod
    def _parse_status(
        value,
        action_index: int,
    ) -> ActionStatus:
        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                "El campo actions elemento "
                f"#{action_index} status debe ser una cadena."
            )

        try:
            return ActionStatus.from_value(
                value
            )
        except (
            TypeError,
            ValueError,
        ) as ex:
            raise ValueError(
                "El campo actions elemento "
                f"#{action_index} status no contiene un estado "
                "válido."
            ) from ex

    @staticmethod
    def _action_item_indices(
        classification: ChunkClassification,
    ) -> set[int]:
        return {
            index
            for index, item in enumerate(
                classification.items
            )
            if (
                item.kind
                is ChunkKnowledgeKind.ACTION
            )
        }

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
                "La respuesta de ChunkActionMetadata no contiene "
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
                "La respuesta de ChunkActionMetadata debe "
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
                "La respuesta de ChunkActionMetadata está vacía."
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
                "La respuesta de ChunkActionMetadata no contiene "
                "un objeto JSON."
            )

        return clean_response[
            first_brace:
            last_brace + 1
        ]
