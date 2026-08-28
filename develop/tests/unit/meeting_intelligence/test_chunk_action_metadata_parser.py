import json
from datetime import date

import pytest

from models.chunk_action_metadata import (
    ChunkActionMetadata,
)
from models.chunk_classification import (
    ChunkClassification,
    ChunkKnowledgeKind,
    ClassifiedKnowledgeItem,
)
from models.meeting_report import (
    ActionStatus,
)
from models.transcript import Segment
from models.transcript_chunk import TranscriptChunk
from services.chunk_action_metadata_parser import (
    ChunkActionMetadataParser,
)


def build_chunk() -> TranscriptChunk:
    return TranscriptChunk(
        index=5,
        segments=[
            Segment(
                start=0.0,
                end=8.0,
                speaker="LOCAL",
                text="Se aprobó migrar la base de datos.",
            ),
            Segment(
                start=8.0,
                end=16.0,
                speaker="REMOTE",
                text=(
                    "María debe preparar el plan antes del "
                    "30 de agosto de 2026."
                ),
            ),
            Segment(
                start=16.0,
                end=24.0,
                speaker="LOCAL",
                text="Infraestructura debe validar el respaldo.",
            ),
        ],
    )


def build_classification() -> ChunkClassification:
    chunk = build_chunk()

    return ChunkClassification(
        chunk_index=chunk.index,
        start=chunk.start,
        end=chunk.end,
        items=[
            ClassifiedKnowledgeItem(
                kind=ChunkKnowledgeKind.DECISION,
                description=(
                    "Se aprobó migrar la base de datos."
                ),
                segment_ids=[
                    0,
                ],
            ),
            ClassifiedKnowledgeItem(
                kind=ChunkKnowledgeKind.ACTION,
                description="María debe preparar el plan.",
                segment_ids=[
                    1,
                ],
            ),
            ClassifiedKnowledgeItem(
                kind=ChunkKnowledgeKind.ACTION,
                description=(
                    "Infraestructura debe validar el respaldo."
                ),
                segment_ids=[
                    2,
                ],
            ),
        ],
    )


def build_response() -> str:
    return json.dumps(
        {
            "actions": [
                {
                    "item_index": 1,
                    "owner": "María",
                    "due_date": "2026-08-30",
                    "status": "pending",
                },
                {
                    "item_index": 2,
                    "owner": "Infraestructura",
                    "due_date": None,
                    "status": "pending",
                },
            ],
        },
        ensure_ascii=False,
    )


def test_parser_builds_batch_metadata() -> None:
    result = ChunkActionMetadataParser().parse(
        response=build_response(),
        classification=build_classification(),
        chunk=build_chunk(),
    )

    assert isinstance(
        result,
        ChunkActionMetadata,
    )
    assert result.chunk_index == 5
    assert len(
        result.entries
    ) == 2
    assert (
        result.entries[0].owner.display_name
        == "María"
    )
    assert result.entries[0].due_date == date(
        2026,
        8,
        30,
    )
    assert (
        result.entries[0].status
        is ActionStatus.PENDING
    )


def test_parser_accepts_fenced_json() -> None:
    result = ChunkActionMetadataParser().parse(
        response=(
            "```json\n"
            + build_response()
            + "\n```"
        ),
        classification=build_classification(),
        chunk=build_chunk(),
    )

    assert len(
        result.entries
    ) == 2


def test_parser_accepts_null_owner_and_due_date() -> None:
    data = json.loads(
        build_response()
    )
    data["actions"][1][
        "owner"
    ] = None

    result = ChunkActionMetadataParser().parse(
        response=json.dumps(
            data,
            ensure_ascii=False,
        ),
        classification=build_classification(),
        chunk=build_chunk(),
    )

    assert result.entries[1].owner is None
    assert result.entries[1].due_date is None


def test_parser_rejects_owner_not_present_in_action_segments() -> None:
    data = json.loads(
        build_response()
    )
    data["actions"][0][
        "owner"
    ] = "REMOTE"

    with pytest.raises(
        ValueError,
        match="no aparece de forma literal",
    ):
        ChunkActionMetadataParser().parse(
            response=json.dumps(
                data,
                ensure_ascii=False,
            ),
            classification=build_classification(),
            chunk=build_chunk(),
        )


def test_parser_owner_grounding_is_case_insensitive() -> None:
    data = json.loads(
        build_response()
    )
    data["actions"][0][
        "owner"
    ] = "maría"

    result = ChunkActionMetadataParser().parse(
        response=json.dumps(
            data,
            ensure_ascii=False,
        ),
        classification=build_classification(),
        chunk=build_chunk(),
    )

    assert (
        result.entries[0].owner.display_name
        == "maría"
    )


def test_parser_rejects_invalid_due_date() -> None:
    data = json.loads(
        build_response()
    )
    data["actions"][0][
        "due_date"
    ] = "30-08-2026"

    with pytest.raises(
        ValueError,
        match="YYYY-MM-DD",
    ):
        ChunkActionMetadataParser().parse(
            response=json.dumps(
                data
            ),
            classification=build_classification(),
            chunk=build_chunk(),
        )


