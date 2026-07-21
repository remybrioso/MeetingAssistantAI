"""
meeting_controller.py

Responsable exclusivamente del ciclo de vida
de una reunión.
"""

from application.dependency_container import container

from services.meeting_finalization_service import (
    MeetingFinalizationService,
)

from services.task_runner import TaskRunner


class MeetingController:
    """
    Controlador del ciclo de vida de una reunión.
    """

    def __init__(self):

        self.state = container.get("app_state")
        self.bus = container.get("event_bus")
        self.logger = container.get("logger")

        self.audio_capture_service = container.get(
            "audio_capture_service"
        )

        self.meeting_timer = container.get(
            "meeting_timer"
        )

        self.meeting_finalization_service = (
            MeetingFinalizationService(
                self.bus
            )
        )

        self.task_runner = TaskRunner()

    def start(self):

        if not self.state.get(
            "application_ready"
        ):

            self.bus.emit(
                "activity",
                "❌ MAI todavía no está preparado para iniciar una reunión.",
            )

            return

        if self.state.get(
            "meeting_active"
        ):

            return

        self.audio_capture_service.start()
        self.meeting_timer.start()

        self.state.set(
            "meeting_active",
            True,
        )

        self.state.set(
            "audio_status",
            "recording",
        )

        self.logger.info(
            "Reunión iniciada."
        )

        self.bus.emit(
            "meeting_started"
        )

        self.bus.emit(
            "activity",
            "Reunión iniciada."
        )

    def pause(self):

        self.state.set(
            "audio_status",
            "paused",
        )

        self.logger.info(
            "Reunión pausada."
        )

        self.bus.emit(
            "meeting_paused"
        )

        self.bus.emit(
            "activity",
            "Reunión pausada."
        )

    def resume(self):

        self.state.set(
            "audio_status",
            "recording",
        )

        self.logger.info(
            "Reunión reanudada."
        )

        self.bus.emit(
            "meeting_resumed"
        )

        self.bus.emit(
            "activity",
            "Reunión reanudada."
        )

    def stop(self):

        if not self.state.get(
            "meeting_active"
        ):

            return

        self.audio_capture_service.stop()
        self.meeting_timer.stop()

        self.state.set(
            "meeting_active",
            False,
        )

        self.state.set(
            "audio_status",
            "idle",
        )

        self.logger.info(
            "Reunión finalizada."
        )

        self.bus.emit(
            "meeting_finished"
        )

        self.bus.emit(
            "activity",
            "Reunión finalizada."
        )

        self.task_runner.run(
            self.meeting_finalization_service.finalize,
            self.audio_capture_service.recording_session,
        )