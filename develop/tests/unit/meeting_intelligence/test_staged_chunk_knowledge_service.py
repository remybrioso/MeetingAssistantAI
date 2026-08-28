import json
from datetime import date

import pytest

from models.chunk_knowledge import (
    ChunkKnowledge,
)
from models.prompt import Prompt
from models.transcript import Segment
from models.transcript_chunk import (
    TranscriptChunk,
)
from services.staged_chunk_knowledge_service import (
    StagedChunkKnowledgeService,
)


class FakeProvider:
    def __init__(
        self,
        responses: list[str],
    ) -> None:
        self.responses = list(
            responses
        )
        self.calls: list[dict] = []

    def generate(
        self,
        prompt: str,
        output_schema: dict | None = None,
    ) -> str:
        self.calls.append(
            {
                "prompt": prompt,
                "schema": output_schema,
            }
        )

        if not self.responses:
            raise AssertionError(
                "FakeProvider no tiene más "
                "respuestas configuradas."
            )

        return self.responses.pop(
            0
        )


class FakeSchemaLoader:
    def __init__(self) -> None:
        self.contracts: list[str] = []

    def load(
        self,
        contract: str,
    ) -> dict:
        self.contracts.append(
            contract
        )

        return {
            "type": "object",
            "contract": contract,
        }


class FakePromptFormatter:
    def __init__(
        self,
        prompt: Prompt,
    ) -> None:
        self.prompt = prompt
        self.calls = 0

    def format(
        self,
        *args,
        **kwargs,
    ) -> Prompt:
        self.calls += 1
        return self.prompt


def build_chunk() -> TranscriptChunk:
    return TranscriptChunk(
        index=2,
        segments=[
            Segment(
                start=0.0,
                end=8.0,
                speaker="LOCAL",
                text=(
                    "Se aprobó migrar la base "
                    "de datos a la nube."
                ),
            ),
            Segment(
                start=8.0,
                end=16.0,
                speaker="REMOTE",
                text=(
                    "María debe preparar el plan "
                    "antes del 30 de agosto de 2026."
                ),
            ),
            Segment(
                start=16.0,
                end=24.0,
                speaker="LOCAL",
                text=(
                    "Existe riesgo de interrupción "
                    "durante la migración."
                ),
            ),
            Segment(
                start=24.0,
                end=32.0,
                speaker="REMOTE",
                text=(
                    "Quedó pendiente confirmar la "
                    "ventana de mantenimiento."
                ),
            ),
            Segment(
                start=32.0,
                end=40.0,
                speaker="LOCAL",
                text=(
                    "Se revisó la arquitectura "
                    "actual."
                ),
            ),
        ],
    )


def classification_response_with_action() -> str:
    return json.dumps(
        {
            "items": [
                {
                    "kind": "decision",
                    "description": (
                        "Migrar la base de datos "
                        "a la nube."
                    ),
                    "segment_ids": [
                        0,
                    ],
                },
                {
                    "kind": "action",
                    "description": (
                        "Preparar el plan."
                    ),
                    "segment_ids": [
                        1,
                    ],
                },
                {
                    "kind": "risk",
                    "description": (
                        "Interrupción durante "
                        "la migración."
                    ),
                    "segment_ids": [
                        2,
                    ],
                },
                {
                    "kind": "pending",
                    "description": (
                        "Confirmar la ventana "
                        "de mantenimiento."
                    ),
                    "segment_ids": [
                        3,
                    ],
                },
                {
                    "kind": "topic",
                    "description": (
                        "Arquitectura actual."
                    ),
                    "segment_ids": [
                        4,
                    ],
                },
            ],
        },
        ensure_ascii=False,
    )


def action_metadata_response() -> str:
    return json.dumps(
        {
            "actions": [
                {
                    "item_index": 1,
                    "owner": "María",
                    "due_date": (
                        "2026-08-30"
                    ),
                    "status": "pending",
                },
            ],
        },
        ensure_ascii=False,
    )


def classification_response_without_action() -> str:
    return json.dumps(
        {
            "items": [
                {
                    "kind": "decision",
                    "description": (
                        "Migrar la base de datos "
                        "a la nube."
                    ),
                    "segment_ids": [
                        0,
                    ],
                },
                {
                    "kind": "risk",
                    "description": (
                        "Interrupción durante "
                        "la migración."
                    ),
                    "segment_ids": [
                        2,
                    ],
                },
            ],
        },
        ensure_ascii=False,
    )


def test_service_runs_complete_staged_pipeline() -> None:
    chunk = build_chunk()

    provider = FakeProvider(
        responses=[
            classification_response_with_action(),
            action_metadata_response(),
        ]
    )

    schema_loader = FakeSchemaLoader()

    service = StagedChunkKnowledgeService(
        provider=provider,
        schema_loader=schema_loader,
    )

    result = service.generate(
        chunk
    )

    assert isinstance(
        result,
        ChunkKnowledge,
    )

    assert result.chunk_index == chunk.index
    assert result.start == chunk.start
    assert result.end == chunk.end

    assert len(
        result.decisions
    ) == 1
    assert len(
        result.action_items
    ) == 1
    assert len(
        result.risks
    ) == 1
    assert len(
        result.pending_items
    ) == 1
    assert len(
        result.topics
    ) == 1

    assert len(
        provider.calls
    ) == 2

    assert schema_loader.contracts == [
        "chunk_classification_v1",
        "chunk_action_metadata_v1",
    ]


