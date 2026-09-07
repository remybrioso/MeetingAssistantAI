# -*- mode: python ; coding: utf-8 -*-

"""
PyInstaller packaging contract for Meeting Assistant AI.
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

PRODUCTIVE_PROMPT_CONTRACTS = (
    "chunk_classification_v2",
    "chunk_classification_repair_v1",
    "chunk_ignored_segment_audit_v1",
    "chunk_action_metadata_v1",
    "meeting_semantic_consolidation_v1",
    "meeting_report_narrative_v1",
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

for prompt_contract in (
    PRODUCTIVE_PROMPT_CONTRACTS
):
    datas.append(
        (
            str(
                PROJECT_ROOT
                / "prompts"
                / f"{prompt_contract}.md"
            ),
            "prompts",
        )
    )

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
    console=False,
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
