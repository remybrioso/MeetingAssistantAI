"""
configuration_service.py

Servicio que administra la configuración de la aplicación.
"""

from engines.audio.device_manager import DeviceManager


class ConfigurationService:

    def __init__(self):

        self.device_manager = DeviceManager()

        self.microphone = None
        self.system_device = None

        self.output_directory = "output"

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

        system_devices = self.device_manager.get_system_devices()

        if system_devices:
            self.system_device = system_devices[0].id

    def reset(self):
        self.__init__()