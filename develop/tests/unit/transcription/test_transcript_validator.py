"""
Pruebas unitarias para TranscriptValidator.
"""

from models.transcript_analysis import TranscriptAnalysis
from services.transcript_validator import TranscriptValidator


def build_analysis(
    *,
    total_segments: int = 2,
    total_words: int = 30,
    total_characters: int = 180,
    total_duration: float = 60.0,
    unique_speakers: int = 1,
    empty_segments: int = 0,
) -> TranscriptAnalysis:
    """
    Construye un TranscriptAnalysis válido por defecto.

    Cada prueba modifica únicamente la métrica que necesita evaluar.
    """

    return TranscriptAnalysis(
        total_segments=total_segments,
        total_words=total_words,
        total_characters=total_characters,
        total_duration=total_duration,
        unique_speakers=unique_speakers,
        empty_segments=empty_segments,
    )


def test_accepts_transcript_with_sufficient_evidence():
    validator = TranscriptValidator()
    analysis = build_analysis()

    valid, errors = validator.validate(analysis)

    assert valid is True
    assert errors == []


def test_rejects_transcript_without_segments():
    validator = TranscriptValidator()

    analysis = build_analysis(
        total_segments=0,
        total_words=0,
        total_characters=0,
        total_duration=0.0,
        unique_speakers=0,
        empty_segments=0,
    )

    valid, errors = validator.validate(analysis)

    assert valid is False
    assert "La transcripción no contiene segmentos." in errors


def test_rejects_transcript_with_only_empty_segments():
    validator = TranscriptValidator()

    analysis = build_analysis(
        total_segments=3,
        total_words=0,
        total_characters=0,
        empty_segments=3,
    )

    valid, errors = validator.validate(analysis)

    assert valid is False
    assert (
        "La transcripción no contiene segmentos con texto."
        in errors
    )


def test_rejects_transcript_with_too_few_words():
    validator = TranscriptValidator()

    analysis = build_analysis(
        total_words=19,
    )

    valid, errors = validator.validate(analysis)

    assert valid is False
    assert any(
        "Mínimo requerido: 20" in error
        for error in errors
    )


def test_rejects_transcript_with_too_few_characters():
    validator = TranscriptValidator()

    analysis = build_analysis(
        total_characters=79,
    )

    valid, errors = validator.validate(analysis)

    assert valid is False
    assert any(
        "Mínimo requerido: 80 caracteres" in error
        for error in errors
    )


def test_accepts_transcript_at_exact_minimum_limits():
    validator = TranscriptValidator()

    analysis = build_analysis(
        total_words=TranscriptValidator.MIN_WORDS,
        total_characters=TranscriptValidator.MIN_CHARACTERS,
    )

    valid, errors = validator.validate(analysis)

    assert valid is True
    assert errors == []


def test_accepts_single_speaker_transcript():
    validator = TranscriptValidator()

    analysis = build_analysis(
        unique_speakers=1,
    )

    valid, errors = validator.validate(analysis)

    assert valid is True
    assert errors == []


def test_does_not_require_minimum_duration():
    validator = TranscriptValidator()

    analysis = build_analysis(
        total_duration=0.0,
    )

    valid, errors = validator.validate(analysis)

    assert valid is True
    assert errors == []