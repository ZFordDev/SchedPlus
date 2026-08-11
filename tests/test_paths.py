from pathlib import Path

import pytest

from logic.storage import paths


@pytest.mark.parametrize(
    ("platform", "appdata", "expected"),
    [
        ("linux", None, Path("/home/test/.local/share/ZFordDev/SchedPlus")),
        (
            "darwin",
            None,
            Path("/home/test/Library/Application Support/ZFordDev/SchedPlus"),
        ),
        (
            "win32",
            "C:/Users/Test/AppData/Roaming",
            Path("C:/Users/Test/AppData/Roaming/ZFordDev/SchedPlus"),
        ),
    ],
)
def test_user_data_directory(monkeypatch, platform, appdata, expected):
    monkeypatch.setattr(paths.sys, "platform", platform)
    monkeypatch.setattr(paths.Path, "home", lambda: Path("/home/test"))
    if appdata is None:
        monkeypatch.delenv("APPDATA", raising=False)
    else:
        monkeypatch.setenv("APPDATA", appdata)

    assert paths.user_data_directory() == expected


def test_prepare_database_moves_legacy_database(monkeypatch, tmp_path, caplog):
    legacy = tmp_path / "package" / "tasks.db"
    destination = tmp_path / "user" / "tasks.db"
    legacy.parent.mkdir()
    legacy.write_bytes(b"database contents")
    monkeypatch.setattr(paths, "legacy_database_path", lambda: legacy)
    monkeypatch.setattr(paths, "database_path", lambda: destination)

    with caplog.at_level("INFO"):
        result = paths.prepare_database()

    assert result == destination
    assert destination.read_bytes() == b"database contents"
    assert not legacy.exists()
    assert "Migrated database" in caplog.text


def test_prepare_database_does_not_replace_existing_database(monkeypatch, tmp_path):
    legacy = tmp_path / "package" / "tasks.db"
    destination = tmp_path / "user" / "tasks.db"
    legacy.parent.mkdir()
    destination.parent.mkdir()
    legacy.write_bytes(b"old")
    destination.write_bytes(b"current")
    monkeypatch.setattr(paths, "legacy_database_path", lambda: legacy)
    monkeypatch.setattr(paths, "database_path", lambda: destination)

    paths.prepare_database()

    assert destination.read_bytes() == b"current"
    assert legacy.read_bytes() == b"old"


def test_prepare_database_wraps_migration_errors(monkeypatch, tmp_path):
    legacy = tmp_path / "package" / "tasks.db"
    destination = tmp_path / "user" / "tasks.db"
    legacy.parent.mkdir()
    legacy.write_bytes(b"database contents")
    monkeypatch.setattr(paths, "legacy_database_path", lambda: legacy)
    monkeypatch.setattr(paths, "database_path", lambda: destination)

    def deny_move(*args):
        raise PermissionError("denied")

    monkeypatch.setattr(paths.shutil, "move", deny_move)

    with pytest.raises(paths.DatabaseMigrationError, match="Check directory permissions"):
        paths.prepare_database()
