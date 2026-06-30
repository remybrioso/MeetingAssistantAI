"""
app_controller.py

Controlador principal de la aplicación.
"""

from application.dependency_container import container


class AppController:

    def __init__(self):

        self.state = container.get("app_state")
        self.bus = container.get("event_bus")
        self.logger = container.get("logger")

    def start_meeting(self):

        self.state.set("meeting_active", True)
        self.state.set("audio_status", "recording")

        self.logger.info("Reunión iniciada.")

        self.bus.emit("meeting_started")

    def pause_meeting(self):

        self.state.set("audio_status", "paused")

        self.logger.info("Reunión pausada.")

        self.bus.emit("meeting_paused")

    def resume_meeting(self):

        self.state.set("audio_status", "recording")

        self.logger.info("Reunión reanudada.")

        self.bus.emit("meeting_resumed")

    def stop_meeting(self):

        self.state.set("meeting_active", False)
        self.state.set("audio_status", "idle")

        self.logger.info("Reunión finalizada.")

        self.bus.emit("meeting_finished")