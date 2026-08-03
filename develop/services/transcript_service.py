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
    """
    Transcribe una colección de fuentes de audio y produce
    un Transcript unificado y ordenado cronológicamente.
    """

    def __init__(
        self,
        provider: WhisperProvider | None = None,
        builder: TranscriptBuilder | None = None,
    ):
        self.provider = (
            provider
            if provider is not None
            else WhisperProvider()
        )

        self.builder = (
            builder
            if builder is not None
            else TranscriptBuilder()
        )

    def transcribe_sources(
        self,
        sources: Sequence[AudioSource],
    ) -> Transcript:
        """
        Transcribe todas las fuentes recibidas y devuelve
        un Transcript unificado.

        Los tiempos de las fuentes deben utilizar el mismo
        origen temporal cuando representan pistas grabadas
        simultáneamente.

        Args:
            sources:
                Fuentes de audio que serán transcritas.

        Returns:
            Transcript:
                Transcripción combinada y ordenada.

        Raises:
            ValueError:
                Si no se reciben fuentes de audio.

            TypeError:
                Si algún elemento no es AudioSource.

            FileNotFoundError:
                Si alguno de los archivos no existe.
        """

        if not sources:
            raise ValueError(
                "Se requiere al menos una fuente de audio."
            )

        raw_segments: list[dict] = []

        for source in sources:

            if not isinstance(
                source,
                AudioSource,
            ):
                raise TypeError(
                    "Todas las fuentes deben ser "
                    "instancias de AudioSource."
                )

            raw_segments.extend(
                self._transcribe_source(
                    source
                )
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

    def _transcribe_source(
        self,
        source: AudioSource,
    ) -> list[dict]:
        """
        Transcribe una fuente individual y adapta el
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