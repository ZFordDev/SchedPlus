from pathlib import Path

from scripts.sync_snap_version import sync_version

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = PROJECT_ROOT / "snap" / "snapcraft.yaml"
WORKFLOW = PROJECT_ROOT / ".github" / "workflows" / "build-snap.yml"


def test_committed_manifest_packages_standard_with_strict_confinement():
    manifest = MANIFEST.read_text(encoding="utf-8")

    assert "name: schedplus" in manifest
    assert "base: core24" in manifest
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
    project_file.write_text('[project]\nversion = "9.8.7"\n', encoding="utf-8")
    manifest.write_text('name: schedplus\nversion: "0.0.0"\n', encoding="utf-8")

    assert sync_version(project_file=project_file, manifest=manifest) == "9.8.7"
    assert manifest.read_text(encoding="utf-8") == 'name: schedplus\nversion: "9.8.7"\n'


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

    assert "name=edge" in workflow
    assert "name=candidate" in workflow
    assert "environment: snap-store-stable" in workflow
    assert "github.event_name == 'workflow_dispatch' && inputs.publish_stable" in workflow
    assert "release: stable" in workflow
    assert "Dynamically Generate Snapcraft Manifest" not in workflow
    assert "python3 scripts/sync_snap_version.py" in workflow


def test_workflow_installs_launches_and_checks_refresh_persistence():
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "snap install --dangerous" in workflow
    assert "snap run schedplus" in workflow
    assert "snap refresh --dangerous" in workflow
    assert 'snap/schedplus/common/SchedPlus/tasks.db' in workflow
