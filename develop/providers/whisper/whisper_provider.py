"""
whisper_provider.py

Proveedor real para transcripción con Faster-Whisper.
"""

from faster_whisper import WhisperModel

from providers.whisper.whisper_configuration import WhisperConfiguration
from providers.whisper.whisper_models import (
    WhisperResult,
    WhisperSegment,
    WhisperWord,
)
from providers.whisper.whisper_segment_normalizer import (
    WhisperSegmentNormalizer,
)


class WhisperProvider:

    def __init__(
        self,
        config: WhisperConfiguration | None = None,
        segment_normalizer: WhisperSegmentNormalizer | None = None,
    ):
        self.config = config or WhisperConfiguration()

        self.segment_normalizer = (
            segment_normalizer
            if segment_normalizer is not None
            else WhisperSegmentNormalizer()
        )

        self._model = None

    def _load_model(self):

        if self._model is None:
            self._model = WhisperModel(
                self.config.model,
                device=self.config.device,
                compute_type=self.config.compute_type
            )

        return self._model

    def transcribe(self, audio_file: str) -> WhisperResult:

        model = self._load_model()

        segments, info = model.transcribe(
            audio_file,
            language=self.config.language,
            task="transcribe",
            beam_size=self.config.beam_size,
            word_timestamps=True,
            initial_prompt=(
                "Esta es una reunión de trabajo en español. "
                "Transcribe fielmente en español, respetando nombres propios, "
                "términos técnicos, acuerdos, responsables y fechas."
            ),
            condition_on_previous_text=False,
            vad_filter=True
        )

        print("=" * 60)
        print("WHISPER TRANSCRIPTION")
        print(f"Idioma configurado: {self.config.language}")
        print(f"Idioma reportado: {info.language}")
        print(
            "Probabilidad:",
            getattr(info, "language_probability", "no disponible")
        )
        print("=" * 60)

        result = WhisperResult(
            language=info.language
        )

        for segment in segments:

            words = []

            if segment.words:
                for word in segment.words:
                    words.append(
                        WhisperWord(
                            start=word.start,
                            end=word.end,
                            text=word.word.strip(),
                            probability=getattr(word, "probability", None)
                        )
                    )

            raw_segment = WhisperSegment(
                start=segment.start,
                end=segment.end,
                text=segment.text.strip(),
                words=words
            )

            result.segments.extend(
                self.segment_normalizer.normalize(
                    raw_segment
                )
            )

        return result
