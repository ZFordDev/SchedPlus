"""Shared, reproducible PyInstaller configuration for SchedPlus editions."""

from __future__ import annotations

from pathlib import Path

from PyInstaller.building.build_main import Analysis, COLLECT, EXE, PYZ


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


def build(*, edition: str, entry_point: str, excludes: list[str], console: bool):
    """Return the PyInstaller build graph for one self-contained onedir edition."""
    analysis = Analysis(
        [str(PROJECT_ROOT / "packaging" / "pyinstaller" / "entry_points" / entry_point)],
        pathex=[str(PROJECT_ROOT / "src")],
        binaries=[],
        datas=ASSETS,
        hiddenimports=[],
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
        icon=ICON,
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
