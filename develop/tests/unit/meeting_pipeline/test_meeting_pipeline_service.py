from pathlib import Path
from types import SimpleNamespace

from models.transcript import Segment, Transcript
from services.meeting_pipeline_service import (
    MeetingPipelineService,
)


class FakeTranscriptStorageService:

    def __init__(
        self,
        transcript,
    ):
        self.transcript = transcript
        self.loaded_filename = None

    def load(
        self,
        filename,
    ):
        self.loaded_filename = filename
        return self.transcript


class FakeTranscriptAnalyzer:

    def __init__(self):
        self.received_transcript = None

    def analyze(
        self,
        transcript,
    ):
        self.received_transcript = transcript
        return object()


class FakeTranscriptValidator:

    def validate(
        self,
        analysis,
    ):
        return True, []


class FakeTranscriptPromptFormatter:

    def __init__(self):
        self.received_transcript = None
        self.formatted_text = (
            '{"segments": [{"text": "Contenido"}]}'
        )

    def format(
        self,
        transcript,
    ):
        self.received_transcript = transcript
        return self.formatted_text


class FakeSummaryService:

    def __init__(self):
        self.received_text = None
        self.summary = object()

    def generate(
        self,
        transcript_text,
    ):
        self.received_text = transcript_text
        return self.summary


class FakeSummaryValidator:

    def validate(
        self,
        summary,
    ):
        return True, []


class FakeArtifactStorageService:

    def __init__(self):
        self.saved_data = None
        self.saved_filename = None

    def save(
        self,
        data,
        filename,
    ):
        self.saved_data = data
        self.saved_filename = filename


class FakeMarkdownExporter:

    def __init__(self):
        self.exported_summary = None
        self.exported_filename = None

    def export(
        self,
        summary,
        filename,
    ):
        self.exported_summary = summary
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


def test_meeting_pipeline_service_can_be_created() -> None:
    pipeline = MeetingPipelineService(
        summary_service=object(),
        validator=object(),
        storage_service=object(),
        markdown_exporter=object(),
    )

    assert pipeline is not None


def test_pipeline_uses_formatter_before_summary_service(
    tmp_path: Path,
) -> None:
    transcript = build_transcript()

    transcript_storage = (
        FakeTranscriptStorageService(
            transcript
        )
    )

    transcript_analyzer = FakeTranscriptAnalyzer()
    transcript_validator = FakeTranscriptValidator()

    transcript_formatter = (
        FakeTranscriptPromptFormatter()
    )

    summary_service = FakeSummaryService()
    summary_validator = FakeSummaryValidator()
    artifact_storage = FakeArtifactStorageService()
    markdown_exporter = FakeMarkdownExporter()

    workspace = SimpleNamespace(
        transcript_json=(
            tmp_path / "transcript.json"
        ),
        summary_json=(
            tmp_path / "summary.json"
        ),
        summary_markdown=(
            tmp_path / "summary.md"
        ),
    )

    recording_session = SimpleNamespace(
        workspace=workspace
    )

    pipeline = MeetingPipelineService(
        summary_service=summary_service,
        transcript_storage_service=(
            transcript_storage
        ),
        transcript_analyzer=transcript_analyzer,
        transcript_validator=transcript_validator,
        transcript_prompt_formatter=(
            transcript_formatter
        ),
        summary_validator=summary_validator,
        storage_service=artifact_storage,
        markdown_exporter=markdown_exporter,
    )

    result = pipeline.process(
        recording_session
    )

    assert result is summary_service.summary

    assert (
        transcript_storage.loaded_filename
        == workspace.transcript_json
    )

    assert (
        transcript_analyzer.received_transcript
        is transcript
    )

    assert (
        transcript_formatter.received_transcript
        is transcript
    )

    assert (
        summary_service.received_text
        == transcript_formatter.formatted_text
    )

    assert (
        artifact_storage.saved_data
        is summary_service.summary
    )

    assert (
        artifact_storage.saved_filename
        == workspace.summary_json
    )

    assert (
        markdown_exporter.exported_summary
        is summary_service.summary
    )

    assert (
        markdown_exporter.exported_filename
        == workspace.summary_markdown
    )