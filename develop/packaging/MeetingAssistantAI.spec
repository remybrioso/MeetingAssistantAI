# -*- mode: python ; coding: utf-8 -*-

"""
PyInstaller packaging contract for Meeting Assistant AI.

This is intentionally an onedir diagnostic build contract.
TASK-061 will execute and validate the generated bundle before
the final GUI/no-console release configuration is frozen.
"""

from pathlib import Path

from PyInstaller.utils.hooks import (
    collect_all,
    collect_data_files,
)


PROJECT_ROOT = (
    Path(SPECPATH)
    .resolve()
    .parent
)


datas = [
    (
        str(
            PROJECT_ROOT
            / "prompts"
            / "schemas"
        ),
        "prompts/schemas",
    ),
]

# CustomTkinter requires non-Python resources such as JSON/OTF files.
datas += collect_data_files(
    "customtkinter"
)


binaries = []
hiddenimports = []


def collect_runtime_package(
    package_name: str,
) -> None:
    package_datas, package_binaries, package_hiddenimports = (
        collect_all(
            package_name
        )
    )

    datas.extend(
        package_datas
    )

    binaries.extend(
        package_binaries
    )

    hiddenimports.extend(
        package_hiddenimports
    )


# Packages with runtime data, native binaries, or imports that
# deserve explicit collection for the first Windows bundle.
for runtime_package in (
    "faster_whisper",
    "ctranslate2",
    "sounddevice",
    "soundfile",
    "soundcard",
):
    collect_runtime_package(
        runtime_package
    )


analysis = Analysis(
    [
        str(
            PROJECT_ROOT
            / "app.py"
        ),
    ],
    pathex=[
        str(
            PROJECT_ROOT
        ),
    ],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)


pyz = PYZ(
    analysis.pure
)


exe = EXE(
    pyz,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name="MeetingAssistantAI",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
)


bundle = COLLECT(
    exe,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="MeetingAssistantAI",
)
