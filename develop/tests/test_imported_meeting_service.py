from pathlib import Path

from services.artifact_storage_service import (
    ArtifactStorageService
)
from services.imported_meeting_service import (
    ImportedMeetingService
)
from services.meeting_pipeline_service import (
    MeetingPipelineService
)
from services.summary_markdown_exporter import (
    SummaryMarkdownExporter
)
from services.summary_service import SummaryService
from services.transcript_service import TranscriptService
from services.validators.summary_validator import (
    SummaryValidator
)
from services.workspace_service import WorkspaceService


def find_test_wav() -> Path:

    candidates = list(
        Path("output").glob(
            "meeting_*/mic.wav"
        )
    )

    candidates.extend(
        Path("output").glob(
            "meeting_*/Audio/Reunion.wav"
        )
    )

    candidates = [
        file
        for file in candidates
        if file.exists() and file.stat().st_size > 0
    ]

    if not candidates:
        raise FileNotFoundError(
            "No se encontró un WAV para la prueba. "
            "Coloca uno en output/meeting_*/mic.wav "
            "o en output/meeting_*/Audio/Reunion.wav."
        )

    return max(
        candidates,
        key=lambda file: file.stat().st_mtime
    )


meeting_pipeline = MeetingPipelineService(
    summary_service=SummaryService(),
    validator=SummaryValidator(),
    storage_service=ArtifactStorageService(),
    markdown_exporter=SummaryMarkdownExporter()
)

service = ImportedMeetingService(
    workspace_service=WorkspaceService(),
    transcript_service=TranscriptService(),
    meeting_pipeline=meeting_pipeline
)

source_file = find_test_wav()

print(f"Importando: {source_file}")

session = service.import_wav(
    source_file
)

workspace = session.workspace

assert workspace.meeting_audio.exists()
assert workspace.transcript_json.exists()
assert workspace.processing_metrics_json.exists()
assert workspace.summary_json.exists()
assert workspace.summary_markdown.exists()

print()
print("Workspace generado:")
print(workspace.root_dir)

print()
print("Archivos:")
print(f"- {workspace.meeting_audio}")
print(f"- {workspace.transcript_json}")
print(f"- {workspace.processing_metrics_json}")
print(f"- {workspace.summary_json}")
print(f"- {workspace.summary_markdown}")

print()
print("Reunión WAV importada correctamente.")