"""
meeting_report_grounding_validator.py

Valida que un MeetingReport consolidado conserve evidencia
procedente del MeetingKnowledge original.
"""

from models.artifacts.meeting_report import MeetingReport
from models.meeting_knowledge import MeetingKnowledge


class MeetingReportGroundingValidator:
    """
    Verifica grounding determinista entre el reporte global y
    las extracciones por chunk.

    Reglas:
    - cada elemento operativo final debe conservar evidencia;
    - la evidencia debe existir literalmente en MeetingKnowledge;
    - la evidencia debe provenir de la misma categoría semántica;
    - metadata estructurada de acciones no puede aparecer de la nada.

    Esta clase no intenta juzgar equivalencia semántica de texto
    libre. Esa responsabilidad permanece en el modelo y en los
    validadores de calidad.
    """

    EVIDENCE_BACKED_SECTIONS = (
        "topics",
        "decisions",
        "action_items",
        "risks",
        "pending_items",
    )

    def validate(
        self,
        report: MeetingReport,
        meeting_knowledge: MeetingKnowledge,
    ) -> tuple[bool, list[str]]:
        if not isinstance(
            report,
            MeetingReport,
        ):
            raise TypeError(
                "report debe ser una instancia de MeetingReport."
            )

        if not isinstance(
            meeting_knowledge,
            MeetingKnowledge,
        ):
            raise TypeError(
                "meeting_knowledge debe ser una instancia "
                "de MeetingKnowledge."
            )

        errors: list[str] = []

        source_evidence = (
            self._build_source_evidence_index(
                meeting_knowledge
            )
        )

        for section_name in (
            self.EVIDENCE_BACKED_SECTIONS
        ):
            self._validate_section_evidence(
                report=report,
                section_name=section_name,
                source_evidence=source_evidence[
                    section_name
                ],
                errors=errors,
            )

        self._validate_action_metadata(
            report=report,
            meeting_knowledge=meeting_knowledge,
            errors=errors,
        )

        return (
            not errors,
            errors,
        )

    def _build_source_evidence_index(
        self,
        meeting_knowledge: MeetingKnowledge,
    ) -> dict[str, set[tuple]]:
        index = {
            section_name: set()
            for section_name in (
                self.EVIDENCE_BACKED_SECTIONS
            )
        }

        for chunk in meeting_knowledge.chunks:
            for section_name in (
                self.EVIDENCE_BACKED_SECTIONS
            ):
                items = getattr(
                    chunk,
                    section_name,
                )

                for item in items:
                    for evidence in item.evidence:
                        index[
                            section_name
                        ].add(
                            self._evidence_key(
                                evidence
                            )
                        )

        return index

    def _validate_section_evidence(
        self,
        report: MeetingReport,
        section_name: str,
        source_evidence: set[tuple],
        errors: list[str],
    ) -> None:
        items = getattr(
            report,
            section_name,
        )

        for item_index, item in enumerate(
            items,
            start=1,
        ):
            if not item.evidence:
                errors.append(
                    f"{section_name} elemento "
                    f"#{item_index} no contiene evidencia."
                )
                continue

            for evidence_index, evidence in enumerate(
                item.evidence,
                start=1,
            ):
                evidence_key = (
                    self._evidence_key(
                        evidence
                    )
                )

                if evidence_key not in source_evidence:
                    errors.append(
                        f"{section_name} elemento "
                        f"#{item_index} evidence "
                        f"#{evidence_index} no existe en "
                        "MeetingKnowledge dentro de la "
                        "misma sección semántica."
                    )

    def _validate_action_metadata(
        self,
        report: MeetingReport,
        meeting_knowledge: MeetingKnowledge,
        errors: list[str],
    ) -> None:
        source_actions = [
            action
            for chunk in meeting_knowledge.chunks
            for action in chunk.action_items
        ]

        for action_index, action in enumerate(
            report.action_items,
            start=1,
        ):
            matching_sources = (
                self._source_actions_sharing_evidence(
                    action=action,
                    source_actions=source_actions,
                )
            )

            if not matching_sources:
                continue

            if (
                action.owner is not None
                and not any(
                    source.owner == action.owner
                    for source in matching_sources
                )
            ):
                errors.append(
                    "action_items elemento "
                    f"#{action_index} contiene un owner "
                    "no respaldado por las acciones fuente "
                    "que comparten su evidencia."
                )

            if (
                action.due_date is not None
                and not any(
                    source.due_date == action.due_date
                    for source in matching_sources
                )
            ):
                errors.append(
                    "action_items elemento "
                    f"#{action_index} contiene un due_date "
                    "no respaldado por las acciones fuente "
                    "que comparten su evidencia."
                )

            if not any(
                source.status == action.status
                for source in matching_sources
            ):
                errors.append(
                    "action_items elemento "
                    f"#{action_index} contiene un status "
                    "no respaldado por las acciones fuente "
                    "que comparten su evidencia."
                )

    def _source_actions_sharing_evidence(
        self,
        action,
        source_actions: list,
    ) -> list:
        report_evidence = {
            self._evidence_key(
                evidence
            )
            for evidence in action.evidence
        }

        if not report_evidence:
            return []

        matching_sources = []

        for source_action in source_actions:
            source_evidence = {
                self._evidence_key(
                    evidence
                )
                for evidence in source_action.evidence
            }

            if report_evidence.intersection(
                source_evidence
            ):
                matching_sources.append(
                    source_action
                )

        return matching_sources

    @staticmethod
    def _evidence_key(
        evidence,
    ) -> tuple:
        return (
            evidence.speaker,
            float(
                evidence.start
            ),
            float(
                evidence.end
            ),
            evidence.excerpt,
        )
