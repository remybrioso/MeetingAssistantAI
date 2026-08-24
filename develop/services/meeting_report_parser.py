"""
meeting_report_parser.py

Convierte una respuesta JSON de IA en un MeetingReport.
"""

import json
from datetime import date
from json import JSONDecodeError

from models.artifacts.meeting_report import MeetingReport
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


class MeetingReportParser:
    """
    Convierte la respuesta textual de un proveedor de IA
    en un MeetingReport validado por el dominio.

    Soporta:

    - campos principales;
    - topics;
    - participants;
    - decisions;
    - action_items;
    - risks;
    - pending_items;
    - evidence.
    """

    REQUIRED_FIELDS = {
        "title",
        "executive_summary",
        "key_points",
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
                Si la respuesta está vacía, contiene JSON
                inválido, carece de campos obligatorios o
                contiene valores no reconocidos.

            TypeError:
                Si la estructura JSON usa tipos incompatibles
                con el contrato esperado.
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

        action_items = self._parse_action_items(
            data.get(
                "action_items",
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
            action_items=action_items,
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

        La validación de cada elemento pertenece al modelo
        MeetingReport.
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

    def _parse_topics(
        self,
        values,
    ) -> list[MeetingTopic]:
        """
        Convierte diccionarios en MeetingTopic.

        Los placeholders sin contenido semántico se ignoran.
        Un elemento parcialmente informado continúa siendo
        validado por el dominio y puede ser rechazado.
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

            title = item["title"]
            summary = item["summary"]

            if (
                self._is_blank_text(title)
                and self._is_blank_text(summary)
            ):
                continue

            topics.append(
                MeetingTopic(
                    title=title,
                    summary=summary,
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

        Una decisión completamente vacía se considera un
        placeholder del proveedor y se ignora.
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

            description = item["description"]
            rationale = item.get(
                "rationale"
            )

            if (
                self._is_blank_text(description)
                and self._is_blank_optional_text(
                    rationale
                )
            ):
                continue

            decisions.append(
                Decision(
                    description=description,
                    rationale=rationale,
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

    def _parse_action_items(
        self,
        values,
    ) -> list[ActionItem]:
        """
        Convierte diccionarios en ActionItem.

        Contrato JSON de cada acción:

        {
            "description": str,
            "owner": str | {"display_name": str} | null,
            "due_date": "YYYY-MM-DD" | null,
            "status": str | null,
            "evidence": list
        }

        Una acción completamente vacía se considera un
        placeholder del proveedor y se ignora.
        """

        self._validate_list_field(
            field_name="action_items",
            values=values,
        )

        action_items: list[ActionItem] = []

        for index, value in enumerate(
            values,
            start=1,
        ):
            item = self._validate_dict_item(
                field_name="action_items",
                index=index,
                value=value,
            )

            self._require_item_fields(
                field_name="action_items",
                index=index,
                item=item,
                required_fields={
                    "description",
                },
            )

            description = item["description"]
            owner = item.get("owner")
            due_date = item.get("due_date")
            status = item.get("status")

            if self._is_empty_action_placeholder(
                description=description,
                owner=owner,
                due_date=due_date,
                status=status,
            ):
                continue

            action_items.append(
                ActionItem(
                    description=description,
                    owner=self._parse_action_owner(
                        owner,
                        action_index=index,
                    ),
                    due_date=self._parse_due_date(
                        due_date,
                        action_index=index,
                    ),
                    status=self._parse_action_status(
                        status,
                        action_index=index,
                    ),
                    evidence=self._parse_evidence(
                        item.get(
                            "evidence",
                            [],
                        ),
                        parent_field="action_items",
                        parent_index=index,
                    ),
                )
            )

        return action_items

    @staticmethod
    def _parse_action_owner(
        value,
        action_index: int,
    ) -> ActionOwner | None:
        """
        Convierte owner en ActionOwner.

        Formas aceptadas:

        - null;
        - cadena;
        - objeto con display_name.
        """

        if value is None:
            return None

        if isinstance(
            value,
            str,
        ):
            return ActionOwner.from_value(
                value
            )

        if isinstance(
            value,
            dict,
        ):
            if "display_name" not in value:
                raise ValueError(
                    "El campo action_items elemento "
                    f"#{action_index} owner no contiene "
                    "el campo requerido: display_name."
                )

            return ActionOwner.from_value(
                value[
                    "display_name"
                ]
            )

        raise TypeError(
            "El campo action_items elemento "
            f"#{action_index} owner debe ser una cadena, "
            "un objeto o null."
        )

    @staticmethod
    def _parse_due_date(
        value,
        action_index: int,
    ) -> date | None:
        """
        Convierte una fecha ISO YYYY-MM-DD en date.

        Las expresiones ambiguas de lenguaje natural no se
        convierten dentro del dominio.
        """

        if value is None:
            return None

        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                "El campo action_items elemento "
                f"#{action_index} due_date debe ser una "
                "cadena ISO o null."
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
        """
        Convierte el estado textual en ActionStatus.

        Un valor ausente o null significa que la reunión
        no expresó un estado y se representa como UNKNOWN.

        Los estados desconocidos se rechazan; no se
        convierten silenciosamente en UNKNOWN.
        """

        if value is None:
            return ActionStatus.UNKNOWN

        try:
            return ActionStatus.from_value(
                value
            )

        except (
            TypeError,
            ValueError,
        ) as ex:
            raise type(ex)(
                "El campo action_items elemento "
                f"#{action_index} status es inválido. "
                f"Detalle: {ex}"
            ) from ex

    def _parse_risks(
        self,
        values,
    ) -> list[MeetingRisk]:
        """
        Convierte diccionarios en MeetingRisk.

        Un riesgo completamente vacío se considera un
        placeholder del proveedor y se ignora.
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

            description = item["description"]
            impact = item.get("impact")

            if (
                self._is_blank_text(description)
                and self._is_blank_optional_text(impact)
            ):
                continue

            risks.append(
                MeetingRisk(
                    description=description,
                    impact=impact,
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

        Un pendiente sin descripción se considera un
        placeholder del proveedor y se ignora.
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

            description = item["description"]

            if self._is_blank_text(description):
                continue

            pending_items.append(
                PendingItem(
                    description=description,
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
    def _is_blank_text(
        value,
    ) -> bool:
        """
        Indica si un valor textual obligatorio está vacío.

        Los tipos distintos de str no se consideran vacíos:
        serán rechazados posteriormente por el dominio.
        """

        return (
            isinstance(value, str)
            and not value.strip()
        )

    @staticmethod
    def _is_blank_optional_text(
        value,
    ) -> bool:
        """
        Indica si un texto opcional no contiene información.
        """

        return (
            value is None
            or (
                isinstance(value, str)
                and not value.strip()
            )
        )

    @classmethod
    def _is_empty_action_placeholder(
        cls,
        description,
        owner,
        due_date,
        status,
    ) -> bool:
        """
        Detecta una acción creada únicamente como placeholder.

        Evidence no participa en esta decisión porque una
        referencia puede existir aunque el modelo no haya
        identificado una acción semántica válida.
        """

        description_empty = cls._is_blank_text(
            description
        )

        owner_empty = (
            owner is None
            or (
                isinstance(owner, str)
                and not owner.strip()
            )
        )

        due_date_empty = (
            due_date is None
            or (
                isinstance(due_date, str)
                and not due_date.strip()
            )
        )

        status_empty = (
            status is None
            or (
                isinstance(status, str)
                and status.strip().lower()
                in {"", "unknown"}
            )
        )

        return (
            description_empty
            and owner_empty
            and due_date_empty
            and status_empty
        )

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