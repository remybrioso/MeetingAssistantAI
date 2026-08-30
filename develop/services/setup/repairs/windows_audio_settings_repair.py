"""
windows_audio_settings_repair.py

Abre la configuración nativa de sonido de Windows para que
el usuario pueda resolver problemas de dispositivos de audio.
"""

import os

from services.setup.repair_action import RepairAction
from services.setup.repair_result import (
    RepairExecutionResult,
    RepairExecutionStatus,
)


WINDOWS_SOUND_SETTINGS_URI = "ms-settings:sound"

SUPPORTED_AUDIO_REPAIR_ACTIONS = frozenset(
    {
        RepairAction.CONFIGURE_MICROPHONE,
        RepairAction.CONFIGURE_SYSTEM_AUDIO,
        RepairAction.REPAIR_AUDIO_DEVICES,
    }
)


class WindowsAudioSettingsRepair:

    def __init__(
        self,
        action: str,
        settings_uri: str = WINDOWS_SOUND_SETTINGS_URI,
        settings_opener=None,
    ) -> None:

        if action not in SUPPORTED_AUDIO_REPAIR_ACTIONS:
            raise ValueError(
                "action no pertenece a las acciones "
                "de reparación de audio soportadas."
            )

        if not isinstance(
            settings_uri,
            str,
        ):
            raise TypeError(
                "settings_uri debe ser una cadena."
            )

        normalized_uri = (
            settings_uri.strip()
        )

        if not normalized_uri:
            raise ValueError(
                "settings_uri no puede estar vacío."
            )

        self.action = action
        self.settings_uri = normalized_uri
        self.settings_opener = (
            settings_opener
            if settings_opener is not None
            else self._open_windows_settings
        )

    def __call__(
        self,
        context: dict,
    ) -> RepairExecutionResult:

        repair_context = dict(
            context or {}
        )

        try:
            opened = self.settings_opener(
                self.settings_uri
            )
        except Exception as ex:
            return RepairExecutionResult(
                action=self.action,
                status=RepairExecutionStatus.FAILED,
                message=(
                    "No fue posible abrir la "
                    "configuración de sonido de Windows."
                ),
                details={
                    "reason": "settings-open-failed",
                    "settings_uri": self.settings_uri,
                    "error_type": (
                        ex.__class__.__name__
                    ),
                    "error": str(ex),
                    "capability_id": (
                        repair_context.get(
                            "capability_id"
                        )
                    ),
                },
            )

        if opened is False:
            return RepairExecutionResult(
                action=self.action,
                status=RepairExecutionStatus.FAILED,
                message=(
                    "Windows no pudo abrir la "
                    "configuración de sonido."
                ),
                details={
                    "reason": (
                        "settings-open-returned-false"
                    ),
                    "settings_uri": self.settings_uri,
                    "capability_id": (
                        repair_context.get(
                            "capability_id"
                        )
                    ),
                },
            )

        return RepairExecutionResult(
            action=self.action,
            status=(
                RepairExecutionStatus
                .USER_ACTION_REQUIRED
            ),
            message=self._user_message(),
            details={
                "settings_uri": self.settings_uri,
                "capability_id": (
                    repair_context.get(
                        "capability_id"
                    )
                ),
            },
        )

    def _user_message(self) -> str:

        if (
            self.action
            == RepairAction.CONFIGURE_MICROPHONE
        ):
            return (
                "Se abrió la configuración de sonido. "
                "Conecta o selecciona un micrófono "
                "utilizable y después pulsa "
                "«Volver a comprobar»."
            )

        if (
            self.action
            == RepairAction.CONFIGURE_SYSTEM_AUDIO
        ):
            return (
                "Se abrió la configuración de sonido. "
                "Comprueba que exista un dispositivo "
                "de salida predeterminado y después "
                "pulsa «Volver a comprobar»."
            )

        return (
            "Se abrió la configuración de sonido. "
            "Revisa los dispositivos de entrada y salida "
            "y después pulsa «Volver a comprobar»."
        )

    @staticmethod
    def _open_windows_settings(
        settings_uri: str,
    ) -> bool:

        startfile = getattr(
            os,
            "startfile",
            None,
        )

        if startfile is None:
            raise RuntimeError(
                "La apertura de Configuración de Windows "
                "solo está disponible en Windows."
            )

        startfile(
            settings_uri
        )

        return True
