import json
from pathlib import Path

import pytest

from services.json_schema_loader import (
    JsonSchemaLoader,
)


def test_loader_reads_real_chunk_contract() -> None:
    loader = JsonSchemaLoader()

    schema = loader.load(
        "chunk_knowledge_v1"
    )

    assert schema["type"] == "object"

    assert set(schema["required"]) == {
        "key_points",
        "topics",
        "decisions",
        "action_items",
        "risks",
        "pending_items",
        "participants",
        "conclusions",
    }


def test_loader_uses_injected_directory(
    tmp_path: Path,
) -> None:
    expected_schema = {
        "type": "object",
        "properties": {},
    }

    (
        tmp_path / "custom_v1.json"
    ).write_text(
        json.dumps(expected_schema),
        encoding="utf-8",
    )

    loader = JsonSchemaLoader(
        schemas_directory=tmp_path
    )

    assert loader.load(
        "custom_v1"
    ) == expected_schema


def test_loader_rejects_invalid_contract_name() -> None:
    loader = JsonSchemaLoader()

    with pytest.raises(
        ValueError,
        match="caracteres no permitidos",
    ):
        loader.load(
            "../schema"
        )


def test_loader_propagates_missing_schema() -> None:
    loader = JsonSchemaLoader()

    with pytest.raises(
        FileNotFoundError,
    ):
        loader.load(
            "contract_that_does_not_exist"
        )


def test_loader_rejects_invalid_json(
    tmp_path: Path,
) -> None:
    (
        tmp_path / "invalid_v1.json"
    ).write_text(
        "{invalid",
        encoding="utf-8",
    )

    loader = JsonSchemaLoader(
        schemas_directory=tmp_path
    )

    with pytest.raises(
        ValueError,
        match="no contiene JSON válido",
    ):
        loader.load(
            "invalid_v1"
        )


def test_loader_rejects_non_object_root(
    tmp_path: Path,
) -> None:
    (
        tmp_path / "array_v1.json"
    ).write_text(
        "[]",
        encoding="utf-8",
    )

    loader = JsonSchemaLoader(
        schemas_directory=tmp_path
    )

    with pytest.raises(
        TypeError,
        match="objeto JSON en la raíz",
    ):
        loader.load(
            "array_v1"
        )


def test_loader_rejects_empty_object(
    tmp_path: Path,
) -> None:
    (
        tmp_path / "empty_v1.json"
    ).write_text(
        "{}",
        encoding="utf-8",
    )

    loader = JsonSchemaLoader(
        schemas_directory=tmp_path
    )

    with pytest.raises(
        ValueError,
        match="está vacío",
    ):
        loader.load(
            "empty_v1"
        )
