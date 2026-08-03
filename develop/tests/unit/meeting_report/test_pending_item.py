import pytest

from models.meeting_report import (
    EvidenceReference,
    PendingItem,
)


def build_evidence() -> EvidenceReference:
    return EvidenceReference(
        speaker="REMOTE",
        start=75.0,
        end=81.0,
        excerpt=(
            "Todavía falta confirmar la ventana "
            "de mantenimiento."
        ),
    )


def test_pending_item_serializes_complete_data() -> None:
    evidence = build_evidence()

    pending_item = PendingItem(
        description=(
            "Confirmar la ventana de mantenimiento."
        ),
        evidence=[
            evidence,
        ],
    )

    assert pending_item.as_dict() == {
        "description": (
            "Confirmar la ventana de mantenimiento."
        ),
        "evidence": [
            evidence.as_dict(),
        ],
    }


def test_pending_item_accepts_empty_evidence() -> None:
    pending_item = PendingItem(
        description=(
            "Definir la fecha del despliegue."
        ),
    )

    assert pending_item.evidence == []

    assert pending_item.as_dict() == {
        "description": (
            "Definir la fecha del despliegue."
        ),
        "evidence": [],
    }


def test_pending_item_normalizes_description() -> None:
    pending_item = PendingItem(
        description=(
            " Confirmar los participantes. "
        ),
    )

    assert (
        pending_item.description
        == "Confirmar los participantes."
    )


def test_pending_item_rejects_empty_description() -> None:
    with pytest.raises(
        ValueError,
        match="PendingItem description no puede estar vacío",
    ):
        PendingItem(
            description="   ",
        )


def test_pending_item_rejects_invalid_evidence() -> None:
    with pytest.raises(
        TypeError,
        match="PendingItem evidence",
    ):
        PendingItem(
            description=(
                "Confirmar la ventana de mantenimiento."
            ),
            evidence=[
                "evidencia inválida",
            ],
        )


def test_pending_item_copies_evidence_collection() -> None:
    evidence = build_evidence()

    original_evidence = [
        evidence,
    ]

    pending_item = PendingItem(
        description=(
            "Confirmar la ventana de mantenimiento."
        ),
        evidence=original_evidence,
    )

    original_evidence.clear()

    assert pending_item.evidence == [
        evidence,
    ]


def test_pending_item_is_value_comparable() -> None:
    first_item = PendingItem(
        description=(
            "Confirmar la ventana de mantenimiento."
        ),
    )

    second_item = PendingItem(
        description=(
            "Confirmar la ventana de mantenimiento."
        ),
    )

    assert first_item == second_item