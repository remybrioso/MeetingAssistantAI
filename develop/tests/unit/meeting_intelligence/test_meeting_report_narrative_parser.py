import json

import pytest

from models.chunk_classification import (
    ChunkKnowledgeKind,
)
from models.meeting_report_narrative import (
    MeetingReportNarrative,
)
from models.meeting_semantic_consolidation import (
    ConsolidatedMeetingKnowledgeItem,
    MeetingKnowledgeItemReference,
    MeetingSemanticConsolidation,
)
from services.meeting_report_narrative_parser import (
    MeetingReportNarrativeParser,
)


def reference(
    chunk_index: int,
    item_index: int,
) -> MeetingKnowledgeItemReference:
    return MeetingKnowledgeItemReference(
        chunk_index=chunk_index,
        item_index=item_index,
    )


def build_consolidation() -> MeetingSemanticConsolidation:
    return MeetingSemanticConsolidation(
        items=[
            ConsolidatedMeetingKnowledgeItem(
                kind=ChunkKnowledgeKind.TOPIC,
                description=(
                    "Arquitectura actual y capacidad del servidor."
                ),
                source_refs=[
                    reference(
                        0,
                        0,
                    )
                ],
            ),
            ConsolidatedMeetingKnowledgeItem(
                kind=ChunkKnowledgeKind.DECISION,
                description=(
                    "Se aprobó migrar la base de datos a la nube."
                ),
                source_refs=[
                    reference(
                        0,
                        0,
                    )
                ],
            ),
            ConsolidatedMeetingKnowledgeItem(
                kind=ChunkKnowledgeKind.ACTION,
                description=(
                    "María preparará el plan de migración."
                ),
                source_refs=[
                    reference(
                        0,
                        0,
                    )
                ],
            ),
        ]
    )


def valid_payload() -> dict:
    return {
        "title": {
            "text": (
                "Migración de la base de datos"
            ),
            "source_item_ids": [
                1,
            ],
        },
        "objective": None,
        "executive_summary": {
            "text": (
                "Se revisó la arquitectura actual, se aprobó "
                "migrar la base de datos a la nube y María "
                "preparará el plan de migración."
            ),
            "source_item_ids": [
                0,
                1,
                2,
            ],
        },
        "key_points": [
            {
                "text": (
                    "Se aprobó migrar la base de datos "
                    "a la nube."
                ),
                "source_item_ids": [
                    1,
                ],
            },
            {
                "text": (
                    "María preparará el plan de migración."
                ),
                "source_item_ids": [
                    2,
                ],
            },
        ],
    }


def parse_payload(
    payload: dict,
) -> MeetingReportNarrative:
    return (
        MeetingReportNarrativeParser()
        .parse(
            response=json.dumps(
                payload,
                ensure_ascii=False,
            ),
            semantic_consolidation=(
                build_consolidation()
            ),
        )
    )


def test_parser_returns_grounded_narrative() -> None:
    result = parse_payload(
        valid_payload()
    )

    assert isinstance(
        result,
        MeetingReportNarrative,
    )
    assert (
        result.title.text
        == "Migración de la base de datos"
    )
    assert result.objective is None
    assert len(
        result.key_points
    ) == 2


def test_parser_accepts_grounded_objective() -> None:
    payload = valid_payload()
    payload["objective"] = {
        "text": (
            "Revisar la arquitectura actual."
        ),
        "source_item_ids": [
            0,
        ],
    }

    result = parse_payload(
        payload
    )

    assert result.objective is not None
    assert (
        result.objective.source_item_ids
        == [
            0
        ]
    )


def test_parser_accepts_wrapped_json() -> None:
    response = (
        "Resultado:\n"
        + json.dumps(
            valid_payload(),
            ensure_ascii=False,
        )
        + "\nFin."
    )

    result = (
        MeetingReportNarrativeParser()
        .parse(
            response=response,
            semantic_consolidation=(
                build_consolidation()
            ),
        )
    )

    assert (
        result.title.text
        == "Migración de la base de datos"
    )


def test_parser_rejects_invalid_consolidation() -> None:
    with pytest.raises(
        TypeError,
        match="MeetingSemanticConsolidation",
    ):
        (
            MeetingReportNarrativeParser()
            .parse(
                response="{}",
                semantic_consolidation=object(),
            )
        )


def test_parser_rejects_empty_consolidation() -> None:
    with pytest.raises(
        ValueError,
        match="no contiene items suficientes",
    ):
        (
            MeetingReportNarrativeParser()
            .parse(
                response="{}",
                semantic_consolidation=(
                    MeetingSemanticConsolidation()
                ),
            )
        )


def test_parser_rejects_extra_root_field() -> None:
    payload = valid_payload()
    payload["topics"] = []

    with pytest.raises(
        ValueError,
        match="campos no soportados",
    ):
        parse_payload(
            payload
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "title",
        "executive_summary",
    ],
)
def test_parser_rejects_non_object_grounded_field(
    field_name: str,
) -> None:
    payload = valid_payload()
    payload[field_name] = "texto"

    with pytest.raises(
        TypeError,
        match="debe ser un objeto",
    ):
        parse_payload(
            payload
        )


def test_parser_rejects_extra_grounded_field() -> None:
    payload = valid_payload()
    payload["title"][
        "kind"
    ] = "topic"

    with pytest.raises(
        ValueError,
        match="campos no soportados",
    ):
        parse_payload(
            payload
        )


