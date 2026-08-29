from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

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

    def __init__(self) -> None:
        self.received_session = None

    def process(
        self,
        recording_session,
    ) -> None:
        self.received_session = (
            recording_session
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
