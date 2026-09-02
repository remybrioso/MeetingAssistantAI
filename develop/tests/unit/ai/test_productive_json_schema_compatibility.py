import pytest

from services.json_schema_loader import (
    JsonSchemaLoader,
)


PRODUCTIVE_CONTRACTS = (
    "chunk_classification_v1",
    "chunk_action_metadata_v1",
    "meeting_semantic_consolidation_v1",
    "meeting_report_narrative_v1",
)

MAX_SAFE_BOUNDED_STRING_LENGTH = 1500
MAX_SAFE_BOUNDED_ARRAY_ITEMS = 100


def _walk_schema(
    value,
    path: str = "$",
):
    if isinstance(
        value,
        dict,
    ):
        yield (
            path,
            value,
        )

        for key, child in value.items():
            child_path = (
                f"{path}.{key}"
            )

            yield from _walk_schema(
                child,
                child_path,
            )

    elif isinstance(
        value,
        list,
    ):
        for index, child in enumerate(
            value
        ):
            child_path = (
                f"{path}[{index}]"
            )

            yield from _walk_schema(
                child,
                child_path,
            )


@pytest.mark.parametrize(
    "contract",
    PRODUCTIVE_CONTRACTS,
)
def test_productive_schema_bounded_repetitions_follow_ollama_policy(
    contract: str,
) -> None:
    schema = JsonSchemaLoader().load(
        contract
    )

    violations: list[str] = []

    policies = {
        "maxLength": (
            MAX_SAFE_BOUNDED_STRING_LENGTH
        ),
        "maxItems": (
            MAX_SAFE_BOUNDED_ARRAY_ITEMS
        ),
    }

    for path, node in _walk_schema(
        schema
    ):
        for (
            keyword,
            maximum,
        ) in policies.items():
            if keyword not in node:
                continue

            value = node[
                keyword
            ]

            if (
                not isinstance(
                    value,
                    int,
                )
                or isinstance(
                    value,
                    bool,
                )
                or value < 0
            ):
                violations.append(
                    f"{path}.{keyword} "
                    "debe ser un entero "
                    "no negativo."
                )
                continue

            if value > maximum:
                violations.append(
                    f"{path}.{keyword}={value} "
                    f"supera el máximo "
                    f"productivo {maximum}."
                )

    assert not violations, (
        f"El contrato {contract} contiene "
        "repeticiones acotadas incompatibles "
        "con la política de salida estructurada "
        "de Ollama:\n"
        + "\n".join(
            violations
        )
    )


def test_global_contract_capacities_are_aligned() -> None:
    loader = JsonSchemaLoader()

    semantic_schema = loader.load(
        "meeting_semantic_consolidation_v1"
    )

    narrative_schema = loader.load(
        "meeting_report_narrative_v1"
    )

    semantic_items = (
        semantic_schema[
            "properties"
        ][
            "items"
        ]
    )

    assert (
        semantic_items[
            "minItems"
        ]
        == 1
    )

    assert (
        semantic_items[
            "maxItems"
        ]
        == 100
    )

    semantic_item = (
        semantic_items[
            "items"
        ]
    )

    assert (
        semantic_item[
            "properties"
        ][
            "description"
        ][
            "maxLength"
        ]
        == 1000
    )

    assert (
        semantic_item[
            "properties"
        ][
            "source_refs"
        ][
            "maxItems"
        ]
        == 100
    )

    properties = (
        narrative_schema[
            "properties"
        ]
    )

    objective_object = next(
        variant
        for variant
        in properties[
            "objective"
        ][
            "anyOf"
        ]
        if (
            isinstance(
                variant,
                dict,
            )
            and variant.get(
                "type"
            )
            == "object"
        )
    )

    source_id_arrays = [
        properties[
            "title"
        ][
            "properties"
        ][
            "source_item_ids"
        ],
        objective_object[
            "properties"
        ][
            "source_item_ids"
        ],
        properties[
            "executive_summary"
        ][
            "properties"
        ][
            "source_item_ids"
        ],
        properties[
            "key_points"
        ][
            "items"
        ][
            "properties"
        ][
            "source_item_ids"
        ],
    ]

    assert all(
        item[
            "maxItems"
        ]
        == semantic_items[
            "maxItems"
        ]
        for item
        in source_id_arrays
    )

    assert (
        properties[
            "executive_summary"
        ][
            "properties"
        ][
            "text"
        ][
            "maxLength"
        ]
        == 1500
    )
