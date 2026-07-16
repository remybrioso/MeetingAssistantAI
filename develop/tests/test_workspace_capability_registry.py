from pathlib import Path
from tempfile import TemporaryDirectory

from services.setup.capabilities.capability_registry import (
    CapabilityRegistry,
)
from services.setup.capabilities.capability_result import (
    CapabilityStatus,
)
from services.setup.capabilities.capability_runner import (
    CapabilityRunner,
)
from services.setup.capabilities.workspace_capability import (
    WorkspaceCapability,
)


with TemporaryDirectory() as temp_directory:

    output_directory = (
        Path(temp_directory)
        / "output"
    )

    registry = CapabilityRegistry()

    registry.register(
        WorkspaceCapability(
            output_directory
        )
    )

    assert len(registry) == 1

    workspace_capability = registry.get(
        "workspace"
    )

    assert workspace_capability is not None

    result = CapabilityRunner().run(
        workspace_capability
    )

    assert (
        result.status
        == CapabilityStatus.AVAILABLE
    )

    print(
        "WorkspaceCapability registrada "
        "y ejecutada correctamente."
    )