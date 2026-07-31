"""
app_controller.py

Controlador principal de la aplicación.
"""

from application.dependency_container import container


class AppController:

    def __init__(self):

        self.state = container.get(
            "app_state"
        )

        self.bus = container.get(
            "event_bus"
        )

        self.logger = container.get(
            "logger"
        )

        self.task_runner = container.get(
            "task_runner"
        )

        self.setup_controller = container.get(
            "setup_controller"
        )

        self.meeting_controller = container.get(
            "meeting_controller"
        )

        self.import_controller = container.get(
            "import_controller"
        )

    def start_meeting(self) -> None:
        self.meeting_controller.start()

    def pause_meeting(self) -> None:
        self.meeting_controller.pause()

    def resume_meeting(self) -> None:
        self.meeting_controller.resume()

    def stop_meeting(self) -> None:
        self.meeting_controller.stop()

    def import_recording(self) -> None:
        self.import_controller.import_recording()

    def start_setup_wizard(self) -> None:
        self.setup_controller.start()

    def retry_setup_wizard(self) -> None:
        self.setup_controller.retry()

    def accept_setup_wizard_result(
        self,
        result,
    ) -> None:
        self.setup_controller.accept_result(
            result
        )

    def continue_with_attention(self) -> bool:
        return (
            self.setup_controller
            .continue_with_attention()
        )