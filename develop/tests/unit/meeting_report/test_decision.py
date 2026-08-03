import pytest

from models.meeting_report import (
    Decision,
    EvidenceReference,
)


def build_evidence() -> EvidenceReference:
    return EvidenceReference(
        speaker="REMOTE",
        start=32.0,
        end=38.5,
        excerpt=(
            "Moveremos la implementación al próximo sprint "
            "porque las pruebas no estarán listas."
        ),
    )


def test_decision_serializes_complete_data() -> None:
    evidence = build_evidence()

    decision = Decision(
        description=(
            "Mover la implementación al próximo sprint."
        ),
        rationale=(
            "Las pruebas no estarán listas esta semana."
        ),
        evidence=[
            evidence,
        ],
    )

    assert decision.as_dict() == {
        "description": (
            "Mover la implementación al próximo sprint."
        ),
        "evidence": [
            evidence.as_dict(),
        ],
        "rationale": (
            "Las pruebas no estarán listas esta semana."
        ),
    }


def test_decision_accepts_missing_rationale() -> None:
    decision = Decision(
        description=(
            "Aprobar la nueva arquitectura."
        ),
    )

    assert decision.rationale is None

    assert decision.as_dict() == {
        "description": (
            "Aprobar la nueva arquitectura."
        ),
        "evidence": [],
        "rationale": None,
    }


def test_decision_normalizes_rationale() -> None:
    decision = Decision(
        description="Aprobar el cambio.",
        rationale=" Reduce la duplicación. ",
    )

    assert (
        decision.rationale
        == "Reduce la duplicación."
    )


def test_decision_converts_empty_rationale_to_none() -> None:
    decision = Decision(
        description="Aprobar el cambio.",
        rationale="   ",
    )

    assert decision.rationale is None


def test_decision_normalizes_description() -> None:
    decision = Decision(
        description=" Aprobar el cambio. ",
    )

    assert (
        decision.description
        == "Aprobar el cambio."
    )


def test_decision_rejects_empty_description() -> None:
    with pytest.raises(
        ValueError,
        match="Decision description no puede estar vacío",
    ):
        Decision(
            description="   ",
        )


def test_decision_rejects_invalid_evidence() -> None:
    with pytest.raises(
        TypeError,
        match="Decision evidence",
    ):
        Decision(
            description="Aprobar el cambio.",
            evidence=[
                "evidencia inválida",
            ],
        )


def test_decision_copies_evidence_collection() -> None:
    evidence = build_evidence()

    original_evidence = [
        evidence,
    ]

    decision = Decision(
        description="Aprobar el cambio.",
        evidence=original_evidence,
    )

    original_evidence.clear()

    assert decision.evidence == [
        evidence,
    ]