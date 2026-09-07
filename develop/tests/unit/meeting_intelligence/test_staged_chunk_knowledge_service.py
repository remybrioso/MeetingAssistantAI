import json
from copy import deepcopy
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
from services.json_schema_loader import JsonSchemaLoader
from services.chunk_classification_parser import (
    ChunkClassificationCoverageError,
    ChunkClassificationParser,
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
        self.classification_schema = JsonSchemaLoader().load(
            "chunk_classification_v2"
        )
        self.audit_schema = JsonSchemaLoader().load(
            "chunk_ignored_segment_audit_v1"
        )

    def load(
        self,
        contract: str,
    ) -> dict:
        self.contracts.append(
            contract
        )

        if contract == "chunk_classification_v2":
            return self.classification_schema

        if contract == "chunk_ignored_segment_audit_v1":
            return self.audit_schema

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
        self.arguments = []

    def format(
        self,
        *args,
        **kwargs,
    ) -> Prompt:
        self.calls += 1
        self.arguments.append((args, kwargs))
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
            "ignored_segment_ids": [],
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
            "ignored_segment_ids": [
                1,
                3,
                4,
            ],
        },
        ensure_ascii=False,
    )


def audit_confirmation_response(segment_ids: list[int]) -> str:
    return json.dumps({
        "items": [],
        "confirmed_ignored_segment_ids": segment_ids,
    })


def one_segment_classification_response() -> str:
    return json.dumps({
        "items": [{
            "kind": "topic",
            "description": "Tema del segmento único.",
            "segment_ids": [0],
        }],
        "ignored_segment_ids": [],
    })


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
        "chunk_classification_v2",
        "chunk_action_metadata_v1",
    ]


def test_service_sends_independent_chunk_specific_schemas() -> None:
    chunk = build_chunk()
    smaller_chunk = TranscriptChunk(index=8, segments=chunk.segments[:1])
    loader = FakeSchemaLoader()
    original_schema = deepcopy(loader.classification_schema)
    provider = FakeProvider(responses=[
        classification_response_with_action(),
        action_metadata_response(),
        one_segment_classification_response(),
    ])
    service = StagedChunkKnowledgeService(
        provider=provider, schema_loader=loader,
    )

    service.generate(chunk)
    service.generate(smaller_chunk)

    classification_calls = [provider.calls[0], provider.calls[2]]
    for call, expected_ids in zip(classification_calls, ([0, 1, 2, 3, 4], [0])):
        schema = call["schema"]
        properties = schema["properties"]
        item_properties = properties["items"]["items"]["properties"]
        assert item_properties["segment_ids"]["items"]["enum"] == expected_ids
        assert properties["ignored_segment_ids"]["items"]["enum"] == expected_ids
        expected_schema = deepcopy(original_schema)
        expected_properties = expected_schema["properties"]
        expected_properties["items"]["items"]["properties"]["segment_ids"]["items"]["enum"] = expected_ids
        expected_properties["ignored_segment_ids"]["items"]["enum"] = expected_ids
        assert schema == expected_schema
        assert schema is not loader.classification_schema

    assert len(provider.calls) == 3
    assert provider.calls[0]["schema"] is not provider.calls[2]["schema"]
    provider.calls[0]["schema"]["required"].append("test_mutation")
    assert provider.calls[2]["schema"]["required"] == original_schema["required"]
    assert loader.classification_schema == original_schema


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
            audit_confirmation_response([1, 3, 4]),
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

    assert len(provider.calls) == 2

    assert schema_loader.contracts == [
        "chunk_classification_v2",
        "chunk_ignored_segment_audit_v1",
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
                    "ignored_segment_ids": [
                        0,
                        1,
                        2,
                        3,
                        4,
                    ],
                }
            ),
            audit_confirmation_response([0, 1, 2, 3, 4]),
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
    assert len(provider.calls) == 2


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
            "chunk_classification_v2"
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


@pytest.mark.parametrize("with_items", [False, True])
def test_service_rejects_partial_coverage_before_action_stage(with_items: bool) -> None:
    data = json.loads(classification_response_without_action())
    if not with_items:
        data["items"] = []
    data["ignored_segment_ids"] = []
    provider = FakeProvider(responses=[json.dumps(data), json.dumps(data)])
    action_formatter = FakePromptFormatter(
        Prompt(content="must not run", version="chunk_action_metadata_v1")
    )
    loader = FakeSchemaLoader()
    service = StagedChunkKnowledgeService(
        provider=provider, schema_loader=loader,
        action_metadata_prompt_formatter=action_formatter,
    )
    with pytest.raises(ChunkClassificationCoverageError, match="cobertura completa"):
        service.generate(build_chunk())
    assert len(provider.calls) == 2
    assert action_formatter.calls == 0
    assert loader.contracts == ["chunk_classification_v2"]


