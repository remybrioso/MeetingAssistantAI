from pathlib import Path

import pytest

from models.recording_session import RecordingSession
from services.artifact_storage_service import ArtifactStorageService
from services.meeting_pipeline_service import MeetingPipelineService
from services.summary_markdown_exporter import SummaryMarkdownExporter
from services.summary_service import SummaryService
from services.validators.summary_validator import SummaryValidator
from services.workspace_service import WorkspaceService


@pytest.mark.integration
def test_meeting_pipeline_processes_latest_existing_meeting() -> None:
    session_dirs = sorted(
        Path("output").glob("meeting_*"),
        reverse=True,
    )

    if not session_dirs:
        pytest.skip(
            "No hay reuniones disponibles en output/meeting_*."
        )

    latest = next(
        (
            session_dir
            for session_dir in session_dirs
            if (session_dir / ".mai" / "transcript.json").exists()
        ),
        None,
    )

    if latest is None:
        pytest.skip(
            "No existe una reunión con transcript.json."
        )

    class ExistingRecordingSession(RecordingSession):

        def __post_init__(self) -> None:
            self.session_dir = latest
            self.session_name = latest.name

            self.mic_file = latest / "mic.wav"
            self.system_file = latest / "system.wav"
            self.meeting_file = latest / "meeting.wav"
            self.metadata_file = latest / "metadata.json"
            workspace = WorkspaceService().create(latest)
            self.attach_workspace(workspace)

    pipeline = MeetingPipelineService(
        summary_service=SummaryService(),
        validator=SummaryValidator(),
        storage_service=ArtifactStorageService(),
        markdown_exporter=SummaryMarkdownExporter(),
    )

    summary = pipeline.process(
        ExistingRecordingSession()
    )

    session = ExistingRecordingSession()

    summary = pipeline.process(session)

    assert summary is not None
    assert session.workspace.summary_json.exists()
    assert session.workspace.summary_markdown.exists()