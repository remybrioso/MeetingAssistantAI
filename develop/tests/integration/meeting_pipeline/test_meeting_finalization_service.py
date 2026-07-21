from pathlib import Path

import pytest

from models.recording_session import RecordingSession
from services.meeting_finalization_service import (
    MeetingFinalizationService,
)
from services.workspace_service import WorkspaceService


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

    service = MeetingFinalizationService()
    session = ExistingRecordingSession()

    transcript = service.finalize(session)

    assert transcript is not None
    assert session.workspace.transcript_json.exists()
    assert len(transcript.segments) > 0