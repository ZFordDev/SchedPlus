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


def test_builder_resolves_relative_appimagetool_path(monkeypatch, tmp_path):
    frozen = tmp_path / "SchedPlusStandard"
    frozen.mkdir()
    (frozen / "SchedPlusStandard").write_bytes(b"binary")
    tool = tmp_path / "appimagetool-x86_64.AppImage"
    tool.write_bytes(b"tool")
    invoked = []

    def fake_run(arguments, **_kwargs):
        invoked.append(arguments)
        Path(arguments[-1]).write_bytes(b"appimage")

    monkeypatch.setattr(build_appimage.subprocess, "run", fake_run)
    monkeypatch.setattr(build_appimage, "architecture", lambda: "x86_64")
    monkeypatch.chdir(tmp_path)

    build_appimage.build(
        frozen_dir=frozen,
        output_dir=tmp_path / "artifacts",
        version="0.8.0",
        appimagetool=Path("appimagetool-x86_64.AppImage"),
    )

    assert invoked[0][0] == str(tool.resolve())
    assert invoked[0][1:3] == ["--comp", "xz"]
