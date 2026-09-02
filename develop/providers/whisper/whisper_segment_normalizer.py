"""
whisper_segment_normalizer.py

Normaliza segmentos de Faster-Whisper antes de incorporarlos
al Transcript de dominio.
"""

from numbers import Real

from providers.whisper.whisper_models import (
    WhisperSegment,
    WhisperWord,
)


class WhisperSegmentNormalizer:
    """
    Elimina discontinuidades temporales internas de un WhisperSegment.

    Faster-Whisper puede devolver un único segmento que contiene grupos
    de palabras separados por silencios muy grandes. Ese segmento no
    representa un intervalo temporal continuo y puede contaminar el
    chunking posterior.

    La normalización conserva intactos los segmentos continuos. Solo
    divide un segmento cuando el salto entre dos palabras consecutivas
    supera max_word_gap_seconds.
    """

    DEFAULT_MAX_WORD_GAP_SECONDS = 10.0

    def __init__(
        self,
        max_word_gap_seconds: float = DEFAULT_MAX_WORD_GAP_SECONDS,
    ) -> None:
        if (
            not isinstance(
                max_word_gap_seconds,
                Real,
            )
            or isinstance(
                max_word_gap_seconds,
                bool,
            )
        ):
            raise TypeError(
                "max_word_gap_seconds debe ser numérico."
            )

        normalized_gap = float(
            max_word_gap_seconds
        )

        if normalized_gap <= 0:
            raise ValueError(
                "max_word_gap_seconds debe ser mayor que cero."
            )

        self.max_word_gap_seconds = (
            normalized_gap
        )

    def normalize(
        self,
        segment: WhisperSegment,
    ) -> list[WhisperSegment]:
        """
        Devuelve uno o más segmentos temporalmente coherentes.

        Un segmento sin palabras se conserva tal como fue entregado por
        Faster-Whisper porque no existe información granular suficiente
        para reconstruir sus límites.

        Un segmento con palabras y sin discontinuidades también se
        conserva sin cambios para no alterar innecesariamente texto ni
        timestamps productivos.

        Cuando existe una discontinuidad, cada grupo se reconstruye
        exclusivamente con sus propias palabras y sus propios límites.
        """
        if not isinstance(
            segment,
            WhisperSegment,
        ):
            raise TypeError(
                "segment debe ser una instancia de WhisperSegment."
            )

        if not segment.words:
            return [
                segment
            ]

        self._validate_words(
            segment.words
        )

        groups: list[
            list[WhisperWord]
        ] = []

        current_group = [
            segment.words[0]
        ]

        for word in segment.words[1:]:
            previous_word = (
                current_group[-1]
            )

            gap_seconds = (
                float(
                    word.start
                )
                - float(
                    previous_word.end
                )
            )

            if (
                gap_seconds
                > self.max_word_gap_seconds
            ):
                groups.append(
                    current_group
                )

                current_group = [
                    word
                ]

                continue

            current_group.append(
                word
            )

        groups.append(
            current_group
        )

        if len(groups) == 1:
            return [
                segment
            ]

        return [
            self._build_segment(
                words=group
            )
            for group in groups
        ]

    @staticmethod
    def _validate_words(
        words: list[WhisperWord],
    ) -> None:
        previous_start: float | None = None

        for index, word in enumerate(
            words,
            start=1,
        ):
            if not isinstance(
                word,
                WhisperWord,
            ):
                raise TypeError(
                    "WhisperSegment words elemento "
                    f"#{index} debe ser WhisperWord."
                )

            if (
                not isinstance(
                    word.start,
                    Real,
                )
                or isinstance(
                    word.start,
                    bool,
                )
                or not isinstance(
                    word.end,
                    Real,
                )
                or isinstance(
                    word.end,
                    bool,
                )
            ):
                raise TypeError(
                    "WhisperSegment words elemento "
                    f"#{index} requiere timestamps numéricos."
                )

            start = float(
                word.start
            )

            end = float(
                word.end
            )

            if start < 0 or end < 0:
                raise ValueError(
                    "WhisperSegment words elemento "
                    f"#{index} no puede tener timestamps negativos."
                )

            if end < start:
                raise ValueError(
                    "WhisperSegment words elemento "
                    f"#{index} tiene end menor que start."
                )

            if (
                previous_start is not None
                and start < previous_start
            ):
                raise ValueError(
                    "WhisperSegment words debe conservar "
                    "orden temporal por start."
                )

            previous_start = start

    @staticmethod
    def _build_segment(
        words: list[WhisperWord],
    ) -> WhisperSegment:
        text = " ".join(
            word.text.strip()
            for word in words
            if word.text.strip()
        )

        if not text:
            raise ValueError(
                "No es posible reconstruir un WhisperSegment "
                "discontinuo sin texto de palabras."
            )

        return WhisperSegment(
            start=min(
                float(
                    word.start
                )
                for word in words
            ),
            end=max(
                float(
                    word.end
                )
                for word in words
            ),
            text=text,
            words=list(
                words
            ),
        )
