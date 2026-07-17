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
from services.setup.capabilities.capability_runner import (
    CapabilityRunner,
)
from services.setup.default_capability_registry import (
    build_default_capability_registry,
)
from services.setup.wizard.setup_wizard_service import (
    SetupWizardService,
)


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

capability_registry = (
    build_default_capability_registry(
        configuration=configuration
    )
)

capability_runner = CapabilityRunner(
    event_bus=container.get("event_bus")
)

setup_wizard_service = SetupWizardService(
    capability_registry=capability_registry,
    capability_runner=capability_runner,
    event_bus=container.get("event_bus"),
)


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
container.register(
    "capability_registry",
    capability_registry,
)

container.register(
    "capability_runner",
    capability_runner,
)

container.register(
    "setup_wizard_service",
    setup_wizard_service,
)