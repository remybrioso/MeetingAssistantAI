"""
meeting_artifact_delivery_service.py

Entrega todos los artefactos derivados de un MeetingReport
validado dentro del Workspace de una reunión.
"""

from models.artifacts.meeting_report import MeetingReport
from models.workspace.meeting_workspace import MeetingWorkspace


class MeetingArtifactDeliveryService:
    """
    Orquesta la persistencia y exportación documental de un
    MeetingReport ya generado y validado.

    No realiza llamadas a proveedores de IA ni reinterpreta
    contenido. Toda transformación se delega a servicios
    deterministas especializados.
    """

    def __init__(
        self,
        storage_service,
        projection_service,
        markdown_exporter,
        docx_exporter,
        pdf_exporter,
    ) -> None:
        self.storage_service = storage_service
        self.projection_service = projection_service
        self.markdown_exporter = markdown_exporter
        self.docx_exporter = docx_exporter
        self.pdf_exporter = pdf_exporter

        self._validate_dependencies()

    def deliver(
        self,
        report: MeetingReport,
        workspace: MeetingWorkspace,
    ) -> None:
        """
        Persiste y exporta la capa completa de artefactos.

        Flujo:
        1. proyecta acciones y decisiones;
        2. persiste los tres artefactos JSON;
        3. exporta Markdown, DOCX y PDF.

        Los errores de cualquier dependencia se propagan al
        consumidor. No se silencian fallos de entrega.
        """

        self._validate_report(
            report
        )
        self._validate_workspace(
            workspace
        )

        (
            action_items_artifact,
            decisions_artifact,
        ) = self.projection_service.project(
            report
        )

        self.storage_service.save(
            report,
            workspace.meeting_report_json,
        )

        self.storage_service.save(
            action_items_artifact,
            workspace.action_items_json,
        )

        self.storage_service.save(
            decisions_artifact,
            workspace.decisions_json,
        )

        self.markdown_exporter.export(
            report,
            workspace.meeting_report_markdown,
        )

        self.docx_exporter.export(
            report,
            workspace.meeting_minutes_docx,
        )

        self.pdf_exporter.export(
            report,
            workspace.meeting_pdf,
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

    @staticmethod
    def _validate_workspace(
        workspace,
    ) -> None:
        if not isinstance(
            workspace,
            MeetingWorkspace,
        ):
            raise TypeError(
                "workspace debe ser una instancia "
                "de MeetingWorkspace."
            )

    def _validate_dependencies(
        self,
    ) -> None:
        missing_dependencies = []

        dependencies = {
            "storage_service": (
                self.storage_service
            ),
            "projection_service": (
                self.projection_service
            ),
            "markdown_exporter": (
                self.markdown_exporter
            ),
            "docx_exporter": (
                self.docx_exporter
            ),
            "pdf_exporter": (
                self.pdf_exporter
            ),
        }

        for name, dependency in dependencies.items():
            if dependency is None:
                missing_dependencies.append(
                    name
                )

        if missing_dependencies:
            raise ValueError(
                "Faltan dependencias obligatorias en "
                "MeetingArtifactDeliveryService: "
                + ", ".join(
                    missing_dependencies
                )
            )
