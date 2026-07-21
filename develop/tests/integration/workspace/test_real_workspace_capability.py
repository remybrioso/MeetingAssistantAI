import pytest

from services.configuration_service import ConfigurationService
from services.setup.capabilities.capability_result import CapabilityStatus
from services.setup.capabilities.capability_runner import CapabilityRunner
from services.setup.capabilities.workspace_capability import WorkspaceCapability


@pytest.mark.integration
def test_real_workspace_capability_is_available() -> None:
    configuration = ConfigurationService()

    result = CapabilityRunner().run(
        WorkspaceCapability(
            configuration.output_directory
        )
    )

    if result.status == CapabilityStatus.UNAVAILABLE:
        pytest.skip(
            "El directorio real de salida no está disponible."
        )

    assert result.status == CapabilityStatus.AVAILABLE
    assert result.is_available is True