import json
from pathlib import Path

import pytest

from application.runtime_paths import RuntimePaths
from services.output_schema_loader import (
    OutputSchemaLoader,
)


def create_schema(
    tmp_path: Path,
    filename: str = "test_v1.json",
    content: str | None = None,
) -> Path:
    schema_file = (
        tmp_path / filename
    )

    schema_file.write_text(
        (
            content
            if content is not None
            else json.dumps(
                {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                        },
                    },
                    "required": [
                        "title",
                    ],
                }
            )
        ),
        encoding="utf-8",
    )

    return schema_file


def test_loader_loads_schema(
    tmp_path: Path,
) -> None:
    create_schema(
        tmp_path
    )

    loader = OutputSchemaLoader(
        schemas_directory=tmp_path
    )

    schema = loader.load(
        "test_v1"
    )

    assert schema["type"] == "object"

    assert (
        schema["required"]
        == [
            "title",
        ]
    )


def test_loader_uses_default_directory() -> None:
    loader = OutputSchemaLoader()

    assert (
        loader.schemas_directory
        == RuntimePaths.resolve().schemas_directory
    )


def test_loader_default_directory_is_independent_of_cwd(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.chdir(
        tmp_path
    )

    schema = OutputSchemaLoader().load(
        "summary_v1"
    )

    assert schema["type"] == "object"


def test_loader_loads_real_summary_schema() -> None:
    schema = OutputSchemaLoader().load(
        "summary_v1"
    )

    assert schema["type"] == "object"

    assert set(
        schema["required"]
    ) == {
        "title",
        "executive_summary",
        "key_points",
    }

    assert (
        schema["properties"][
            "key_points"
        ]["minItems"]
        == 3
    )

    assert (
        schema["properties"][
            "key_points"
        ]["maxItems"]
        == 5
    )


def test_loader_loads_real_meeting_report_schema() -> None:
    schema = OutputSchemaLoader().load(
        "meeting_report_v1"
    )

    assert schema["type"] == "object"

    expected_fields = {
        "title",
        "objective",
        "executive_summary",
        "key_points",
        "topics",
        "decisions",
        "action_items",
        "risks",
        "pending_items",
        "participants",
        "conclusions",
    }

    assert (
        set(
            schema["required"]
        )
        == expected_fields
    )

    assert (
        set(
            schema["properties"].keys()
        )
        == expected_fields
    )


def test_loader_rejects_invalid_json(
    tmp_path: Path,
) -> None:
    create_schema(
        tmp_path,
        content="{invalid-json}",
    )

    loader = OutputSchemaLoader(
        schemas_directory=tmp_path
    )

    with pytest.raises(
        ValueError,
        match="no contiene JSON válido",
    ):
        loader.load(
            "test_v1"
        )


def test_loader_rejects_non_object_schema(
    tmp_path: Path,
) -> None:
    create_schema(
        tmp_path,
        content="[]",
    )

    loader = OutputSchemaLoader(
        schemas_directory=tmp_path
    )

    with pytest.raises(
        ValueError,
        match="objeto JSON en la raíz",
    ):
        loader.load(
            "test_v1"
        )


def test_loader_reports_missing_schema(
    tmp_path: Path,
) -> None:
    loader = OutputSchemaLoader(
        schemas_directory=tmp_path
    )

    with pytest.raises(
        FileNotFoundError,
    ):
        loader.load(
            "missing_v1"
        )


def test_loader_rejects_non_string_contract() -> None:
    loader = OutputSchemaLoader()

    with pytest.raises(
        TypeError,
        match="contract debe ser una cadena",
    ):
        loader.load(
            123
        )


def test_loader_rejects_empty_contract() -> None:
    loader = OutputSchemaLoader()

    with pytest.raises(
        ValueError,
        match="contract no puede estar vacío",
    ):
        loader.load(
            "   "
        )


@pytest.mark.parametrize(
    "invalid_contract",
    [
        "../summary_v1",
        "schemas/summary_v1",
        "summary_v1.json",
        "summary v1",
    ],
)
def test_loader_rejects_invalid_contract_name(
    invalid_contract: str,
) -> None:
    loader = OutputSchemaLoader()

    with pytest.raises(
        ValueError,
        match="caracteres no permitidos",
    ):
        loader.load(
            invalid_contract
        )


def test_loader_rejects_invalid_directory_type() -> None:
    with pytest.raises(
        TypeError,
        match="schemas_directory debe ser",
    ):
        OutputSchemaLoader(
            schemas_directory="prompts/schemas"
        )
