"""
audio_capture_service.py

Servicio encargado de coordinar la captura de audio.
"""

import math

from engines.audio.audio_session import AudioSession
from engines.audio.microphone_engine import MicrophoneEngine
from engines.audio.system_audio_engine import SystemAudioEngine
from application.event_bus import EventBus
from models.recording_session import RecordingSession
from services.workspace_service import WorkspaceService


class AudioCaptureService:

    def __init__(
        self,
        configuration,
        workspace_service=None,
        event_bus=None,
    ):

        self.audio_session = AudioSession()
        self.recording_session = None
        self.event_bus = (
            event_bus
            if event_bus is not None
            else EventBus()
        )

        self.microphone = MicrophoneEngine(
            level_callback=self._on_microphone_audio_level,
        )
        self.system_audio = SystemAudioEngine(
            level_callback=self._on_system_audio_level,
        )

        self.config = configuration

        self.workspace_service = (
            workspace_service or WorkspaceService()
        )

    def start(self):

        self.recording_session = RecordingSession(
            base_output_dir=self.config.output_directory
        )

        workspace = self.workspace_service.create(
            self.recording_session.session_dir
        )

        self.recording_session.attach_workspace(
            workspace
        )

        self.audio_session.start()

        self.microphone.start(
            device_id=self.config.microphone,
            filename=str(
                self.recording_session.mic_file
            ),
            samplerate=self.config.sample_rate,
            channels=self.config.channels
        )

        self.system_audio.start(
            filename=str(
                self.recording_session.system_file
            ),
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

    def _on_microphone_audio_level(self, level: float) -> None:
        self._emit_audio_level(
            "microphone_audio_level",
            level,
        )

    def _on_system_audio_level(self, level: float) -> None:
        self._emit_audio_level(
            "system_audio_level",
            level,
        )

    def _emit_audio_level(
        self,
        event_name: str,
        level: float,
    ) -> None:
        try:
            value = float(level)
        except (TypeError, ValueError):
            value = 0.0

        if not math.isfinite(value):
            value = 0.0

        self.event_bus.emit(
            event_name,
            max(0.0, min(1.0, value)),
        )
