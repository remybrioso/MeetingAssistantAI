from pathlib import Path
from types import SimpleNamespace

from application.runtime_paths import RuntimePaths
from services.setup.capabilities.capability_result import (
    CapabilityStatus,
)
from services.setup.capabilities.runtime_resources_capability import (
    RuntimeResourcesCapability,
)
from services.setup.capabilities.transcription_capability import (
    TranscriptionCapability,
)
from services.setup.default_capability_registry import (
    build_default_capability_registry,
)
from services.setup.task_result import TaskStatus
from services.setup.tasks.runtime_resources_task import (
    RuntimeResourcesTask,
)
from services.setup.tasks.transcription_model_task import (
    TranscriptionModelTask,
)
from services.setup.wizard.setup_wizard_policy import (
    SetupWizardPolicy,
)


REQUIRED_SCHEMA_CONTRACTS = (
    "chunk_classification_v2",
    "chunk_ignored_segment_audit_v1",
    "chunk_action_metadata_v1",
    "meeting_semantic_consolidation_v1",
    "meeting_report_narrative_v1",
)

PRODUCTIVE_PROMPTS = {
    "chunk_classification_v2": "{{SEGMENTS}}",
    "chunk_classification_repair_v1": "{{REPAIR_CONTEXT}}",
    "chunk_ignored_segment_audit_v1": "{{CANDIDATE_SEGMENTS}}",
    "chunk_action_metadata_v1": "{{ACTIONS}}",
    "meeting_semantic_consolidation_v1": "{{SOURCE_CATALOG}}",
    "meeting_report_narrative_v1": "{{CONSOLIDATED_ITEMS}}",
}


class FakeSchemaLoader:

    def __init__(
        self,
        failing_contract: str | None = None,
    ) -> None:
        self.failing_contract = failing_contract
        self.loaded_contracts = []

    def load(
        self,
        contract: str,
    ) -> dict:
        self.loaded_contracts.append(
            contract
        )

        if contract == self.failing_contract:
            raise FileNotFoundError(
                contract
            )

        return {
            "type": "object",
        }


class FakeAIProvider:
    pass


def build_runtime_paths(
    tmp_path: Path,
    *,
    missing_prompt: str | None = None,
    invalid_prompt: str | None = None,
) -> RuntimePaths:
    runtime_paths = RuntimePaths.resolve(
        resource_root=tmp_path / "bundle",
        user_data_root=tmp_path / "data",
        meetings_root=tmp_path / "meetings",
        logs_root=tmp_path / "logs",
    )

    runtime_paths.prompts_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    for contract, placeholder in (
        PRODUCTIVE_PROMPTS.items()
    ):
        if contract == missing_prompt:
            continue

        content = placeholder

        if contract == invalid_prompt:
            content = "missing placeholder"

        (
            runtime_paths.prompts_directory
            / f"{contract}.md"
        ).write_text(
            content,
            encoding="utf-8",
        )

    return runtime_paths


def test_runtime_resources_task_checks_productive_schemas_and_prompts(
    tmp_path: Path,
) -> None:
    loader = FakeSchemaLoader()
    runtime_paths = build_runtime_paths(
        tmp_path
    )

    result = RuntimeResourcesTask(
        runtime_paths=runtime_paths,
        schema_loader=loader,
    ).run()

    assert result.status == TaskStatus.SUCCESS

    assert tuple(
        loader.loaded_contracts
    ) == REQUIRED_SCHEMA_CONTRACTS

    assert (
        result.details[
            "validated_prompt_contracts"
        ]
        == list(PRODUCTIVE_PROMPTS)
    )

    assert result.details["validated_schema_contracts"] == list(
        REQUIRED_SCHEMA_CONTRACTS
    )
    assert result.details["required_schema_count"] == 5
    assert result.details["required_prompt_count"] == 6


def test_runtime_resources_exclude_retired_classification_contract() -> None:
    assert (
        "chunk_classification_v1"
        not in RuntimeResourcesTask.REQUIRED_SCHEMA_CONTRACTS
    )
    assert "chunk_classification_v1" not in {
        contract
        for contract, _ in RuntimeResourcesTask.REQUIRED_PROMPT_CONTRACTS
    }


def test_runtime_resources_do_not_require_a_dedicated_repair_schema() -> None:
    assert (
        "chunk_classification_repair_v1"
        not in RuntimeResourcesTask.REQUIRED_SCHEMA_CONTRACTS
    )


def test_runtime_resources_task_fails_when_schema_is_missing(
    tmp_path: Path,
) -> None:
    result = RuntimeResourcesTask(
        runtime_paths=build_runtime_paths(
            tmp_path
        ),
        schema_loader=FakeSchemaLoader(
            failing_contract=(
                "meeting_report_narrative_v1"
            )
        ),
    ).run()

    assert result.status == TaskStatus.FAILED
    assert (
        "meeting_report_narrative_v1"
        in result.error
    )


