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

    def __init__(self):

        self._recorder = AudioRecorder()

    def start(
        self,
        device_id: int,
        filename: str,
        samplerate: int,
        channels: int
    ):

        Path(filename).parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self._recorder.start(
            device_id=device_id,
            filename=filename,
            samplerate=samplerate,
            channels=channels
        )

    def stop(self):

        self._recorder.stop()