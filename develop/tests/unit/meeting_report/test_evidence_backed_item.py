from dataclasses import dataclass

import pytest

from models.meeting_report import (
    EvidenceBackedItem,
    EvidenceReference,
)


@dataclass(
    frozen=True,
    slots=True,
)
class ExampleEvidenceItem(
    EvidenceBackedItem
):
    """
    Implementación mínima utilizada únicamente para probar
    el contrato de EvidenceBackedItem.
    """

    category: str | None = None

    def __post_init__(self) -> None:
        super().__post_init__()

        normalized_category = (
            self.category.strip()
            if self.category is not None
            else None
        )

        object.__setattr__(
            self,
            "category",
            normalized_category or None,
        )

    def _extra_fields(self) -> dict:
        return {
            "category": self.category,
        }


def build_evidence() -> EvidenceReference:
    return EvidenceReference(
        speaker="REMOTE",
        start=10.0,
        end=14.0,
        excerpt="Se aprobó mover la fecha.",
    )


def test_evidence_backed_item_is_abstract() -> None:
    with pytest.raises(
        TypeError,
        match="abstract",
    ):
        EvidenceBackedItem(
            description="No debe crearse.",
        )


def test_evidence_backed_item_normalizes_description() -> None:
    item = ExampleEvidenceItem(
        description=" Decisión confirmada. ",
    )

    assert (
        item.description
        == "Decisión confirmada."
    )


def test_evidence_backed_item_accepts_empty_evidence() -> None:
    item = ExampleEvidenceItem(
        description="Decisión confirmada.",
    )

    assert item.evidence == []

    assert item.as_dict() == {
        "description": "Decisión confirmada.",
        "evidence": [],
        "category": None,
    }


def test_evidence_backed_item_serializes_evidence() -> None:
    evidence = build_evidence()

    item = ExampleEvidenceItem(
        description="Mover la implementación.",
        evidence=[
            evidence,
        ],
        category=" decisión ",
    )

    assert item.as_dict() == {
        "description": "Mover la implementación.",
        "evidence": [
            evidence.as_dict(),
        ],
        "category": "decisión",
    }


def test_evidence_backed_item_rejects_empty_description() -> None:
    with pytest.raises(
        ValueError,
        match="description no puede estar vacío",
    ):
        ExampleEvidenceItem(
            description="   ",
        )


def test_evidence_backed_item_rejects_invalid_evidence() -> None:
    with pytest.raises(
        TypeError,
        match="EvidenceReference",
    ):
        ExampleEvidenceItem(
            description="Decisión confirmada.",
            evidence=[
                "evidencia inválida",
            ],
        )


def test_evidence_list_is_copied() -> None:
    evidence = build_evidence()

    original_evidence = [
        evidence,
    ]

    item = ExampleEvidenceItem(
        description="Decisión confirmada.",
        evidence=original_evidence,
    )

    original_evidence.clear()

    assert item.evidence == [
        evidence,
    ]