def test_parser_rejects_empty_grounded_text() -> None:
    payload = valid_payload()
    payload["title"][
        "text"
    ] = "   "

    with pytest.raises(
        ValueError,
        match="text no puede estar vacío",
    ):
        parse_payload(
            payload
        )


def test_parser_rejects_non_list_source_ids() -> None:
    payload = valid_payload()
    payload["title"][
        "source_item_ids"
    ] = 1

    with pytest.raises(
        TypeError,
        match="debe ser una lista",
    ):
        parse_payload(
            payload
        )


def test_parser_rejects_empty_source_ids() -> None:
    payload = valid_payload()
    payload["title"][
        "source_item_ids"
    ] = []

    with pytest.raises(
        ValueError,
        match="al menos un source_item_id",
    ):
        parse_payload(
            payload
        )


@pytest.mark.parametrize(
    "source_item_id",
    [
        1.5,
        True,
        "1",
    ],
)
def test_parser_rejects_non_integer_source_id(
    source_item_id,
) -> None:
    payload = valid_payload()
    payload["title"][
        "source_item_ids"
    ] = [
        source_item_id
    ]

    with pytest.raises(
        TypeError,
        match="debe ser entero",
    ):
        parse_payload(
            payload
        )


def test_parser_rejects_unknown_source_id() -> None:
    payload = valid_payload()
    payload["title"][
        "source_item_ids"
    ] = [
        99
    ]

    with pytest.raises(
        ValueError,
        match="item semántico inexistente",
    ):
        parse_payload(
            payload
        )


def test_parser_rejects_duplicate_source_ids() -> None:
    payload = valid_payload()
    payload["title"][
        "source_item_ids"
    ] = [
        1,
        1,
    ]

    with pytest.raises(
        ValueError,
        match="valores duplicados",
    ):
        parse_payload(
            payload
        )


@pytest.mark.parametrize(
    "title",
    [
        "Presentación Global de la Reunión",
        "Resumen de la reunión",
        "Reunión de seguimiento",
        "Meeting Report",
    ],
)
def test_parser_rejects_generic_title(
    title: str,
) -> None:
    payload = valid_payload()
    payload["title"] = {
        "text": title,
        "source_item_ids": [
            1,
        ],
    }

    with pytest.raises(
        ValueError,
        match="demasiado genérico",
    ):
        parse_payload(
            payload
        )


def test_parser_rejects_title_without_lexical_grounding() -> None:
    payload = valid_payload()
    payload["title"] = {
        "text": (
            "Plan financiero trimestral"
        ),
        "source_item_ids": [
            1,
        ],
    }

    with pytest.raises(
        ValueError,
        match="grounding temático",
    ):
        parse_payload(
            payload
        )


def test_parser_accepts_specific_title_with_grounding() -> None:
    payload = valid_payload()
    payload["title"] = {
        "text": (
            "Arquitectura y migración de datos"
        ),
        "source_item_ids": [
            0,
            1,
        ],
    }

    result = parse_payload(
        payload
    )

    assert (
        result.title.text
        == "Arquitectura y migración de datos"
    )


def test_parser_rejects_summary_missing_source_item() -> None:
    payload = valid_payload()
    payload[
        "executive_summary"
    ][
        "source_item_ids"
    ] = [
        0,
        1,
    ]

    with pytest.raises(
        ValueError,
        match="referenciar todos los items semánticos",
    ):
        parse_payload(
            payload
        )


def test_parser_rejects_empty_key_points() -> None:
    payload = valid_payload()
    payload["key_points"] = []

    with pytest.raises(
        ValueError,
        match="al menos un elemento",
    ):
        parse_payload(
            payload
        )


def test_parser_rejects_excessive_key_points() -> None:
    payload = valid_payload()
    payload["key_points"] = [
        {
            "text": (
                f"Punto respaldado número {index}."
            ),
            "source_item_ids": [
                0,
            ],
        }
        for index in range(
            21
        )
    ]

    with pytest.raises(
        ValueError,
        match="más de 20",
    ):
        parse_payload(
            payload
        )


def test_parser_rejects_duplicate_key_point_text() -> None:
    payload = valid_payload()
    payload["key_points"] = [
        {
            "text": (
                "Se aprobó la migración."
            ),
            "source_item_ids": [
                1,
            ],
        },
        {
            "text": (
                "  SE APROBÓ LA MIGRACIÓN.  "
            ),
            "source_item_ids": [
                1,
            ],
        },
    ]

    with pytest.raises(
        ValueError,
        match="textos duplicados",
    ):
        parse_payload(
            payload
        )


def test_parser_propagates_json_decode_error() -> None:
    with pytest.raises(
        ValueError,
        match="JSON válido",
    ):
        (
            MeetingReportNarrativeParser()
            .parse(
                response="{invalid}",
                semantic_consolidation=(
                    build_consolidation()
                ),
            )
        )


def test_parser_does_not_mutate_consolidation() -> None:
    consolidation = (
        build_consolidation()
    )

    original = (
        consolidation.as_dict()
    )

    (
        MeetingReportNarrativeParser()
        .parse(
            response=json.dumps(
                valid_payload(),
                ensure_ascii=False,
            ),
            semantic_consolidation=(
                consolidation
            ),
        )
    )

    assert (
        consolidation.as_dict()
        == original
    )
