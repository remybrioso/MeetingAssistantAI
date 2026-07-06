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


class WhisperProvider:

    def __init__(self, config: WhisperConfiguration | None = None):

        self.config = config or WhisperConfiguration()
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
            beam_size=self.config.beam_size,
            word_timestamps=True
        )

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

            result.segments.append(
                WhisperSegment(
                    start=segment.start,
                    end=segment.end,
                    text=segment.text.strip(),
                    words=words
                )
            )

        return result