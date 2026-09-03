from pathlib import Path
from types import SimpleNamespace

import pytest

from exceptions.insufficient_meeting_evidence_error import (
    InsufficientMeetingEvidenceError,
)
from exceptions.insufficient_transcript_evidence_error import (
    InsufficientTranscriptEvidenceError,
)
from models.transcript import Segment, Transcript
from services.meeting_pipeline_service import (
    MeetingPipelineService,
)


class FakeTranscriptStorageService:

    def __init__(
        self,
        transcript,
    ) -> None:
        self.transcript = transcript
        self.loaded_filename = None

    def load(
        self,
        filename,
    ):
        self.loaded_filename = filename

        return self.transcript


class FakeTranscriptAnalyzer:

    def __init__(
        self,
    ) -> None:
        self.received_transcript = None
        self.analysis = object()

    def analyze(
        self,
        transcript,
    ):
        self.received_transcript = transcript

        return self.analysis


class FakeTranscriptValidator:

    def __init__(
        self,
        valid: bool = True,
        errors: list[str] | None = None,
    ) -> None:
        self.valid = valid
        self.errors = (
            errors
            if errors is not None
            else []
        )

        self.received_analysis = None

    def validate(
        self,
        analysis,
    ):
        self.received_analysis = analysis

        return (
            self.valid,
            self.errors,
        )


class FakeArtifactGenerator:

    def __init__(
        self,
    ) -> None:
        self.received_transcript = None
        self.artifact = object()

    def generate(
        self,
        transcript,
    ):
        self.received_transcript = transcript

        return self.artifact


class FakeArtifactDeliveryService:

    def __init__(
        self,
    ) -> None:
        self.received_report = None
        self.received_workspace = None

    def deliver(
        self,
        report,
        workspace,
    ) -> None:
        self.received_report = report
        self.received_workspace = workspace


def build_transcript() -> Transcript:
    transcript = Transcript()

    transcript.add_segment(
        Segment(
            start=0.0,
            end=4.5,
            speaker="SPEAKER_00",
            text=(
                "Esta es una transcripción suficientemente "
                "extensa para probar el pipeline."
            ),
        )
    )

    return transcript


def build_pipeline(
    tmp_path: Path,
    *,
    transcript_valid: bool = True,
    transcript_errors: list[str] | None = None,
):
    transcript = build_transcript()

    transcript_storage = FakeTranscriptStorageService(
        transcript
    )

    transcript_analyzer = FakeTranscriptAnalyzer()

    transcript_validator = FakeTranscriptValidator(
        valid=transcript_valid,
        errors=transcript_errors,
    )

    artifact_generator = FakeArtifactGenerator()

    delivery_service = FakeArtifactDeliveryService()

    workspace = SimpleNamespace(
        transcript_json=(
            tmp_path
            / ".mai"
            / "transcript.json"
        ),
    )

    recording_session = SimpleNamespace(
        workspace=workspace
    )

    pipeline = MeetingPipelineService(
        artifact_generator=artifact_generator,
        artifact_delivery_service=(
            delivery_service
        ),
        transcript_storage_service=(
            transcript_storage
        ),
        transcript_analyzer=(
            transcript_analyzer
        ),
        transcript_validator=(
            transcript_validator
        ),
    )

    return (
        pipeline,
        recording_session,
        transcript,
        transcript_storage,
        transcript_analyzer,
        transcript_validator,
        artifact_generator,
        delivery_service,
        workspace,
    )


def test_meeting_pipeline_service_can_be_created() -> None:
    pipeline = MeetingPipelineService(
        artifact_generator=object(),
        artifact_delivery_service=object(),
    )

    assert pipeline is not None


def test_pipeline_loads_and_validates_transcript(
    tmp_path: Path,
) -> None:
    (
        pipeline,
        recording_session,
        transcript,
        transcript_storage,
        transcript_analyzer,
        transcript_validator,
        _,
        _,
        workspace,
    ) = build_pipeline(
        tmp_path
    )

    pipeline.process(
        recording_session
    )

    assert (
        transcript_storage.loaded_filename
        == workspace.transcript_json
    )

    assert (
        transcript_analyzer.received_transcript
        is transcript
    )

    assert (
        transcript_validator.received_analysis
        is transcript_analyzer.analysis
    )


def test_pipeline_generates_artifact_from_transcript(
    tmp_path: Path,
) -> None:
    (
        pipeline,
        recording_session,
        transcript,
        _,
        _,
        _,
        artifact_generator,
        _,
        _,
    ) = build_pipeline(
        tmp_path
    )

    pipeline.process(
        recording_session
    )

    assert (
        artifact_generator.received_transcript
        is transcript
    )


def test_pipeline_delegates_artifact_delivery(
    tmp_path: Path,
) -> None:
    (
        pipeline,
        recording_session,
        _,
        _,
        _,
        _,
        artifact_generator,
        delivery_service,
        workspace,
    ) = build_pipeline(
        tmp_path
    )

    pipeline.process(
        recording_session
    )

    assert (
        delivery_service.received_report
        is artifact_generator.artifact
    )

    assert (
        delivery_service.received_workspace
        is workspace
    )


def test_pipeline_returns_generated_artifact(
    tmp_path: Path,
) -> None:
    (
        pipeline,
        recording_session,
        _,
        _,
        _,
        _,
        artifact_generator,
        _,
        _,
    ) = build_pipeline(
        tmp_path
    )

    result = pipeline.process(
        recording_session
    )

    assert (
        result
        is artifact_generator.artifact
    )


def test_pipeline_stops_when_transcript_is_invalid(
    tmp_path: Path,
) -> None:
    (
        pipeline,
        recording_session,
        _,
        _,
        _,
        _,
        artifact_generator,
        delivery_service,
        _,
    ) = build_pipeline(
        tmp_path,
        transcript_valid=False,
        transcript_errors=[
            "Transcript demasiado corto.",
            "No existe evidencia suficiente.",
        ],
    )

    with pytest.raises(
        InsufficientTranscriptEvidenceError,
    ) as error:
        pipeline.process(
            recording_session
        )

    message = str(
        error.value
    )

    assert isinstance(
        error.value,
        InsufficientMeetingEvidenceError,
    )

    assert (
        "Transcript demasiado corto."
        in message
    )

    assert (
        "No existe evidencia suficiente."
        in message
    )

    assert (
        artifact_generator.received_transcript
        is None
    )

    assert (
        delivery_service.received_report
        is None
    )

    assert (
        delivery_service.received_workspace
        is None
    )


@pytest.mark.parametrize(
    (
        "missing_dependency",
        "kwargs",
    ),
    [
        (
            "artifact_generator",
            {
                "artifact_generator": None,
                "artifact_delivery_service": object(),
            },
        ),
        (
            "artifact_delivery_service",
            {
                "artifact_generator": object(),
                "artifact_delivery_service": None,
            },
        ),
    ],
)
def test_pipeline_rejects_missing_dependency(
    missing_dependency: str,
    kwargs: dict,
) -> None:
    with pytest.raises(
        ValueError,
        match=missing_dependency,
    ):
        MeetingPipelineService(
            **kwargs
        )
