import base64
import json

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from scripts.update_release_metadata import (
    build_info_document,
    embed_packaged_build_info,
    generate_signed_manifest,
)
from updater.manifest import parse_signed_manifest


def _keys():
    private = Ed25519PrivateKey.generate()
    private_bytes = private.private_bytes(
        serialization.Encoding.Raw,
        serialization.PrivateFormat.Raw,
        serialization.NoEncryption(),
    )
    public_bytes = private.public_key().public_bytes(
        serialization.Encoding.Raw,
        serialization.PublicFormat.Raw,
    )
    return (
        base64.b64encode(private_bytes).decode("ascii"),
        base64.b64encode(public_bytes).decode("ascii"),
    )


def test_enabled_build_info_contains_complete_package_identity():
    _, public_key = _keys()
    document = build_info_document(
        version="0.8.1",
        edition="standard",
        platform="linux",
        architecture="x86_64",
        package_format="appimage",
        channel="preview",
        manifest_url="https://example.test/preview.json",
        public_key=public_key,
        updates_enabled=True,
    )

    assert document == {
        "version": "0.8.1",
        "edition": "standard",
        "platform": "linux",
        "architecture": "x86_64",
        "format": "appimage",
        "channel": "preview",
        "update_manifest_url": "https://example.test/preview.json",
        "update_public_key": public_key,
        "updates_enabled": True,
        "updater_executable": "",
        "install_root": "",
        "launch_relative_path": "",
    }


def test_enabled_build_info_rejects_missing_or_invalid_verification_key():
    with pytest.raises(ValueError, match="public key"):
        build_info_document(
            version="0.8.1",
            edition="standard",
            platform="linux",
            architecture="x86_64",
            package_format="deb",
            channel="stable",
            manifest_url="https://example.test/stable.json",
            public_key="",
            updates_enabled=True,
        )


def test_release_manifest_is_signed_and_covers_artifact_hashes(tmp_path):
    private_key, public_key = _keys()
    artifact = tmp_path / "SchedPlus-0.8.2-test-x86_64.AppImage"
    artifact.write_bytes(b"verified test release")
    output = tmp_path / "preview.json"

    generate_signed_manifest(
        artifact_directory=tmp_path,
        output=output,
        version="0.8.2-test",
        channel="preview",
        minimum_updater_version="0.8.1",
        release_base_url="https://example.test/releases/test",
        release_notes_url="https://example.test/releases/test/notes",
        private_key_b64=private_key,
    )

    manifest = parse_signed_manifest(output.read_bytes(), public_key)
    assert manifest.version == "0.8.2-test"
    assert manifest.artifacts[0].size == artifact.stat().st_size
    assert manifest.artifacts[0].url.endswith(artifact.name)
    assert private_key not in output.read_text(encoding="utf-8")


def test_store_build_info_remains_externally_managed():
    document = build_info_document(
        version="0.8.1",
        edition="standard",
        platform="win32",
        architecture="x86_64",
        package_format="msix-store",
        channel="stable",
        manifest_url="",
        public_key="",
        updates_enabled=False,
    )
    assert not document["updates_enabled"]
    assert json.dumps(document)


def test_unsupported_installer_stays_opted_out_in_release_environment(
    tmp_path, monkeypatch
):
    _, public_key = _keys()
    monkeypatch.setenv("SCHEDPLUS_ENABLE_UPDATES", "1")
    monkeypatch.setenv("SCHEDPLUS_UPDATE_PUBLIC_KEY", public_key)
    payload = tmp_path / "SchedPlusStandard"

    destination = embed_packaged_build_info(
        payload,
        version="0.8.1",
        edition="standard",
        platform="win32",
        architecture="x86_64",
        package_format="windows-installer",
        updates_supported=False,
    )

    assert not json.loads(destination.read_text(encoding="utf-8"))["updates_enabled"]
