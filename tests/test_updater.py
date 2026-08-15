import base64
import json
import stat
import sys
import zipfile
from dataclasses import replace

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from updater.checker import check_for_update
from updater.config import BuildInfo, resolve_install_root
from updater.errors import (
    UpdateConfigurationError,
    UpdateInstallError,
    UpdateVerificationError,
)
from updater.health import confirm_startup_health, consume_health_argument
from updater.installer import apply_managed_update, rollback_managed_update
from updater.manifest import canonical_payload, parse_signed_manifest
from updater.staging import extract_managed_zip, normalize_managed_payload


def _key_pair():
    private = Ed25519PrivateKey.generate()
    public = private.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return private, base64.b64encode(public).decode("ascii")


def _signed_manifest(private, **overrides):
    document = {
        "version": "0.8.1",
        "channel": "stable",
        "minimum_updater_version": "0.8.0",
        "release_notes_url": "https://example.test/releases/0.8.1",
        "artifacts": [
            {
                "edition": "standard",
                "platform": "win32",
                "architecture": "x86_64",
                "format": "managed",
                "url": "https://example.test/SchedPlus.zip",
                "size": 123,
                "sha256": "a" * 64,
            }
        ],
    }
    document.update(overrides)
    document["signature"] = base64.b64encode(
        private.sign(canonical_payload(document))
    ).decode("ascii")
    return json.dumps(document).encode("utf-8")


def _build_info(public_key):
    return BuildInfo(
        version="0.8.0",
        edition="standard",
        package_format="managed",
        platform="win32",
        architecture="x86_64",
        channel="stable",
        update_manifest_url="https://example.test/updates.json",
        update_public_key=public_key,
        updates_enabled=True,
    )


def test_signed_manifest_selects_exact_compatible_artifact():
    private, public = _key_pair()
    result = check_for_update(
        _build_info(public), raw_manifest=_signed_manifest(private)
    )

    assert result.available
    assert result.latest_version == "0.8.1"
    assert result.artifact.edition == "standard"


def test_manifest_tampering_is_rejected():
    private, public = _key_pair()
    raw = _signed_manifest(private).replace(b"0.8.1", b"0.9.1", 1)

    with pytest.raises(UpdateVerificationError, match="signature"):
        parse_signed_manifest(raw, public)


def test_store_and_source_builds_cannot_self_update():
    for package_format in ("source", "snap", "msix-store"):
        info = replace(
            _build_info("unused"),
            package_format=package_format,
            updates_enabled=package_format != "source",
        )
        with pytest.raises(UpdateConfigurationError):
            info.validate_for_updates()


def test_relative_install_root_is_resolved_from_packaged_executable(
    tmp_path, monkeypatch
):
    executable = tmp_path / "SchedPlus" / "current" / "schedplus"
    monkeypatch.setattr("updater.config.sys.executable", str(executable))
    info = replace(_build_info("unused"), install_root="..")
    assert resolve_install_root(info) == tmp_path / "SchedPlus"


def test_update_requires_exact_edition_platform_architecture_and_format():
    private, public = _key_pair()
    info = replace(_build_info(public), edition="lite")
    result = check_for_update(info, raw_manifest=_signed_manifest(private))
    assert not result.available
    assert result.artifact is None


def test_zip_staging_rejects_path_traversal(tmp_path):
    archive = tmp_path / "bad.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr("../outside.txt", "bad")

    with pytest.raises(UpdateVerificationError, match="unsafe"):
        extract_managed_zip(archive, tmp_path / "staged")
    assert not (tmp_path / "outside.txt").exists()


def test_distributable_portable_zip_selects_nested_current_payload(tmp_path):
    extracted = tmp_path / "unpacked"
    payload = extracted / "SchedPlus-Standard-0.8.2-test-windows-x86_64" / "current"
    payload.mkdir(parents=True)
    (payload / "SchedPlusStandard.exe").write_bytes(b"launcher")

    staged = normalize_managed_payload(
        extracted, tmp_path / "staged", "SchedPlusStandard.exe"
    )

    assert (staged / "SchedPlusStandard.exe").read_bytes() == b"launcher"
    assert not extracted.exists()


