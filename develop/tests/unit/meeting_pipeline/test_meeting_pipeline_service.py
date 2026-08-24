from pathlib import Path
from types import SimpleNamespace

import pytest

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


class FakeArtifactStorageService:

    def __init__(
        self,
    ) -> None:
        self.saved_artifact = None
        self.saved_filename = None

    def save(
        self,
        artifact,
        filename,
    ) -> None:
        self.saved_artifact = artifact
        self.saved_filename = filename


class FakeMarkdownExporter:

    def __init__(
        self,
    ) -> None:
        self.exported_artifact = None
        self.exported_filename = None

    def export(
        self,
        artifact,
        filename,
    ) -> None:
        self.exported_artifact = artifact
        self.exported_filename = filename


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

    storage_service = FakeArtifactStorageService()

    markdown_exporter = FakeMarkdownExporter()

    workspace = SimpleNamespace(
        transcript_json=(
            tmp_path
            / ".mai"
            / "transcript.json"
        ),
        meeting_report_json=(
            tmp_path
            / ".mai"
            / "meeting_report.json"
        ),
        meeting_report_markdown=(
            tmp_path
            / "Documentos"
            / "Meeting Report.md"
        ),
    )

    recording_session = SimpleNamespace(
        workspace=workspace
    )

    pipeline = MeetingPipelineService(
        artifact_generator=artifact_generator,
        storage_service=storage_service,
        markdown_exporter=markdown_exporter,
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
        storage_service,
        markdown_exporter,
        workspace,
    )


def test_meeting_pipeline_service_can_be_created() -> None:
    pipeline = MeetingPipelineService(
        artifact_generator=object(),
        storage_service=object(),
        markdown_exporter=object(),
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
        _,
    ) = build_pipeline(
        tmp_path
    )

    result = pipeline.process(
        recording_session
    )

    assert (
        artifact_generator.received_transcript
        is transcript
    )

    assert (
        result
        is artifact_generator.artifact
    )


def test_pipeline_persists_meeting_report_json(
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
        storage_service,
        _,
        workspace,
    ) = build_pipeline(
        tmp_path
    )

    pipeline.process(
        recording_session
    )

    assert (
        storage_service.saved_artifact
        is artifact_generator.artifact
    )

    assert (
        storage_service.saved_filename
        == workspace.meeting_report_json
    )


def test_pipeline_exports_meeting_report_markdown(
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
        markdown_exporter,
        workspace,
    ) = build_pipeline(
        tmp_path
    )

    pipeline.process(
        recording_session
    )

    assert (
        markdown_exporter.exported_artifact
        is artifact_generator.artifact
    )

    assert (
        markdown_exporter.exported_filename
        == workspace.meeting_report_markdown
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
        storage_service,
        markdown_exporter,
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
        storage_service.saved_artifact
        is None
    )

    assert (
        markdown_exporter.exported_artifact
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
                "storage_service": object(),
                "markdown_exporter": object(),
            },
        ),
        (
            "storage_service",
            {
                "artifact_generator": object(),
                "storage_service": None,
                "markdown_exporter": object(),
            },
        ),
        (
            "markdown_exporter",
            {
                "artifact_generator": object(),
                "storage_service": object(),
                "markdown_exporter": None,
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