from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from exceptions.insufficient_meeting_semantic_evidence_error import (
    InsufficientMeetingSemanticEvidenceError,
)
from exceptions.insufficient_transcript_evidence_error import (
    InsufficientTranscriptEvidenceError,
)
from models.recording_session import RecordingSession
from models.transcript import Segment, Transcript, Word
from services.meeting_finalization_service import (
    MeetingFinalizationService,
)
from services.transcript_storage_service import (
    TranscriptStorageService,
)
from services.workspace_service import WorkspaceService


class FakeTranscriptService:
    """
    Sustituye únicamente el proveedor pesado de transcripción.

    El resto del flujo de finalización usa servicios reales.
    """

    def __init__(self) -> None:
        self.received_sources = None

    def transcribe_sources(
        self,
        sources,
    ) -> Transcript:
        self.received_sources = list(
            sources
        )

        return Transcript(
            segments=[
                Segment(
                    start=0.0,
                    end=1.0,
                    speaker="LOCAL",
                    text=(
                        "Se validó el flujo de "
                        "finalización de la reunión."
                    ),
                    words=[
                        Word(
                            start=0.0,
                            end=0.4,
                            text="Se",
                            confidence=0.99,
                        ),
                        Word(
                            start=0.4,
                            end=1.0,
                            text="validó",
                            confidence=0.98,
                        ),
                    ],
                )
            ]
        )


class FakeMeetingPipeline:

    def __init__(
        self,
        error: Exception | None = None,
    ) -> None:
        self.received_session = None
        self.error = error

    def process(
        self,
        recording_session,
    ) -> None:
        self.received_session = (
            recording_session
        )

        if self.error is not None:
            raise self.error


class FakeBus:

    def __init__(self) -> None:
        self.events = []

    def emit(
        self,
        event_name,
        *args,
    ) -> None:
        self.events.append(
            (
                event_name,
                args,
            )
        )


class FakeLogger:

    def __init__(self) -> None:
        self.warnings = []
        self.errors = []

    def warning(
        self,
        message,
    ) -> None:
        self.warnings.append(
            message
        )

    def error(
        self,
        message,
    ) -> None:
        self.errors.append(
            message
        )


