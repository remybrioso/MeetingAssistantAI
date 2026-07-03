"""
audio_capture_service.py

Servicio encargado de coordinar la captura de audio.
"""

from engines.audio.audio_session import AudioSession
from engines.audio.microphone_engine import MicrophoneEngine
from models.recording_session import RecordingSession


class AudioCaptureService:

    def __init__(self, configuration):

        self.audio_session = AudioSession()
        self.recording_session = None

        self.microphone = MicrophoneEngine()
        self.config = configuration

    def start(self):

        self.recording_session = RecordingSession(
            base_output_dir=self.config.output_directory
        )

        self.audio_session.start()

        self.microphone.start(
            device_id=self.config.microphone,
            filename=str(self.recording_session.meeting_file),
            samplerate=self.config.sample_rate,
            channels=self.config.channels
        )

    def pause(self):

        self.audio_session.pause()

    def resume(self):

        self.audio_session.resume()

    def stop(self):

        self.microphone.stop()
        self.audio_session.stop()