"""
microphone_engine.py

Motor encargado de capturar audio desde el micrófono.

Este componente reemplazará progresivamente AudioRecorder.
"""

from pathlib import Path

from engines.audio.recorder import AudioRecorder


class MicrophoneEngine:
    """
    Motor de captura de micrófono.

    En esta primera versión actúa como un adaptador sobre
    AudioRecorder para mantener compatibilidad mientras
    realizamos la migración de arquitectura.
    """

    def __init__(
        self,
        level_callback=None,
    ):

        self._recorder = AudioRecorder()
        self._level_callback = level_callback

    def start(
        self,
        device_id: int,
        filename: str,
        samplerate: int,
        channels: int,
        level_callback=None,
    ):

        Path(filename).parent.mkdir(
            parents=True,
            exist_ok=True
        )

        callback = (
            level_callback
            if level_callback is not None
            else self._level_callback
        )

        recorder_kwargs = dict(
            device_id=device_id,
            filename=filename,
            samplerate=samplerate,
            channels=channels,
        )

        if callback is not None:
            recorder_kwargs["level_callback"] = callback

        self._recorder.start(**recorder_kwargs)

    def stop(self):

        self._recorder.stop()
