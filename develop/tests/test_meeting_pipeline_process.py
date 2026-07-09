from pathlib import Path

from models.recording_session import RecordingSession
from services.meeting_pipeline_service import MeetingPipelineService
from services.summary_service import SummaryService
from services.validators.summary_validator import SummaryValidator
from services.artifact_storage_service import ArtifactStorageService
from services.summary_markdown_exporter import SummaryMarkdownExporter


session_dirs = sorted(
    Path("output").glob("meeting_*"),
    reverse=True
)

if not session_dirs:
    raise FileNotFoundError(
        "No hay reuniones en output/meeting_*"
    )

latest = session_dirs[0]

transcript_file = latest / "transcript.json"

if not transcript_file.exists():
    raise FileNotFoundError(
        f"No existe {transcript_file}"
    )


class ExistingRecordingSession(RecordingSession):

    def __post_init__(self):

        self.session_dir = latest
        self.session_name = latest.name

        self.mic_file = latest / "mic.wav"
        self.system_file = latest / "system.wav"
        self.meeting_file = latest / "meeting.wav"
        self.metadata_file = latest / "metadata.json"


pipeline = MeetingPipelineService(
    summary_service=SummaryService(),
    validator=SummaryValidator(),
    storage_service=ArtifactStorageService(),
    markdown_exporter=SummaryMarkdownExporter()
)

session = ExistingRecordingSession()

summary = pipeline.process(session)

artifacts_dir = latest / "artifacts"

assert (artifacts_dir / "summary.json").exists()
assert (artifacts_dir / "summary.md").exists()

print(summary.as_dict())

print()
print("MeetingPipelineService ejecutado correctamente.")