"""
recorder.py

Motor encargado de grabar audio desde un dispositivo.
"""

import threading

import sounddevice as sd
import soundfile as sf


class AudioRecorder:

    def __init__(self):

        self._stream = None
        self._file = None

        self._recording = False

    def start(
        self,
        device_id: int,
        filename: str,
        samplerate: int = 44100,
        channels: int = 1
    ):

        if self._recording:
            return

        self._recording = True

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

    def _callback(self, indata, frames, time, status):

        if status:
            print(status)

        if self._recording:
            self._file.write(indata.copy())