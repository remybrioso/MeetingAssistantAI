"""
meeting_report_validator.py

Validador de calidad semántica para MeetingReport.
"""

from collections.abc import Iterable

from models.artifacts.meeting_report import MeetingReport
from models.meeting_report import EvidenceReference


class MeetingReportValidator:
    """
    Evalúa si un MeetingReport posee calidad mínima
    suficiente para ser persistido y presentado.

    El modelo MeetingReport protege estructura, tipos e
    invariantes básicas. Este validador se concentra en
    calidad, utilidad y duplicación evidente.
    """

    MIN_TITLE_LENGTH = 3
    MAX_TITLE_LENGTH = 200

    MIN_SUMMARY_LENGTH = 30
    MAX_SUMMARY_LENGTH = 10_000

    MIN_OBJECTIVE_LENGTH = 5
    MAX_OBJECTIVE_LENGTH = 1_000

    MIN_KEY_POINTS = 1
    MAX_KEY_POINTS = 20

    MIN_TEXT_ITEM_LENGTH = 5
    MAX_TEXT_ITEM_LENGTH = 2_000

    MAX_TOPICS = 50
    MAX_DECISIONS = 100
    MAX_ACTION_ITEMS = 100
    MAX_RISKS = 100
    MAX_PENDING_ITEMS = 100
    MAX_PARTICIPANTS = 100
    MAX_CONCLUSIONS = 50

    MIN_EVIDENCE_EXCERPT_LENGTH = 3
    MAX_EVIDENCE_EXCERPT_LENGTH = 2_000

    def validate(
        self,
        report: MeetingReport,
    ) -> tuple[bool, list[str]]:
        """
        Devuelve el estado de validez y todos los errores
        detectados.

        No lanza una excepción por errores de calidad.
        """

        errors: list[str] = []

        self._validate_title(
            report,
            errors,
        )

        self._validate_objective(
            report,
            errors,
        )

        self._validate_executive_summary(
            report,
            errors,
        )

        self._validate_text_collection(
            values=report.key_points,
            section_name="puntos clave",
            item_name="punto clave",
            minimum_items=self.MIN_KEY_POINTS,
            maximum_items=self.MAX_KEY_POINTS,
            errors=errors,
        )

        self._validate_text_collection(
            values=report.conclusions,
            section_name="conclusiones",
            item_name="conclusión",
            minimum_items=0,
            maximum_items=self.MAX_CONCLUSIONS,
            errors=errors,
        )

        self._validate_maximum_collection_size(
            collection=report.topics,
            section_name="temas",
            maximum=self.MAX_TOPICS,
            errors=errors,
        )

        self._validate_maximum_collection_size(
            collection=report.decisions,
            section_name="decisiones",
            maximum=self.MAX_DECISIONS,
            errors=errors,
        )

        self._validate_maximum_collection_size(
            collection=report.action_items,
            section_name="acciones",
            maximum=self.MAX_ACTION_ITEMS,
            errors=errors,
        )

        self._validate_maximum_collection_size(
            collection=report.risks,
            section_name="riesgos",
            maximum=self.MAX_RISKS,
            errors=errors,
        )

        self._validate_maximum_collection_size(
            collection=report.pending_items,
            section_name="asuntos pendientes",
            maximum=self.MAX_PENDING_ITEMS,
            errors=errors,
        )

        self._validate_maximum_collection_size(
            collection=report.participants,
            section_name="participantes",
            maximum=self.MAX_PARTICIPANTS,
            errors=errors,
        )

        self._validate_topics(
            report,
            errors,
        )

        self._validate_described_items(
            items=report.decisions,
            section_name="decisiones",
            item_name="decisión",
            errors=errors,
        )

        self._validate_described_items(
            items=report.action_items,
            section_name="acciones",
            item_name="acción",
            errors=errors,
        )

        self._validate_described_items(
            items=report.risks,
            section_name="riesgos",
            item_name="riesgo",
            errors=errors,
        )

        self._validate_described_items(
            items=report.pending_items,
            section_name="asuntos pendientes",
            item_name="asunto pendiente",
            errors=errors,
        )

        return (
            len(errors) == 0,
            errors,
        )

    def _validate_title(
        self,
        report: MeetingReport,
        errors: list[str],
    ) -> None:
        title_length = len(
            report.title.strip()
        )

        if title_length < self.MIN_TITLE_LENGTH:
            errors.append(
                "El título es demasiado corto."
            )

        if title_length > self.MAX_TITLE_LENGTH:
            errors.append(
                "El título es demasiado largo."
            )

    def _validate_objective(
        self,
        report: MeetingReport,
        errors: list[str],
    ) -> None:
        if report.objective is None:
            return

        objective_length = len(
            report.objective.strip()
        )

        if objective_length < self.MIN_OBJECTIVE_LENGTH:
            errors.append(
                "El objetivo es demasiado corto."
            )

        if objective_length > self.MAX_OBJECTIVE_LENGTH:
            errors.append(
                "El objetivo es demasiado largo."
            )

    def _validate_executive_summary(
        self,
        report: MeetingReport,
        errors: list[str],
    ) -> None:
        summary_length = len(
            report.executive_summary.strip()
        )

        if summary_length < self.MIN_SUMMARY_LENGTH:
            errors.append(
                "El resumen ejecutivo es demasiado corto."
            )

        if summary_length > self.MAX_SUMMARY_LENGTH:
            errors.append(
                "El resumen ejecutivo es demasiado largo."
            )

    def _validate_text_collection(
        self,
        values: list[str],
        section_name: str,
        item_name: str,
        minimum_items: int,
        maximum_items: int,
        errors: list[str],
    ) -> None:
        item_count = len(
            values
        )

        if item_count < minimum_items:
            errors.append(
                f"La sección {section_name} debe contener "
                f"al menos {minimum_items} elemento."
            )

        if item_count > maximum_items:
            errors.append(
                f"La sección {section_name} no debe "
                f"contener más de {maximum_items} elementos."
            )

        for index, value in enumerate(
            values,
            start=1,
        ):
            text_length = len(
                value.strip()
            )

            if text_length < self.MIN_TEXT_ITEM_LENGTH:
                errors.append(
                    f"El {item_name} #{index} es "
                    "demasiado corto."
                )

            if text_length > self.MAX_TEXT_ITEM_LENGTH:
                errors.append(
                    f"El {item_name} #{index} es "
                    "demasiado largo."
                )

        self._validate_duplicate_texts(
            values=values,
            section_name=section_name,
            errors=errors,
        )

    def _validate_topics(
        self,
        report: MeetingReport,
        errors: list[str],
    ) -> None:
        topic_titles: list[str] = []

        for index, topic in enumerate(
            report.topics,
            start=1,
        ):
            topic_titles.append(
                topic.title
            )

            if (
                len(topic.title.strip())
                < self.MIN_TEXT_ITEM_LENGTH
            ):
                errors.append(
                    f"El título del tema #{index} es "
                    "demasiado corto."
                )

            if (
                len(topic.summary.strip())
                < self.MIN_TEXT_ITEM_LENGTH
            ):
                errors.append(
                    f"El resumen del tema #{index} es "
                    "demasiado corto."
                )

            self._validate_evidence_collection(
                evidence=topic.evidence,
                section_name="tema",
                item_index=index,
                errors=errors,
            )

        self._validate_duplicate_texts(
            values=topic_titles,
            section_name="temas",
            errors=errors,
        )

    def _validate_described_items(
        self,
        items: Iterable,
        section_name: str,
        item_name: str,
        errors: list[str],
    ) -> None:
        descriptions: list[str] = []

        for index, item in enumerate(
            items,
            start=1,
        ):
            description = item.description
            descriptions.append(
                description
            )

            description_length = len(
                description.strip()
            )

            if (
                description_length
                < self.MIN_TEXT_ITEM_LENGTH
            ):
                errors.append(
                    f"La descripción de la {item_name} "
                    f"#{index} es demasiado corta."
                )

            if (
                description_length
                > self.MAX_TEXT_ITEM_LENGTH
            ):
                errors.append(
                    f"La descripción de la {item_name} "
                    f"#{index} es demasiado larga."
                )

            self._validate_evidence_collection(
                evidence=item.evidence,
                section_name=item_name,
                item_index=index,
                errors=errors,
            )

        self._validate_duplicate_texts(
            values=descriptions,
            section_name=section_name,
            errors=errors,
        )

    def _validate_evidence_collection(
        self,
        evidence: list[EvidenceReference],
        section_name: str,
        item_index: int,
        errors: list[str],
    ) -> None:
        article = self._resolve_evidence_article(
            section_name
        )

        for evidence_index, reference in enumerate(
            evidence,
            start=1,
        ):
            excerpt_length = len(
                reference.excerpt.strip()
            )

            if (
                excerpt_length
                < self.MIN_EVIDENCE_EXCERPT_LENGTH
            ):
                errors.append(
                    f"La evidencia #{evidence_index} "
                    f"{article} {section_name} "
                    f"#{item_index} es demasiado corta."
                )

            if (
                excerpt_length
                > self.MAX_EVIDENCE_EXCERPT_LENGTH
            ):
                errors.append(
                    f"La evidencia #{evidence_index} "
                    f"{article} {section_name} "
                    f"#{item_index} es demasiado larga."
                )

            if reference.end < reference.start:
                errors.append(
                    f"La evidencia #{evidence_index} "
                    f"{article} {section_name} "
                    f"#{item_index} posee un rango "
                    "de tiempo inválido."
                )

    @staticmethod
    def _resolve_evidence_article(
        section_name: str,
        ) -> str:
        """
        Devuelve la contracción o artículo correcto para
        construir mensajes legibles en español.
        """

        feminine_sections = {
            "decisión",
            "acción",
        }

        if section_name in feminine_sections:
            return "de la"

        return "del"

    @staticmethod
    def _validate_maximum_collection_size(
            collection: list,
            section_name: str,
            maximum: int,
            errors: list[str],
        ) -> None:
            if len(collection) > maximum:
                errors.append(
                    f"La sección {section_name} no debe "
                    f"contener más de {maximum} elementos."
                )

    @staticmethod
    def _validate_duplicate_texts(
            values: list[str],
            section_name: str,
            errors: list[str],
        ) -> None:
            normalized_values = [
                " ".join(
                    value.casefold().split()
                )
                for value in values
            ]

            seen: set[str] = set()

            for normalized_value in normalized_values:
                if normalized_value in seen:
                    errors.append(
                        f"La sección {section_name} contiene "
                        "elementos duplicados."
                    )
                    return

                seen.add(
                    normalized_value
                )