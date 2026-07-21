from pathlib import Path

import pytest

from services.artifact_storage_service import (
    ArtifactStorageService,
)
from services.imported_meeting_service import (
    ImportedMeetingService,
)
from services.meeting_pipeline_service import (
    MeetingPipelineService,
)
from services.summary_markdown_exporter import (
    SummaryMarkdownExporter,
)
from services.summary_service import SummaryService
from services.transcript_service import TranscriptService
from services.validators.summary_validator import (
    SummaryValidator,
)
from services.workspace_service import WorkspaceService


def find_test_wav() -> Path | None:
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

    valid_candidates = [
        file
        for file in candidates
        if file.exists()
        and file.stat().st_size > 0
    ]

    if not valid_candidates:
        return None

    return max(
        valid_candidates,
        key=lambda file: file.stat().st_mtime,
    )


@pytest.mark.integration
def test_imported_meeting_service_imports_wav() -> None:
    source_file = find_test_wav()

    if source_file is None:
        pytest.skip(
            "No existe un archivo WAV válido para importar."
        )

    meeting_pipeline = MeetingPipelineService(
        summary_service=SummaryService(),
        validator=SummaryValidator(),
        storage_service=ArtifactStorageService(),
        markdown_exporter=SummaryMarkdownExporter(),
    )

    service = ImportedMeetingService(
        workspace_service=WorkspaceService(),
        transcript_service=TranscriptService(),
        meeting_pipeline=meeting_pipeline,
    )

    session = service.import_wav(
        source_file
    )

    workspace = session.workspace

    assert workspace is not None
    assert workspace.meeting_audio.exists()
    assert workspace.transcript_json.exists()
    assert workspace.processing_metrics_json.exists()
    assert workspace.summary_json.exists()
    assert workspace.summary_markdown.exists()