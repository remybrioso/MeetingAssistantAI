"""
audio_capture_service.py

Servicio encargado de coordinar la captura de audio.
"""

from engines.audio.audio_session import AudioSession
from engines.audio.microphone_engine import MicrophoneEngine
from models.recording_session import RecordingSession
from engines.audio.system_audio_engine import SystemAudioEngine


class AudioCaptureService:

    def __init__(self, configuration):

        self.audio_session = AudioSession()
        self.recording_session = None

        self.microphone = MicrophoneEngine()
        self.system_audio = SystemAudioEngine()
        self.config = configuration

    def start(self):

        self.recording_session = RecordingSession(
            base_output_dir=self.config.output_directory
        )

        self.audio_session.start()

        self.microphone.start(
            device_id=self.config.microphone,
            filename=str(self.recording_session.mic_file),
            samplerate=self.config.sample_rate,
            channels=self.config.channels
        )

        self.system_audio.start(
            filename=str(self.recording_session.system_file),
            samplerate=self.config.sample_rate
        )

    def pause(self):

        self.audio_session.pause()

    def resume(self):

        self.audio_session.resume()

    def stop(self):

        self.microphone.stop()
        self.system_audio.stop()
        self.audio_session.stop()