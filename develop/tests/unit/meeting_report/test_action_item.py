from datetime import date

import pytest

from models.meeting_report import (
    ActionItem,
    ActionOwner,
    ActionStatus,
    EvidenceReference,
)


def build_evidence() -> EvidenceReference:
    return EvidenceReference(
        speaker="REMOTE",
        start=45.0,
        end=52.0,
        excerpt=(
            "El equipo DBA actualizará el servidor "
            "antes del siete de agosto."
        ),
    )


def test_action_item_serializes_complete_data() -> None:
    evidence = build_evidence()

    action = ActionItem(
        description="Actualizar el servidor Oracle.",
        owner=ActionOwner(
            display_name="Equipo DBA",
        ),
        due_date=date(
            2026,
            8,
            7,
        ),
        status=ActionStatus.PENDING,
        evidence=[
            evidence,
        ],
    )

    assert action.as_dict() == {
        "description": "Actualizar el servidor Oracle.",
        "evidence": [
            evidence.as_dict(),
        ],
        "owner": {
            "display_name": "Equipo DBA",
        },
        "due_date": "2026-08-07",
        "status": "pending",
    }


def test_action_item_uses_safe_defaults() -> None:
    action = ActionItem(
        description="Revisar el documento.",
    )

    assert action.owner is None
    assert action.due_date is None
    assert action.status is ActionStatus.UNKNOWN

    assert action.as_dict() == {
        "description": "Revisar el documento.",
        "evidence": [],
        "owner": None,
        "due_date": None,
        "status": "unknown",
    }


def test_action_item_accepts_owner_as_string() -> None:
    action = ActionItem(
        description="Actualizar la documentación.",
        owner=" Equipo de Infraestructura ",
    )

    assert isinstance(
        action.owner,
        ActionOwner,
    )

    assert (
        action.owner.display_name
        == "Equipo de Infraestructura"
    )


def test_action_item_accepts_owner_value_object() -> None:
    owner = ActionOwner(
        display_name="Remy",
    )

    action = ActionItem(
        description="Preparar el informe.",
        owner=owner,
    )

    assert action.owner is owner


def test_action_item_accepts_status_as_string() -> None:
    action = ActionItem(
        description="Ejecutar las pruebas.",
        status=" PENDING ",
    )

    assert (
        action.status
        is ActionStatus.PENDING
    )


def test_action_item_accepts_existing_status() -> None:
    action = ActionItem(
        description="Ejecutar las pruebas.",
        status=ActionStatus.COMPLETED,
    )

    assert (
        action.status
        is ActionStatus.COMPLETED
    )


def test_action_item_rejects_invalid_status() -> None:
    with pytest.raises(
        ValueError,
        match="Estado de acción no válido",
    ):
        ActionItem(
            description="Ejecutar las pruebas.",
            status="in progress",
        )


def test_action_item_rejects_invalid_owner() -> None:
    with pytest.raises(
        TypeError,
        match="ActionOwner requiere una cadena",
    ):
        ActionItem(
            description="Ejecutar las pruebas.",
            owner=123,
        )


def test_action_item_rejects_invalid_due_date() -> None:
    with pytest.raises(
        TypeError,
        match="due_date debe ser una fecha",
    ):
        ActionItem(
            description="Ejecutar las pruebas.",
            due_date="2026-08-07",
        )


def test_action_item_normalizes_description() -> None:
    action = ActionItem(
        description=" Actualizar el servidor. ",
    )

    assert (
        action.description
        == "Actualizar el servidor."
    )


def test_action_item_rejects_empty_description() -> None:
    with pytest.raises(
        ValueError,
        match="ActionItem description no puede estar vacío",
    ):
        ActionItem(
            description="   ",
        )


def test_action_item_rejects_invalid_evidence() -> None:
    with pytest.raises(
        TypeError,
        match="ActionItem evidence",
    ):
        ActionItem(
            description="Actualizar el servidor.",
            evidence=[
                "evidencia inválida",
            ],
        )


def test_action_item_copies_evidence_collection() -> None:
    evidence = build_evidence()

    original_evidence = [
        evidence,
    ]

    action = ActionItem(
        description="Actualizar el servidor.",
        evidence=original_evidence,
    )

    original_evidence.clear()

    assert action.evidence == [
        evidence,
    ]


def test_action_item_serializes_cancelled_status() -> None:
    action = ActionItem(
        description="Ejecutar la migración.",
        status=ActionStatus.CANCELLED,
    )

    assert (
        action.as_dict()["status"]
        == "cancelled"
    )