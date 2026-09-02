"""
meeting_report_narrative_parser.py

Convierte la respuesta JSON de la etapa global G2 en
MeetingReportNarrative y valida sus referencias contra G1.
"""

import json
import re
import unicodedata
from json import JSONDecodeError

from models.meeting_report_narrative import (
    GroundedNarrativeText,
    MeetingReportNarrative,
)
from models.meeting_semantic_consolidation import (
    MeetingSemanticConsolidation,
)


class MeetingReportNarrativeParser:
    """
    Parser estricto de G2.

    Valida:
    - campos exactos;
    - referencias a item_id existentes;
    - referencias sin duplicados;
    - title específico mediante grounding léxico contra sus fuentes;
    - objective opcional.
    """

    ROOT_FIELDS = {
        "title",
        "objective",
        "executive_summary",
        "key_points",
    }

    GROUNDED_TEXT_FIELDS = {
        "text",
        "source_item_ids",
    }

    GENERIC_TITLE_TOKENS = {
        "acta",
        "global",
        "informe",
        "meeting",
        "minuta",
        "notes",
        "presentacion",
        "reunion",
        "report",
        "resumen",
        "seguimiento",
        "summary",
    }

    STOPWORDS = {
        "a",
        "al",
        "and",
        "con",
        "de",
        "del",
        "el",
        "en",
        "for",
        "la",
        "las",
        "los",
        "of",
        "para",
        "por",
        "the",
        "y",
    }

    def parse(
        self,
        response: str,
        semantic_consolidation: MeetingSemanticConsolidation,
    ) -> MeetingReportNarrative:
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
                "suficientes para validar narrativa."
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

        title = self._parse_grounded_text(
            value=data["title"],
            field_name="title",
            semantic_consolidation=(
                semantic_consolidation
            ),
        )

        self._validate_specific_title(
            title=title,
            semantic_consolidation=(
                semantic_consolidation
            ),
        )

        objective = (
            self._parse_optional_grounded_text(
                value=data["objective"],
                field_name="objective",
                semantic_consolidation=(
                    semantic_consolidation
                ),
            )
        )

        executive_summary = (
            self._parse_grounded_text(
                value=data[
                    "executive_summary"
                ],
                field_name=(
                    "executive_summary"
                ),
                semantic_consolidation=(
                    semantic_consolidation
                ),
            )
        )

        key_points = self._parse_key_points(
            values=data["key_points"],
            semantic_consolidation=(
                semantic_consolidation
            ),
        )

        return MeetingReportNarrative(
            title=title,
            objective=objective,
            executive_summary=(
                executive_summary
            ),
            key_points=key_points,
        )

    def _parse_optional_grounded_text(
        self,
        value,
        field_name: str,
        semantic_consolidation: MeetingSemanticConsolidation,
    ) -> GroundedNarrativeText | None:
        if value is None:
            return None

        return self._parse_grounded_text(
            value=value,
            field_name=field_name,
            semantic_consolidation=(
                semantic_consolidation
            ),
        )

    def _parse_grounded_text(
        self,
        value,
        field_name: str,
        semantic_consolidation: MeetingSemanticConsolidation,
    ) -> GroundedNarrativeText:
        if not isinstance(
            value,
            dict,
        ):
            raise TypeError(
                f"El campo {field_name} debe ser un objeto."
            )

        self._require_exact_fields(
            field_name=field_name,
            item=value,
            required_fields=(
                self.GROUNDED_TEXT_FIELDS
            ),
        )

        text = value["text"]

        if not isinstance(
            text,
            str,
        ):
            raise TypeError(
                f"El campo {field_name} text debe ser una cadena."
            )

        normalized_text = text.strip()

        if not normalized_text:
            raise ValueError(
                f"El campo {field_name} text no puede estar vacío."
            )

        source_item_ids = (
            self._parse_source_item_ids(
                values=value[
                    "source_item_ids"
                ],
                field_name=field_name,
                semantic_consolidation=(
                    semantic_consolidation
                ),
            )
        )

        return GroundedNarrativeText(
            text=normalized_text,
            source_item_ids=(
                source_item_ids
            ),
        )

    def _parse_source_item_ids(
        self,
        values,
        field_name: str,
        semantic_consolidation: MeetingSemanticConsolidation,
    ) -> list[int]:
        if not isinstance(
            values,
            list,
        ):
            raise TypeError(
                f"El campo {field_name} source_item_ids "
                "debe ser una lista."
            )

        if not values:
            raise ValueError(
                f"El campo {field_name} requiere al menos "
                "un source_item_id."
            )

        parsed_ids: list[int] = []
        seen_ids: set[int] = set()

        maximum_id = (
            len(
                semantic_consolidation.items
            )
            - 1
        )

        for index, source_item_id in enumerate(
            values,
            start=1,
        ):
            if (
                not isinstance(
                    source_item_id,
                    int,
                )
                or isinstance(
                    source_item_id,
                    bool,
                )
            ):
                raise TypeError(
                    f"El campo {field_name} source_item_ids "
                    f"elemento #{index} debe ser entero."
                )

            if (
                source_item_id < 0
                or source_item_id > maximum_id
            ):
                raise ValueError(
                    f"El campo {field_name} source_item_ids "
                    f"elemento #{index} referencia un "
                    "item semántico inexistente."
                )

            if source_item_id in seen_ids:
                raise ValueError(
                    f"El campo {field_name} source_item_ids "
                    "no puede contener valores duplicados."
                )

            seen_ids.add(
                source_item_id
            )
            parsed_ids.append(
                source_item_id
            )

        return parsed_ids

    def _parse_key_points(
        self,
        values,
        semantic_consolidation: MeetingSemanticConsolidation,
    ) -> list[
        GroundedNarrativeText
    ]:
        if not isinstance(
            values,
            list,
        ):
            raise TypeError(
                "El campo key_points debe ser una lista."
            )

        if not values:
            raise ValueError(
                "El campo key_points debe contener al menos "
                "un elemento."
            )

        if len(values) > 20:
            raise ValueError(
                "El campo key_points no puede contener más "
                "de 20 elementos."
            )

        parsed: list[
            GroundedNarrativeText
        ] = []

        seen_texts: set[str] = set()

        for index, value in enumerate(
            values,
            start=1,
        ):
            item = self._parse_grounded_text(
                value=value,
                field_name=(
                    f"key_points elemento #{index}"
                ),
                semantic_consolidation=(
                    semantic_consolidation
                ),
            )

            normalized_key = " ".join(
                item.text.casefold().split()
            )

            if normalized_key in seen_texts:
                raise ValueError(
                    "El campo key_points contiene "
                    "textos duplicados."
                )

            seen_texts.add(
                normalized_key
            )
            parsed.append(
                item
            )

        return parsed

    def _validate_specific_title(
        self,
        title: GroundedNarrativeText,
        semantic_consolidation: MeetingSemanticConsolidation,
    ) -> None:
        title_tokens = (
            self._content_tokens(
                title.text
            )
        )

        if not title_tokens:
            raise ValueError(
                "El campo title es demasiado genérico; "
                "debe identificar el asunto real de la reunión."
            )

        source_tokens: set[str] = set()

        for source_item_id in (
            title.source_item_ids
        ):
            source_item = (
                semantic_consolidation.items[
                    source_item_id
                ]
            )

            source_tokens.update(
                self._content_tokens(
                    source_item.description
                )
            )

        if not (
            title_tokens
            & source_tokens
        ):
            raise ValueError(
                "El campo title no contiene grounding "
                "temático suficiente respecto de sus "
                "source_item_ids."
            )

    @classmethod
    def _content_tokens(
        cls,
        value: str,
    ) -> set[str]:
        normalized = unicodedata.normalize(
            "NFKD",
            value.casefold(),
        )

        without_accents = "".join(
            character
            for character in normalized
            if not unicodedata.combining(
                character
            )
        )

        tokens = set(
            re.findall(
                r"[a-z0-9]+",
                without_accents,
            )
        )

        return {
            token
            for token in tokens
            if (
                len(token) >= 4
                and token
                not in cls.STOPWORDS
                and token
                not in cls.GENERIC_TITLE_TOKENS
            )
        }

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
                "La respuesta de MeetingReportNarrative "
                "no contiene JSON válido. "
                f"Detalle: {ex}"
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
                "La respuesta de MeetingReportNarrative "
                "debe contener un objeto JSON."
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
                f"El campo {field_name} no contiene los "
                "campos requeridos: "
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
                f"El campo {field_name} contiene campos "
                "no soportados: "
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
                "La respuesta de MeetingReportNarrative "
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
                "La respuesta de MeetingReportNarrative "
                "no contiene un objeto JSON."
            )

        return clean_response[
            first_brace:
            last_brace + 1
        ]