def test_service_enriches_action_metadata() -> None:
    chunk = build_chunk()

    service = StagedChunkKnowledgeService(
        provider=FakeProvider(
            responses=[
                classification_response_with_action(),
                action_metadata_response(),
            ]
        ),
        schema_loader=FakeSchemaLoader(),
    )

    result = service.generate(
        chunk
    )

    action = result.action_items[
        0
    ]

    assert action.owner is not None
    assert (
        action.owner.display_name
        == "María"
    )

    assert action.due_date == date(
        2026,
        8,
        30,
    )

    assert (
        action.status.value
        == "pending"
    )


def test_service_reconstructs_evidence_from_chunk() -> None:
    chunk = build_chunk()

    service = StagedChunkKnowledgeService(
        provider=FakeProvider(
            responses=[
                classification_response_with_action(),
                action_metadata_response(),
            ]
        ),
        schema_loader=FakeSchemaLoader(),
    )

    result = service.generate(
        chunk
    )

    evidence = result.action_items[
        0
    ].evidence[
        0
    ]

    source_segment = chunk.segments[
        1
    ]

    assert (
        evidence.speaker
        == source_segment.speaker
    )
    assert (
        evidence.start
        == source_segment.start
    )
    assert (
        evidence.end
        == source_segment.end
    )
    assert (
        evidence.excerpt
        == source_segment.text
    )


def test_service_skips_action_stage_when_no_actions() -> None:
    chunk = build_chunk()

    provider = FakeProvider(
        responses=[
            classification_response_without_action(),
        ]
    )

    schema_loader = FakeSchemaLoader()

    service = StagedChunkKnowledgeService(
        provider=provider,
        schema_loader=schema_loader,
    )

    result = service.generate(
        chunk
    )

    assert len(
        provider.calls
    ) == 1

    assert schema_loader.contracts == [
        "chunk_classification_v1",
    ]

    assert result.action_items == []
    assert len(
        result.decisions
    ) == 1
    assert len(
        result.risks
    ) == 1


def test_service_accepts_empty_classification() -> None:
    chunk = build_chunk()

    provider = FakeProvider(
        responses=[
            json.dumps(
                {
                    "items": [],
                }
            ),
        ]
    )

    service = StagedChunkKnowledgeService(
        provider=provider,
        schema_loader=FakeSchemaLoader(),
    )

    result = service.generate(
        chunk
    )

    assert result.has_content is False
    assert len(
        provider.calls
    ) == 1


def test_service_rejects_non_chunk_input() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "chunk debe ser una instancia"
        ),
    ):
        StagedChunkKnowledgeService().generate(
            object()
        )


def test_service_rejects_wrong_classification_contract() -> None:
    chunk = build_chunk()

    formatter = FakePromptFormatter(
        Prompt(
            content="classification",
            version="wrong_contract",
        )
    )

    provider = FakeProvider(
        responses=[]
    )

    service = StagedChunkKnowledgeService(
        provider=provider,
        classification_prompt_formatter=(
            formatter
        ),
        schema_loader=FakeSchemaLoader(),
    )

    with pytest.raises(
        ValueError,
        match=(
            "chunk_classification_v1"
        ),
    ):
        service.generate(
            chunk
        )

    assert provider.calls == []


def test_service_propagates_classification_parser_error() -> None:
    chunk = build_chunk()

    provider = FakeProvider(
        responses=[
            "{invalid}",
        ]
    )

    service = StagedChunkKnowledgeService(
        provider=provider,
        schema_loader=FakeSchemaLoader(),
    )

    with pytest.raises(
        ValueError,
        match="JSON válido",
    ):
        service.generate(
            chunk
        )

    assert len(
        provider.calls
    ) == 1


def test_service_propagates_action_metadata_parser_error() -> None:
    chunk = build_chunk()

    provider = FakeProvider(
        responses=[
            classification_response_with_action(),
            "{invalid}",
        ]
    )

    service = StagedChunkKnowledgeService(
        provider=provider,
        schema_loader=FakeSchemaLoader(),
    )

    with pytest.raises(
        ValueError,
        match="JSON válido",
    ):
        service.generate(
            chunk
        )

    assert len(
        provider.calls
    ) == 2


def test_service_propagates_provider_error() -> None:
    chunk = build_chunk()

    class FailingProvider:
        def generate(
            self,
            prompt,
            output_schema=None,
        ):
            raise RuntimeError(
                "provider unavailable"
            )

    service = StagedChunkKnowledgeService(
        provider=FailingProvider(),
        schema_loader=FakeSchemaLoader(),
    )

    with pytest.raises(
        RuntimeError,
        match="provider unavailable",
    ):
        service.generate(
            chunk
        )


def test_service_rejects_wrong_action_metadata_contract() -> None:
    chunk = build_chunk()

    provider = FakeProvider(
        responses=[
            classification_response_with_action(),
        ]
    )

    action_formatter = FakePromptFormatter(
        Prompt(
            content="actions",
            version="wrong_contract",
        )
    )

    service = StagedChunkKnowledgeService(
        provider=provider,
        action_metadata_prompt_formatter=(
            action_formatter
        ),
        schema_loader=FakeSchemaLoader(),
    )

    with pytest.raises(
        ValueError,
        match=(
            "chunk_action_metadata_v1"
        ),
    ):
        service.generate(
            chunk
        )

    assert len(
        provider.calls
    ) == 1