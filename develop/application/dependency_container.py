"""
dependency_container.py

Contenedor de dependencias de la aplicación.
"""

from application.app_state import AppState
from application.event_bus import EventBus
from application.controllers.import_controller import (
    ImportController,
)
from application.controllers.meeting_controller import (
    MeetingController,
)
from application.controllers.setup_controller import (
    SetupController,
)
from services.artifact_storage_service import (
    ArtifactStorageService,
)
from services.audio_capture_service import AudioCaptureService
from services.configuration_service import ConfigurationService
from services.imported_meeting_service import (
    ImportedMeetingService,
)
from services.logger_service import LoggerService
from services.meeting_artifact_delivery_service import (
    MeetingArtifactDeliveryService,
)
from services.meeting_finalization_service import (
    MeetingFinalizationService,
)
from services.meeting_knowledge_assembler import (
    MeetingKnowledgeAssembler,
)
from services.meeting_pipeline_service import (
    MeetingPipelineService,
)
from services.meeting_report_docx_exporter import (
    MeetingReportDocxExporter,
)
from services.meeting_report_generator import (
    MeetingReportGenerator,
)
from services.meeting_report_markdown_exporter import (
    MeetingReportMarkdownExporter,
)
from services.meeting_report_pdf_exporter import (
    MeetingReportPdfExporter,
)
from services.meeting_report_projection_service import (
    MeetingReportProjectionService,
)
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
from services.staged_chunk_knowledge_service import (
    StagedChunkKnowledgeService,
)
from services.staged_meeting_report_consolidation_service import (
    StagedMeetingReportConsolidationService,
)
from services.task_runner import TaskRunner
from services.transcript_analyzer import TranscriptAnalyzer
from services.transcript_chunker import TranscriptChunker
from services.transcript_service import TranscriptService
from services.transcript_storage_service import (
    TranscriptStorageService,
)
from services.transcript_validator import TranscriptValidator
from services.validators.meeting_report_validator import (
    MeetingReportValidator,
)
from services.workspace_service import WorkspaceService


class DependencyContainer:
    """
    Registra y entrega las dependencias de la aplicación.
    """

    def __init__(self):
        self._services = {}

    def register(
        self,
        name: str,
        service,
    ) -> None:
        self._services[name] = service

    def get(
        self,
        name: str,
    ):
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


# Servicios generales
audio_capture_service = AudioCaptureService(
    configuration
)

meeting_timer = MeetingTimer()
task_runner = TaskRunner()
workspace_service = WorkspaceService()


# Servicios de transcripción
transcript_service = TranscriptService()
transcript_storage_service = TranscriptStorageService()
transcript_analyzer = TranscriptAnalyzer()
transcript_validator = TranscriptValidator()


# Persistencia genérica de artefactos
artifact_storage_service = ArtifactStorageService()


# Meeting Intelligence: extracción staged por chunks
transcript_chunker = TranscriptChunker()

staged_chunk_knowledge_service = (
    StagedChunkKnowledgeService()
)

meeting_knowledge_assembler = (
    MeetingKnowledgeAssembler()
)


# Meeting Intelligence: consolidación global staged
meeting_report_validator = (
    MeetingReportValidator()
)

staged_meeting_report_consolidation_service = (
    StagedMeetingReportConsolidationService(
        report_validator=(
            meeting_report_validator
        ),
    )
)

meeting_report_generator = MeetingReportGenerator(
    transcript_chunker=transcript_chunker,
    chunk_knowledge_service=(
        staged_chunk_knowledge_service
    ),
    meeting_knowledge_assembler=(
        meeting_knowledge_assembler
    ),
    consolidation_service=(
        staged_meeting_report_consolidation_service
    ),
)


# Meeting Artifact Delivery
meeting_report_projection_service = (
    MeetingReportProjectionService()
)

meeting_report_markdown_exporter = (
    MeetingReportMarkdownExporter()
)

meeting_report_docx_exporter = (
    MeetingReportDocxExporter()
)

meeting_report_pdf_exporter = (
    MeetingReportPdfExporter()
)

