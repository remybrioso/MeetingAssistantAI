import wave
from pathlib import Path

import pytest

from exceptions.insufficient_meeting_semantic_evidence_error import (
    InsufficientMeetingSemanticEvidenceError,
)
from models.transcript import Segment, Transcript
from services.imported_meeting_service import (
    ImportedMeetingService,
)
from services.meeting_pipeline_service import (
    MeetingPipelineService,
)
from services.transcript_storage_service import (
    TranscriptStorageService,
)
from services.workspace_service import WorkspaceService


class FakeTranscriptService:

    def transcribe_sources(
        self,
        sources,
    ) -> Transcript:
        return Transcript(
            segments=[
                Segment(
                    start=0.0,
                    end=0.1,
                    speaker="IMPORTED",
                    text=(
                        "Se importó una reunión para validar "
                        "su workspace canónico."
                    ),
                )
            ]
        )


class FakeTranscriptAnalyzer:

    def analyze(
        self,
        transcript,
    ):
        return transcript


class FakeTranscriptValidator:

    def validate(
        self,
        analysis,
    ) -> tuple[bool, list[str]]:
        return (
            True,
            [],
        )


class FakeArtifactGenerator:

    def __init__(self) -> None:
        self.artifact = object()

    def generate(
        self,
        transcript,
    ):
        return self.artifact


class FakeArtifactDeliveryService:

    def __init__(self) -> None:
        self.received_report = None
        self.received_workspace = None

    def deliver(
        self,
        report,
        workspace,
    ) -> None:
        self.received_report = report
        self.received_workspace = workspace


class FailingMeetingPipeline:

    def __init__(
        self,
        error: Exception,
    ) -> None:
        self.error = error
        self.received_session = None

    def process(
        self,
        session,
    ) -> None:
        self.received_session = session
        raise self.error


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


@pytest.mark.integration
def test_imported_meeting_service_imports_wav_under_controlled_root(
    tmp_path: Path,
    monkeypatch,
) -> None:
    source_file = (
        tmp_path
        / "source"
        / "meeting.wav"
    )
    write_minimal_wav(
        source_file
    )

    meetings_root = (
        tmp_path
        / "Canonical Meetings"
    ).resolve()

    simulated_install_directory = (
        tmp_path
        / "Installed Application"
    )
    simulated_install_directory.mkdir()
    monkeypatch.chdir(
        simulated_install_directory
    )

    transcript_storage_service = (
        TranscriptStorageService()
    )
    artifact_generator = FakeArtifactGenerator()
    artifact_delivery_service = (
        FakeArtifactDeliveryService()
    )

    meeting_pipeline = MeetingPipelineService(
        artifact_generator=artifact_generator,
        artifact_delivery_service=(
            artifact_delivery_service
        ),
        transcript_storage_service=(
            transcript_storage_service
        ),
        transcript_analyzer=FakeTranscriptAnalyzer(),
        transcript_validator=FakeTranscriptValidator(),
    )

    service = ImportedMeetingService(
        workspace_service=WorkspaceService(),
        transcript_service=FakeTranscriptService(),
        transcript_storage_service=(
            transcript_storage_service
        ),
        meeting_pipeline=meeting_pipeline,
        meetings_root=meetings_root,
    )

    session = service.import_wav(
        source_file
    )
    workspace = session.workspace

    assert session.session_dir.parent == meetings_root
    assert workspace.root_dir == session.session_dir
    assert workspace.meeting_audio.is_file()
    assert workspace.transcript_json.is_file()
    assert workspace.processing_metrics_json.is_file()

    assert (
        artifact_delivery_service.received_report
        is artifact_generator.artifact
    )
    assert (
        artifact_delivery_service.received_workspace
        is workspace
    )

    assert not (
        simulated_install_directory
        / "output"
    ).exists()


@pytest.mark.integration
def test_import_preserves_workspace_before_insufficient_evidence_outcome(
    tmp_path: Path,
) -> None:
    source_file = (
        tmp_path
        / "source"
        / "non_meeting.wav"
    )
    write_minimal_wav(
        source_file
    )
    source_bytes = source_file.read_bytes()

    meetings_root = (
        tmp_path
        / "Canonical Meetings"
    ).resolve()

    expected_error = (
        InsufficientMeetingSemanticEvidenceError(
            source_chunk_count=1,
            content_chunk_count=0,
        )
    )
    pipeline = FailingMeetingPipeline(
        expected_error
    )

    service = ImportedMeetingService(
        workspace_service=WorkspaceService(),
        transcript_service=FakeTranscriptService(),
        transcript_storage_service=(
            TranscriptStorageService()
        ),
        meeting_pipeline=pipeline,
        meetings_root=meetings_root,
    )

    with pytest.raises(
        InsufficientMeetingSemanticEvidenceError,
    ) as error:
        service.import_wav(
            source_file
        )

    assert error.value is expected_error
    assert source_file.read_bytes() == source_bytes

    session_directories = list(
        meetings_root.glob(
            "meeting_imported_*"
        )
    )
    assert len(session_directories) == 1

    session_dir = session_directories[0]
    assert pipeline.received_session is not None
    assert pipeline.received_session.session_dir == session_dir

    workspace = pipeline.received_session.workspace
    assert workspace.workspace_manifest.is_file()
    assert workspace.meeting_audio.read_bytes() == source_bytes
    assert workspace.transcript_json.is_file()
    assert workspace.processing_metrics_json.is_file()

    assert not workspace.meeting_report_json.exists()
    assert not workspace.action_items_json.exists()
    assert not workspace.decisions_json.exists()
    assert not workspace.meeting_report_markdown.exists()
    assert not workspace.meeting_minutes_docx.exists()
    assert not workspace.meeting_pdf.exists()
