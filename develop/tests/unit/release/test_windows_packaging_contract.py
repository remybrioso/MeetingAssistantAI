from pathlib import Path


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[3]
)

SPEC_FILE = (
    PROJECT_ROOT
    / "packaging"
    / "MeetingAssistantAI.spec"
)

BUILD_SCRIPT = (
    PROJECT_ROOT
    / "scripts"
    / "build_windows_executable.ps1"
)

BUILD_REQUIREMENTS = (
    PROJECT_ROOT
    / "requirements-build.txt"
)

PRODUCTIVE_PROMPTS = (
    "chunk_classification_v1",
    "chunk_action_metadata_v1",
    "meeting_semantic_consolidation_v1",
    "meeting_report_narrative_v1",
)


def test_packaging_contract_files_exist() -> None:
    assert SPEC_FILE.is_file()
    assert BUILD_SCRIPT.is_file()
    assert BUILD_REQUIREMENTS.is_file()


def test_build_tool_version_is_pinned() -> None:
    assert (
        BUILD_REQUIREMENTS
        .read_text(
            encoding="utf-8"
        )
        .splitlines()
        == [
            "pyinstaller==6.22.2"
        ]
    )


def test_spec_uses_application_entrypoint() -> None:
    spec = SPEC_FILE.read_text(
        encoding="utf-8"
    )

    assert '"app.py"' in spec
    assert 'name="MeetingAssistantAI"' in spec


def test_spec_bundles_productive_schema_resources() -> None:
    spec = SPEC_FILE.read_text(
        encoding="utf-8"
    )

    assert '"prompts/schemas"' in spec


def test_spec_bundles_productive_prompt_templates() -> None:
    spec = SPEC_FILE.read_text(
        encoding="utf-8"
    )

    for contract in PRODUCTIVE_PROMPTS:
        assert (
            f'"{contract}"'
            in spec
        )

    assert (
        'f"{prompt_contract}.md"'
        in spec
    )


def test_spec_collects_customtkinter_data() -> None:
    spec = SPEC_FILE.read_text(
        encoding="utf-8"
    )

    assert (
        'collect_data_files(\n'
        '    "customtkinter"\n'
        ')'
        in spec
    )


def test_spec_collects_native_runtime_packages() -> None:
    spec = SPEC_FILE.read_text(
        encoding="utf-8"
    )

    for package_name in (
        "faster_whisper",
        "ctranslate2",
        "sounddevice",
        "soundfile",
        "soundcard",
    ):
        assert (
            f'"{package_name}"'
            in spec
        )


def test_spec_defines_onedir_bundle() -> None:
    spec = SPEC_FILE.read_text(
        encoding="utf-8"
    )

    assert "COLLECT(" in spec
    assert (
        "exclude_binaries=True"
        in spec
    )


def test_production_bundle_uses_gui_subsystem() -> None:
    spec = SPEC_FILE.read_text(
        encoding="utf-8"
    )

    assert "console=False" in spec
    assert "console=True" not in spec


def test_build_script_uses_virtual_environment() -> None:
    assert (
        ".venv\\Scripts\\python.exe"
        in BUILD_SCRIPT.read_text(
            encoding="utf-8"
        )
    )


def test_build_script_uses_pinned_build_requirements() -> None:
    script = BUILD_SCRIPT.read_text(
        encoding="utf-8"
    )

    assert "requirements-build.txt" in script
    assert "-r $BuildRequirements" in script


def test_build_script_uses_committed_spec_file() -> None:
    script = BUILD_SCRIPT.read_text(
        encoding="utf-8"
    )

    assert (
        "packaging\\MeetingAssistantAI.spec"
        in script
    )
    assert "-m PyInstaller" in script


def test_build_script_validates_expected_executable() -> None:
    assert (
        "dist\\MeetingAssistantAI"
        "\\MeetingAssistantAI.exe"
        in BUILD_SCRIPT.read_text(
            encoding="utf-8"
        )
    )
