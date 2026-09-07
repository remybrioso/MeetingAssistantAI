"""
system_audio_engine.py

Motor para capturar audio del sistema usando SoundCard Loopback.
"""

import threading
from pathlib import Path

import soundcard as sc
import soundfile as sf

from engines.audio.audio_level import (
    calculate_audio_level,
)


class SystemAudioEngine:

    def __init__(
        self,
        level_callback=None,
    ):

        self._recording = False
        self._thread = None
        self._level_callback = level_callback

    @property
    def is_recording(self):

        return self._recording

    def start(
        self,
        filename: str,
        samplerate: int = 48000,
        level_callback=None,
    ):

        if self._recording:
            return

        if level_callback is not None:
            self._level_callback = level_callback

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

                capture_frames = max(
                    1,
                    round(samplerate * 0.1),
                )

                while self._recording:

                    data = recorder.record(
                        numframes=capture_frames
                    )

                    file.write(data)
                    self._publish_level(data)

    def _publish_level(self, samples) -> None:
        if self._level_callback is None:
            return

        try:
            self._level_callback(
                calculate_audio_level(samples)
            )
        except Exception:
            # Visualization must never interrupt WAV capture.
            return
