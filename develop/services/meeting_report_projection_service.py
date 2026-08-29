"""
meeting_report_projection_service.py

Construye artefactos estructurados derivados de un MeetingReport
ya validado.

No realiza llamadas al proveedor de IA, no modifica el reporte
fuente y no reinterpreta contenido.
"""

from models.artifacts.action_items_artifact import (
    ActionItemsArtifact,
)
from models.artifacts.decisions_artifact import (
    DecisionsArtifact,
)
from models.artifacts.meeting_report import (
    MeetingReport,
)


class MeetingReportProjectionService:
    """
    Proyecta secciones confiables de MeetingReport en artefactos
    independientes destinados a persistencia y consumo externo.
    """

    ACTION_ITEMS_ARTIFACT_TYPE = (
        "meeting_action_items"
    )

    DECISIONS_ARTIFACT_TYPE = (
        "meeting_decisions"
    )

    def project_action_items(
        self,
        report: MeetingReport,
    ) -> ActionItemsArtifact:
        self._validate_report(
            report
        )

        return ActionItemsArtifact(
            artifact_type=(
                self.ACTION_ITEMS_ARTIFACT_TYPE
            ),
            provider=report.provider,
            model=report.model,
            prompt_version=(
                report.prompt_version
            ),
            meeting_title=report.title,
            source_report_created_at=(
                report.created_at
            ),
            items=list(
                report.action_items
            ),
        )

    def project_decisions(
        self,
        report: MeetingReport,
    ) -> DecisionsArtifact:
        self._validate_report(
            report
        )

        return DecisionsArtifact(
            artifact_type=(
                self.DECISIONS_ARTIFACT_TYPE
            ),
            provider=report.provider,
            model=report.model,
            prompt_version=(
                report.prompt_version
            ),
            meeting_title=report.title,
            source_report_created_at=(
                report.created_at
            ),
            items=list(
                report.decisions
            ),
        )

    def project(
        self,
        report: MeetingReport,
    ) -> tuple[
        ActionItemsArtifact,
        DecisionsArtifact,
    ]:
        """
        Devuelve todas las proyecciones estructuradas soportadas.

        El orden es estable:
        1. acciones;
        2. decisiones.
        """

        self._validate_report(
            report
        )

        return (
            self.project_action_items(
                report
            ),
            self.project_decisions(
                report
            ),
        )

    @staticmethod
    def _validate_report(
        report,
    ) -> None:
        if not isinstance(
            report,
            MeetingReport,
        ):
            raise TypeError(
                "report debe ser una instancia "
                "de MeetingReport."
            )
