import pytest

from models.meeting_report_narrative import (
    GroundedNarrativeText,
    MeetingReportNarrative,
)


def grounded(
    text: str = "Migración de plataforma",
    source_item_ids=None,
) -> GroundedNarrativeText:
    return GroundedNarrativeText(
        text=text,
        source_item_ids=(
            source_item_ids
            if source_item_ids is not None
            else [0]
        ),
    )


def build_narrative(
    **overrides,
) -> MeetingReportNarrative:
    data = {
        "title": grounded(
            "Migración de plataforma",
            [0],
        ),
        "objective": None,
        "executive_summary": grounded(
            "Se revisó y aprobó la migración de la plataforma.",
            [0, 1],
        ),
        "key_points": [
            grounded(
                "Se aprobó la migración.",
                [1],
            ),
        ],
    }

    data.update(
        overrides
    )

    return MeetingReportNarrative(
        **data
    )


def test_grounded_text_normalizes_text() -> None:
    result = grounded(
        "  Migración de plataforma  "
    )

    assert (
        result.text
        == "Migración de plataforma"
    )


def test_grounded_text_rejects_empty_text() -> None:
    with pytest.raises(
        ValueError,
        match="no puede estar vacío",
    ):
        grounded(
            "   "
        )


def test_grounded_text_requires_source_ids() -> None:
    with pytest.raises(
        ValueError,
        match="al menos un source_item_id",
    ):
        grounded(
            source_item_ids=[]
        )


@pytest.mark.parametrize(
    "value",
    [
        1.5,
        True,
        "0",
    ],
)
def test_grounded_text_rejects_non_integer_source_ids(
    value,
) -> None:
    with pytest.raises(
        TypeError,
        match="debe ser entero",
    ):
        grounded(
            source_item_ids=[
                value
            ]
        )


def test_grounded_text_rejects_negative_source_id() -> None:
    with pytest.raises(
        ValueError,
        match="no puede ser negativo",
    ):
        grounded(
            source_item_ids=[
                -1
            ]
        )


def test_grounded_text_rejects_duplicate_source_ids() -> None:
    with pytest.raises(
        ValueError,
        match="valores duplicados",
    ):
        grounded(
            source_item_ids=[
                0,
                0,
            ]
        )


def test_grounded_text_as_dict_returns_copy() -> None:
    result = grounded(
        source_item_ids=[
            0,
            2,
        ]
    )

    data = result.as_dict()

    assert data == {
        "text": (
            "Migración de plataforma"
        ),
        "source_item_ids": [
            0,
            2,
        ],
    }

    data[
        "source_item_ids"
    ].append(
        9
    )

    assert (
        result.source_item_ids
        == [
            0,
            2,
        ]
    )


def test_narrative_accepts_null_objective() -> None:
    result = build_narrative(
        objective=None
    )

    assert result.objective is None


def test_narrative_accepts_grounded_objective() -> None:
    result = build_narrative(
        objective=grounded(
            "Evaluar la migración propuesta.",
            [0],
        )
    )

    assert (
        result.objective.text
        == "Evaluar la migración propuesta."
    )


def test_narrative_requires_key_points() -> None:
    with pytest.raises(
        ValueError,
        match="al menos un elemento",
    ):
        build_narrative(
            key_points=[]
        )


def test_narrative_rejects_duplicate_key_points() -> None:
    with pytest.raises(
        ValueError,
        match="textos duplicados",
    ):
        build_narrative(
            key_points=[
                grounded(
                    "Se aprobó la migración.",
                    [0],
                ),
                grounded(
                    "  SE APROBÓ LA MIGRACIÓN.  ",
                    [1],
                ),
            ]
        )


def test_narrative_rejects_invalid_title_type() -> None:
    with pytest.raises(
        TypeError,
        match="title debe ser",
    ):
        build_narrative(
            title="Título"
        )


def test_narrative_rejects_invalid_objective_type() -> None:
    with pytest.raises(
        TypeError,
        match="objective debe ser",
    ):
        build_narrative(
            objective="Objetivo"
        )


def test_narrative_rejects_invalid_summary_type() -> None:
    with pytest.raises(
        TypeError,
        match="executive_summary debe ser",
    ):
        build_narrative(
            executive_summary="Resumen"
        )


def test_narrative_rejects_invalid_key_point_type() -> None:
    with pytest.raises(
        TypeError,
        match="key_points elemento #1",
    ):
        build_narrative(
            key_points=[
                "Punto"
            ]
        )


def test_narrative_as_dict_preserves_grounding() -> None:
    result = build_narrative(
        objective=grounded(
            "Evaluar la migración propuesta.",
            [0],
        )
    )

    data = result.as_dict()

    assert (
        data["title"][
            "source_item_ids"
        ]
        == [
            0
        ]
    )
    assert (
        data["objective"][
            "source_item_ids"
        ]
        == [
            0
        ]
    )
    assert (
        data["executive_summary"][
            "source_item_ids"
        ]
        == [
            0,
            1,
        ]
    )
