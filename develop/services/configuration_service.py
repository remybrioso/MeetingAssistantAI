"""
configuration_service.py

Servicio que administra la configuración de la aplicación.
"""

from application.runtime_paths import RuntimePaths
from engines.audio.device_manager import DeviceManager


class ConfigurationService:

    def __init__(
        self,
        runtime_paths: RuntimePaths | None = None,
        device_manager=None,
    ):
        if (
            runtime_paths is not None
            and not isinstance(
                runtime_paths,
                RuntimePaths,
            )
        ):
            raise TypeError(
                "runtime_paths debe ser una "
                "instancia de RuntimePaths o None."
            )

        self.runtime_paths = (
            runtime_paths
            if runtime_paths is not None
            else RuntimePaths.resolve()
        )

        self.device_manager = (
            device_manager
            if device_manager is not None
            else DeviceManager()
        )

        self._restore_defaults()

    def _restore_defaults(self) -> None:
        """
        Restaura la configuración base manteniendo las
        dependencias inyectadas.
        """

        self.microphone = None
        self.system_device = None

        self.output_directory = str(
            self.runtime_paths.meetings_root
        )

        self.sample_rate = 44100
        self.channels = 1

        self.language = "es"

        self.whisper_model = "base"

        self.load_defaults()

    def load_defaults(self):
        """
        Selecciona automáticamente los dispositivos disponibles.
        """

        microphones = self.device_manager.get_microphones()

        if microphones:
            self.microphone = microphones[0].id

        system_devices = (
            self.device_manager.get_system_devices()
        )

        if system_devices:
            self.system_device = (
                system_devices[0].id
            )

    def reset(self):
        """
        Restaura valores por defecto sin perder las
        dependencias de runtime ya resueltas.
        """

        self._restore_defaults()