def repair_formatter() -> FakePromptFormatter:
    return FakePromptFormatter(Prompt(
        content="repair coverage",
        version="chunk_classification_repair_v1",
    ))


def invalid_coverage_response(violation: str) -> str:
    data = json.loads(classification_response_with_action())
    if violation == "overlap":
        data["ignored_segment_ids"] = [0]
    else:
        data["items"] = data["items"][:-1]
    return json.dumps(data, ensure_ascii=False)


@pytest.mark.parametrize("with_actions", [False, True])
def test_valid_classification_never_formats_repair(with_actions: bool) -> None:
    responses = (
        [classification_response_with_action(), action_metadata_response()]
        if with_actions else [
            classification_response_without_action(),
            audit_confirmation_response([1, 3, 4]),
        ]
    )
    provider = FakeProvider(responses)
    formatter = repair_formatter()
    audit_formatter = FakePromptFormatter(
        Prompt("audit", "chunk_ignored_segment_audit_v1")
    )
    result = StagedChunkKnowledgeService(
        provider=provider, schema_loader=FakeSchemaLoader(),
        classification_repair_prompt_formatter=formatter,
        ignored_segment_audit_prompt_formatter=audit_formatter,
    ).generate(build_chunk())
    assert formatter.calls == 0
    assert audit_formatter.calls == (0 if with_actions else 1)
    assert len(provider.calls) == 2
    assert bool(result.action_items) == with_actions


@pytest.mark.parametrize("violation", ["overlap", "missing"])
def test_service_repairs_coverage_once_and_continues(violation: str) -> None:
    chunk = build_chunk()
    invalid_response = invalid_coverage_response(violation)
    with pytest.raises(ChunkClassificationCoverageError) as error:
        ChunkClassificationParser().parse(invalid_response, chunk)
    formatter = repair_formatter()
    loader = FakeSchemaLoader()
    original_schema = deepcopy(loader.classification_schema)
    provider = FakeProvider([
        invalid_response, classification_response_with_action(),
        action_metadata_response(),
    ])
    result = StagedChunkKnowledgeService(
        provider=provider, schema_loader=loader,
        classification_repair_prompt_formatter=formatter,
    ).generate(chunk)

    assert formatter.calls == 1
    assert formatter.arguments == [((), {
        "chunk": chunk,
        "invalid_response": invalid_response,
        "coverage_error": str(error.value),
    })]
    assert len(provider.calls) == 3  # J1, repair, action metadata.
    assert provider.calls[1]["prompt"] == "repair coverage"
    assert provider.calls[0]["schema"] is provider.calls[1]["schema"]
    for call in provider.calls[:2]:
        properties = call["schema"]["properties"]
        item_properties = properties["items"]["items"]["properties"]
        assert item_properties["segment_ids"]["items"]["enum"] == [0, 1, 2, 3, 4]
        assert properties["ignored_segment_ids"]["items"]["enum"] == [0, 1, 2, 3, 4]
    assert loader.contracts == ["chunk_classification_v2", "chunk_action_metadata_v1"]
    assert loader.classification_schema == original_schema
    assert len(result.action_items) == 1
    assert len(result.topics) == 1


@pytest.mark.parametrize("repaired_response, error_type", [
    (invalid_coverage_response("overlap"), ChunkClassificationCoverageError),
    (invalid_coverage_response("missing"), ChunkClassificationCoverageError),
    ("{invalid}", ValueError),
    ('{"items":[],"ignored_segment_ids":[5]}', ValueError),
    ('{"items":[],"ignored_segment_ids":[true]}', TypeError),
])
def test_invalid_repair_stops_before_actions(repaired_response, error_type) -> None:
    formatter = repair_formatter()
    actions = FakePromptFormatter(Prompt("must not run", "chunk_action_metadata_v1"))
    provider = FakeProvider([invalid_coverage_response("overlap"), repaired_response])
    loader = FakeSchemaLoader()
    service = StagedChunkKnowledgeService(
        provider=provider, schema_loader=loader,
        classification_repair_prompt_formatter=formatter,
        action_metadata_prompt_formatter=actions,
    )
    with pytest.raises(error_type):
        service.generate(build_chunk())
    assert formatter.calls == 1
    assert len(provider.calls) == 2
    assert actions.calls == 0
    assert loader.contracts == ["chunk_classification_v2"]


