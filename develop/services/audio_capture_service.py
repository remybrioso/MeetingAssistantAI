"""
audio_capture_service.py

Servicio encargado de coordinar la captura de audio.
"""

import os

from engines.audio.audio_session import AudioSession
from engines.audio.microphone_engine import MicrophoneEngine


class AudioCaptureService:

    def __init__(self, configuration):

        self.session = AudioSession()
        self.microphone = MicrophoneEngine()

        self.config = configuration

    def start(self):

        os.makedirs(
            self.config.output_directory,
            exist_ok=True
        )

        filename = os.path.join(
            self.config.output_directory,
            "meeting.wav"
        )

        self.session.start()

        self.microphone.start(
            device_id=self.config.microphone,
            filename=filename,
            samplerate=self.config.sample_rate,
            channels=self.config.channels
        )

    def pause(self):

        self.session.pause()

    def resume(self):

        self.session.resume()

    def stop(self):

        self.microphone.stop()

        self.session.stop()