"""
app_controller.py

Controlador principal de la aplicación.
"""

from application.dependency_container import container
from services.meeting_finalization_service import MeetingFinalizationService
from services.task_runner import TaskRunner
from pathlib import Path
from tkinter import filedialog

from services.artifact_storage_service import ArtifactStorageService
from services.imported_meeting_service import ImportedMeetingService
from services.meeting_pipeline_service import MeetingPipelineService
from services.summary_markdown_exporter import SummaryMarkdownExporter
from services.summary_service import SummaryService
from services.transcript_service import TranscriptService
from services.validators.summary_validator import SummaryValidator
from services.workspace_service import WorkspaceService


class AppController:

    def __init__(self):

        self.state = container.get("app_state")
        self.bus = container.get("event_bus")
        self.logger = container.get("logger")
        self.audio_capture_service = container.get("audio_capture_service")
        self.meeting_timer = container.get("meeting_timer")
        self.meeting_finalization_service = MeetingFinalizationService(self.bus)
        self.task_runner = TaskRunner()
        self.imported_meeting_service = ImportedMeetingService(
            workspace_service=WorkspaceService(),
            transcript_service=TranscriptService(),
            meeting_pipeline=MeetingPipelineService(
                summary_service=SummaryService(),
                validator=SummaryValidator(),
                storage_service=ArtifactStorageService(),
                markdown_exporter=SummaryMarkdownExporter()
            )
        )
        self.setup_wizard_service = container.get(
            "setup_wizard_service"
        )

    def start_meeting(self):

        if not self.state.get(
            "application_ready"
        ):

            self.bus.emit(
                "activity",
                "❌ MAI todavía no está preparado "
                "para iniciar una reunión.",
            )

            return

        if self.state.get("meeting_active"):
            return
        self.audio_capture_service.start()
        self.meeting_timer.start()
        

        self.state.set("meeting_active", True)
        self.state.set("audio_status", "recording")

        self.logger.info("Reunión iniciada.")

        self.bus.emit("meeting_started")
        self.bus.emit("activity", "Reunión iniciada.")

    def pause_meeting(self):

        self.state.set("audio_status", "paused")

        self.logger.info("Reunión pausada.")

        self.bus.emit("meeting_paused")
        self.bus.emit("activity", "Reunión pausada.")

    def resume_meeting(self):

        self.state.set("audio_status", "recording")

        self.logger.info("Reunión reanudada.")

        self.bus.emit("meeting_resumed")
        self.bus.emit("activity", "Reunión reanudada.")

    def stop_meeting(self):
        if not self.state.get("meeting_active"):
            return
        self.audio_capture_service.stop()
        self.meeting_timer.stop()

        self.state.set("meeting_active", False)
        self.state.set("audio_status", "idle")

        self.logger.info("Reunión finalizada.")

        self.bus.emit("meeting_finished")
        self.bus.emit("activity", "Reunión finalizada.")
        self.task_runner.run(
            self.meeting_finalization_service.finalize,
            self.audio_capture_service.recording_session
            )

    def import_recording(self):
        
        if not self.state.get(
            "application_ready"
        ):

            self.bus.emit(
                "activity",
                "❌ Complete primero la "
                "configuración inicial de MAI.",
            )

            return


        if self.state.get("meeting_active"):
            self.bus.emit(
                "activity",
                "❌ Finalice la reunión actual antes de importar un archivo."
            )
            return

        selected_file = filedialog.askopenfilename(
            title="Seleccionar grabación WAV",
            filetypes=[
                ("Archivos WAV", "*.wav")
            ]
        )

        if not selected_file:
            return

        source_file = Path(selected_file)

        self.logger.info(
            f"Importación iniciada: {source_file}"
        )

        self.bus.emit(
            "meeting_import_started",
            source_file.name
        )

        self.bus.emit(
            "activity",
            f"Importando grabación: {source_file.name}"
        )

        self.task_runner.run(
            self._process_imported_recording,
            source_file
        )


    def _process_imported_recording(
        self,
        source_file: Path
    ):

        try:
            session = (
                self.imported_meeting_service
                .import_wav(source_file)
            )

            self.logger.info(
                "Grabación importada correctamente: "
                f"{session.session_dir}"
            )

            self.bus.emit(
                "meeting_import_completed",
                session
            )

            self.bus.emit(
                "activity",
                "✅ Grabación importada y procesada correctamente."
            )

        except Exception as ex:

            self.logger.error(
                f"Error importando grabación: {ex}"
            )

            self.bus.emit(
                "meeting_import_failed",
                str(ex)
            )

            self.bus.emit(
                "activity",
                f"❌ Error importando grabación: {ex}"
            )

    def start_setup_wizard(self) -> None:
        """
        Ejecuta el diagnóstico inicial fuera del hilo
        gráfico de CustomTkinter.
        """

        if self.setup_wizard_service is None:

            self.bus.emit(
                "setup_wizard_ui_failed",
                "SetupWizardService no está registrado.",
            )

            return

        if self.state.get(
            "setup_wizard_status"
        ) == "running":

            return

        self.state.set(
            "setup_wizard_status",
            "running",
        )

        self.state.set(
            "setup_wizard_completed",
            False,
        )

        self.state.set(
            "application_ready",
            False,
        )

        self.bus.emit(
            "setup_wizard_ui_started"
        )

        self.task_runner.run(
            self._execute_setup_wizard
        )

    def retry_setup_wizard(self) -> None:
        """
        Repite el diagnóstico completo.
        """

        self.start_setup_wizard()

    def accept_setup_wizard_result(
        self,
        result,
    ) -> None:
        """
        Actualiza AppState desde el hilo gráfico cuando
        MainWindow recibe el resultado.
        """

        status = result.status.value.lower()

        self.state.set(
            "setup_wizard_status",
            status,
        )

        self.state.set(
            "setup_wizard_completed",
            True,
        )

        self.state.set(
            "application_ready",
            result.can_continue,
        )

    def continue_with_attention(self) -> bool:
        """
        Permite entrar a MAI cuando el diagnóstico terminó
        con elementos no bloqueantes.
        """

        status = self.state.get(
            "setup_wizard_status"
        )

        if status not in {
            "ready",
            "attention",
        }:

            return False

        self.state.set(
            "application_ready",
            True,
        )

        self.bus.emit(
            "setup_wizard_continue_requested"
        )

        return True

    def _execute_setup_wizard(self) -> None:

        try:
            result = (
                self.setup_wizard_service.run()
            )

            self.bus.emit(
                "setup_wizard_ui_completed",
                result,
            )

        except Exception as ex:

            self.logger.error(
                "Error ejecutando Setup Wizard: "
                f"{ex}"
            )

            self.bus.emit(
                "setup_wizard_ui_failed",
                str(ex),
            )
