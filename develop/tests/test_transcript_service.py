from pathlib import Path

from models.recording_session import RecordingSession
from services.transcript_service import TranscriptService


session_dirs = sorted(
    Path("output").glob("meeting_*"),
    reverse=True
)

if not session_dirs:
    raise FileNotFoundError(
        "No hay sesiones en output/meeting_*"
    )

latest_session_dir = session_dirs[0]

mic_file = latest_session_dir / "mic.wav"

if not mic_file.exists():
    raise FileNotFoundError(
        f"No existe {mic_file}"
    )


class ExistingRecordingSession(RecordingSession):

    def __post_init__(self):
        self.session_dir = latest_session_dir
        self.session_name = latest_session_dir.name

        self.mic_file = self.session_dir / "mic.wav"
        self.system_file = self.session_dir / "system.wav"
        self.meeting_file = self.session_dir / "meeting.wav"
        self.metadata_file = self.session_dir / "metadata.json"


session = ExistingRecordingSession()

service = TranscriptService()

transcript = service.transcribe_microphone(session)

print(transcript.as_dict())

assert len(transcript.segments) > 0

print()
print("Segmentos:", len(transcript.segments))
print("Prueba satisfactoria.")