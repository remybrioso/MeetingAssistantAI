"""
app_controller.py

Controlador principal de la aplicación.
"""

from application.dependency_container import container
from application.controllers.meeting_controller import MeetingController
from services.meeting_finalization_service import MeetingFinalizationService
from application.controllers.import_controller import ImportController



class AppController:

    def __init__(self):

        self.meeting_controller = MeetingController()
        self.state = container.get("app_state")
        self.bus = container.get("event_bus")
        self.logger = container.get("logger")
        self.audio_capture_service = container.get("audio_capture_service")
        self.meeting_timer = container.get("meeting_timer")
        self.meeting_finalization_service = MeetingFinalizationService(self.bus)
        self.import_controller = ImportController()
        self.task_runner = container.get(
            "task_runner"
        )

        self.setup_wizard_service = container.get(
            "setup_wizard_service"
        )

    def start_meeting(self):
        self.meeting_controller.start()

    def pause_meeting(self):
        self.meeting_controller.pause()

    def resume_meeting(self):
        self.meeting_controller.resume()

    def stop_meeting(self):
        self.meeting_controller.stop()

    def import_recording(self):

        self.import_controller.import_recording()




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
