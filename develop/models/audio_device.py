"""
audio_device.py

Modelo que representa un dispositivo de audio.
"""

from dataclasses import dataclass


@dataclass
class AudioDevice:
    """
    Representa un dispositivo de entrada o salida de audio.
    """

    id: int

    name: str

    type: str

    default: bool = False