from pathlib import Path

from models.audio_source import AudioSource
from services.transcript_service import TranscriptService
from services.transcript_storage_service import (
    TranscriptStorageService,
)


session_dirs = sorted(
    Path("output").glob("meeting_*"),
    reverse=True,
)

if not session_dirs:
    raise FileNotFoundError(
        "No existen reuniones en output/meeting_*."
    )

latest_session_dir = next(
    (
        session_dir
        for session_dir in session_dirs
        if (
            session_dir / "mic.wav"
        ).is_file()
        or (
            session_dir / "Audio" / "Microfono.wav"
        ).is_file()
    ),
    None,
)

if latest_session_dir is None:
    raise FileNotFoundError(
        "No existe una reunión con audio de micrófono."
    )

legacy_mic_file = (
    latest_session_dir / "mic.wav"
)

workspace_mic_file = (
    latest_session_dir
    / "Audio"
    / "Microfono.wav"
)

mic_file = (
    workspace_mic_file
    if workspace_mic_file.is_file()
    else legacy_mic_file
)

transcript_service = TranscriptService()
storage_service = TranscriptStorageService()

transcript = transcript_service.transcribe_sources(
    [
        AudioSource(
            file=mic_file,
            speaker="LOCAL",
        )
    ]
)

output_file = (
    latest_session_dir
    / "transcript_storage_test.json"
)

storage_service.save(
    transcript,
    output_file,
)

loaded_transcript = storage_service.load(
    output_file
)

print(
    loaded_transcript.as_dict()
)

assert (
    len(loaded_transcript.segments)
    == len(transcript.segments)
)

assert (
    loaded_transcript.as_dict()
    == transcript.as_dict()
)

print()
print(
    "Archivo utilizado:",
    mic_file,
)

print(
    "Archivo generado:",
    output_file,
)

print(
    "Prueba satisfactoria."
)