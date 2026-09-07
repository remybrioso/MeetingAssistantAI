"""
recorder.py

Motor encargado de grabar audio desde un dispositivo.
"""

import time

import sounddevice as sd
import soundfile as sf

from engines.audio.audio_level import (
    calculate_audio_level,
)


class AudioRecorder:

    LEVEL_UPDATE_INTERVAL_SECONDS = 0.1

    def __init__(
        self,
        level_callback=None,
    ):

        self._stream = None
        self._file = None

        self._recording = False
        self._level_callback = level_callback
        self._last_level_publish = None

    def start(
        self,
        device_id: int,
        filename: str,
        samplerate: int = 44100,
        channels: int = 1,
        level_callback=None,
    ):

        if self._recording:
            return

        if level_callback is not None:
            self._level_callback = level_callback

        self._recording = True
        self._last_level_publish = None

        self._file = sf.SoundFile(
            filename,
            mode="w",
            samplerate=samplerate,
            channels=channels
        )

        self._stream = sd.InputStream(
            samplerate=samplerate,
            channels=channels,
            device=device_id,
            callback=self._callback
        )

        self._stream.start()

    def stop(self):

        if not self._recording:
            return

        self._recording = False

        if self._stream:
            self._stream.stop()
            self._stream.close()

        if self._file:
            self._file.close()

    def _callback(self, indata, frames, callback_time, status):

        if status:
            print(status)

        if self._recording:
            self._file.write(indata.copy())
            self._publish_level(indata)

    def _publish_level(self, samples) -> None:
        if self._level_callback is None:
            return

        now = time.monotonic()
        if (
            self._last_level_publish is not None
            and now - self._last_level_publish
            < self.LEVEL_UPDATE_INTERVAL_SECONDS
        ):
            return

        self._last_level_publish = now

        try:
            level = calculate_audio_level(samples)
            self._level_callback(level)
        except Exception:
            # Visualization must never interrupt the recording callback.
            return
