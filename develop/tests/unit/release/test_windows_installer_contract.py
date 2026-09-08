from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
INSTALLER_SCRIPT = PROJECT_ROOT / "packaging" / "MeetingAssistantAI.iss"
BUILD_SCRIPT = PROJECT_ROOT / "scripts" / "build_windows_installer.ps1"


def installer_contract() -> str:
    return INSTALLER_SCRIPT.read_text(encoding="utf-8")


def build_contract() -> str:
    return BUILD_SCRIPT.read_text(encoding="utf-8")


def test_installer_contract_files_exist() -> None:
    assert INSTALLER_SCRIPT.is_file()
    assert BUILD_SCRIPT.is_file()


def test_installer_requires_injected_release_version() -> None:
    script = installer_contract()
    assert "#ifndef AppVersion" in script
    assert "#error AppVersion must be provided" in script
    assert "AppVersion={#AppVersion}" in script
    assert "OutputBaseFilename=MeetingAssistantAI-Setup-{#AppVersion}" in script


def test_installer_is_per_user_without_elevation() -> None:
    script = installer_contract()
    assert "PrivilegesRequired=lowest" in script
    assert "DefaultDirName={localappdata}\\Programs\\Meeting Assistant AI" in script


def test_installer_targets_x64_compatible_windows() -> None:
    assert "ArchitecturesAllowed=x64compatible" in installer_contract()


def test_installer_packages_complete_onedir_bundle() -> None:
    script = installer_contract()
    assert 'Source: "..\\dist\\MeetingAssistantAI\\*"' in script
    assert 'DestDir: "{app}"' in script
    assert "recursesubdirs" in script
    assert "createallsubdirs" in script


def test_installer_declares_obsolete_prompt_cleanup_before_files() -> None:
    script = installer_contract()
    assert "[InstallDelete]" in script
    assert script.index("[InstallDelete]") < script.index("[Files]")


def test_installer_deletes_only_the_retired_prompt_on_upgrade() -> None:
    delete_entries = []
    section = ""
    for line in installer_contract().splitlines():
        line = line.strip()
        if line.startswith("[") and line.endswith("]"):
            section = line.casefold()
        elif section == "[installdelete]" and line and not line.startswith(";"):
            delete_entries.append(line)

    # An exact allowlist rejects directory deletion, wildcards and extra paths.
    assert delete_entries == [
        'Type: files; Name: "{app}\\_internal\\prompts\\chunk_classification_v1.md"'
    ]


def test_installer_creates_start_menu_shortcut() -> None:
    script = installer_contract()
    assert 'Name: "{group}\\Meeting Assistant AI"' in script
    assert 'Filename: "{app}\\{#AppExeName}"' in script


def test_installer_offers_optional_desktop_shortcut() -> None:
    script = installer_contract()
    assert 'Name: "desktopicon"' in script
    assert "Flags: unchecked" in script
    assert 'Name: "{userdesktop}\\Meeting Assistant AI"' in script
    assert "Tasks: desktopicon" in script


def test_installer_registers_uninstall_support() -> None:
    script = installer_contract()
    assert "Uninstallable=yes" in script
    assert "CreateUninstallRegKey=yes" in script
    assert "UninstallDisplayIcon={app}\\{#AppExeName}" in script


def test_installer_offers_post_install_launch() -> None:
    script = installer_contract()
    assert "[Run]" in script
    assert "postinstall" in script
    assert "skipifsilent" in script


def test_installer_uses_compressed_solid_output() -> None:
    script = installer_contract()
    assert "Compression=lzma2" in script
    assert "SolidCompression=yes" in script
    assert "OutputDir=..\\dist\\installer" in script


def test_build_script_reads_and_validates_version_file() -> None:
    script = build_contract()
    assert 'Join-Path $ProjectRoot "VERSION"' in script
    assert "Get-Content" in script
    assert "^v\\d+\\.\\d+\\.\\d+" in script


def test_build_script_resolves_inno_setup_compiler() -> None:
    script = build_contract()
    assert 'Get-Command "ISCC.exe"' in script
    assert "Inno Setup 6\\ISCC.exe" in script
    assert "Resolve-InnoSetupCompiler" in script


def test_build_script_builds_executable_by_default() -> None:
    script = build_contract()
    assert "[switch]$SkipExecutableBuild" in script
    assert "if (-not $SkipExecutableBuild)" in script
    assert "scripts\\build_windows_executable.ps1" in script


def test_build_script_validates_frozen_bundle() -> None:
    script = build_contract()
    assert "dist\\MeetingAssistantAI" in script
    assert "MeetingAssistantAI.exe" in script
    assert "Executable bundle is incomplete" in script


def test_build_script_injects_version_into_iscc() -> None:
    script = build_contract()
    assert '"-dAppVersion=$Version"' in script
    assert "--define=AppVersion" not in script
    assert "& $InnoSetupCompiler" in script


def test_build_script_validates_expected_installer() -> None:
    script = build_contract()
    assert '"MeetingAssistantAI-Setup-$Version.exe"' in script
    assert "Installer build completed successfully." in script
