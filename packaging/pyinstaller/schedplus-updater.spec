# SPDX-License-Identifier: GPL-3.0-only

from pathlib import Path

from PyInstaller.building.build_main import Analysis, EXE, PYZ

project_root = Path(SPECPATH).parents[1]
analysis = Analysis(
    [str(project_root / "packaging" / "pyinstaller" / "entry_points" / "updater.py")],
    pathex=[str(project_root / "src")],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    excludes=["PyQt6", "tkinter", "tkcalendar"],
    noarchive=False,
)
pyz = PYZ(analysis.pure)
app = EXE(
    pyz,
    analysis.scripts,
    analysis.binaries,
    analysis.datas,
    [],
    name="SchedPlusUpdater",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
)
