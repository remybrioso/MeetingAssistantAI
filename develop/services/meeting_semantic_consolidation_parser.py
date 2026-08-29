"""
meeting_semantic_consolidation_parser.py

Convierte la respuesta JSON de la etapa global G1 en
MeetingSemanticConsolidation y valida cobertura exacta contra
MeetingKnowledge.
"""

import json
from json import JSONDecodeError

from models.chunk_classification import (
    ChunkKnowledgeKind,
)
from models.meeting_knowledge import MeetingKnowledge
from models.meeting_semantic_consolidation import (
    ConsolidatedMeetingKnowledgeItem,
    MeetingKnowledgeItemReference,
    MeetingSemanticConsolidation,
)


class MeetingSemanticConsolidationParser:
    """
    Parser estricto de la consolidación semántica global.

    Garantiza:
    - campos exactos;
    - referencias existentes;
    - misma categoría semántica;
    - ninguna referencia duplicada;
    - cobertura del 100 % de los items fuente exactamente una vez.
    """

    ROOT_FIELDS = {
        "items",
    }

    ITEM_FIELDS = {
        "kind",
        "description",
        "source_refs",
    }

    REFERENCE_FIELDS = {
        "chunk_index",
        "item_index",
    }

    KIND_TO_SECTION = {
        ChunkKnowledgeKind.TOPIC: (
            "topics"
        ),
        ChunkKnowledgeKind.DECISION: (
            "decisions"
        ),
        ChunkKnowledgeKind.ACTION: (
            "action_items"
        ),
        ChunkKnowledgeKind.RISK: (
            "risks"
        ),
        ChunkKnowledgeKind.PENDING: (
            "pending_items"
        ),
    }

    def parse(
        self,
        response: str,
        meeting_knowledge: MeetingKnowledge,
    ) -> MeetingSemanticConsolidation:
        if not isinstance(
            meeting_knowledge,
            MeetingKnowledge,
        ):
            raise TypeError(
                "meeting_knowledge debe ser una instancia "
                "de MeetingKnowledge."
            )

        clean_response = (
            self._clean_json_response(
                response
            )
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
            required_fields=(
                self.ROOT_FIELDS
            ),
        )

        items = self._parse_items(
            values=data["items"],
            meeting_knowledge=meeting_knowledge,
        )

        self._validate_exact_coverage(
            items=items,
            meeting_knowledge=meeting_knowledge,
        )

        return MeetingSemanticConsolidation(
            items=items
        )

    def _parse_items(
        self,
        values,
        meeting_knowledge: MeetingKnowledge,
    ) -> list[
        ConsolidatedMeetingKnowledgeItem
    ]:
        if not isinstance(
            values,
            list,
        ):
            raise TypeError(
                "El campo items debe ser una lista."
            )

        parsed_items: list[
            ConsolidatedMeetingKnowledgeItem
        ] = []

        seen_source_keys: set[
            tuple[str, int, int]
        ] = set()

        for item_index, value in enumerate(
            values,
            start=1,
        ):
            if not isinstance(
                value,
                dict,
            ):
                raise TypeError(
                    "El campo items elemento "
                    f"#{item_index} debe ser un objeto."
                )

            self._require_exact_fields(
                field_name=(
                    f"items elemento #{item_index}"
                ),
                item=value,
                required_fields=(
                    self.ITEM_FIELDS
                ),
            )

            kind = self._parse_kind(
                value=value["kind"],
                item_index=item_index,
            )

            description = (
                self._parse_description(
                    value=value[
                        "description"
                    ],
                    item_index=item_index,
                )
            )

            source_refs = (
                self._parse_source_refs(
                    values=value[
                        "source_refs"
                    ],
                    kind=kind,
                    output_item_index=(
                        item_index
                    ),
                    meeting_knowledge=(
                        meeting_knowledge
                    ),
                    seen_source_keys=(
                        seen_source_keys
                    ),
                )
            )

            parsed_items.append(
                ConsolidatedMeetingKnowledgeItem(
                    kind=kind,
                    description=description,
                    source_refs=source_refs,
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
                f"#{item_index} kind no contiene "
                "un valor válido."
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
                f"#{item_index} description debe ser "
                "una cadena."
            )

        normalized_value = (
            value.strip()
        )

        if not normalized_value:
            raise ValueError(
                "El campo items elemento "
                f"#{item_index} description no puede "
                "estar vacío."
            )

        return normalized_value

    def _parse_source_refs(
        self,
        values,
        kind: ChunkKnowledgeKind,
        output_item_index: int,
        meeting_knowledge: MeetingKnowledge,
        seen_source_keys: set[
            tuple[str, int, int]
        ],
    ) -> list[
        MeetingKnowledgeItemReference
    ]:
        if not isinstance(
            values,
            list,
        ):
            raise TypeError(
                "El campo items elemento "
                f"#{output_item_index} source_refs "
                "debe ser una lista."
            )

        if not values:
            raise ValueError(
                "El campo items elemento "
                f"#{output_item_index} requiere "
                "al menos una source_ref."
            )

        parsed_refs: list[
            MeetingKnowledgeItemReference
        ] = []

        local_seen: set[
            tuple[int, int]
        ] = set()

        for ref_index, value in enumerate(
            values,
            start=1,
        ):
            if not isinstance(
                value,
                dict,
            ):
                raise TypeError(
                    "El campo items elemento "
                    f"#{output_item_index} source_refs "
                    f"elemento #{ref_index} debe ser "
                    "un objeto."
                )

            self._require_exact_fields(
                field_name=(
                    "items elemento "
                    f"#{output_item_index} source_refs "
                    f"elemento #{ref_index}"
                ),
                item=value,
                required_fields=(
                    self.REFERENCE_FIELDS
                ),
            )

            chunk_index = (
                self._parse_non_negative_int(
                    value=value[
                        "chunk_index"
                    ],
                    field_name=(
                        "items elemento "
                        f"#{output_item_index} "
                        "source_refs elemento "
                        f"#{ref_index} chunk_index"
                    ),
                )
            )

            item_index = (
                self._parse_non_negative_int(
                    value=value[
                        "item_index"
                    ],
                    field_name=(
                        "items elemento "
                        f"#{output_item_index} "
                        "source_refs elemento "
                        f"#{ref_index} item_index"
                    ),
                )
            )

            self._validate_reference_exists(
                kind=kind,
                chunk_index=chunk_index,
                item_index=item_index,
                meeting_knowledge=(
                    meeting_knowledge
                ),
                output_item_index=(
                    output_item_index
                ),
                ref_index=ref_index,
            )

            local_key = (
                chunk_index,
                item_index,
            )

            if local_key in local_seen:
                raise ValueError(
                    "El campo items elemento "
                    f"#{output_item_index} source_refs "
                    "no puede contener referencias "
                    "duplicadas."
                )

            local_seen.add(
                local_key
            )

            global_key = (
                kind.value,
                chunk_index,
                item_index,
            )

            if global_key in seen_source_keys:
                raise ValueError(
                    "La consolidación semántica no puede "
                    "reutilizar un item fuente en más de "
                    "un item consolidado. Referencia: "
                    f"{global_key}."
                )

            seen_source_keys.add(
                global_key
            )

            parsed_refs.append(
                MeetingKnowledgeItemReference(
                    chunk_index=chunk_index,
                    item_index=item_index,
                )
            )

        return parsed_refs

    def _validate_reference_exists(
        self,
        kind: ChunkKnowledgeKind,
        chunk_index: int,
        item_index: int,
        meeting_knowledge: MeetingKnowledge,
        output_item_index: int,
        ref_index: int,
    ) -> None:
        if (
            chunk_index
            >= len(
                meeting_knowledge.chunks
            )
        ):
            raise ValueError(
                "El campo items elemento "
                f"#{output_item_index} source_refs "
                f"elemento #{ref_index} referencia "
                "un chunk inexistente."
            )

        chunk = meeting_knowledge.chunks[
            chunk_index
        ]

        if (
            chunk.chunk_index
            != chunk_index
        ):
            raise ValueError(
                "MeetingKnowledge no conserva la "
                "cobertura contigua esperada."
            )

        section_name = (
            self.KIND_TO_SECTION[
                kind
            ]
        )

        source_items = getattr(
            chunk,
            section_name,
        )

        if item_index >= len(
            source_items
        ):
            raise ValueError(
                "El campo items elemento "
                f"#{output_item_index} source_refs "
                f"elemento #{ref_index} referencia "
                "un item fuente inexistente para "
                f"kind={kind.value}."
            )

    def _validate_exact_coverage(
        self,
        items: list[
            ConsolidatedMeetingKnowledgeItem
        ],
        meeting_knowledge: MeetingKnowledge,
    ) -> None:
        expected_keys = (
            self._build_expected_source_keys(
                meeting_knowledge
            )
        )

        actual_keys = {
            (
                item.kind.value,
                reference.chunk_index,
                reference.item_index,
            )
            for item in items
            for reference in item.source_refs
        }

        missing_keys = (
            expected_keys
            - actual_keys
        )

        if missing_keys:
            formatted = ", ".join(
                str(
                    key
                )
                for key in sorted(
                    missing_keys
                )
            )

            raise ValueError(
                "La consolidación semántica omitió "
                "items fuente obligatorios: "
                f"{formatted}."
            )

        unexpected_keys = (
            actual_keys
            - expected_keys
        )

        if unexpected_keys:
            formatted = ", ".join(
                str(
                    key
                )
                for key in sorted(
                    unexpected_keys
                )
            )

            raise ValueError(
                "La consolidación semántica contiene "
                "referencias fuente inesperadas: "
                f"{formatted}."
            )

    def _build_expected_source_keys(
        self,
        meeting_knowledge: MeetingKnowledge,
    ) -> set[
        tuple[str, int, int]
    ]:
        keys: set[
            tuple[str, int, int]
        ] = set()

        for chunk in meeting_knowledge.chunks:
            for (
                kind,
                section_name,
            ) in self.KIND_TO_SECTION.items():
                source_items = getattr(
                    chunk,
                    section_name,
                )

                for item_index in range(
                    len(
                        source_items
                    )
                ):
                    keys.add(
                        (
                            kind.value,
                            chunk.chunk_index,
                            item_index,
                        )
                    )

        return keys

    @staticmethod
    def _parse_non_negative_int(
        value,
        field_name: str,
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
                f"El campo {field_name} debe ser entero."
            )

        if value < 0:
            raise ValueError(
                f"El campo {field_name} no puede ser negativo."
            )

        return value

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
                "La respuesta de "
                "MeetingSemanticConsolidation no contiene "
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
                "La respuesta de "
                "MeetingSemanticConsolidation debe "
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

        missing_fields = (
            required_fields.difference(
                actual_fields
            )
        )

        if missing_fields:
            raise ValueError(
                f"El campo {field_name} no contiene "
                "los campos requeridos: "
                + ", ".join(
                    sorted(
                        missing_fields
                    )
                )
            )

        unexpected_fields = (
            actual_fields.difference(
                required_fields
            )
        )

        if unexpected_fields:
            raise ValueError(
                f"El campo {field_name} contiene "
                "campos no soportados: "
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

        clean_response = (
            response.strip()
        )

        if not clean_response:
            raise ValueError(
                "La respuesta de "
                "MeetingSemanticConsolidation "
                "está vacía."
            )

        first_brace = (
            clean_response.find(
                "{"
            )
        )

        last_brace = (
            clean_response.rfind(
                "}"
            )
        )

        if (
            first_brace == -1
            or last_brace == -1
            or last_brace < first_brace
        ):
            raise ValueError(
                "La respuesta de "
                "MeetingSemanticConsolidation no contiene "
                "un objeto JSON."
            )

        return clean_response[
            first_brace:
            last_brace + 1
        ]