@pytest.mark.parametrize("response, error_type", [
    ("{invalid}", ValueError),
    ('{"items":[]}', ValueError),
    ('{"items":[],"ignored_segment_ids":[5]}', ValueError),
    ('{"items":[],"ignored_segment_ids":[0,0]}', ValueError),
    ('{"items":[],"ignored_segment_ids":[true]}', TypeError),
])
def test_unrelated_parser_errors_do_not_trigger_repair(response, error_type) -> None:
    formatter = repair_formatter()
    provider = FakeProvider([response])
    with pytest.raises(error_type) as error:
        StagedChunkKnowledgeService(
            provider=provider, schema_loader=FakeSchemaLoader(),
            classification_repair_prompt_formatter=formatter,
        ).generate(build_chunk())
    assert not isinstance(error.value, ChunkClassificationCoverageError)
    assert formatter.calls == 0
    assert len(provider.calls) == 1


@pytest.mark.parametrize("fail_on_call", [1, 2])
def test_provider_error_propagates_without_further_repair(fail_on_call: int) -> None:
    failure = RuntimeError("provider unavailable")

    class FailingProvider:
        calls = 0

        def generate(self, prompt, output_schema=None):
            self.calls += 1
            if self.calls == fail_on_call:
                raise failure
            return invalid_coverage_response("overlap")

    provider = FailingProvider()
    formatter = repair_formatter()
    actions = FakePromptFormatter(Prompt("must not run", "chunk_action_metadata_v1"))
    with pytest.raises(RuntimeError) as error:
        StagedChunkKnowledgeService(
            provider=provider, schema_loader=FakeSchemaLoader(),
            classification_repair_prompt_formatter=formatter,
            action_metadata_prompt_formatter=actions,
        ).generate(build_chunk())
    assert error.value is failure
    assert provider.calls == fail_on_call
    assert formatter.calls == fail_on_call - 1
    assert actions.calls == 0


@pytest.mark.parametrize("prompt, error_type", [
    (Prompt("repair", "chunk_classification_v2"), ValueError),
    (object(), TypeError),
])
def test_service_validates_repair_prompt_before_generation(prompt, error_type) -> None:
    provider = FakeProvider([invalid_coverage_response("overlap")])
    with pytest.raises(error_type):
        StagedChunkKnowledgeService(
            provider=provider, schema_loader=FakeSchemaLoader(),
            classification_repair_prompt_formatter=FakePromptFormatter(prompt),
        ).generate(build_chunk())
    assert len(provider.calls) == 1


def classification_with_ignored(candidate_ids: list[int], count: int = 5) -> str:
    kinds = ["decision", "topic", "risk", "pending", "topic"]
    items = [
        {
            "kind": kinds[index],
            "description": f"Conocimiento sustantivo {index}.",
            "segment_ids": [index],
        }
        for index in range(count)
        if index not in candidate_ids
    ]
    return json.dumps({
        "items": items,
        "ignored_segment_ids": candidate_ids,
    })


def audit_response_with_items(items, confirmed) -> str:
    return json.dumps({
        "items": items,
        "confirmed_ignored_segment_ids": confirmed,
    })


def audit_item(kind: str, segment_id: int, description: str = "Recuperado.") -> dict:
    return {
        "kind": kind,
        "description": description,
        "segment_ids": [segment_id],
    }


def test_ignored_audit_recovers_false_topic_before_assembly() -> None:
    provider = FakeProvider([
        classification_with_ignored([4]),
        audit_response_with_items([audit_item("topic", 4, "Presupuesto e infraestructura.")], []),
    ])
    audit_formatter = FakePromptFormatter(
        Prompt("audit", "chunk_ignored_segment_audit_v1")
    )
    result = StagedChunkKnowledgeService(
        provider=provider,
        schema_loader=FakeSchemaLoader(),
        ignored_segment_audit_prompt_formatter=audit_formatter,
    ).generate(build_chunk())
    assert audit_formatter.calls == 1
    assert len(provider.calls) == 2
    assert len(result.topics) == 2
    assert result.topics[-1].title == "Presupuesto e infraestructura."


def test_ignored_audit_recovers_action_and_runs_j2() -> None:
    initial = classification_with_ignored([1])
    provider = FakeProvider([
        initial,
        audit_response_with_items([audit_item("action", 1, "Preparar el plan.")], []),
        json.dumps({
            "actions": [{
                "item_index": 4,
                "owner": "María",
                "due_date": "2026-08-30",
                "status": "pending",
            }]
        }),
    ])
    result = StagedChunkKnowledgeService(
        provider=provider, schema_loader=FakeSchemaLoader(),
    ).generate(build_chunk())
    assert len(provider.calls) == 3
    assert len(result.action_items) == 1
    assert result.action_items[0].owner.display_name == "María"
    assert provider.calls[2]["prompt"].startswith("# Metadatos de acciones")


def test_ignored_audit_confirms_truly_ignorable_segment() -> None:
    provider = FakeProvider([
        classification_with_ignored([4]),
        audit_response_with_items([], [4]),
    ])
    result = StagedChunkKnowledgeService(
        provider=provider, schema_loader=FakeSchemaLoader(),
    ).generate(build_chunk())
    assert len(provider.calls) == 2
    assert len(result.topics) == 1
    assert result.action_items == []


