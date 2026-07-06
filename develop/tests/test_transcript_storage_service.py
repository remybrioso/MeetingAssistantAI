from pathlib import Path

from services.transcript_storage_service import TranscriptStorageService
from services.transcript_service import TranscriptService
from models.recording_session import RecordingSession


session_dirs = sorted(
    Path("output").glob("meeting_*"),
    reverse=True
)

if not session_dirs:
    raise FileNotFoundError("No existen reuniones.")

latest = session_dirs[0]


class ExistingRecordingSession(RecordingSession):

    def __post_init__(self):

        self.session_dir = latest
        self.session_name = latest.name

        self.mic_file = latest / "mic.wav"
        self.system_file = latest / "system.wav"
        self.meeting_file = latest / "meeting.wav"
        self.metadata_file = latest / "metadata.json"


session = ExistingRecordingSession()

transcript_service = TranscriptService()

storage = TranscriptStorageService()

transcript = transcript_service.transcribe_microphone(session)

output_file = session.session_dir / "transcript.json"

storage.save(
    transcript,
    output_file
)

loaded = storage.load(output_file)

print(loaded.as_dict())

assert len(loaded.segments) == len(transcript.segments)

print()
print("Prueba satisfactoria.")