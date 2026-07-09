"""
meeting_workspace.py

Representa la estructura física de una reunión.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class MeetingWorkspace:

    root_dir: Path

    audio_dir: Path

    documents_dir: Path

    internal_dir: Path

    @property
    def microphone_audio(self) -> Path:
        return self.audio_dir / "Microfono.wav"

    @property
    def system_audio(self) -> Path:
        return self.audio_dir / "Sistema.wav"

    @property
    def meeting_audio(self) -> Path:
        return self.audio_dir / "Reunion.wav"

    @property
    def transcript_json(self) -> Path:
        return self.internal_dir / "transcript.json"

    @property
    def summary_json(self) -> Path:
        return self.internal_dir / "summary.json"

    @property
    def processing_metrics_json(self) -> Path:
        return self.internal_dir / "processing_metrics.json"

    @property
    def metadata_json(self) -> Path:
        return self.internal_dir / "metadata.json"

    @property
    def summary_markdown(self) -> Path:
        return self.documents_dir / "Resumen.md"