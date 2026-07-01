"""
device_manager.py

Administrador de dispositivos de audio.
"""

import sounddevice as sd

from models.audio_device import AudioDevice


class DeviceManager:

    def __init__(self):
        self._devices = []

    def get_devices(self):

        self._devices.clear()

        devices = sd.query_devices()

        for index, device in enumerate(devices):

            name = device["name"]

            device_type = self._detect_type(device, name)

            self._devices.append(
                AudioDevice(
                    id=index,
                    name=name,
                    type=device_type
                )
            )

        return self._devices

    def get_microphones(self):

        return [
            d for d in self.get_devices()
            if d.type == "microphone"
        ]

    def get_system_devices(self):

        return [
            d for d in self.get_devices()
            if d.type == "system"
        ]

    def _detect_type(self, device, name):

        lower = name.lower()

        if "stereo mix" in lower:
            return "system"

        if "loopback" in lower:
            return "system"

        if device["max_input_channels"] > 0:
            return "microphone"

        if device["max_output_channels"] > 0:
            return "speaker"

        return "unknown"