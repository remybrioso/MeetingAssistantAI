from pathlib import Path

from models.recording_session import RecordingSession
from services.meeting_finalization_service import (
    MeetingFinalizationService,
)


session_dirs = sorted(
    Path("output").glob("meeting_*"),
    reverse=True
)

if not session_dirs:
    raise FileNotFoundError(
        "No existen reuniones."
    )

latest = session_dirs[0]


class ExistingRecordingSession(RecordingSession):

    def __post_init__(self):

        self.session_dir = latest
        self.session_name = latest.name

        self.mic_file = latest / "mic.wav"
        self.system_file = latest / "system.wav"
        self.meeting_file = latest / "meeting.wav"
        self.metadata_file = latest / "metadata.json"


service = MeetingFinalizationService()

session = ExistingRecordingSession()

transcript = service.finalize(session)

assert (latest / "transcript.json").exists()

print()
print("Transcript generado correctamente.")
print("Segmentos:", len(transcript.segments))
print()
print("Prueba satisfactoria.")