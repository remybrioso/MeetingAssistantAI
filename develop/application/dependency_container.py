"""
dependency_container.py

Contenedor de dependencias de la aplicación.
"""

from application.app_state import AppState
from application.event_bus import EventBus
from services.logger_service import LoggerService
from services.audio_capture_service import AudioCaptureService
from services.configuration_service import ConfigurationService
from services.meeting_timer import MeetingTimer


class DependencyContainer:
    """
    Registra y entrega las dependencias de la aplicación.
    """

    def __init__(self):
        self._services = {}

    def register(self, name: str, service) -> None:
        self._services[name] = service

    def get(self, name: str):
        return self._services.get(name)


# Instancia única del contenedor
container = DependencyContainer()

# Registro de servicios base
container.register("event_bus", EventBus())
container.register("app_state", AppState())
container.register("logger", LoggerService())


configuration = ConfigurationService()
event_bus = container.get("event_bus")

# Servicios de negocio
container.register(
    "configuration",
    configuration
)

container.register(
    "audio_capture_service",
    AudioCaptureService(configuration)
)
container.register(
    "meeting_timer",
    MeetingTimer()
)