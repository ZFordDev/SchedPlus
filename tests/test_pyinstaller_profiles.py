from pathlib import Path

import pytest

from scripts.validate_frozen_artifact import EDITION_CONFIG, REQUIRED_SUFFIXES, validate


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SPEC_DIRECTORY = PROJECT_ROOT / "packaging" / "pyinstaller"


@pytest.mark.parametrize(
    ("edition", "entry_point", "excluded"),
    [
        ("standard", "standard.py", ("tkinter", "tkcalendar")),
        ("lite", "lite.py", ("PyQt6",)),
        ("full", "full.py", ()),
        ("cli", "cli_launcher.py", ("PyQt6", "tkinter", "tkcalendar")),
    ],
)
def test_each_profile_has_a_dedicated_onedir_spec(edition, entry_point, excluded):
    source = (SPEC_DIRECTORY / f"schedplus-{edition}.spec").read_text(encoding="utf-8")

    assert f'entry_point="{entry_point}"' in source
    assert "app = build(" in source
    assert "sys.path.insert(0, SPECPATH)" in source
    for framework in excluded:
        assert f'"{framework}"' in source


@pytest.mark.parametrize("edition", EDITION_CONFIG)
def test_artifact_validator_accepts_complete_edition_directory(tmp_path, edition):
    artifact = tmp_path / EDITION_CONFIG[edition]["directory"]
    artifact.mkdir()
    (artifact / f"{artifact.name}.exe").write_bytes(b"launcher")
    for suffix in REQUIRED_SUFFIXES:
        destination = artifact / "_internal" / suffix
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(b"asset")

    assert validate(artifact, edition) == []


def test_artifact_validator_rejects_excluded_frameworks(tmp_path):
    artifact = tmp_path / "SchedPlusCli"
    artifact.mkdir()
    (artifact / "SchedPlusCli.exe").write_bytes(b"launcher")
    for suffix in REQUIRED_SUFFIXES:
        destination = artifact / suffix
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(b"asset")
    (artifact / "_internal" / "PyQt6" / "QtCore.pyd").parent.mkdir(parents=True)
    (artifact / "_internal" / "PyQt6" / "QtCore.pyd").write_bytes(b"unexpected")

    assert "cli artifact unexpectedly includes PyQt6" in validate(artifact, "cli")