def test_ignored_audit_accepts_mixed_recovery_and_confirmation() -> None:
    provider = FakeProvider([
        classification_with_ignored([2, 4]),
        audit_response_with_items([audit_item("topic", 2)], [4]),
    ])
    result = StagedChunkKnowledgeService(
        provider=provider, schema_loader=FakeSchemaLoader(),
    ).generate(build_chunk())
    assert len(provider.calls) == 2
    assert any(item.title == "Recuperado." for item in result.topics)


def test_ignored_audit_runs_after_valid_initial_classification() -> None:
    formatter = FakePromptFormatter(Prompt("audit", "chunk_ignored_segment_audit_v1"))
    provider = FakeProvider([
        classification_with_ignored([4]),
        audit_response_with_items([], [4]),
    ])
    StagedChunkKnowledgeService(
        provider=provider,
        schema_loader=FakeSchemaLoader(),
        ignored_segment_audit_prompt_formatter=formatter,
    ).generate(build_chunk())
    assert formatter.calls == 1
    assert len(provider.calls) == 2


def test_ignored_audit_runs_after_successful_bounded_repair() -> None:
    repair = repair_formatter()
    audit = FakePromptFormatter(Prompt("audit", "chunk_ignored_segment_audit_v1"))
    provider = FakeProvider([
        invalid_coverage_response("overlap"),
        classification_with_ignored([4]),
        audit_response_with_items([audit_item("topic", 4)], []),
    ])
    result = StagedChunkKnowledgeService(
        provider=provider,
        schema_loader=FakeSchemaLoader(),
        classification_repair_prompt_formatter=repair,
        ignored_segment_audit_prompt_formatter=audit,
    ).generate(build_chunk())
    assert repair.calls == 1
    assert audit.calls == 1
    assert len(provider.calls) == 3
    assert result.topics[-1].title == "Recuperado."


@pytest.mark.parametrize("audit_raw, error_type", [
    (audit_response_with_items([], []), ValueError),
    (audit_response_with_items([audit_item("topic", 4)], [4]), ValueError),
    ("{invalid}", ValueError),
])
def test_invalid_ignored_audit_stops_before_j2(audit_raw, error_type) -> None:
    action_formatter = FakePromptFormatter(Prompt("must not run", "chunk_action_metadata_v1"))
    provider = FakeProvider([classification_with_ignored([4]), audit_raw])
    with pytest.raises(error_type):
        StagedChunkKnowledgeService(
            provider=provider,
            schema_loader=FakeSchemaLoader(),
            action_metadata_prompt_formatter=action_formatter,
        ).generate(build_chunk())
    assert len(provider.calls) == 2
    assert action_formatter.calls == 0


def test_ignored_audit_provider_error_propagates() -> None:
    class FailingProvider:
        calls = 0

        def generate(self, prompt, output_schema=None):
            self.calls += 1
            if self.calls == 2:
                raise RuntimeError("audit unavailable")
            return classification_with_ignored([4])

    provider = FailingProvider()
    with pytest.raises(RuntimeError, match="audit unavailable"):
        StagedChunkKnowledgeService(
            provider=provider, schema_loader=FakeSchemaLoader(),
        ).generate(build_chunk())
    assert provider.calls == 2


def test_ignored_audit_specializes_independent_candidate_schemas() -> None:
    loader = FakeSchemaLoader()
    original = deepcopy(loader.audit_schema)
    smaller_chunk = TranscriptChunk(index=3, segments=build_chunk().segments[:3])
    provider = FakeProvider([
        classification_with_ignored([4]),
        audit_response_with_items([], [4]),
        classification_with_ignored([2], count=3),
        audit_response_with_items([], [2]),
    ])
    service = StagedChunkKnowledgeService(provider=provider, schema_loader=loader)
    service.generate(build_chunk())
    service.generate(smaller_chunk)
    audit_calls = [provider.calls[1], provider.calls[3]]
    for call, expected in zip(audit_calls, ([4], [2])):
        properties = call["schema"]["properties"]
        assert properties["items"]["items"]["properties"]["segment_ids"]["items"]["enum"] == expected
        assert properties["confirmed_ignored_segment_ids"]["items"]["enum"] == expected
    assert loader.audit_schema == original


def test_repaired_false_ignored_topic_is_recovered_by_audit() -> None:
    provider = FakeProvider([
        invalid_coverage_response("overlap"),
        classification_with_ignored([4]),
        audit_response_with_items([audit_item("topic", 4, "Presupuesto." )], []),
    ])
    result = StagedChunkKnowledgeService(
        provider=provider, schema_loader=FakeSchemaLoader(),
    ).generate(build_chunk())
    assert len(result.topics) == 2
    assert result.topics[-1].title == "Presupuesto."
