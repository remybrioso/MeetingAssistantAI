"""
audio_health_service.py

Diagnostica la disponibilidad del micrófono y
de la captura del audio del sistema sin iniciar
una grabación.
"""

from typing import Any

import soundcard as sc

from engines.audio.device_manager import (
    DeviceManager,
)
from models.audio_health import AudioHealth


class AudioHealthService:

    def __init__(
        self,
        device_manager=None,
        soundcard_module=None,
    ):

        self.device_manager = (
            device_manager or DeviceManager()
        )

        self.soundcard = (
            soundcard_module or sc
        )

    def check(self) -> AudioHealth:

        microphone_error = None
        system_audio_error = None

        microphones = []
        system_devices = []

        try:
            microphones = (
                self.device_manager.get_microphones()
            )

        except Exception as ex:
            microphone_error = str(ex)

        try:
            system_devices = (
                self.device_manager.get_system_devices()
            )

        except Exception as ex:
            system_audio_error = str(ex)

        microphone = (
            microphones[0]
            if microphones
            else None
        )

        loopback_result = (
            self._check_soundcard_loopback()
        )

        system_audio_available = (
            loopback_result["available"]
        )

        if not system_audio_available:
            system_audio_error = (
                loopback_result["error"]
                or system_audio_error
            )

        details_microphones = [
            self._device_as_dict(device)
            for device in microphones
        ]

        details_system_devices = [
            self._device_as_dict(device)
            for device in system_devices
        ]

        microphone_available = (
            microphone is not None
        )

        if (
            microphone_available
            and system_audio_available
        ):

            message = (
                "El micrófono y la captura del audio "
                "del sistema están disponibles."
            )

        elif microphone_available:

            message = (
                "El micrófono está disponible, pero "
                "el audio del sistema no puede capturarse."
            )

        else:

            message = (
                "No se encontró un micrófono utilizable."
            )

        errors = [
            error
            for error in (
                microphone_error,
                system_audio_error,
            )
            if error
        ]

        return AudioHealth(
            microphone_available=(
                microphone_available
            ),
            system_audio_available=(
                system_audio_available
            ),
            microphone_id=(
                microphone.id
                if microphone
                else None
            ),
            microphone_name=(
                microphone.name
                if microphone
                else None
            ),
            system_device_name=(
                loopback_result["device_name"]
            ),
            system_audio_method=(
                loopback_result["method"]
            ),
            available_microphones=(
                details_microphones
            ),
            available_system_devices=(
                details_system_devices
            ),
            message=message,
            error=(
                " | ".join(errors)
                if errors
                else None
            ),
        )

    def _check_soundcard_loopback(
        self
    ) -> dict[str, Any]:

        try:
            speaker = (
                self.soundcard.default_speaker()
            )

            if speaker is None:

                return {
                    "available": False,
                    "device_name": None,
                    "method": "soundcard-loopback",
                    "error": (
                        "No existe un altavoz "
                        "predeterminado."
                    ),
                }

            loopback = (
                self.soundcard.get_microphone(
                    id=str(speaker.name),
                    include_loopback=True,
                )
            )

            if loopback is None:

                return {
                    "available": False,
                    "device_name": (
                        str(speaker.name)
                    ),
                    "method": "soundcard-loopback",
                    "error": (
                        "No fue posible obtener el "
                        "loopback del altavoz."
                    ),
                }

            return {
                "available": True,
                "device_name": str(
                    speaker.name
                ),
                "method": "soundcard-loopback",
                "error": None,
            }

        except Exception as ex:

            return {
                "available": False,
                "device_name": None,
                "method": "soundcard-loopback",
                "error": str(ex),
            }

    @staticmethod
    def _device_as_dict(
        device
    ) -> dict[str, Any]:

        return {
            "id": device.id,
            "name": device.name,
            "type": device.type,
        }