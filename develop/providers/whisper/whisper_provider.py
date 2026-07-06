"""
whisper_provider.py

Proveedor base para transcripción con Whisper.

Esta versión no ejecuta Whisper todavía.
"""


class WhisperProvider:

    def transcribe(self, audio_file: str):

        raise NotImplementedError(
            "WhisperProvider aún no implementa transcripción real."
        )