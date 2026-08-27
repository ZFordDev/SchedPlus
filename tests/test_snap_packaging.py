from pathlib import Path

from scripts.sync_release_versions import sync_versions

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = PROJECT_ROOT / "snap" / "snapcraft.yaml"
WORKFLOW_EDGE = PROJECT_ROOT / ".github" / "workflows" / "build-snap-edge.yml"
WORKFLOW_CANDIDATE = PROJECT_ROOT / ".github" / "workflows" / "build-snap-candidate.yml"
WORKFLOW_MANUAL = PROJECT_ROOT / ".github" / "workflows" / "build-snap.yml"
WORKFLOW_STABLE = PROJECT_ROOT / ".github" / "workflows" / "build-snap-stable.yml"


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


def test_snap_release_channels_and_manual_build_policy_are_explicit():
    workflow = WORKFLOW_MANUAL.read_text(encoding="utf-8")
    documentation = (PROJECT_ROOT / "packaging" / "snap" / "README.md").read_text(
        encoding="utf-8"
    )

    assert "snapcore/action-publish" not in workflow
    assert "SNAPCRAFT_STORE_CREDENTIALS" not in workflow
    assert "Dynamically Generate Snapcraft Manifest" not in workflow
    assert "python3 scripts/sync_release_versions.py" in workflow
    assert "`main` publish to `edge`" in documentation
    assert "`pre-release-*` tags publish to `candidate`" in documentation
    assert "`release-*` tags publish to `stable`" in documentation
    assert "Manual dispatch builds and" in documentation
    assert "does not publish it" in documentation


def test_workflow_leaves_store_refresh_testing_to_supported_manual_hosts():
    workflow = WORKFLOW_MANUAL.read_text(encoding="utf-8")

    assert "snap install --dangerous" not in workflow
    assert "snap refresh --dangerous" not in workflow
    assert "Inspect package metadata and desktop integration" in workflow


def test_workflow_embeds_and_verifies_externally_managed_update_policy():
    workflow = WORKFLOW_MANUAL.read_text(encoding="utf-8")

    assert "--format snap" in workflow
    assert "--updates-enabled" not in workflow
    assert 'info["format"] == "snap"' in workflow
    assert 'info["updates_enabled"] is False' in workflow
    assert 'info["update_manifest_url"] == ""' in workflow
    assert 'grep -F "version: $SCHEDPLUS_PROJECT_VERSION"' in workflow


def test_edge_workflow_embeds_and_verifies_externally_managed_update_policy():
    edge_workflow = (PROJECT_ROOT / ".github/workflows/build-snap-edge.yml").read_text(
        encoding="utf-8"
    )

    assert "--format snap" in edge_workflow
    assert "--updates-enabled" not in edge_workflow
    assert 'info["format"] == "snap"' in edge_workflow
    assert 'info["updates_enabled"] is False' in edge_workflow
    assert 'info["update_manifest_url"] == ""' in edge_workflow
    assert 'grep -F "version: $SCHEDPLUS_PROJECT_VERSION"' in edge_workflow


def test_edge_workflow_only_runs_automatically_for_snap_inputs_on_main():
    edge_workflow = WORKFLOW_EDGE.read_text(encoding="utf-8")

    assert "branches:\n      - main" in edge_workflow
    for path in (
        "'snap/**'",
        "'packaging/snap/**'",
        "'src/**'",
        "'pyproject.toml'",
        "'scripts/sync_release_versions.py'",
        "'scripts/update_release_metadata.py'",
    ):
        assert path in edge_workflow
    assert "tests/test_snap_packaging.py" not in edge_workflow
    assert ".github/workflows/build-snap-edge.yml" not in edge_workflow


def test_snap_publish_workflows_upload_and_release_once_to_their_channel():
    for workflow_path, channel in (
        (WORKFLOW_EDGE, "edge"),
        (WORKFLOW_CANDIDATE, "candidate"),
        (WORKFLOW_STABLE, "stable"),
    ):
        workflow = workflow_path.read_text(encoding="utf-8")

        assert f"snapcraft upload --release={channel}" in workflow
        assert "snapcraft release schedplus" not in workflow
