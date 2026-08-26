"""
chunk_knowledge_parser.py

Convierte una respuesta JSON de IA en ChunkKnowledge.
"""

import json
from datetime import date
from json import JSONDecodeError
from numbers import Real

from models.chunk_knowledge import ChunkKnowledge
from models.meeting_report import (
    ActionItem,
    ActionOwner,
    ActionStatus,
    Decision,
    EvidenceReference,
    MeetingRisk,
    MeetingTopic,
    Participant,
    PendingItem,
)
from models.transcript_chunk import TranscriptChunk


class ChunkKnowledgeParser:
    """
    Traduce la salida estructurada del proveedor a dominio.

    La procedencia del bloque nunca se acepta desde el LLM.
    chunk_index, start y end se toman exclusivamente del
    TranscriptChunk recibido.

    Las referencias de evidencia deben corresponder a contenido
    real del chunk: speaker, rango temporal y excerpt.
    """

    REQUIRED_FIELDS = {
        "key_points",
        "topics",
        "decisions",
        "action_items",
        "risks",
        "pending_items",
        "participants",
        "conclusions",
    }

    SUPPORTED_FIELDS = REQUIRED_FIELDS

    EVIDENCE_FIELDS = {
        "speaker",
        "start",
        "end",
        "excerpt",
    }

    def parse(
        self,
        response: str,
        chunk: TranscriptChunk,
    ) -> ChunkKnowledge:
        """
        Convierte JSON textual en ChunkKnowledge.

        Raises:
            TypeError:
                Si response, chunk o alguna sección utilizan
                tipos incompatibles con el contrato.

            ValueError:
                Si faltan campos, existe JSON inválido o la
                evidencia no está respaldada por el chunk.
        """

        if not isinstance(
            chunk,
            TranscriptChunk,
        ):
            raise TypeError(
                "chunk debe ser una instancia "
                "de TranscriptChunk."
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

        self._validate_root_fields(
            data
        )

        key_points = self._parse_text_collection(
            values=data["key_points"],
            field_name="key_points",
        )

        conclusions = self._parse_text_collection(
            values=data["conclusions"],
            field_name="conclusions",
        )

        topics = self._parse_topics(
            values=data["topics"],
            chunk=chunk,
        )

        decisions = self._parse_decisions(
            values=data["decisions"],
            chunk=chunk,
        )

        action_items = self._parse_action_items(
            values=data["action_items"],
            chunk=chunk,
        )

        risks = self._parse_risks(
            values=data["risks"],
            chunk=chunk,
        )

        pending_items = self._parse_pending_items(
            values=data["pending_items"],
            chunk=chunk,
        )

        participants = self._parse_participants(
            values=data["participants"],
        )

        return ChunkKnowledge(
            chunk_index=chunk.index,
            start=chunk.start,
            end=chunk.end,
            key_points=key_points,
            topics=topics,
            decisions=decisions,
            action_items=action_items,
            risks=risks,
            pending_items=pending_items,
            participants=participants,
            conclusions=conclusions,
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
                "La respuesta de ChunkKnowledge no "
                "contiene JSON válido. "
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
                "La respuesta de ChunkKnowledge debe "
                "contener un objeto JSON."
            )

    def _validate_root_fields(
        self,
        data: dict,
    ) -> None:
        missing_fields = (
            self.REQUIRED_FIELDS.difference(
                data.keys()
            )
        )

        if missing_fields:
            raise ValueError(
                "La respuesta de ChunkKnowledge no "
                "contiene los campos requeridos: "
                + ", ".join(
                    sorted(
                        missing_fields
                    )
                )
            )

        unexpected_fields = (
            set(
                data.keys()
            )
            .difference(
                self.SUPPORTED_FIELDS
            )
        )

        if unexpected_fields:
            raise ValueError(
                "La respuesta de ChunkKnowledge contiene "
                "campos no soportados: "
                + ", ".join(
                    sorted(
                        unexpected_fields
                    )
                )
            )

    def _parse_text_collection(
        self,
        values,
        field_name: str,
    ) -> list[str]:
        self._validate_list_field(
            field_name=field_name,
            values=values,
        )

        parsed_values: list[str] = []

        for index, value in enumerate(
            values,
            start=1,
        ):
            if not isinstance(
                value,
                str,
            ):
                raise TypeError(
                    f"El campo {field_name} elemento "
                    f"#{index} debe ser una cadena."
                )

            parsed_values.append(
                value
            )

        return parsed_values

    def _parse_topics(
        self,
        values,
        chunk: TranscriptChunk,
    ) -> list[MeetingTopic]:
        self._validate_list_field(
            field_name="topics",
            values=values,
        )

        topics: list[MeetingTopic] = []

        for index, value in enumerate(
            values,
            start=1,
        ):
            item = self._validate_object_item(
                field_name="topics",
                index=index,
                value=value,
            )

            self._require_exact_fields(
                field_name="topics",
                index=index,
                item=item,
                required_fields={
                    "title",
                    "summary",
                    "evidence",
                },
            )

            topics.append(
                MeetingTopic(
                    title=item["title"],
                    summary=item["summary"],
                    evidence=self._parse_evidence(
                        values=item["evidence"],
                        parent_field="topics",
                        parent_index=index,
                        chunk=chunk,
                    ),
                )
            )

        return topics

    def _parse_decisions(
        self,
        values,
        chunk: TranscriptChunk,
    ) -> list[Decision]:
        self._validate_list_field(
            field_name="decisions",
            values=values,
        )

        decisions: list[Decision] = []

        for index, value in enumerate(
            values,
            start=1,
        ):
            item = self._validate_object_item(
                field_name="decisions",
                index=index,
                value=value,
            )

            self._require_exact_fields(
                field_name="decisions",
                index=index,
                item=item,
                required_fields={
                    "description",
                    "rationale",
                    "evidence",
                },
            )

            decisions.append(
                Decision(
                    description=item["description"],
                    rationale=item["rationale"],
                    evidence=self._parse_evidence(
                        values=item["evidence"],
                        parent_field="decisions",
                        parent_index=index,
                        chunk=chunk,
                    ),
                )
            )

        return decisions

    def _parse_action_items(
        self,
        values,
        chunk: TranscriptChunk,
    ) -> list[ActionItem]:
        self._validate_list_field(
            field_name="action_items",
            values=values,
        )

        action_items: list[ActionItem] = []

        for index, value in enumerate(
            values,
            start=1,
        ):
            item = self._validate_object_item(
                field_name="action_items",
                index=index,
                value=value,
            )

            self._require_exact_fields(
                field_name="action_items",
                index=index,
                item=item,
                required_fields={
                    "description",
                    "owner",
                    "due_date",
                    "status",
                    "evidence",
                },
            )

            action_items.append(
                ActionItem(
                    description=item[
                        "description"
                    ],
                    owner=self._parse_action_owner(
                        value=item["owner"],
                        action_index=index,
                    ),
                    due_date=self._parse_due_date(
                        value=item["due_date"],
                        action_index=index,
                    ),
                    status=self._parse_action_status(
                        value=item["status"],
                        action_index=index,
                    ),
                    evidence=self._parse_evidence(
                        values=item["evidence"],
                        parent_field="action_items",
                        parent_index=index,
                        chunk=chunk,
                    ),
                )
            )

        return action_items

    def _parse_risks(
        self,
        values,
        chunk: TranscriptChunk,
    ) -> list[MeetingRisk]:
        self._validate_list_field(
            field_name="risks",
            values=values,
        )

        risks: list[MeetingRisk] = []

        for index, value in enumerate(
            values,
            start=1,
        ):
            item = self._validate_object_item(
                field_name="risks",
                index=index,
                value=value,
            )

            self._require_exact_fields(
                field_name="risks",
                index=index,
                item=item,
                required_fields={
                    "description",
                    "impact",
                    "evidence",
                },
            )

            risks.append(
                MeetingRisk(
                    description=item[
                        "description"
                    ],
                    impact=item["impact"],
                    evidence=self._parse_evidence(
                        values=item["evidence"],
                        parent_field="risks",
                        parent_index=index,
                        chunk=chunk,
                    ),
                )
            )

        return risks

    def _parse_pending_items(
        self,
        values,
        chunk: TranscriptChunk,
    ) -> list[PendingItem]:
        self._validate_list_field(
            field_name="pending_items",
            values=values,
        )

        pending_items: list[PendingItem] = []

        for index, value in enumerate(
            values,
            start=1,
        ):
            item = self._validate_object_item(
                field_name="pending_items",
                index=index,
                value=value,
            )

            self._require_exact_fields(
                field_name="pending_items",
                index=index,
                item=item,
                required_fields={
                    "description",
                    "evidence",
                },
            )

            pending_items.append(
                PendingItem(
                    description=item[
                        "description"
                    ],
                    evidence=self._parse_evidence(
                        values=item["evidence"],
                        parent_field="pending_items",
                        parent_index=index,
                        chunk=chunk,
                    ),
                )
            )

        return pending_items

    def _parse_participants(
        self,
        values,
    ) -> list[Participant]:
        self._validate_list_field(
            field_name="participants",
            values=values,
        )

        participants: list[Participant] = []

        for index, value in enumerate(
            values,
            start=1,
        ):
            item = self._validate_object_item(
                field_name="participants",
                index=index,
                value=value,
            )

            self._require_exact_fields(
                field_name="participants",
                index=index,
                item=item,
                required_fields={
                    "name",
                    "speaker",
                    "role",
                },
            )

            participants.append(
                Participant(
                    name=item["name"],
                    speaker=item["speaker"],
                    role=item["role"],
                )
            )

        return participants

    @staticmethod
    def _parse_action_owner(
        value,
        action_index: int,
    ) -> ActionOwner | None:
        if value is None:
            return None

        if not isinstance(
            value,
            dict,
        ):
            raise TypeError(
                "El campo action_items elemento "
                f"#{action_index} owner debe ser "
                "un objeto o null."
            )

        expected_fields = {
            "display_name",
        }

        actual_fields = set(
            value.keys()
        )

        if actual_fields != expected_fields:
            raise ValueError(
                "El campo action_items elemento "
                f"#{action_index} owner debe contener "
                "únicamente display_name."
            )

        return ActionOwner(
            display_name=value[
                "display_name"
            ]
        )

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
                "El campo action_items elemento "
                f"#{action_index} due_date debe ser "
                "una cadena ISO o null."
            )

        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError(
                "El campo action_items elemento "
                f"#{action_index} due_date no puede "
                "estar vacío."
            )

        try:
            return date.fromisoformat(
                normalized_value
            )
        except ValueError as ex:
            raise ValueError(
                "El campo action_items elemento "
                f"#{action_index} due_date no contiene "
                "una fecha ISO válida con formato "
                "YYYY-MM-DD."
            ) from ex

    @staticmethod
    def _parse_action_status(
        value,
        action_index: int,
    ) -> ActionStatus:
        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                "El campo action_items elemento "
                f"#{action_index} status debe ser "
                "una cadena."
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
                "El campo action_items elemento "
                f"#{action_index} status no contiene "
                "un estado válido."
            ) from ex

    def _parse_evidence(
        self,
        values,
        parent_field: str,
        parent_index: int,
        chunk: TranscriptChunk,
    ) -> list[EvidenceReference]:
        if not isinstance(
            values,
            list,
        ):
            raise TypeError(
                f"El campo {parent_field} elemento "
                f"#{parent_index} evidence debe ser "
                "una lista."
            )

        if not values:
            raise ValueError(
                f"El campo {parent_field} elemento "
                f"#{parent_index} requiere al menos "
                "una referencia de evidencia."
            )

        evidence_items: list[EvidenceReference] = []

        for evidence_index, value in enumerate(
            values,
            start=1,
        ):
            item = self._validate_object_item(
                field_name=(
                    f"{parent_field} elemento "
                    f"#{parent_index} evidence"
                ),
                index=evidence_index,
                value=value,
            )

            self._require_exact_fields(
                field_name=(
                    f"{parent_field} elemento "
                    f"#{parent_index} evidence"
                ),
                index=evidence_index,
                item=item,
                required_fields=self.EVIDENCE_FIELDS,
            )

            speaker = item["speaker"]
            start = item["start"]
            end = item["end"]
            excerpt = item["excerpt"]

            self._validate_evidence_types(
                parent_field=parent_field,
                parent_index=parent_index,
                evidence_index=evidence_index,
                speaker=speaker,
                start=start,
                end=end,
                excerpt=excerpt,
            )

            reference = EvidenceReference(
                speaker=speaker,
                start=float(
                    start
                ),
                end=float(
                    end
                ),
                excerpt=excerpt,
            )

            self._validate_evidence_grounding(
                reference=reference,
                chunk=chunk,
                parent_field=parent_field,
                parent_index=parent_index,
                evidence_index=evidence_index,
            )

            evidence_items.append(
                reference
            )

        return evidence_items

    @staticmethod
    def _validate_evidence_types(
        parent_field: str,
        parent_index: int,
        evidence_index: int,
        speaker,
        start,
        end,
        excerpt,
    ) -> None:
        location = (
            f"{parent_field} elemento "
            f"#{parent_index} evidence elemento "
            f"#{evidence_index}"
        )

        if not isinstance(
            speaker,
            str,
        ):
            raise TypeError(
                f"El campo {location} speaker "
                "debe ser una cadena."
            )

        if (
            not isinstance(
                start,
                Real,
            )
            or isinstance(
                start,
                bool,
            )
        ):
            raise TypeError(
                f"El campo {location} start "
                "debe ser numérico."
            )

        if (
            not isinstance(
                end,
                Real,
            )
            or isinstance(
                end,
                bool,
            )
        ):
            raise TypeError(
                f"El campo {location} end "
                "debe ser numérico."
            )

        if not isinstance(
            excerpt,
            str,
        ):
            raise TypeError(
                f"El campo {location} excerpt "
                "debe ser una cadena."
            )

    @classmethod
    def _validate_evidence_grounding(
        cls,
        reference: EvidenceReference,
        chunk: TranscriptChunk,
        parent_field: str,
        parent_index: int,
        evidence_index: int,
    ) -> None:
        grounded = any(
            cls._reference_matches_segment(
                reference=reference,
                segment=segment,
            )
            for segment in chunk.segments
        )

        if not grounded:
            raise ValueError(
                f"El campo {parent_field} elemento "
                f"#{parent_index} evidence elemento "
                f"#{evidence_index} no corresponde "
                "a evidencia verificable del chunk."
            )

    @classmethod
    def _reference_matches_segment(
        cls,
        reference: EvidenceReference,
        segment,
    ) -> bool:
        tolerance = 0.001

        same_speaker = (
            reference.speaker.strip().casefold()
            == segment.speaker.strip().casefold()
        )

        inside_time_range = (
            reference.start
            >= segment.start - tolerance
            and reference.end
            <= segment.end + tolerance
        )

        normalized_excerpt = cls._normalize_whitespace(
            reference.excerpt
        ).casefold()

        normalized_segment_text = cls._normalize_whitespace(
            segment.text
        ).casefold()

        excerpt_is_verbatim = (
            normalized_excerpt
            in normalized_segment_text
        )

        return (
            same_speaker
            and inside_time_range
            and excerpt_is_verbatim
        )

    @staticmethod
    def _normalize_whitespace(
        value: str,
    ) -> str:
        return " ".join(
            value.split()
        )

    @staticmethod
    def _validate_list_field(
        field_name: str,
        values,
    ) -> None:
        if not isinstance(
            values,
            list,
        ):
            raise TypeError(
                f"El campo {field_name} debe ser "
                "una lista."
            )

    @staticmethod
    def _validate_object_item(
        field_name: str,
        index: int,
        value,
    ) -> dict:
        if not isinstance(
            value,
            dict,
        ):
            raise TypeError(
                f"El campo {field_name} elemento "
                f"#{index} debe ser un objeto."
            )

        return value

    @staticmethod
    def _require_exact_fields(
        field_name: str,
        index: int,
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
                f"El campo {field_name} elemento "
                f"#{index} no contiene los campos "
                "requeridos: "
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
                f"El campo {field_name} elemento "
                f"#{index} contiene campos no "
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
                "La respuesta de ChunkKnowledge "
                "está vacía."
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
                "La respuesta de ChunkKnowledge no "
                "contiene un objeto JSON."
            )

        return clean_response[
            first_brace:
            last_brace + 1
        ]
