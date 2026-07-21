from pathlib import Path

from services.setup.capabilities.capability_registry import CapabilityRegistry
from services.setup.capabilities.capability_result import CapabilityStatus
from services.setup.capabilities.capability_runner import CapabilityRunner
from services.setup.capabilities.workspace_capability import WorkspaceCapability


def test_workspace_capability_can_be_registered_and_executed(
    tmp_path: Path,
) -> None:
    output_directory = tmp_path / "output"

    registry = CapabilityRegistry()

    registry.register(
        WorkspaceCapability(
            output_directory
        )
    )

    assert len(registry) == 1

    capability = registry.get("workspace")

    assert capability is not None

    result = CapabilityRunner().run(capability)

    assert result.status == CapabilityStatus.AVAILABLE
    assert result.is_available is True