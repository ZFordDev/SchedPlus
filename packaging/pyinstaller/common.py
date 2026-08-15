"""Shared, reproducible PyInstaller configuration for SchedPlus editions."""

from __future__ import annotations

import sys
from pathlib import Path

from PyInstaller.building.build_main import COLLECT, EXE, PYZ, Analysis

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ASSETS = [
    (str(PROJECT_ROOT / "assets" / "icons"), "assets/icons"),
    (str(PROJECT_ROOT / "assets" / "windows" / "SchedPlus.ico"), "assets/windows"),
    (str(PROJECT_ROOT / "packaging" / "metadata"), "packaging/metadata"),
    (str(PROJECT_ROOT / "LICENSE"), "licenses"),
    (str(PROJECT_ROOT / "LICENSES"), "licenses/LICENSES"),
    (str(PROJECT_ROOT / "NOTICE"), "licenses"),
]
ICON = str(PROJECT_ROOT / "assets" / "windows" / "SchedPlus.ico")
VERSION_INFO = str(PROJECT_ROOT / "packaging" / "pyinstaller" / "version_info.txt")
UPDATER_HIDDEN_IMPORTS = [
    "updater.background",
    "updater.checker",
    "updater.config",
    "updater.downloader",
    "updater.errors",
    "updater.health",
    "updater.installer",
    "updater.manifest",
    "updater.preferences",
    "updater.service",
    "updater.staging",
    "updater.state",
    "updater.update",
]


def build(
    *,
    edition: str,
    entry_point: str,
    excludes: list[str],
    console: bool,
    hiddenimports: list[str] | None = None,
):
    """Return the PyInstaller build graph for one self-contained onedir edition."""
    analysis = Analysis(
        [str(PROJECT_ROOT / "packaging" / "pyinstaller" / "entry_points" / entry_point)],
        pathex=[str(PROJECT_ROOT / "src")],
        binaries=[],
        datas=ASSETS,
        hiddenimports=[*UPDATER_HIDDEN_IMPORTS, *(hiddenimports or [])],
        hookspath=[],
        hooksconfig={},
        runtime_hooks=[],
        excludes=excludes,
        noarchive=False,
    )
    pyz = PYZ(analysis.pure)
    executable = EXE(
        pyz,
        analysis.scripts,
        [],
        exclude_binaries=True,
        name=edition,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=False,
        console=console,
        icon=ICON if sys.platform == "win32" else None,
        version=VERSION_INFO if sys.platform == "win32" else None,
    )
    return COLLECT(
        executable,
        analysis.binaries,
        analysis.zipfiles,
        analysis.datas,
        strip=False,
        upx=False,
        name=edition,
    )
