import json

import pytest

from models.chunk_classification import (
    ChunkClassification,
    ChunkKnowledgeKind,
)
from models.transcript import Segment
from models.transcript_chunk import TranscriptChunk
from services.chunk_classification_parser import (
    ChunkClassificationParser,
)


def build_chunk() -> TranscriptChunk:
    return TranscriptChunk(
        index=4,
        segments=[
            Segment(
                start=10.0,
                end=15.0,
                speaker="LOCAL",
                text="Se aprobó migrar el servicio.",
            ),
            Segment(
                start=15.0,
                end=20.0,
                speaker="REMOTE",
                text="María preparará el plan.",
            ),
        ],
    )


def build_response() -> str:
    return json.dumps(
        {
            "items": [
                {
                    "kind": "decision",
                    "description": (
                        "Se aprobó migrar el servicio."
                    ),
                    "segment_ids": [
                        0,
                    ],
                },
                {
                    "kind": "action",
                    "description": (
                        "María preparará el plan."
                    ),
                    "segment_ids": [
                        1,
                    ],
                },
            ],
        },
        ensure_ascii=False,
    )


def test_parser_builds_system_owned_classification() -> None:
    chunk = build_chunk()

    result = ChunkClassificationParser().parse(
        response=build_response(),
        chunk=chunk,
    )

    assert isinstance(
        result,
        ChunkClassification,
    )
    assert result.chunk_index == chunk.index
    assert result.start == chunk.start
    assert result.end == chunk.end
    assert len(
        result.items
    ) == 2
    assert (
        result.items[0].kind
        is ChunkKnowledgeKind.DECISION
    )
    assert result.items[1].segment_ids == [
        1,
    ]


def test_parser_accepts_empty_items() -> None:
    result = ChunkClassificationParser().parse(
        response='{"items":[]}',
        chunk=build_chunk(),
    )

    assert result.items == []
    assert result.has_content is False


def test_parser_extracts_json_from_fenced_response() -> None:
    response = (
        "```json\n"
        + build_response()
        + "\n```"
    )

    result = ChunkClassificationParser().parse(
        response=response,
        chunk=build_chunk(),
    )

    assert len(
        result.items
    ) == 2


def test_parser_rejects_root_metadata_from_llm() -> None:
    data = json.loads(
        build_response()
    )
    data["chunk_index"] = 99

    with pytest.raises(
        ValueError,
        match="campos no soportados",
    ):
        ChunkClassificationParser().parse(
            response=json.dumps(
                data
            ),
            chunk=build_chunk(),
        )


def test_parser_rejects_missing_root_items() -> None:
    with pytest.raises(
        ValueError,
        match="campos requeridos",
    ):
        ChunkClassificationParser().parse(
            response="{}",
            chunk=build_chunk(),
        )


def test_parser_rejects_unknown_item_field() -> None:
    data = json.loads(
        build_response()
    )
    data["items"][0][
        "owner"
    ] = "María"

    with pytest.raises(
        ValueError,
        match="campos no soportados",
    ):
        ChunkClassificationParser().parse(
            response=json.dumps(
                data,
                ensure_ascii=False,
            ),
            chunk=build_chunk(),
        )


def test_parser_rejects_unknown_kind() -> None:
    data = json.loads(
        build_response()
    )
    data["items"][0][
        "kind"
    ] = "conclusion"

    with pytest.raises(
        ValueError,
        match="kind no contiene un valor válido",
    ):
        ChunkClassificationParser().parse(
            response=json.dumps(
                data
            ),
            chunk=build_chunk(),
        )


def test_parser_rejects_empty_description() -> None:
    data = json.loads(
        build_response()
    )
    data["items"][0][
        "description"
    ] = " "

    with pytest.raises(
        ValueError,
        match="description no puede estar vacío",
    ):
        ChunkClassificationParser().parse(
            response=json.dumps(
                data
            ),
            chunk=build_chunk(),
        )


def test_parser_rejects_empty_segment_ids() -> None:
    data = json.loads(
        build_response()
    )
    data["items"][0][
        "segment_ids"
    ] = []

    with pytest.raises(
        ValueError,
        match="al menos un segment_id",
    ):
        ChunkClassificationParser().parse(
            response=json.dumps(
                data
            ),
            chunk=build_chunk(),
        )


def test_parser_rejects_out_of_range_segment_id() -> None:
    data = json.loads(
        build_response()
    )
    data["items"][0][
        "segment_ids"
    ] = [
        2,
    ]

    with pytest.raises(
        ValueError,
        match="segmento inexistente",
    ):
        ChunkClassificationParser().parse(
            response=json.dumps(
                data
            ),
            chunk=build_chunk(),
        )


def test_parser_rejects_boolean_segment_id() -> None:
    data = json.loads(
        build_response()
    )
    data["items"][0][
        "segment_ids"
    ] = [
        True,
    ]

    with pytest.raises(
        TypeError,
        match="debe ser entero",
    ):
        ChunkClassificationParser().parse(
            response=json.dumps(
                data
            ),
            chunk=build_chunk(),
        )


def test_parser_rejects_duplicate_segment_ids() -> None:
    data = json.loads(
        build_response()
    )
    data["items"][0][
        "segment_ids"
    ] = [
        0,
        0,
    ]

    with pytest.raises(
        ValueError,
        match="duplicados",
    ):
        ChunkClassificationParser().parse(
            response=json.dumps(
                data
            ),
            chunk=build_chunk(),
        )


def test_parser_rejects_non_chunk() -> None:
    with pytest.raises(
        TypeError,
        match="TranscriptChunk",
    ):
        ChunkClassificationParser().parse(
            response='{"items":[]}',
            chunk=object(),
        )


def test_parser_rejects_invalid_json() -> None:
    with pytest.raises(
        ValueError,
        match="JSON válido",
    ):
        ChunkClassificationParser().parse(
            response="{invalid}",
            chunk=build_chunk(),
        )
