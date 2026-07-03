"""
system_audio_engine.py

Motor para capturar audio del sistema usando SoundCard Loopback.
"""

import threading
from pathlib import Path

import soundcard as sc
import soundfile as sf


class SystemAudioEngine:

    def __init__(self):

        self._recording = False
        self._thread = None

    @property
    def is_recording(self):

        return self._recording

    def start(
        self,
        filename: str,
        samplerate: int = 48000
    ):

        if self._recording:
            return

        self._recording = True

        self._thread = threading.Thread(
            target=self._record,
            args=(filename, samplerate),
            daemon=True
        )

        self._thread.start()

    def stop(self):

        self._recording = False

        if self._thread:
            self._thread.join(timeout=3)

    def _record(
        self,
        filename: str,
        samplerate: int
    ):

        Path(filename).parent.mkdir(
            parents=True,
            exist_ok=True
        )

        speaker = sc.default_speaker()

        loopback = sc.get_microphone(
            id=str(speaker.name),
            include_loopback=True
        )

        with sf.SoundFile(
            filename,
            mode="w",
            samplerate=samplerate,
            channels=2
        ) as file:

            with loopback.recorder(samplerate=samplerate) as recorder:

                while self._recording:

                    data = recorder.record(
                        numframes=samplerate
                    )

                    file.write(data)