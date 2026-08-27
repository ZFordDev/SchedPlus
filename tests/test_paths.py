from pathlib import Path

import pytest

from logic.storage import paths


@pytest.mark.parametrize(
    ("platform", "appdata", "snap_user_common", "expected"),
    [
        ("linux", None, None, Path("/home/test/.local/share/ZFordDev/SchedPlus")),
        (
            "darwin",
            None,
            None,
            Path("/home/test/Library/Application Support/ZFordDev/SchedPlus"),
        ),
        (
            "win32",
            "C:/Users/Test/AppData/Roaming",
            None,
            Path("C:/Users/Test/AppData/Roaming/ZFordDev/SchedPlus"),
        ),
        (
            "linux",
            None,
            "/home/test/snap/schedplus/common",
            Path("/home/test/snap/schedplus/common/SchedPlus"),
        ),
    ],
)
def test_user_data_directory(
    monkeypatch, platform, appdata, snap_user_common, expected
):
    monkeypatch.setattr(paths.sys, "platform", platform)
    monkeypatch.setattr(paths.Path, "home", lambda: Path("/home/test"))
    if appdata is None:
        monkeypatch.delenv("APPDATA", raising=False)
    else:
        monkeypatch.setenv("APPDATA", appdata)
    if snap_user_common is None:
        monkeypatch.delenv("SNAP_USER_COMMON", raising=False)
    else:
        monkeypatch.setenv("SNAP_USER_COMMON", snap_user_common)

    assert paths.user_data_directory() == expected


def test_empty_snap_common_falls_back_to_normal_linux_location(monkeypatch):
    monkeypatch.setattr(paths.sys, "platform", "linux")
    monkeypatch.setattr(paths.Path, "home", lambda: Path("/home/test"))
    monkeypatch.setenv("SNAP_USER_COMMON", "   ")

    assert paths.user_data_directory() == Path(
        "/home/test/.local/share/ZFordDev/SchedPlus"
    )


def test_snap_database_path_stays_stable_when_revision_home_changes(monkeypatch):
    monkeypatch.setattr(paths.sys, "platform", "linux")
    monkeypatch.setenv("SNAP_USER_COMMON", "/home/test/snap/schedplus/common")
    monkeypatch.setattr(
        paths.Path, "home", lambda: Path("/home/test/snap/schedplus/12")
    )
    before_refresh = paths.database_path()
    monkeypatch.setattr(
        paths.Path, "home", lambda: Path("/home/test/snap/schedplus/13")
    )

    assert (
        before_refresh
        == paths.database_path()
        == Path("/home/test/snap/schedplus/common/SchedPlus/tasks.db")
    )


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

    with pytest.raises(
        paths.DatabaseMigrationError, match="Check directory permissions"
    ):
        paths.prepare_database()
