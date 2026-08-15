import sqlite3

import pytest

from scripts.post_release_smoke import (
    SMOKE_TASK_ID,
    sanitize_log,
    seed_legacy_database,
    verify_upgraded_database,
)


def test_populated_legacy_database_survives_schema_upgrade(tmp_path):
    database = tmp_path / "tasks.db"
    seed_legacy_database(database, "0.8.0")
    with sqlite3.connect(database) as connection:
        assert connection.execute("PRAGMA user_version").fetchone() == (0,)
        connection.execute("PRAGMA user_version = 1")

    verify_upgraded_database(database, 1)


def test_seed_refuses_to_replace_existing_data(tmp_path):
    database = tmp_path / "tasks.db"
    database.write_text("keep me", encoding="utf-8")

    with pytest.raises(FileExistsError):
        seed_legacy_database(database, "0.8.0")

    assert database.read_text(encoding="utf-8") == "keep me"


def test_verifier_rejects_missing_smoke_task(tmp_path):
    database = tmp_path / "tasks.db"
    seed_legacy_database(database, "0.7.3")
    with sqlite3.connect(database) as connection:
        connection.execute("DELETE FROM entries WHERE id = ?", (SMOKE_TASK_ID,))
        connection.execute("PRAGMA user_version = 1")

    with pytest.raises(ValueError, match="not preserved"):
        verify_upgraded_database(database, 1)


def test_log_sanitizer_redacts_paths_and_secret_values(tmp_path):
    source = tmp_path / "schedplus.log"
    output = tmp_path / "sanitized.log"
    source.write_text(
        "database=/home/private/tasks.db\nTOKEN=do-not-publish\nnormal status\n",
        encoding="utf-8",
    )

    sanitize_log(source, output, ["/home/private"])

    text = output.read_text(encoding="utf-8")
    assert "/home/private" not in text
    assert "do-not-publish" not in text
    assert "<redacted-path>/tasks.db" in text
    assert "TOKEN=<redacted>" in text
