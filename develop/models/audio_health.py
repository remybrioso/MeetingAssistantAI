"""
audio_health.py

Resultado técnico del diagnóstico de los
dispositivos de audio utilizados por MAI.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AudioHealth:

    microphone_available: bool
    system_audio_available: bool

    microphone_id: int | None = None
    microphone_name: str | None = None

    system_device_name: str | None = None
    system_audio_method: str | None = None

    available_microphones: list[dict[str, Any]] = field(
        default_factory=list
    )

    available_system_devices: list[dict[str, Any]] = field(
        default_factory=list
    )

    message: str = ""
    error: str | None = None

    @property
    def is_healthy(self) -> bool:

        return (
            self.microphone_available
            and self.system_audio_available
        )

    @property
    def is_usable(self) -> bool:

        return self.microphone_available

    def as_dict(self) -> dict:

        return {
            "microphone_available": (
                self.microphone_available
            ),
            "system_audio_available": (
                self.system_audio_available
            ),
            "microphone_id": self.microphone_id,
            "microphone_name": self.microphone_name,
            "system_device_name": (
                self.system_device_name
            ),
            "system_audio_method": (
                self.system_audio_method
            ),
            "available_microphones": (
                self.available_microphones
            ),
            "available_system_devices": (
                self.available_system_devices
            ),
            "message": self.message,
            "error": self.error,
        }