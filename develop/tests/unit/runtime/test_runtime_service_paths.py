from pathlib import Path
from types import SimpleNamespace

import pytest

from application.runtime_paths import RuntimePaths
from services.configuration_service import (
    ConfigurationService,
)
from services.logger_service import LoggerService


class FakeDeviceManager:

    def __init__(self) -> None:
        self.microphones = [
            SimpleNamespace(
                id=10
            )
        ]

        self.system_devices = [
            SimpleNamespace(
                id=20
            )
        ]

    def get_microphones(self):
        return list(
            self.microphones
        )

    def get_system_devices(self):
        return list(
            self.system_devices
        )


def build_runtime_paths(
    tmp_path: Path,
) -> RuntimePaths:
    return RuntimePaths.resolve(
        resource_root=tmp_path / "bundle",
        user_data_root=tmp_path / "data",
        meetings_root=tmp_path / "meetings",
        logs_root=tmp_path / "logs",
    )


def test_configuration_uses_runtime_meetings_directory(
    tmp_path: Path,
) -> None:
    runtime_paths = build_runtime_paths(
        tmp_path
    )

    configuration = ConfigurationService(
        runtime_paths=runtime_paths,
        device_manager=FakeDeviceManager(),
    )

    assert (
        configuration.output_directory
        == str(
            runtime_paths.meetings_root
        )
    )


def test_configuration_preserves_existing_defaults(
    tmp_path: Path,
) -> None:
    configuration = ConfigurationService(
        runtime_paths=build_runtime_paths(
            tmp_path
        ),
        device_manager=FakeDeviceManager(),
    )

    assert configuration.sample_rate == 44100
    assert configuration.channels == 1
    assert configuration.language == "es"
    assert configuration.whisper_model == "base"
    assert configuration.microphone == 10
    assert configuration.system_device == 20


def test_configuration_reset_preserves_runtime_paths(
    tmp_path: Path,
) -> None:
    runtime_paths = build_runtime_paths(
        tmp_path
    )

    configuration = ConfigurationService(
        runtime_paths=runtime_paths,
        device_manager=FakeDeviceManager(),
    )

    configuration.output_directory = "invalid"
    configuration.sample_rate = 123

    configuration.reset()

    assert (
        configuration.runtime_paths
        is runtime_paths
    )

    assert (
        configuration.output_directory
        == str(
            runtime_paths.meetings_root
        )
    )

    assert configuration.sample_rate == 44100


def test_configuration_rejects_invalid_runtime_paths() -> None:
    with pytest.raises(
        TypeError,
        match="runtime_paths",
    ):
        ConfigurationService(
            runtime_paths="invalid",
            device_manager=FakeDeviceManager(),
        )


def test_imported_meeting_composition_uses_runtime_meetings_directory(
) -> None:
    from application.dependency_container import (
        configuration,
        imported_meeting_service,
    )

    assert (
        imported_meeting_service.meetings_root
        == configuration.runtime_paths.meetings_root
    )

    assert (
        Path(
            configuration.output_directory
        )
        == configuration.runtime_paths.meetings_root
    )


def test_logger_uses_runtime_log_directory(
    tmp_path: Path,
) -> None:
    runtime_paths = build_runtime_paths(
        tmp_path
    )

    logger = LoggerService(
        runtime_paths=runtime_paths
    )

    assert (
        logger.log_directory
        == runtime_paths.logs_root
    )

    assert (
        logger.log_file
        == runtime_paths.logs_root
        / "meeting_assistant.log"
    )


def test_logger_creates_runtime_log_directory(
    tmp_path: Path,
) -> None:
    runtime_paths = build_runtime_paths(
        tmp_path
    )

    assert not (
        runtime_paths.logs_root.exists()
    )

    LoggerService(
        runtime_paths=runtime_paths
    )

    assert (
        runtime_paths.logs_root.is_dir()
    )


def test_logger_writes_to_runtime_log_file(
    tmp_path: Path,
) -> None:
    logger = LoggerService(
        runtime_paths=build_runtime_paths(
            tmp_path
        )
    )

    logger.info(
        "runtime-path-test"
    )

    for handler in logger.logger.handlers:
        handler.flush()

    content = logger.log_file.read_text(
        encoding="utf-8"
    )

    assert (
        "runtime-path-test"
        in content
    )


def test_logger_rejects_invalid_runtime_paths() -> None:
    with pytest.raises(
        TypeError,
        match="runtime_paths",
    ):
        LoggerService(
            runtime_paths="invalid"
        )
