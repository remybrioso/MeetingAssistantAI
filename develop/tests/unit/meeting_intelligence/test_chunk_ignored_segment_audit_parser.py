import json

import pytest

from models.transcript import Segment
from models.transcript_chunk import TranscriptChunk
from services.chunk_ignored_segment_audit_parser import (
    ChunkIgnoredSegmentAuditParser,
)


def build_chunk() -> TranscriptChunk:
    return TranscriptChunk(
        index=0,
        segments=[
            Segment(start=float(index), end=float(index + 1), speaker="LOCAL", text=f"Segmento {index}.")
            for index in range(5)
        ],
    )


def response(items, confirmed):
    return json.dumps({
        "items": items,
        "confirmed_ignored_segment_ids": confirmed,
    }, ensure_ascii=False)


def topic(segment_id=2):
    return {
        "kind": "topic",
        "description": "Se revisó un asunto sustantivo.",
        "segment_ids": [segment_id],
    }


def test_parser_recovers_items_and_confirms_remaining_candidates() -> None:
    result = ChunkIgnoredSegmentAuditParser().parse(
        response([topic(2)], [4]), build_chunk(), [2, 4]
    )
    assert len(result.recovered_items) == 1
    assert result.recovered_items[0].segment_ids == [2]
    assert result.confirmed_ignored_segment_ids == (4,)


@pytest.mark.parametrize("items, confirmed, match", [
    ([topic(2)], [], "faltan IDs"),
    ([topic(2)], [2, 4], "recuperar y confirmar"),
    ([topic(1), topic(2)], [4], "no fueron enviados"),
    ([], [4, 4, 2], "valores duplicados"),
])
def test_parser_rejects_invalid_coverage(items, confirmed, match) -> None:
    with pytest.raises((ValueError, TypeError), match=match):
        ChunkIgnoredSegmentAuditParser().parse(
            response(items, confirmed), build_chunk(), [2, 4]
        )


def test_parser_rejects_non_candidate_in_confirmed_ids() -> None:
    with pytest.raises(ValueError, match="no fueron enviados"):
        ChunkIgnoredSegmentAuditParser().parse(
            response([], [1, 4]), build_chunk(), [2, 4]
        )


@pytest.mark.parametrize("payload, error_type", [
    ("{invalid}", ValueError),
    ({"items": [], "confirmed_ignored_segment_ids": [True, 4]}, TypeError),
    ({"items": [{"kind": "topic", "description": "", "segment_ids": [2]}], "confirmed_ignored_segment_ids": [4]}, ValueError),
    ({"items": [{"kind": "unknown", "description": "x", "segment_ids": [2]}], "confirmed_ignored_segment_ids": [4]}, ValueError),
    ({"items": [], "confirmed_ignored_segment_ids": [4], "extra": 1}, ValueError),
    ({"items": [{"kind": "topic", "description": "x"}], "confirmed_ignored_segment_ids": [4]}, ValueError),
])
def test_parser_rejects_malformed_output(payload, error_type) -> None:
    raw = payload if isinstance(payload, str) else json.dumps(payload)
    with pytest.raises(error_type):
        ChunkIgnoredSegmentAuditParser().parse(raw, build_chunk(), [2, 4])


def test_parser_rejects_invalid_candidates() -> None:
    with pytest.raises(ValueError, match="duplicados"):
        ChunkIgnoredSegmentAuditParser().parse(response([], [2]), build_chunk(), [2, 2])
    with pytest.raises(ValueError, match="inexistentes"):
        ChunkIgnoredSegmentAuditParser().parse(response([], [8]), build_chunk(), [8])
