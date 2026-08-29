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


class FakeSchemaLoader:

    def __init__(
        self,
        failing_contract: str | None = None,
    ) -> None:
        self.failing_contract = (
            failing_contract
        )
        self.loaded_contracts = []

    def load(
        self,
        contract: str,
    ) -> dict:
        self.loaded_contracts.append(
            contract
        )

        if (
            contract
            == self.failing_contract
        ):
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
) -> RuntimePaths:
    return RuntimePaths.resolve(
        resource_root=tmp_path / "bundle",
        user_data_root=tmp_path / "data",
        meetings_root=tmp_path / "meetings",
        logs_root=tmp_path / "logs",
    )


def test_runtime_resources_task_checks_only_productive_contracts(
    tmp_path: Path,
) -> None:
    loader = FakeSchemaLoader()

    task = RuntimeResourcesTask(
        runtime_paths=build_runtime_paths(
            tmp_path
        ),
        schema_loader=loader,
    )

    result = task.run()

    assert (
        result.status
        == TaskStatus.SUCCESS
    )

    assert tuple(
        loader.loaded_contracts
    ) == (
        "chunk_classification_v1",
        "chunk_action_metadata_v1",
        "meeting_semantic_consolidation_v1",
        "meeting_report_narrative_v1",
    )


def test_runtime_resources_task_fails_when_contract_is_missing(
    tmp_path: Path,
) -> None:
    task = RuntimeResourcesTask(
        runtime_paths=build_runtime_paths(
            tmp_path
        ),
        schema_loader=FakeSchemaLoader(
            failing_contract=(
                "meeting_report_narrative_v1"
            )
        ),
    )

    result = task.run()

    assert (
        result.status
        == TaskStatus.FAILED
    )

    assert (
        "meeting_report_narrative_v1"
        in result.error
    )


def test_runtime_resources_capability_is_available_when_task_passes(
    tmp_path: Path,
) -> None:
    capability = (
        RuntimeResourcesCapability(
            runtime_paths=build_runtime_paths(
                tmp_path
            ),
            schema_loader=FakeSchemaLoader(),
        )
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
    capability = (
        RuntimeResourcesCapability(
            runtime_paths=build_runtime_paths(
                tmp_path
            ),
            schema_loader=FakeSchemaLoader(
                failing_contract=(
                    "chunk_classification_v1"
                )
            ),
        )
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

    task = TranscriptionModelTask(
        model_name="base",
        model_resolver=resolver,
    )

    result = task.run()

    assert (
        result.status
        == TaskStatus.SUCCESS
    )

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

    task = TranscriptionModelTask(
        model_name="base",
        model_resolver=resolver,
    )

    result = task.run()

    assert (
        result.status
        == TaskStatus.FAILED
    )

    assert (
        result.details["model"]
        == "base"
    )

    assert (
        result.details[
            "local_files_only"
        ]
        is True
    )


def test_transcription_capability_is_available_when_model_exists() -> None:
    capability = TranscriptionCapability(
        model_name="base",
        model_resolver=lambda model, local_files_only: (
            "C:/cache/model"
        ),
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
        == "DOWNLOAD_TRANSCRIPTION_MODEL"
    )


def test_default_registry_contains_runtime_and_transcription_capabilities(
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

    registry = (
        build_default_capability_registry(
            configuration=configuration,
            ai_provider=FakeAIProvider(),
            transcription_model_resolver=(
                lambda model, local_files_only: (
                    "C:/cache/model"
                )
            ),
        )
    )

    capability_ids = {
        capability.capability_id
        for capability in (
            registry.get_all()
        )
    }

    assert capability_ids == {
        "runtime-resources",
        "workspace",
        "transcription",
        "artificial-intelligence",
        "audio",
    }


def test_setup_policy_requires_all_runtime_capabilities() -> None:
    policy = SetupWizardPolicy()

    assert (
        policy.required_capability_ids
        == {
            "runtime-resources",
            "workspace",
            "transcription",
            "artificial-intelligence",
            "audio",
        }
    )
