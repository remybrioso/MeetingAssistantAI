"""
system_audio_engine.py

Motor para capturar audio del sistema usando SoundCard Loopback.
"""

from pathlib import Path

import soundcard as sc
import soundfile as sf


class SystemAudioEngine:

    def __init__(self):

        self._recording = False

    @property
    def is_recording(self):

        return self._recording

    def record(
        self,
        filename: str,
        duration: int,
        samplerate: int = 48000
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

        self._recording = True

        with loopback.recorder(samplerate=samplerate) as recorder:
            data = recorder.record(
                numframes=samplerate * duration
            )

        sf.write(
            filename,
            data,
            samplerate
        )

        self._recording = False