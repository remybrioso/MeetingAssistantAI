"""
whisper_configuration.py

Configuración del proveedor Whisper.
"""

from dataclasses import dataclass


@dataclass
class WhisperConfiguration:

    model: str = "base"

    language: str = "es"

    device: str = "cpu"

    compute_type: str = "int8"

    beam_size: int = 5

    def as_dict(self):

        return {
            "model": self.model,
            "language": self.language,
            "device": self.device,
            "compute_type": self.compute_type,
            "beam_size": self.beam_size,
        }