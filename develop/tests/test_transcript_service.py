from pathlib import Path

from models.audio_source import AudioSource
from services.transcript_service import TranscriptService


session_dirs = sorted(
    Path("output").glob("meeting_*"),
    reverse=True,
)

if not session_dirs:
    raise FileNotFoundError(
        "No hay sesiones en output/meeting_*."
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
        "No existe una sesión con audio de micrófono."
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

service = TranscriptService()

transcript = service.transcribe_sources(
    [
        AudioSource(
            file=mic_file,
            speaker="LOCAL",
        )
    ]
)

print(transcript.as_dict())

assert len(transcript.segments) > 0

print()
print(
    "Archivo transcrito:",
    mic_file,
)

print(
    "Segmentos:",
    len(transcript.segments),
)

print(
    "Prueba satisfactoria."
)