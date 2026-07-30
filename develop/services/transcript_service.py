"""
transcript_service.py

Servicio que orquesta la transcripción de una o varias
fuentes de audio y construye un Transcript unificado.
"""

from collections.abc import Sequence

from builders.transcript_builder import TranscriptBuilder
from models.audio_source import AudioSource
from models.transcript import Transcript
from providers.whisper.whisper_provider import WhisperProvider


class TranscriptService:

    def __init__(
        self,
        provider: WhisperProvider | None = None,
        builder: TranscriptBuilder | None = None,
    ):

        self.provider = provider or WhisperProvider()
        self.builder = builder or TranscriptBuilder()

    def transcribe_sources(
        self,
        sources: Sequence[AudioSource],
    ) -> Transcript:
        """
        Transcribe todas las fuentes recibidas y devuelve
        un único Transcript ordenado cronológicamente.

        Los tiempos de cada fuente deben compartir el mismo
        origen temporal, como ocurre con las pistas grabadas
        simultáneamente durante una reunión.
        """

        raw_segments: list[dict] = []

        for source in sources:
            raw_segments.extend(
                self._transcribe_source(source)
            )

        raw_segments.sort(
            key=lambda segment: (
                segment["start"],
                segment["end"],
                segment["speaker"],
            )
        )

        return self.builder.from_segments(
            raw_segments
        )

    def transcribe_microphone(
        self,
        recording_session,
    ) -> Transcript:
        """
        Método de compatibilidad para el flujo actual.

        Será retirado cuando todos los consumidores utilicen
        directamente transcribe_sources().
        """

        return self.transcribe_sources(
            [
                AudioSource(
                    file=recording_session.mic_file,
                    speaker="LOCAL",
                )
            ]
        )

    def _transcribe_source(
        self,
        source: AudioSource,
    ) -> list[dict]:
        """
        Transcribe una fuente individual y convierte el
        resultado del proveedor al formato del builder.
        """

        if not source.file.is_file():
            raise FileNotFoundError(
                f"Audio source not found: {source.file}"
            )

        whisper_result = self.provider.transcribe(
            str(source.file)
        )

        raw_segments: list[dict] = []

        for segment in whisper_result.segments:

            raw_segments.append(
                {
                    "start": segment.start,
                    "end": segment.end,
                    "speaker": source.speaker,
                    "text": segment.text,
                    "words": [
                        {
                            "start": word.start,
                            "end": word.end,
                            "text": word.text,
                            "confidence": word.probability,
                        }
                        for word in segment.words
                    ],
                }
            )

        return raw_segments