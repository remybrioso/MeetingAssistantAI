from pathlib import Path

import pytest

from models.recording_session import RecordingSession
from services.meeting_finalization_service import (
    MeetingFinalizationService,
)
from services.workspace_service import WorkspaceService
from services.artifact_storage_service import (
    ArtifactStorageService,
)
from services.meeting_pipeline_service import (
    MeetingPipelineService,
)
from services.summary_markdown_exporter import (
    SummaryMarkdownExporter,
)
from services.summary_service import SummaryService
from services.transcript_analyzer import TranscriptAnalyzer
from services.transcript_prompt_formatter import (
    TranscriptPromptFormatter,
)
from services.transcript_service import TranscriptService
from services.transcript_storage_service import (
    TranscriptStorageService,
)
from services.transcript_validator import TranscriptValidator
from services.validators.summary_validator import (
    SummaryValidator,
)


@pytest.mark.integration
def test_meeting_finalization_generates_transcript_for_existing_meeting() -> None:
    session_dirs = sorted(
        Path("output").glob("meeting_*"),
        reverse=True,
    )

    latest = next(
    (
        session_dir
        for session_dir in session_dirs
        if all(
            (
                session_dir / "Audio" / filename
            ).exists()
            for filename in (
                "Microfono.wav",
                "Sistema.wav",
                "Reunion.wav",
            )
        )
    ),
    None,
)

    if latest is None:
        pytest.skip(
            "No existe una reunión con los tres archivos de audio."
        )

    class ExistingRecordingSession(RecordingSession):

        def __post_init__(self) -> None:
            self.session_dir = latest
            self.session_name = latest.name

            workspace = WorkspaceService().create(latest)
            self.attach_workspace(workspace)

    transcript_storage_service = (
    TranscriptStorageService()
)

    meeting_pipeline = MeetingPipelineService(
        summary_service=SummaryService(),
        transcript_storage_service=(
            transcript_storage_service
        ),
        transcript_analyzer=TranscriptAnalyzer(),
        transcript_validator=TranscriptValidator(),
        transcript_prompt_formatter=(
            TranscriptPromptFormatter()
        ),
        summary_validator=SummaryValidator(),
        storage_service=ArtifactStorageService(),
        markdown_exporter=SummaryMarkdownExporter(),
    )

    service = MeetingFinalizationService(
        transcript_service=TranscriptService(),
        transcript_storage_service=(
            transcript_storage_service
        ),
        workspace_service=WorkspaceService(),
        meeting_pipeline=meeting_pipeline,
    )
    session = ExistingRecordingSession()

    transcript = service.finalize(session)

    assert transcript is not None
    assert session.workspace.transcript_json.exists()
    assert len(transcript.segments) > 0