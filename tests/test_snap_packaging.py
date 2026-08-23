from pathlib import Path

from scripts.sync_release_versions import sync_versions

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = PROJECT_ROOT / "snap" / "snapcraft.yaml"
WORKFLOW = PROJECT_ROOT / ".github" / "workflows" / "build-snap.yml"


def test_committed_manifest_packages_standard_with_strict_confinement():
    manifest = MANIFEST.read_text(encoding="utf-8")

    assert "name: schedplus" in manifest
    assert "base: core24" in manifest
    assert "platforms:\n  amd64:" in manifest
    assert "confinement: strict" in manifest
    assert 'version: "' in manifest
    assert "command: bin/schedplus-standard" in manifest
    assert "extensions: [gnome]" in manifest
    assert '".[standard]"' in manifest
    assert "schedplus-full" not in manifest
    assert "adopt-info:" not in manifest
    assert "craftctl set version=" not in manifest
    assert "KeyPlus" not in manifest


def test_snap_version_sync_uses_project_metadata(tmp_path):
    project_file = tmp_path / "pyproject.toml"
    manifest = tmp_path / "snapcraft.yaml"
    windows_version = tmp_path / "version_info.txt"
    project_file.write_text('[project]\nversion = "9.8.7"\n', encoding="utf-8")
    manifest.write_text('name: schedplus\nversion: "0.0.0"\n', encoding="utf-8")
    windows_version.write_text(
        "    filevers=(0, 0, 0, 0),\n"
        "    prodvers=(0, 0, 0, 0),\n"
        "StringStruct('FileVersion', '0.0.0')\n"
        "StringStruct('ProductVersion', '0.0.0')\n",
        encoding="utf-8",
    )

    assert (
        sync_versions(
            project_file=project_file,
            snap_manifest=manifest,
            windows_version=windows_version,
        )
        == "9.8.7"
    )
    assert manifest.read_text(encoding="utf-8") == 'name: schedplus\nversion: "9.8.7"\n'
    assert "filevers=(9, 8, 7, 0)" in windows_version.read_text(encoding="utf-8")


def test_snap_desktop_assets_use_registered_identity():
    desktop = (PROJECT_ROOT / "snap" / "gui" / "schedplus.desktop").read_text(
        encoding="utf-8"
    )

    assert "Name=SchedPlus" in desktop
    assert "Exec=schedplus" in desktop
    assert "Icon=${SNAP}/meta/gui/schedplus.png" in desktop
    snap_icon = PROJECT_ROOT / "snap" / "gui" / "schedplus.png"
    release_icon = PROJECT_ROOT / "assets" / "icons" / "icon-256.png"
    assert snap_icon.read_bytes() == release_icon.read_bytes()
    assert not (PROJECT_ROOT / "snap" / "gui" / "schedplus.svg").exists()
    assert "KeyPlus" not in desktop


def test_snap_release_channels_and_manual_stable_gate_are_explicit():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    documentation = (PROJECT_ROOT / "packaging" / "snap" / "README.md").read_text(
        encoding="utf-8"
    )

    assert "snapcore/action-publish" not in workflow
    assert "SNAPCRAFT_STORE_CREDENTIALS" not in workflow
    assert "Dynamically Generate Snapcraft Manifest" not in workflow
    assert "python3 scripts/sync_release_versions.py" in workflow
    assert "trial prereleases go to `edge`" in documentation
    assert "release candidates to `candidate`" in documentation
    assert "promoted to `stable` only after final approval" in documentation


def test_workflow_leaves_store_refresh_testing_to_supported_manual_hosts():
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "snap install --dangerous" not in workflow
    assert "snap refresh --dangerous" not in workflow
    assert "Inspect package metadata and desktop integration" in workflow


def test_workflow_embeds_and_verifies_externally_managed_update_policy():
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "--format snap" in workflow
    assert "--updates-enabled" not in workflow
    assert 'info["format"] == "snap"' in workflow
    assert 'info["updates_enabled"] is False' in workflow
    assert 'info["update_manifest_url"] == ""' in workflow
    assert 'grep -F "version: $SCHEDPLUS_PROJECT_VERSION"' in workflow