def test_parser_rejects_unknown_status() -> None:
    data = json.loads(
        build_response()
    )
    data["actions"][0][
        "status"
    ] = "open"

    with pytest.raises(
        ValueError,
        match="estado válido",
    ):
        ChunkActionMetadataParser().parse(
            response=json.dumps(
                data
            ),
            classification=build_classification(),
            chunk=build_chunk(),
        )


def test_parser_rejects_missing_action_metadata() -> None:
    data = json.loads(
        build_response()
    )
    data["actions"] = data[
        "actions"
    ][:1]

    with pytest.raises(
        ValueError,
        match="Faltan item_index: 2",
    ):
        ChunkActionMetadataParser().parse(
            response=json.dumps(
                data
            ),
            classification=build_classification(),
            chunk=build_chunk(),
        )


def test_parser_rejects_duplicate_item_index() -> None:
    data = json.loads(
        build_response()
    )
    data["actions"][1][
        "item_index"
    ] = 1
    data["actions"][1][
        "owner"
    ] = "María"

    with pytest.raises(
        ValueError,
        match="duplicado",
    ):
        ChunkActionMetadataParser().parse(
            response=json.dumps(
                data,
                ensure_ascii=False,
            ),
            classification=build_classification(),
            chunk=build_chunk(),
        )


def test_parser_rejects_non_action_item_index() -> None:
    data = json.loads(
        build_response()
    )
    data["actions"][0][
        "item_index"
    ] = 0
    data["actions"][0][
        "owner"
    ] = None

    with pytest.raises(
        ValueError,
        match="no referencia una acción",
    ):
        ChunkActionMetadataParser().parse(
            response=json.dumps(
                data
            ),
            classification=build_classification(),
            chunk=build_chunk(),
        )


def test_parser_rejects_out_of_range_item_index() -> None:
    data = json.loads(
        build_response()
    )
    data["actions"][0][
        "item_index"
    ] = 99

    with pytest.raises(
        ValueError,
        match="item inexistente",
    ):
        ChunkActionMetadataParser().parse(
            response=json.dumps(
                data
            ),
            classification=build_classification(),
            chunk=build_chunk(),
        )


def test_parser_rejects_boolean_item_index() -> None:
    data = json.loads(
        build_response()
    )
    data["actions"][0][
        "item_index"
    ] = True

    with pytest.raises(
        TypeError,
        match="debe ser entero",
    ):
        ChunkActionMetadataParser().parse(
            response=json.dumps(
                data
            ),
            classification=build_classification(),
            chunk=build_chunk(),
        )


def test_parser_rejects_unknown_action_field() -> None:
    data = json.loads(
        build_response()
    )
    data["actions"][0][
        "description"
    ] = "No permitido"

    with pytest.raises(
        ValueError,
        match="campos no soportados",
    ):
        ChunkActionMetadataParser().parse(
            response=json.dumps(
                data
            ),
            classification=build_classification(),
            chunk=build_chunk(),
        )


def test_parser_rejects_unknown_root_field() -> None:
    data = json.loads(
        build_response()
    )
    data["chunk_index"] = 5

    with pytest.raises(
        ValueError,
        match="campos no soportados",
    ):
        ChunkActionMetadataParser().parse(
            response=json.dumps(
                data
            ),
            classification=build_classification(),
            chunk=build_chunk(),
        )


def test_parser_accepts_empty_actions_when_classification_has_none() -> None:
    chunk = build_chunk()
    classification = ChunkClassification(
        chunk_index=chunk.index,
        start=chunk.start,
        end=chunk.end,
        items=[
            ClassifiedKnowledgeItem(
                kind=ChunkKnowledgeKind.TOPIC,
                description="Tema general.",
                segment_ids=[
                    0,
                ],
            )
        ],
    )

    result = ChunkActionMetadataParser().parse(
        response='{"actions":[]}',
        classification=classification,
        chunk=chunk,
    )

    assert result.entries == []


def test_parser_rejects_classification_chunk_index_mismatch() -> None:
    classification = build_classification()
    classification.chunk_index = 99

    with pytest.raises(
        ValueError,
        match="chunk_index",
    ):
        ChunkActionMetadataParser().parse(
            response=build_response(),
            classification=classification,
            chunk=build_chunk(),
        )


def test_parser_rejects_invalid_json() -> None:
    with pytest.raises(
        ValueError,
        match="JSON válido",
    ):
        ChunkActionMetadataParser().parse(
            response="{invalid}",
            classification=build_classification(),
            chunk=build_chunk(),
        )


def test_parser_rejects_non_classification() -> None:
    with pytest.raises(
        TypeError,
        match="ChunkClassification",
    ):
        ChunkActionMetadataParser().parse(
            response='{"actions":[]}',
            classification=object(),
            chunk=build_chunk(),
        )


def test_parser_rejects_non_chunk() -> None:
    with pytest.raises(
        TypeError,
        match="TranscriptChunk",
    ):
        ChunkActionMetadataParser().parse(
            response='{"actions":[]}',
            classification=build_classification(),
            chunk=object(),
        )
