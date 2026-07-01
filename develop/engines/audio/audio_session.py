"""
audio_session.py

Controla el estado de una sesión de grabación.
"""

from datetime import datetime

from models.recording_state import RecordingState


class AudioSession:

    def __init__(self):

        self._started_at = None
        self._finished_at = None

        self._state = RecordingState.IDLE

    def start(self):

        self._started_at = datetime.now()
        self._finished_at = None

        self._state = RecordingState.RECORDING

    def pause(self):

        if self._state == RecordingState.RECORDING:
            self._state = RecordingState.PAUSED

    def resume(self):

        if self._state == RecordingState.PAUSED:
            self._state = RecordingState.RECORDING

    def stop(self):

        if self._state in (
            RecordingState.RECORDING,
            RecordingState.PAUSED
        ):

            self._finished_at = datetime.now()
            self._state = RecordingState.FINISHED

    @property
    def state(self):
        return self._state

    @property
    def is_recording(self):
        return self._state == RecordingState.RECORDING

    @property
    def is_paused(self):
        return self._state == RecordingState.PAUSED

    @property
    def duration(self):

        if self._started_at is None:
            return 0

        end = self._finished_at or datetime.now()

        return int((end - self._started_at).total_seconds())