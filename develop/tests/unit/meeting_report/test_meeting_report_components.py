import pytest

from models.meeting_report import (
    EvidenceReference,
    MeetingTopic,
    Participant,
)


def build_evidence() -> EvidenceReference:
    return EvidenceReference(
        speaker="REMOTE",
        start=12.5,
        end=18.0,
        excerpt=(
            "La actualización debe completarse "
            "antes del viernes."
        ),
    )


def test_evidence_reference_serializes() -> None:
    evidence = build_evidence()

    assert evidence.as_dict() == {
        "speaker": "REMOTE",
        "start": 12.5,
        "end": 18.0,
        "excerpt": (
            "La actualización debe completarse "
            "antes del viernes."
        ),
    }


def test_evidence_reference_normalizes_text() -> None:
    evidence = EvidenceReference(
        speaker=" REMOTE ",
        start=0.0,
        end=2.0,
        excerpt=" Contenido confirmado. ",
    )

    assert evidence.speaker == "REMOTE"
    assert evidence.excerpt == "Contenido confirmado."


def test_evidence_reference_rejects_negative_start() -> None:
    with pytest.raises(
        ValueError,
        match="no puede ser negativo",
    ):
        EvidenceReference(
            speaker="LOCAL",
            start=-1.0,
            end=2.0,
            excerpt="Texto.",
        )


def test_evidence_reference_rejects_invalid_range() -> None:
    with pytest.raises(
        ValueError,
        match="menor que start",
    ):
        EvidenceReference(
            speaker="LOCAL",
            start=5.0,
            end=4.0,
            excerpt="Texto.",
        )


def test_evidence_reference_rejects_empty_excerpt() -> None:
    with pytest.raises(
        ValueError,
        match="excerpt no puede estar vacío",
    ):
        EvidenceReference(
            speaker="LOCAL",
            start=0.0,
            end=1.0,
            excerpt="   ",
        )


def test_participant_accepts_logical_speaker() -> None:
    participant = Participant(
        speaker="REMOTE",
    )

    assert participant.as_dict() == {
        "name": None,
        "speaker": "REMOTE",
        "role": None,
    }


def test_participant_normalizes_optional_values() -> None:
    participant = Participant(
        name=" Remy ",
        speaker=" LOCAL ",
        role=" Coordinador ",
    )

    assert participant.name == "Remy"
    assert participant.speaker == "LOCAL"
    assert participant.role == "Coordinador"


def test_participant_converts_empty_values_to_none() -> None:
    participant = Participant(
        name="Remy",
        speaker=" ",
        role=" ",
    )

    assert participant.name == "Remy"
    assert participant.speaker is None
    assert participant.role is None


def test_participant_rejects_completely_empty_identity() -> None:
    with pytest.raises(
        ValueError,
        match="requiere al menos un dato",
    ):
        Participant()


def test_meeting_topic_serializes_evidence() -> None:
    evidence = build_evidence()

    topic = MeetingTopic(
        title="Actualización de Oracle",
        summary=(
            "Se revisó el plazo de actualización "
            "del servidor."
        ),
        evidence=[
            evidence,
        ],
    )

    assert topic.as_dict() == {
        "title": "Actualización de Oracle",
        "summary": (
            "Se revisó el plazo de actualización "
            "del servidor."
        ),
        "evidence": [
            evidence.as_dict(),
        ],
    }


def test_meeting_topic_accepts_empty_evidence() -> None:
    topic = MeetingTopic(
        title="Planificación",
        summary="Se revisaron los próximos pasos.",
    )

    assert topic.evidence == []
    assert topic.as_dict()["evidence"] == []


def test_meeting_topic_rejects_invalid_evidence() -> None:
    with pytest.raises(
        TypeError,
        match="EvidenceReference",
    ):
        MeetingTopic(
            title="Planificación",
            summary="Se revisaron los próximos pasos.",
            evidence=[
                "texto no válido",
            ],
        )