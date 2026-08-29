from pathlib import Path

import pytest

from application.runtime_paths import (
    RuntimePaths,
)


def test_resolve_does_not_depend_on_current_working_directory(
    tmp_path: Path,
    monkeypatch,
) -> None:
    original = RuntimePaths.resolve()

    other_directory = (
        tmp_path
        / "unrelated-working-directory"
    )

    other_directory.mkdir(
        parents=True,
    )

    monkeypatch.chdir(
        other_directory
    )

    resolved = RuntimePaths.resolve()

    assert (
        resolved.resource_root
        == original.resource_root
    )


def test_default_resource_root_points_to_project_root() -> None:
    resolved = RuntimePaths.resolve()

    expected = (
        Path(__file__)
        .resolve()
        .parents[3]
    )

    assert (
        resolved.resource_root
        == expected
    )


def test_schema_directory_is_relative_to_resource_root(
    tmp_path: Path,
) -> None:
    resource_root = (
        tmp_path
        / "bundle"
    )

    resolved = RuntimePaths.resolve(
        resource_root=resource_root,
        user_data_root=tmp_path / "data",
        meetings_root=tmp_path / "meetings",
        logs_root=tmp_path / "logs",
    )

    assert (
        resolved.schemas_directory
        == resource_root.resolve()
        / "prompts"
        / "schemas"
    )


def test_resolve_accepts_explicit_user_path_overrides(
    tmp_path: Path,
) -> None:
    resolved = RuntimePaths.resolve(
        resource_root=tmp_path / "bundle",
        user_data_root=tmp_path / "data",
        meetings_root=tmp_path / "meetings",
        logs_root=tmp_path / "logs",
    )

    assert (
        resolved.user_data_root
        == (tmp_path / "data").resolve()
    )

    assert (
        resolved.meetings_root
        == (tmp_path / "meetings").resolve()
    )

    assert (
        resolved.logs_root
        == (tmp_path / "logs").resolve()
    )


def test_models_directory_belongs_to_private_user_data(
    tmp_path: Path,
) -> None:
    resolved = RuntimePaths.resolve(
        resource_root=tmp_path / "bundle",
        user_data_root=tmp_path / "data",
        meetings_root=tmp_path / "meetings",
        logs_root=tmp_path / "logs",
    )

    assert (
        resolved.models_directory
        == (tmp_path / "data").resolve()
        / "models"
    )


def test_ensure_user_directories_creates_writable_locations(
    tmp_path: Path,
) -> None:
    resolved = RuntimePaths.resolve(
        resource_root=tmp_path / "bundle",
        user_data_root=tmp_path / "data",
        meetings_root=tmp_path / "meetings",
        logs_root=tmp_path / "logs",
    )

    resolved.ensure_user_directories()

    assert (
        resolved.user_data_root.is_dir()
    )

    assert (
        resolved.meetings_root.is_dir()
    )

    assert (
        resolved.logs_root.is_dir()
    )

    assert (
        resolved.models_directory.is_dir()
    )


def test_ensure_user_directories_does_not_create_resource_root(
    tmp_path: Path,
) -> None:
    resource_root = (
        tmp_path
        / "missing-bundle"
    )

    resolved = RuntimePaths.resolve(
        resource_root=resource_root,
        user_data_root=tmp_path / "data",
        meetings_root=tmp_path / "meetings",
        logs_root=tmp_path / "logs",
    )

    resolved.ensure_user_directories()

    assert not (
        resource_root.exists()
    )


@pytest.mark.parametrize(
    "parameter_name",
    (
        "resource_root",
        "user_data_root",
        "meetings_root",
        "logs_root",
    ),
)
def test_resolve_rejects_non_path_overrides(
    parameter_name: str,
) -> None:
    kwargs = {
        "resource_root": Path("resources"),
        "user_data_root": Path("data"),
        "meetings_root": Path("meetings"),
        "logs_root": Path("logs"),
    }

    kwargs[parameter_name] = "invalid"

    with pytest.raises(
        TypeError,
        match=parameter_name,
    ):
        RuntimePaths.resolve(
            **kwargs
        )


def test_frozen_flag_is_boolean() -> None:
    resolved = RuntimePaths.resolve()

    assert isinstance(
        resolved.frozen,
        bool,
    )