def test_health_tokens_are_consumed_and_confined(tmp_path):
    token = tmp_path / "temp" / ("health-" + "a" * 32 + ".ok")
    arguments, value = consume_health_argument(
        ["--py", "--update-health-token", str(token)]
    )
    assert arguments == ["--py"]
    assert value == str(token)

    confirm_startup_health(value, str(tmp_path))
    assert token.read_text(encoding="utf-8") == "ok\n"

    with pytest.raises(UpdateInstallError):
        confirm_startup_health(str(tmp_path / "unrelated.txt"), str(tmp_path))


@pytest.mark.skipif(sys.platform == "win32", reason="uses a POSIX test launcher")
def test_managed_update_keeps_last_good_version(tmp_path, monkeypatch):
    monkeypatch.setattr("updater.state.user_data_directory", lambda: tmp_path / "data")
    root = tmp_path / "install"
    current = root / "current"
    staged = root / "temp" / "staged"
    current.mkdir(parents=True)
    staged.mkdir(parents=True)
    (current / "version.txt").write_text("old", encoding="utf-8")
    launcher = staged / "schedplus"
    launcher.write_text(
        "#!/bin/sh\nprintf 'ok\\n' > \"$2\"\n",
        encoding="utf-8",
    )
    launcher.chmod(launcher.stat().st_mode | stat.S_IXUSR)
    (staged / "version.txt").write_text("new", encoding="utf-8")

    apply_managed_update(
        root,
        staged,
        "schedplus",
        current_version="0.8.0",
        target_version="0.8.1",
        health_timeout=2,
    )

    assert (root / "current" / "version.txt").read_text() == "new"
    assert (root / "_old" / "version.txt").read_text() == "old"

    rollback_managed_update(root)
    assert (root / "current" / "version.txt").read_text() == "old"


@pytest.mark.skipif(sys.platform == "win32", reason="uses a POSIX test launcher")
def test_failed_health_check_rolls_back(tmp_path, monkeypatch):
    monkeypatch.setattr("updater.state.user_data_directory", lambda: tmp_path / "data")
    root = tmp_path / "install"
    current = root / "current"
    staged = root / "temp" / "staged"
    current.mkdir(parents=True)
    staged.mkdir(parents=True)
    (current / "version.txt").write_text("old", encoding="utf-8")
    launcher = staged / "schedplus"
    launcher.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
    launcher.chmod(launcher.stat().st_mode | stat.S_IXUSR)

    with pytest.raises(UpdateInstallError, match="restored"):
        apply_managed_update(
            root,
            staged,
            "schedplus",
            current_version="0.8.0",
            target_version="0.8.1",
            health_timeout=1,
        )

    assert (root / "current" / "version.txt").read_text() == "old"


@pytest.mark.skipif(sys.platform == "win32", reason="uses a POSIX test launcher")
def test_081_to_signed_test_release_runs_end_to_end(tmp_path, monkeypatch):
    """Exercise signed discovery, compatibility selection, swap, and health check."""
    monkeypatch.setattr("updater.state.user_data_directory", lambda: tmp_path / "data")
    private, public = _key_pair()
    raw_manifest = _signed_manifest(private, version="0.8.2-test")
    info = replace(_build_info(public), version="0.8.1")

    result = check_for_update(info, raw_manifest=raw_manifest)
    assert result.available
    assert result.latest_version == "0.8.2-test"

    root = tmp_path / "install"
    current = root / "current"
    staged = root / "temp" / "staged"
    current.mkdir(parents=True)
    staged.mkdir(parents=True)
    (current / "version.txt").write_text("0.8.1", encoding="utf-8")
    launcher = staged / "schedplus"
    launcher.write_text("#!/bin/sh\nprintf 'ok\\n' > \"$2\"\n", encoding="utf-8")
    launcher.chmod(launcher.stat().st_mode | stat.S_IXUSR)
    (staged / "version.txt").write_text("0.8.2-test", encoding="utf-8")

    apply_managed_update(
        root,
        staged,
        "schedplus",
        current_version=info.version,
        target_version=result.latest_version,
        health_timeout=2,
    )

    assert (root / "current" / "version.txt").read_text() == "0.8.2-test"
    assert (root / "_old" / "version.txt").read_text() == "0.8.1"
