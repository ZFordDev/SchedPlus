from pathlib import Path
import os

import pytest

from scripts import build_appimage


def test_appdir_contains_portable_standard_launch_metadata(tmp_path):
    frozen = tmp_path / "SchedPlusStandard"
    frozen.mkdir()
    (frozen / "SchedPlusStandard").write_bytes(b"binary")

    appdir = build_appimage.create_appdir(frozen_dir=frozen, appdir=tmp_path / "SchedPlus.AppDir")

    if os.name != "nt":
        assert (appdir / "AppRun").stat().st_mode & 0o111
    assert "usr/lib/schedplus/SchedPlusStandard" in (appdir / "AppRun").read_text()
    desktop = (appdir / "dev.zford.SchedPlus.desktop").read_text()
    assert "Exec=SchedPlus" in desktop
    assert "Icon=dev.zford.SchedPlus" in desktop
    assert (appdir / "dev.zford.SchedPlus.png").is_file()
    assert (appdir / ".DirIcon").is_file()
    assert (appdir / "usr" / "lib" / "schedplus" / "SchedPlusStandard").is_file()


def test_appdir_rejects_the_wrong_frozen_edition(tmp_path):
    with pytest.raises(ValueError, match="SchedPlusStandard"):
        build_appimage.create_appdir(
            frozen_dir=tmp_path / "SchedPlusLite", appdir=tmp_path / "SchedPlus.AppDir"
        )