def test_runtime_resources_task_fails_when_prompt_is_missing(
    tmp_path: Path,
) -> None:
    result = RuntimeResourcesTask(
        runtime_paths=build_runtime_paths(
            tmp_path,
            missing_prompt=(
                "chunk_classification_v2"
            ),
        ),
        schema_loader=FakeSchemaLoader(),
    ).run()

    assert result.status == TaskStatus.FAILED
    assert (
        "chunk_classification_v2.md"
        in result.error
    )


def test_runtime_resources_task_fails_when_prompt_contract_is_invalid(
    tmp_path: Path,
) -> None:
    result = RuntimeResourcesTask(
        runtime_paths=build_runtime_paths(
            tmp_path,
            invalid_prompt=(
                "meeting_report_narrative_v1"
            ),
        ),
        schema_loader=FakeSchemaLoader(),
    ).run()

    assert result.status == TaskStatus.FAILED
    assert (
        "{{CONSOLIDATED_ITEMS}}"
        in result.error
    )


def test_runtime_resources_capability_is_available_when_task_passes(
    tmp_path: Path,
) -> None:
    capability = RuntimeResourcesCapability(
        runtime_paths=build_runtime_paths(
            tmp_path
        ),
        schema_loader=FakeSchemaLoader(),
    )

    task_result = (
        capability.get_tasks()[0].run()
    )
    result = capability.evaluate(
        [task_result]
    )

    assert (
        result.status
        == CapabilityStatus.AVAILABLE
    )
    assert result.repairable is False


def test_runtime_resources_capability_requests_install_repair_on_failure(
    tmp_path: Path,
) -> None:
    capability = RuntimeResourcesCapability(
        runtime_paths=build_runtime_paths(
            tmp_path,
            missing_prompt=(
                "chunk_action_metadata_v1"
            ),
        ),
        schema_loader=FakeSchemaLoader(),
    )

    task_result = (
        capability.get_tasks()[0].run()
    )
    result = capability.evaluate(
        [task_result]
    )

    assert (
        result.status
        == CapabilityStatus.UNAVAILABLE
    )
    assert (
        result.repair_action
        == "REPAIR_APPLICATION_INSTALLATION"
    )


def test_transcription_model_task_checks_cache_without_network() -> None:
    calls = []

    def resolver(
        model_name,
        *,
        local_files_only,
    ):
        calls.append(
            (
                model_name,
                local_files_only,
            )
        )
        return (
            "C:/cache/faster-whisper-base"
        )

    result = TranscriptionModelTask(
        model_name="base",
        model_resolver=resolver,
    ).run()

    assert result.status == TaskStatus.SUCCESS
    assert calls == [
        (
            "base",
            True,
        )
    ]
    assert (
        result.details[
            "local_files_only"
        ]
        is True
    )


def test_transcription_model_task_reports_missing_local_model() -> None:
    def resolver(
        model_name,
        *,
        local_files_only,
    ):
        raise FileNotFoundError(
            model_name
        )

    result = TranscriptionModelTask(
        model_name="base",
        model_resolver=resolver,
    ).run()

    assert result.status == TaskStatus.FAILED
    assert result.details["model"] == "base"
    assert (
        result.details[
            "local_files_only"
        ]
        is True
    )


def test_transcription_capability_is_available_when_model_exists() -> None:
    capability = TranscriptionCapability(
        model_name="base",
        model_resolver=(
            lambda model, local_files_only:
            "C:/cache/model"
        ),
    )

    result = capability.evaluate(
        [
            capability
            .get_tasks()[0]
            .run()
        ]
    )

    assert (
        result.status
        == CapabilityStatus.AVAILABLE
    )
    assert result.repairable is False


def test_transcription_capability_requests_model_download_when_missing() -> None:
    def resolver(
        model,
        local_files_only,
    ):
        raise RuntimeError(
            "model not cached"
        )

    capability = TranscriptionCapability(
        model_name="base",
        model_resolver=resolver,
    )

    result = capability.evaluate(
        [
            capability
            .get_tasks()[0]
            .run()
        ]
    )

    assert (
        result.status
        == CapabilityStatus.UNAVAILABLE
    )
    assert (
        result.repair_action
        == "DOWNLOAD_TRANSCRIPTION_MODEL"
    )


def test_default_registry_contains_all_runtime_capabilities(
    tmp_path: Path,
) -> None:
    runtime_paths = build_runtime_paths(
        tmp_path
    )

    configuration = SimpleNamespace(
        runtime_paths=runtime_paths,
        output_directory=str(
            runtime_paths.meetings_root
        ),
        whisper_model="base",
    )

    registry = build_default_capability_registry(
        configuration=configuration,
        ai_provider=FakeAIProvider(),
        transcription_model_resolver=(
            lambda model, local_files_only:
            "C:/cache/model"
        ),
    )

    assert {
        capability.capability_id
        for capability in registry.get_all()
    } == {
        "runtime-resources",
        "workspace",
        "transcription",
        "artificial-intelligence",
        "audio",
    }


def test_setup_policy_requires_all_runtime_capabilities() -> None:
    assert (
        SetupWizardPolicy()
        .required_capability_ids
        == {
            "runtime-resources",
            "workspace",
            "transcription",
            "artificial-intelligence",
            "audio",
        }
    )
