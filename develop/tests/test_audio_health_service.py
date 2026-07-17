from engines.audio.device_manager import DeviceManager
from models.audio_device import AudioDevice
from services.audio_health_service import (
    AudioHealthService,
)


class FakeDeviceManager(DeviceManager):

    def get_microphones(self):

        return [
            AudioDevice(
                id=4,
                name="Jabra Evolve 20",
                type="microphone",
            )
        ]

    def get_system_devices(self):

        return []


class FakeSpeaker:

    name = "Speakers Realtek Audio"


class FakeLoopback:

    name = "Speakers Realtek Audio Loopback"


class FakeSoundCard:

    @staticmethod
    def default_speaker():

        return FakeSpeaker()

    @staticmethod
    def get_microphone(
        id,
        include_loopback=False,
    ):

        assert id == "Speakers Realtek Audio"
        assert include_loopback is True

        return FakeLoopback()


service = AudioHealthService(
    device_manager=FakeDeviceManager(),
    soundcard_module=FakeSoundCard,
)

result = service.check()

assert result.microphone_available
assert result.system_audio_available

assert result.microphone_id == 4

assert (
    result.microphone_name
    == "Jabra Evolve 20"
)

assert (
    result.system_device_name
    == "Speakers Realtek Audio"
)

assert (
    result.system_audio_method
    == "soundcard-loopback"
)

print(
    "AudioHealthService validado "
    "con dependencias simuladas."
)