import pytest

from models.meeting_report import (
    EvidenceReference,
    MeetingRisk,
)


def build_evidence() -> EvidenceReference:
    return EvidenceReference(
        speaker="REMOTE",
        start=62.0,
        end=69.5,
        excerpt=(
            "Si las pruebas se retrasan, también podría "
            "moverse la fecha del despliegue."
        ),
    )


def test_meeting_risk_serializes_complete_data() -> None:
    evidence = build_evidence()

    risk = MeetingRisk(
        description=(
            "Las pruebas pueden retrasarse."
        ),
        impact=(
            "La fecha del despliegue podría moverse."
        ),
        evidence=[
            evidence,
        ],
    )

    assert risk.as_dict() == {
        "description": (
            "Las pruebas pueden retrasarse."
        ),
        "evidence": [
            evidence.as_dict(),
        ],
        "impact": (
            "La fecha del despliegue podría moverse."
        ),
    }


def test_meeting_risk_accepts_missing_impact() -> None:
    risk = MeetingRisk(
        description=(
            "Existe un bloqueo en las pruebas."
        ),
    )

    assert risk.impact is None

    assert risk.as_dict() == {
        "description": (
            "Existe un bloqueo en las pruebas."
        ),
        "evidence": [],
        "impact": None,
    }


def test_meeting_risk_normalizes_impact() -> None:
    risk = MeetingRisk(
        description="Existe un riesgo.",
        impact=" Puede retrasar el proyecto. ",
    )

    assert (
        risk.impact
        == "Puede retrasar el proyecto."
    )


def test_meeting_risk_converts_empty_impact_to_none() -> None:
    risk = MeetingRisk(
        description="Existe un riesgo.",
        impact="   ",
    )

    assert risk.impact is None


def test_meeting_risk_normalizes_description() -> None:
    risk = MeetingRisk(
        description=" Existe un bloqueo. ",
    )

    assert (
        risk.description
        == "Existe un bloqueo."
    )


def test_meeting_risk_rejects_empty_description() -> None:
    with pytest.raises(
        ValueError,
        match="MeetingRisk description no puede estar vacío",
    ):
        MeetingRisk(
            description="   ",
        )


def test_meeting_risk_rejects_invalid_evidence() -> None:
    with pytest.raises(
        TypeError,
        match="MeetingRisk evidence",
    ):
        MeetingRisk(
            description="Existe un bloqueo.",
            evidence=[
                "evidencia inválida",
            ],
        )


def test_meeting_risk_copies_evidence_collection() -> None:
    evidence = build_evidence()

    original_evidence = [
        evidence,
    ]

    risk = MeetingRisk(
        description="Existe un bloqueo.",
        evidence=original_evidence,
    )

    original_evidence.clear()

    assert risk.evidence == [
        evidence,
    ]