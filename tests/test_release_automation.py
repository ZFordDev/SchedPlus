from pathlib import Path

from scripts.verify_release_artifacts import validate

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_release_workflow_gates_draft_on_every_independent_builder():
    workflow = (PROJECT_ROOT / ".github" / "workflows" / "release.yml").read_text(
        encoding="utf-8"
    )

    assert "needs: [validate, appimage, debian, windows, snap]" in workflow
    assert "draft: true" in workflow
    assert "git archive --format=tar.gz" in workflow
    assert "sha256sum --check SHA256SUMS.txt" in workflow
    assert "anchore/sbom-action@v0" in workflow
    assert "sudo apt-get install --yes libegl1 libgl1" in workflow
    assert "QT_QPA_PLATFORM=offscreen python -m pytest -q" in workflow
    assert "snapcore/action-publish" not in workflow
    assert "SNAPCRAFT_STORE_CREDENTIALS" not in workflow


def test_release_verifier_reports_missing_payload(tmp_path):
    errors = validate(tmp_path, "0.8.0")

    assert any("AppImage" in error for error in errors)
    assert any("source.tar.gz" in error for error in errors)


def test_post_release_smoke_workflow_gates_stable_promotion():
    workflow = (
        PROJECT_ROOT / ".github" / "workflows" / "post-release-smoke.yml"
    ).read_text(encoding="utf-8")

    assert "Post-release installation and upgrade smoke tests" in workflow
    assert "post_release_smoke.py download" in workflow
    assert "seed --database" in workflow
    assert "verify --database" in workflow
    assert "Remove application without removing user data" in workflow
    assert "Windows portable ${{ matrix.edition }}" in workflow
    assert "Windows installed Standard" in workflow
    assert "Store packages use external updates" in workflow
    assert "if: always()" in workflow
    assert "sanitize diagnostic log" in workflow.lower()
    assert "${{ runner.temp }}" not in workflow
    assert "XDG_DATA_HOME=$RUNNER_TEMP" in workflow
    assert "APPDATA=$env:RUNNER_TEMP" in workflow
    assert "needs: [linux-packages, windows-portable, windows-installer, store-policy]" in workflow
    assert 'gh release edit "$TAG"' in workflow
