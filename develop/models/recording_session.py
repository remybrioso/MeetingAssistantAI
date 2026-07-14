"""
recording_session.py

Modelo que representa una sesión de grabación.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class RecordingSession:

    base_output_dir: str = "output"
    session_prefix: str = "meeting"
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):

        timestamp = self.created_at.strftime("%Y%m%d_%H%M%S")

        self.session_name = (
        f"{self.session_prefix}_{timestamp}"
    )

        self.session_dir = Path(self.base_output_dir) / self.session_name

        self.session_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.mic_file = self.session_dir / "mic.wav"
        self.system_file = self.session_dir / "system.wav"
        self.meeting_file = self.session_dir / "meeting.wav"
        self.metadata_file = self.session_dir / "metadata.json"

    def as_dict(self):

        return {
            "session_name": self.session_name,
            "session_dir": str(self.session_dir),
            "mic_file": str(self.mic_file),
            "system_file": str(self.system_file),
            "meeting_file": str(self.meeting_file),
            "metadata_file": str(self.metadata_file),
            "created_at": self.created_at.isoformat(),
        }