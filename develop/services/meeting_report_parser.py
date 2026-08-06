"""
meeting_report_parser.py

Convierte una respuesta JSON de IA en un MeetingReport.
"""

import json
from json import JSONDecodeError

from models.artifacts.meeting_report import MeetingReport
from models.meeting_report import (
    Decision,
    EvidenceReference,
    MeetingRisk,
    MeetingTopic,
    Participant,
    PendingItem,
)


class MeetingReportParser:
    """
    Convierte la respuesta textual de un proveedor de IA
    en un MeetingReport validado por el dominio.

    Esta versión soporta:

    - campos principales;
    - topics;
    - participants;
    - decisions;
    - risks;
    - pending_items;
    - evidence.

    ActionItem se incorporará en la siguiente tarea.
    """

    REQUIRED_FIELDS = {
        "title",
        "executive_summary",
        "key_points",
    }

    UNSUPPORTED_NESTED_FIELDS = {
        "action_items",
    }

    def parse(
        self,
        response: str,
        provider: str,
        model: str,
        prompt_version: str,
    ) -> MeetingReport:
        """
        Convierte una respuesta JSON en MeetingReport.

        Raises:
            ValueError:
                Si la respuesta está vacía, no contiene
                JSON válido, faltan campos obligatorios
                o contiene una sección aún no soportada.

            TypeError:
                Si la estructura JSON contiene tipos
                incompatibles con el contrato esperado.
        """

        clean_response = self._clean_json_response(
            response
        )

        data = self._load_json(
            clean_response
        )

        self._validate_root_object(
            data
        )

        self._validate_required_fields(
            data
        )

        self._validate_text_collections(
            data
        )

        self._validate_unsupported_nested_fields(
            data
        )

        topics = self._parse_topics(
            data.get(
                "topics",
                [],
            )
        )

        participants = self._parse_participants(
            data.get(
                "participants",
                [],
            )
        )

        decisions = self._parse_decisions(
            data.get(
                "decisions",
                [],
            )
        )

        risks = self._parse_risks(
            data.get(
                "risks",
                [],
            )
        )

        pending_items = self._parse_pending_items(
            data.get(
                "pending_items",
                [],
            )
        )

        return MeetingReport(
            artifact_type="meeting_report",
            provider=provider,
            model=model,
            prompt_version=prompt_version,
            title=data["title"],
            objective=data.get(
                "objective"
            ),
            executive_summary=data[
                "executive_summary"
            ],
            key_points=data["key_points"],
            topics=topics,
            decisions=decisions,
            action_items=[],
            risks=risks,
            pending_items=pending_items,
            participants=participants,
            conclusions=data.get(
                "conclusions",
                [],
            ),
        )

    @staticmethod
    def _load_json(
        clean_response: str,
    ):
        """
        Convierte el contenido JSON limpio en datos Python.
        """

        try:
            return json.loads(
                clean_response
            )

        except JSONDecodeError as ex:
            raise ValueError(
                "La respuesta de IA no contiene JSON "
                f"válido. Detalle: {ex}"
            ) from ex

    @staticmethod
    def _validate_root_object(
        data,
    ) -> None:
        """
        Verifica que la raíz del JSON sea un objeto.
        """

        if not isinstance(
            data,
            dict,
        ):
            raise TypeError(
                "La respuesta de MeetingReport debe "
                "contener un objeto JSON."
            )

    def _validate_required_fields(
        self,
        data: dict,
    ) -> None:
        """
        Verifica la presencia de los campos obligatorios.
        """

        missing_fields = (
            self.REQUIRED_FIELDS.difference(
                data.keys()
            )
        )

        if missing_fields:
            raise ValueError(
                "La respuesta de MeetingReport no contiene "
                "los campos requeridos: "
                + ", ".join(
                    sorted(
                        missing_fields
                    )
                )
            )

    @staticmethod
    def _validate_text_collections(
        data: dict,
    ) -> None:
        """
        Verifica las colecciones textuales principales.

        La validación del contenido individual pertenece
        al modelo MeetingReport.
        """

        if not isinstance(
            data["key_points"],
            list,
        ):
            raise TypeError(
                "El campo key_points debe ser una lista."
            )

        conclusions = data.get(
            "conclusions",
            [],
        )

        if not isinstance(
            conclusions,
            list,
        ):
            raise TypeError(
                "El campo conclusions debe ser una lista."
            )

    def _validate_unsupported_nested_fields(
        self,
        data: dict,
    ) -> None:
        """
        Evita descartar silenciosamente secciones anidadas
        todavía no soportadas.
        """

        for field_name in sorted(
            self.UNSUPPORTED_NESTED_FIELDS
        ):
            if field_name not in data:
                continue

            value = data[field_name]

            if not isinstance(
                value,
                list,
            ):
                raise TypeError(
                    f"El campo {field_name} debe ser "
                    "una lista."
                )

            if value:
                raise ValueError(
                    f"El campo {field_name} todavía no "
                    "está soportado por "
                    "MeetingReportParser."
                )

    def _parse_topics(
        self,
        values,
    ) -> list[MeetingTopic]:
        """
        Convierte diccionarios de topics en MeetingTopic.
        """

        self._validate_list_field(
            field_name="topics",
            values=values,
        )

        topics: list[MeetingTopic] = []

        for index, value in enumerate(
            values,
            start=1,
        ):
            item = self._validate_dict_item(
                field_name="topics",
                index=index,
                value=value,
            )

            self._require_item_fields(
                field_name="topics",
                index=index,
                item=item,
                required_fields={
                    "title",
                    "summary",
                },
            )

            topics.append(
                MeetingTopic(
                    title=item["title"],
                    summary=item["summary"],
                    evidence=self._parse_evidence(
                        item.get(
                            "evidence",
                            [],
                        ),
                        parent_field="topics",
                        parent_index=index,
                    ),
                )
            )

        return topics

    def _parse_participants(
        self,
        values,
    ) -> list[Participant]:
        """
        Convierte diccionarios en Participant.
        """

        self._validate_list_field(
            field_name="participants",
            values=values,
        )

        participants: list[Participant] = []

        for index, value in enumerate(
            values,
            start=1,
        ):
            item = self._validate_dict_item(
                field_name="participants",
                index=index,
                value=value,
            )

            participants.append(
                Participant(
                    name=item.get(
                        "name"
                    ),
                    speaker=item.get(
                        "speaker"
                    ),
                    role=item.get(
                        "role"
                    ),
                )
            )

        return participants

    def _parse_decisions(
        self,
        values,
    ) -> list[Decision]:
        """
        Convierte diccionarios en Decision.
        """

        self._validate_list_field(
            field_name="decisions",
            values=values,
        )

        decisions: list[Decision] = []

        for index, value in enumerate(
            values,
            start=1,
        ):
            item = self._validate_dict_item(
                field_name="decisions",
                index=index,
                value=value,
            )

            self._require_item_fields(
                field_name="decisions",
                index=index,
                item=item,
                required_fields={
                    "description",
                },
            )

            decisions.append(
                Decision(
                    description=item[
                        "description"
                    ],
                    rationale=item.get(
                        "rationale"
                    ),
                    evidence=self._parse_evidence(
                        item.get(
                            "evidence",
                            [],
                        ),
                        parent_field="decisions",
                        parent_index=index,
                    ),
                )
            )

        return decisions

    def _parse_risks(
        self,
        values,
    ) -> list[MeetingRisk]:
        """
        Convierte diccionarios en MeetingRisk.
        """

        self._validate_list_field(
            field_name="risks",
            values=values,
        )

        risks: list[MeetingRisk] = []

        for index, value in enumerate(
            values,
            start=1,
        ):
            item = self._validate_dict_item(
                field_name="risks",
                index=index,
                value=value,
            )

            self._require_item_fields(
                field_name="risks",
                index=index,
                item=item,
                required_fields={
                    "description",
                },
            )

            risks.append(
                MeetingRisk(
                    description=item[
                        "description"
                    ],
                    impact=item.get(
                        "impact"
                    ),
                    evidence=self._parse_evidence(
                        item.get(
                            "evidence",
                            [],
                        ),
                        parent_field="risks",
                        parent_index=index,
                    ),
                )
            )

        return risks

    def _parse_pending_items(
        self,
        values,
    ) -> list[PendingItem]:
        """
        Convierte diccionarios en PendingItem.
        """

        self._validate_list_field(
            field_name="pending_items",
            values=values,
        )

        pending_items: list[PendingItem] = []

        for index, value in enumerate(
            values,
            start=1,
        ):
            item = self._validate_dict_item(
                field_name="pending_items",
                index=index,
                value=value,
            )

            self._require_item_fields(
                field_name="pending_items",
                index=index,
                item=item,
                required_fields={
                    "description",
                },
            )

            pending_items.append(
                PendingItem(
                    description=item[
                        "description"
                    ],
                    evidence=self._parse_evidence(
                        item.get(
                            "evidence",
                            [],
                        ),
                        parent_field="pending_items",
                        parent_index=index,
                    ),
                )
            )

        return pending_items

    def _parse_evidence(
        self,
        values,
        parent_field: str,
        parent_index: int,
    ) -> list[EvidenceReference]:
        """
        Convierte referencias de evidencia anidadas.
        """

        if not isinstance(
            values,
            list,
        ):
            raise TypeError(
                f"El campo {parent_field} elemento "
                f"#{parent_index} evidence debe ser "
                "una lista."
            )

        evidence_items: list[EvidenceReference] = []

        for evidence_index, value in enumerate(
            values,
            start=1,
        ):
            if not isinstance(
                value,
                dict,
            ):
                raise TypeError(
                    f"El campo {parent_field} elemento "
                    f"#{parent_index} evidence elemento "
                    f"#{evidence_index} debe ser un objeto."
                )

            required_fields = {
                "speaker",
                "start",
                "end",
                "excerpt",
            }

            missing_fields = (
                required_fields.difference(
                    value.keys()
                )
            )

            if missing_fields:
                raise ValueError(
                    f"El campo {parent_field} elemento "
                    f"#{parent_index} evidence elemento "
                    f"#{evidence_index} no contiene los "
                    "campos requeridos: "
                    + ", ".join(
                        sorted(
                            missing_fields
                        )
                    )
                )

            evidence_items.append(
                EvidenceReference(
                    speaker=value[
                        "speaker"
                    ],
                    start=value[
                        "start"
                    ],
                    end=value[
                        "end"
                    ],
                    excerpt=value[
                        "excerpt"
                    ],
                )
            )

        return evidence_items

    @staticmethod
    def _validate_list_field(
        field_name: str,
        values,
    ) -> None:
        """
        Verifica que una sección anidada sea una lista.
        """

        if not isinstance(
            values,
            list,
        ):
            raise TypeError(
                f"El campo {field_name} debe ser "
                "una lista."
            )

    @staticmethod
    def _validate_dict_item(
        field_name: str,
        index: int,
        value,
    ) -> dict:
        """
        Verifica que un elemento anidado sea un objeto.
        """

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
    def _require_item_fields(
        field_name: str,
        index: int,
        item: dict,
        required_fields: set[str],
    ) -> None:
        """
        Verifica campos obligatorios de una entidad anidada.
        """

        missing_fields = required_fields.difference(
            item.keys()
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

    @staticmethod
    def _clean_json_response(
        response: str,
    ) -> str:
        """
        Extrae un objeto JSON de la respuesta textual.

        Tolera bloques Markdown y texto externo, pero exige
        la presencia de un objeto delimitado por llaves.
        """

        if (
            not isinstance(
                response,
                str,
            )
            or not response.strip()
        ):
            raise ValueError(
                "La respuesta de IA está vacía."
            )

        cleaned = response.strip()

        if cleaned.startswith(
            "```json"
        ):
            cleaned = cleaned[
                len("```json"):
            ]

        elif cleaned.startswith(
            "```"
        ):
            cleaned = cleaned[3:]

        if cleaned.endswith(
            "```"
        ):
            cleaned = cleaned[:-3]

        cleaned = cleaned.strip()

        first_brace = cleaned.find(
            "{"
        )

        last_brace = cleaned.rfind(
            "}"
        )

        if (
            first_brace == -1
            or last_brace == -1
            or last_brace < first_brace
        ):
            raise ValueError(
                "No se encontró un objeto JSON en la "
                "respuesta de IA."
            )

        return cleaned[
            first_brace:last_brace + 1
        ]