meeting_artifact_delivery_service = (
    MeetingArtifactDeliveryService(
        storage_service=(
            artifact_storage_service
        ),
        projection_service=(
            meeting_report_projection_service
        ),
        markdown_exporter=(
            meeting_report_markdown_exporter
        ),
        docx_exporter=(
            meeting_report_docx_exporter
        ),
        pdf_exporter=(
            meeting_report_pdf_exporter
        ),
    )
)


# Knowledge Pipeline
meeting_pipeline = MeetingPipelineService(
    artifact_generator=(
        meeting_report_generator
    ),
    artifact_delivery_service=(
        meeting_artifact_delivery_service
    ),
    transcript_storage_service=(
        transcript_storage_service
    ),
    transcript_analyzer=transcript_analyzer,
    transcript_validator=transcript_validator,
)


# Servicios de reunión e importación
meeting_finalization_service = (
    MeetingFinalizationService(
        transcript_service=transcript_service,
        transcript_storage_service=(
            transcript_storage_service
        ),
        workspace_service=workspace_service,
        meeting_pipeline=meeting_pipeline,
        bus=event_bus,
    )
)

imported_meeting_service = (
    ImportedMeetingService(
        workspace_service=workspace_service,
        transcript_service=transcript_service,
        transcript_storage_service=(
            transcript_storage_service
        ),
        meeting_pipeline=meeting_pipeline,
    )
)


# Controladores
meeting_controller = MeetingController(
    state=app_state,
    bus=event_bus,
    logger=logger,
    audio_capture_service=audio_capture_service,
    meeting_timer=meeting_timer,
    meeting_finalization_service=(
        meeting_finalization_service
    ),
    task_runner=task_runner,
)

import_controller = ImportController(
    state=app_state,
    bus=event_bus,
    logger=logger,
    task_runner=task_runner,
    imported_meeting_service=(
        imported_meeting_service
    ),
)

setup_controller = SetupController(
    state=app_state,
    bus=event_bus,
    logger=logger,
    task_runner=task_runner,
    setup_wizard_service=setup_wizard_service,
)


# Registro de servicios
container.register(
    "event_bus",
    event_bus,
)

container.register(
    "app_state",
    app_state,
)

container.register(
    "logger",
    logger,
)

container.register(
    "configuration",
    configuration,
)

container.register(
    "audio_capture_service",
    audio_capture_service,
)

container.register(
    "meeting_timer",
    meeting_timer,
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

container.register(
    "task_runner",
    task_runner,
)

container.register(
    "workspace_service",
    workspace_service,
)

container.register(
    "transcript_service",
    transcript_service,
)

container.register(
    "transcript_storage_service",
    transcript_storage_service,
)

container.register(
    "transcript_analyzer",
    transcript_analyzer,
)

container.register(
    "transcript_validator",
    transcript_validator,
)

container.register(
    "artifact_storage_service",
    artifact_storage_service,
)

container.register(
    "transcript_chunker",
    transcript_chunker,
)

container.register(
    "staged_chunk_knowledge_service",
    staged_chunk_knowledge_service,
)

container.register(
    "meeting_knowledge_assembler",
    meeting_knowledge_assembler,
)

container.register(
    "meeting_report_validator",
    meeting_report_validator,
)

container.register(
    "staged_meeting_report_consolidation_service",
    staged_meeting_report_consolidation_service,
)

container.register(
    "meeting_report_generator",
    meeting_report_generator,
)

container.register(
    "meeting_report_projection_service",
    meeting_report_projection_service,
)

container.register(
    "meeting_report_markdown_exporter",
    meeting_report_markdown_exporter,
)

container.register(
    "meeting_report_docx_exporter",
    meeting_report_docx_exporter,
)

container.register(
    "meeting_report_pdf_exporter",
    meeting_report_pdf_exporter,
)

container.register(
    "meeting_artifact_delivery_service",
    meeting_artifact_delivery_service,
)

container.register(
    "meeting_pipeline",
    meeting_pipeline,
)

container.register(
    "imported_meeting_service",
    imported_meeting_service,
)

container.register(
    "meeting_finalization_service",
    meeting_finalization_service,
)

container.register(
    "meeting_controller",
    meeting_controller,
)

container.register(
    "import_controller",
    import_controller,
)

container.register(
    "setup_controller",
    setup_controller,
)
