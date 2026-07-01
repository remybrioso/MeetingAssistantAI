"""
audio_session.py

Controla el estado de una sesión de grabación.
"""

from datetime import datetime


class AudioSession:

    def __init__(self):

        self._started_at = None
        self._finished_at = None

        self._recording = False
        self._paused = False

    def start(self):

        self._started_at = datetime.now()

        self._finished_at = None

        self._recording = True

        self._paused = False

    def pause(self):

        if self._recording:
            self._paused = True

    def resume(self):

        if self._recording:
            self._paused = False

    def stop(self):

        self._finished_at = datetime.now()

        self._recording = False

        self._paused = False

    @property
    def is_recording(self):
        return self._recording

    @property
    def is_paused(self):
        return self._paused

    @property
    def duration(self):

        if self._started_at is None:
            return 0

        end = self._finished_at or datetime.now()

        return int((end - self._started_at).total_seconds())