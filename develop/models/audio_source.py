"""
audio_source.py

Modelo de dominio que representa una fuente de audio
disponible para transcripción.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class AudioSource:
    """
    Representa una pista o archivo de audio asociado
    a una identidad lógica dentro de la transcripción.

    Ejemplos de speaker:
    - LOCAL
    - REMOTE
    - IMPORTED
    """

    file: Path
    speaker: str

    def __post_init__(self):

        normalized_file = Path(self.file)
        normalized_speaker = self.speaker.strip().upper()

        if not normalized_speaker:
            raise ValueError(
                "AudioSource speaker cannot be empty."
            )

        object.__setattr__(
            self,
            "file",
            normalized_file
        )

        object.__setattr__(
            self,
            "speaker",
            normalized_speaker
        )