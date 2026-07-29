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
from services.artifact_storage_service import ArtifactStorageService
from services.imported_meeting_service import ImportedMeetingService
from services.meeting_pipeline_service import MeetingPipelineService
from services.summary_markdown_exporter import SummaryMarkdownExporter
from services.summary_service import SummaryService
from services.task_runner import TaskRunner
from services.transcript_service import TranscriptService
from services.validators.summary_validator import SummaryValidator
from services.workspace_service import WorkspaceService


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

# Servicios base
event_bus = EventBus()
app_state = AppState()
logger = LoggerService()
configuration = ConfigurationService()

# Setup Wizard
capability_registry = build_default_capability_registry(
    configuration=configuration
)

capability_runner = CapabilityRunner(
    event_bus=event_bus
)

setup_wizard_service = SetupWizardService(
    capability_registry=capability_registry,
    capability_runner=capability_runner,
    event_bus=event_bus,
)

# Servicios de reunión e importación
audio_capture_service = AudioCaptureService(configuration)
meeting_timer = MeetingTimer()
task_runner = TaskRunner()

workspace_service = WorkspaceService()
transcript_service = TranscriptService()

meeting_pipeline = MeetingPipelineService(
    summary_service=SummaryService(),
    validator=SummaryValidator(),
    storage_service=ArtifactStorageService(),
    markdown_exporter=SummaryMarkdownExporter(),
)

imported_meeting_service = ImportedMeetingService(
    workspace_service=workspace_service,
    transcript_service=transcript_service,
    meeting_pipeline=meeting_pipeline,
)

# Registro de servicios
container.register("event_bus", event_bus)
container.register("app_state", app_state)
container.register("logger", logger)
container.register("configuration", configuration)
container.register("audio_capture_service", audio_capture_service)
container.register("meeting_timer", meeting_timer)
container.register("capability_registry", capability_registry)
container.register("capability_runner", capability_runner)
container.register("setup_wizard_service", setup_wizard_service)
container.register("task_runner", task_runner)
container.register("workspace_service", workspace_service)
container.register("transcript_service", transcript_service)
container.register("meeting_pipeline", meeting_pipeline)
container.register("imported_meeting_service", imported_meeting_service)
