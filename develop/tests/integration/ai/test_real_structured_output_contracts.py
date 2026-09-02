import json
import os
from json import JSONDecodeError

import pytest

from providers.ollama_provider import (
    OllamaProvider,
)
from services.json_schema_loader import (
    JsonSchemaLoader,
)


RUN_ENVIRONMENT_VARIABLE = (
    "MAI_RUN_REAL_OLLAMA_SCHEMA_TESTS"
)

CONTRACT_PROMPTS = (
    (
        "chunk_classification_v1",
        (
            "Devuelve únicamente este JSON: "
            '{"items":[]}'
        ),
    ),
    (
        "chunk_action_metadata_v1",
        (
            "Devuelve únicamente este JSON: "
            '{"actions":[]}'
        ),
    ),
    (
        "meeting_semantic_consolidation_v1",
        (
            "Devuelve únicamente JSON compatible "
            "con el schema. Usa un solo item topic "
            'con description "Validación técnica MAI" '
            "y source_refs con chunk_index 0 "
            "e item_index 0."
        ),
    ),
    (
        "meeting_report_narrative_v1",
        (
            "Devuelve únicamente JSON compatible "
            "con el schema. Usa item_id 0 como "
            "fuente. El título debe ser "
            '"Validación técnica MAI". '
            "objective debe ser null. "
            "El executive_summary debe contener "
            "al menos 30 caracteres y describir "
            "una validación técnica del contrato. "
            "Incluye un único key_point respaldado "
            "por item_id 0."
        ),
    ),
)


@pytest.mark.integration
def test_real_ollama_accepts_all_productive_structured_output_contracts() -> None:
    if (
        os.environ.get(
            RUN_ENVIRONMENT_VARIABLE
        )
        != "1"
    ):
        pytest.skip(
            "Prueba real de schemas de Ollama "
            f"deshabilitada. Define "
            f"{RUN_ENVIRONMENT_VARIABLE}=1 "
            "para ejecutarla."
        )

    provider = OllamaProvider()

    health = provider.health()

    if (
        not health.connected
        or not health.model_found
    ):
        pytest.skip(
            "Ollama o el modelo configurado "
            "no están disponibles."
        )

    loader = JsonSchemaLoader()

    failures: list[str] = []

    for (
        contract,
        prompt,
    ) in CONTRACT_PROMPTS:
        schema = loader.load(
            contract
        )

        try:
            response = provider.generate(
                prompt,
                schema,
            )
        except Exception as ex:
            failures.append(
                f"{contract}: {ex}"
            )
            continue

        try:
            payload = json.loads(
                response
            )
        except JSONDecodeError as ex:
            failures.append(
                f"{contract}: respuesta "
                f"no contiene JSON válido: {ex}"
            )
            continue

        if not isinstance(
            payload,
            dict,
        ):
            failures.append(
                f"{contract}: la raíz "
                "de la respuesta no es un objeto."
            )

    assert not failures, (
        "Ollama rechazó o incumplió uno o más "
        "contratos productivos:\n"
        + "\n".join(
            failures
        )
    )