def _write_audio(
    path: Path,
    *,
    seconds: float = 1.0,
    sample_rate: int = 16000,
) -> None:
    sample_count = int(
        seconds
        * sample_rate
    )

    audio = np.zeros(
        sample_count,
        dtype=np.float32,
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    sf.write(
        str(path),
        audio,
        sample_rate,
    )


@pytest.mark.integration
def test_meeting_finalization_is_self_contained_and_uses_current_pipeline(
    tmp_path: Path,
) -> None:
    session = RecordingSession(
        base_output_dir=str(
            tmp_path
        ),
        session_prefix="meeting_finalize_e2e",
    )

    workspace_service = (
        WorkspaceService()
    )

    workspace = (
        workspace_service.create(
            session.session_dir
        )
    )

    session.attach_workspace(
        workspace
    )

    _write_audio(
        workspace.microphone_audio,
    )

    _write_audio(
        workspace.meeting_audio,
    )

    transcript_service = (
        FakeTranscriptService()
    )

    meeting_pipeline = (
        FakeMeetingPipeline()
    )

    transcript_storage_service = (
        TranscriptStorageService()
    )

    service = MeetingFinalizationService(
        transcript_service=(
            transcript_service
        ),
        transcript_storage_service=(
            transcript_storage_service
        ),
        workspace_service=(
            workspace_service
        ),
        meeting_pipeline=(
            meeting_pipeline
        ),
        logger=FakeLogger(),
    )

    transcript = service.finalize(
        session
    )

    assert transcript is not None

    assert (
        session.workspace
        is workspace
    )

    assert (
        workspace.transcript_json.exists()
    )

    assert (
        workspace.processing_metrics_json.exists()
    )

    stored_transcript = (
        transcript_storage_service.load(
            workspace.transcript_json
        )
    )

    assert (
        stored_transcript.as_dict()
        == transcript.as_dict()
    )

    assert (
        transcript_service.received_sources
        is not None
    )

    assert len(
        transcript_service.received_sources
    ) == 1

    assert (
        transcript_service
        .received_sources[0]
        .speaker
        == "LOCAL"
    )

    assert (
        transcript_service
        .received_sources[0]
        .file
        == workspace.microphone_audio
    )

    assert (
        meeting_pipeline.received_session
        is session
    )


def _build_finalization_case(
    tmp_path: Path,
    pipeline_error: Exception,
):
    session = RecordingSession(
        base_output_dir=str(
            tmp_path
        ),
        session_prefix="meeting_finalize_failure",
    )

    workspace_service = WorkspaceService()
    workspace = workspace_service.create(
        session.session_dir
    )
    session.attach_workspace(
        workspace
    )

    _write_audio(
        workspace.microphone_audio
    )
    _write_audio(
        workspace.meeting_audio
    )

    bus = FakeBus()
    logger = FakeLogger()
    pipeline = FakeMeetingPipeline(
        error=pipeline_error
    )

    service = MeetingFinalizationService(
        transcript_service=FakeTranscriptService(),
        transcript_storage_service=(
            TranscriptStorageService()
        ),
        workspace_service=workspace_service,
        meeting_pipeline=pipeline,
        logger=logger,
        bus=bus,
    )

    return (
        service,
        session,
        workspace,
        bus,
        logger,
    )


@pytest.mark.integration
@pytest.mark.parametrize(
    "pipeline_error",
    [
        InsufficientTranscriptEvidenceError(
            "Transcript demasiado corto."
        ),
        InsufficientMeetingSemanticEvidenceError(
            source_chunk_count=2,
            content_chunk_count=0,
        ),
    ],
)
def test_expected_insufficient_evidence_preserves_transcript_and_metrics(
    tmp_path: Path,
    pipeline_error: Exception,
) -> None:
    (
        service,
        session,
        workspace,
        bus,
        logger,
    ) = _build_finalization_case(
        tmp_path=tmp_path,
        pipeline_error=pipeline_error,
    )

    transcript = service.finalize(
        session
    )

    assert transcript is not None
    assert workspace.microphone_audio.is_file()
    assert workspace.transcript_json.is_file()
    assert workspace.processing_metrics_json.is_file()
    assert workspace.workspace_manifest.is_file()

    event_names = [
        event_name
        for event_name, _ in bus.events
    ]

    assert event_names[-1] == (
        "meeting_processing_insufficient_evidence"
    )
    assert "meeting_processing_failed" not in event_names
    assert "meeting_processing_completed" not in event_names
    assert bus.events[-1][1] == (
        pipeline_error,
    )

    assert len(logger.warnings) == 1
    assert type(pipeline_error).__name__ in (
        logger.warnings[0]
    )
    assert str(pipeline_error) in logger.warnings[0]
    assert session.session_name in logger.warnings[0]
    assert str(session.session_dir) in logger.warnings[0]
    assert logger.errors == []

    assert not workspace.meeting_report_json.exists()
    assert not workspace.action_items_json.exists()
    assert not workspace.decisions_json.exists()
    assert not workspace.meeting_report_markdown.exists()
    assert not workspace.meeting_minutes_docx.exists()
    assert not workspace.meeting_pdf.exists()


@pytest.mark.integration
@pytest.mark.parametrize(
    "pipeline_error",
    [
        RuntimeError(
            "ollama unavailable"
        ),
        ValueError(
            "malformed model output"
        ),
    ],
)
def test_technical_pipeline_failure_remains_failure(
    tmp_path: Path,
    pipeline_error: Exception,
) -> None:
    (
        service,
        session,
        workspace,
        bus,
        logger,
    ) = _build_finalization_case(
        tmp_path=tmp_path,
        pipeline_error=pipeline_error,
    )

    with pytest.raises(
        type(pipeline_error),
        match=str(pipeline_error),
    ):
        service.finalize(
            session
        )

    assert workspace.transcript_json.is_file()
    assert workspace.processing_metrics_json.is_file()

    event_names = [
        event_name
        for event_name, _ in bus.events
    ]

    assert event_names[-1] == "meeting_processing_failed"
    assert (
        "meeting_processing_insufficient_evidence"
        not in event_names
    )
    assert "meeting_processing_completed" not in event_names
    assert logger.warnings == []
    assert len(logger.errors) == 1
    assert type(pipeline_error).__name__ in logger.errors[0]
    assert str(pipeline_error) in logger.errors[0]
