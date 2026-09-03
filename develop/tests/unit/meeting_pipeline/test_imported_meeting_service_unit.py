import wave
from pathlib import Path

import pytest

from models.transcript import Segment, Transcript
from services.imported_meeting_service import (
    ImportedMeetingService,
)
from services.workspace_service import WorkspaceService


class FakeTranscriptService:

    def __init__(self) -> None:
        self.received_sources = None
        self.transcript = Transcript(
            segments=[
                Segment(
                    start=0.0,
                    end=0.1,
                    speaker="IMPORTED",
                    text="Reunión importada de prueba.",
                )
            ]
        )

    def transcribe_sources(
        self,
        sources,
    ) -> Transcript:
        self.received_sources = list(
            sources
        )

        return self.transcript


class FakeTranscriptStorageService:

    def __init__(self) -> None:
        self.save_calls = []
        self.save_json_calls = []

    def save(
        self,
        transcript,
        filename,
    ) -> None:
        self.save_calls.append(
            (
                transcript,
                filename,
            )
        )

    def save_json(
        self,
        data,
        filename,
    ) -> None:
        self.save_json_calls.append(
            (
                data,
                filename,
            )
        )


class FakeMeetingPipeline:

    def __init__(self) -> None:
        self.received_session = None

    def process(
        self,
        session,
    ) -> None:
        self.received_session = session


def write_minimal_wav(
    filename: Path,
) -> None:
    filename.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with wave.open(
        str(filename),
        "wb",
    ) as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(8000)
        wav_file.writeframes(
            b"\x00\x00" * 800
        )


def build_service(
    meetings_root: Path,
):
    transcript_service = FakeTranscriptService()
    transcript_storage = (
        FakeTranscriptStorageService()
    )
    meeting_pipeline = FakeMeetingPipeline()

    service = ImportedMeetingService(
        workspace_service=WorkspaceService(),
        transcript_service=transcript_service,
        transcript_storage_service=(
            transcript_storage
        ),
        meeting_pipeline=meeting_pipeline,
        meetings_root=meetings_root,
    )

    return (
        service,
        transcript_service,
        transcript_storage,
        meeting_pipeline,
    )


def test_import_uses_injected_absolute_meetings_root(
    tmp_path: Path,
    monkeypatch,
) -> None:
    meetings_root = (
        tmp_path
        / "OneDrive - Corporate Tenant"
        / "Documents"
        / "Meeting Assistant AI"
        / "Meetings"
    ).resolve()

    installation_directory = (
        tmp_path
        / "Programs"
        / "Meeting Assistant AI"
    )
    installation_directory.mkdir(
        parents=True,
    )

    source_file = (
        tmp_path
        / "Imported Sources"
        / "meeting.wav"
    )
    write_minimal_wav(
        source_file
    )
    source_before = source_file.read_bytes()

    monkeypatch.chdir(
        installation_directory
    )

    (
        service,
        transcript_service,
        transcript_storage,
        meeting_pipeline,
    ) = build_service(
        meetings_root
    )

    session = service.import_wav(
        source_file
    )
    workspace = session.workspace

    assert session.session_dir.parent == meetings_root
    assert session.session_name.startswith(
        "meeting_imported_"
    )
    assert workspace.root_dir == session.session_dir

    workspace_paths = [
        workspace.audio_dir,
        workspace.documents_dir,
        workspace.internal_dir,
        workspace.meeting_audio,
        workspace.transcript_json,
        workspace.processing_metrics_json,
    ]

    assert all(
        path.is_relative_to(
            session.session_dir
        )
        for path in workspace_paths
    )

    assert workspace.meeting_audio.read_bytes() == source_before
    assert source_file.read_bytes() == source_before

    assert transcript_service.received_sources is not None
    assert len(
        transcript_service.received_sources
    ) == 1
    assert (
        transcript_service
        .received_sources[0]
        .file
        == workspace.meeting_audio
    )

    assert transcript_storage.save_calls == [
        (
            transcript_service.transcript,
            workspace.transcript_json,
        )
    ]
    assert (
        transcript_storage
        .save_json_calls[0][1]
        == workspace.processing_metrics_json
    )
    assert meeting_pipeline.received_session is session

    assert not (
        installation_directory
        / "output"
    ).exists()


def test_constructor_requires_meetings_root() -> None:
    with pytest.raises(
        TypeError,
        match="meetings_root",
    ):
        ImportedMeetingService(
            workspace_service=object(),
            transcript_service=object(),
            transcript_storage_service=object(),
            meeting_pipeline=object(),
        )


def test_constructor_rejects_non_path_meetings_root() -> None:
    with pytest.raises(
        TypeError,
        match="meetings_root",
    ):
        ImportedMeetingService(
            workspace_service=object(),
            transcript_service=object(),
            transcript_storage_service=object(),
            meeting_pipeline=object(),
            meetings_root="output",
        )


def test_constructor_rejects_relative_meetings_root() -> None:
    with pytest.raises(
        ValueError,
        match="absoluta",
    ):
        ImportedMeetingService(
            workspace_service=object(),
            transcript_service=object(),
            transcript_storage_service=object(),
            meeting_pipeline=object(),
            meetings_root=Path("output"),
        )
