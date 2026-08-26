import json

import pytest

from models.chunk_knowledge import ChunkKnowledge
from models.prompt import Prompt
from models.transcript import Segment
from models.transcript_chunk import TranscriptChunk
from services.chunk_knowledge_service import (
    ChunkKnowledgeService,
)


EMPTY_RESPONSE = json.dumps(
    {
        "key_points": [],
        "topics": [],
        "decisions": [],
        "action_items": [],
        "risks": [],
        "pending_items": [],
        "participants": [],
        "conclusions": [],
    }
)


class FakeProvider:
    def __init__(
        self,
        response: str = EMPTY_RESPONSE,
        error: Exception | None = None,
    ) -> None:
        self.response = response
        self.error = error
        self.calls = 0
        self.received_prompt = None
        self.received_schema = None

    def generate(
        self,
        prompt,
        schema,
    ):
        self.calls += 1
        self.received_prompt = prompt
        self.received_schema = schema

        if self.error is not None:
            raise self.error

        return self.response


class FakeSchemaLoader:
    def __init__(
        self,
        schema=None,
        error: Exception | None = None,
    ) -> None:
        self.schema = (
            schema
            if schema is not None
            else {"type": "object"}
        )
        self.error = error
        self.calls = 0
        self.received_contract = None

    def load(
        self,
        contract,
    ):
        self.calls += 1
        self.received_contract = contract

        if self.error is not None:
            raise self.error

        return self.schema


class FakeParser:
    def __init__(
        self,
        result=None,
        error: Exception | None = None,
    ) -> None:
        self.result = result
        self.error = error
        self.calls = 0
        self.received_response = None
        self.received_chunk = None

    def parse(
        self,
        response,
        chunk,
    ):
        self.calls += 1
        self.received_response = response
        self.received_chunk = chunk

        if self.error is not None:
            raise self.error

        return self.result


def build_chunk() -> TranscriptChunk:
    return TranscriptChunk(
        index=3,
        segments=[
            Segment(
                start=30.0,
                end=36.0,
                speaker="REMOTE",
                text=(
                    "Se revisó el estado del proyecto."
                ),
            ),
        ],
    )


def build_prompt() -> Prompt:
    return Prompt(
        content=(
            "Prompt estructurado del chunk."
        ),
        version="chunk_knowledge_v1",
    )


def test_service_runs_structured_generation_flow() -> None:
    chunk = build_chunk()
    prompt = build_prompt()

    expected = ChunkKnowledge(
        chunk_index=chunk.index,
        start=chunk.start,
        end=chunk.end,
        key_points=[
            "Se revisó el estado del proyecto.",
        ],
    )

    provider = FakeProvider()
    schema_loader = FakeSchemaLoader(
        schema={
            "type": "object",
            "required": [
                "key_points",
            ],
        }
    )
    parser = FakeParser(
        result=expected
    )

    service = ChunkKnowledgeService(
        provider=provider,
        parser=parser,
        schema_loader=schema_loader,
    )

    result = service.generate(
        prompt=prompt,
        chunk=chunk,
    )

    assert result is expected
    assert schema_loader.calls == 1
    assert (
        schema_loader.received_contract
        == "chunk_knowledge_v1"
    )
    assert provider.calls == 1
    assert (
        provider.received_prompt
        == prompt.content
    )
    assert (
        provider.received_schema
        == schema_loader.schema
    )
    assert parser.calls == 1
    assert (
        parser.received_response
        == provider.response
    )
    assert parser.received_chunk is chunk


def test_service_with_real_parser_builds_chunk_knowledge() -> None:
    chunk = build_chunk()

    service = ChunkKnowledgeService(
        provider=FakeProvider(),
        schema_loader=FakeSchemaLoader(),
    )

    result = service.generate(
        prompt=build_prompt(),
        chunk=chunk,
    )

    assert isinstance(
        result,
        ChunkKnowledge,
    )
    assert result.chunk_index == 3
    assert result.start == 30.0
    assert result.end == 36.0
    assert result.has_content is False


def test_service_rejects_invalid_prompt() -> None:
    service = ChunkKnowledgeService(
        provider=FakeProvider(),
        schema_loader=FakeSchemaLoader(),
    )

    with pytest.raises(
        TypeError,
        match="instancia de Prompt",
    ):
        service.generate(
            prompt=object(),
            chunk=build_chunk(),
        )


def test_service_rejects_invalid_chunk() -> None:
    service = ChunkKnowledgeService(
        provider=FakeProvider(),
        schema_loader=FakeSchemaLoader(),
    )

    with pytest.raises(
        TypeError,
        match="instancia de TranscriptChunk",
    ):
        service.generate(
            prompt=build_prompt(),
            chunk=object(),
        )


def test_service_rejects_wrong_contract() -> None:
    provider = FakeProvider()
    schema_loader = FakeSchemaLoader()

    service = ChunkKnowledgeService(
        provider=provider,
        schema_loader=schema_loader,
    )

    with pytest.raises(
        ValueError,
        match="requiere el contrato chunk_knowledge_v1",
    ):
        service.generate(
            prompt=Prompt(
                content="Prompt.",
                version="meeting_report_v1",
            ),
            chunk=build_chunk(),
        )

    assert provider.calls == 0
    assert schema_loader.calls == 0


def test_service_propagates_schema_loader_error() -> None:
    provider = FakeProvider()

    service = ChunkKnowledgeService(
        provider=provider,
        schema_loader=FakeSchemaLoader(
            error=FileNotFoundError(
                "schema ausente"
            )
        ),
    )

    with pytest.raises(
        FileNotFoundError,
        match="schema ausente",
    ):
        service.generate(
            prompt=build_prompt(),
            chunk=build_chunk(),
        )

    assert provider.calls == 0


def test_service_propagates_provider_error() -> None:
    service = ChunkKnowledgeService(
        provider=FakeProvider(
            error=RuntimeError(
                "provider failure"
            )
        ),
        schema_loader=FakeSchemaLoader(),
    )

    with pytest.raises(
        RuntimeError,
        match="provider failure",
    ):
        service.generate(
            prompt=build_prompt(),
            chunk=build_chunk(),
        )


def test_service_propagates_parser_error() -> None:
    parser = FakeParser(
        error=ValueError(
            "invalid structured response"
        )
    )

    service = ChunkKnowledgeService(
        provider=FakeProvider(),
        parser=parser,
        schema_loader=FakeSchemaLoader(),
    )

    with pytest.raises(
        ValueError,
        match="invalid structured response",
    ):
        service.generate(
            prompt=build_prompt(),
            chunk=build_chunk(),
        )

    assert parser.calls == 1


def test_service_does_not_mutate_prompt_or_chunk() -> None:
    prompt = build_prompt()
    chunk = build_chunk()

    original_prompt = (
        prompt.content,
        prompt.version,
    )
    original_chunk = chunk.as_dict()

    service = ChunkKnowledgeService(
        provider=FakeProvider(),
        schema_loader=FakeSchemaLoader(),
    )

    service.generate(
        prompt=prompt,
        chunk=chunk,
    )

    assert (
        prompt.content,
        prompt.version,
    ) == original_prompt

    assert chunk.as_dict() == original_chunk
