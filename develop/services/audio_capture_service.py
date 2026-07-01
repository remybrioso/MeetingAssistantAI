"""
audio_capture_service.py

Servicio encargado de coordinar una sesión de grabación.
"""

from engines.audio.audio_session import AudioSession
from engines.audio.recorder import AudioRecorder


class AudioCaptureService:

    def __init__(self):

        self.session = AudioSession()
        self.recorder = AudioRecorder()

    def start(
        self,
        device_id: int,
        filename: str
    ):

        self.session.start()

        self.recorder.start(
            device_id=device_id,
            filename=filename
        )

    def pause(self):

        self.session.pause()

    def resume(self):

        self.session.resume()

    def stop(self):

        self.recorder.stop()

        self.session.stop()