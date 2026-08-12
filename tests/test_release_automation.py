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
    assert "environment: snap-store-candidate" in workflow
    assert "needs: [validate, appimage, debian, windows, snap, draft-release]" in workflow
    assert "SNAPCRAFT_STORE_CREDENTIALS: ${{ secrets.SNAPCRAFT_STORE_CREDENTIALS }}" in workflow


def test_release_verifier_reports_missing_payload(tmp_path):
    errors = validate(tmp_path, "0.8.0")

    assert any("AppImage" in error for error in errors)
    assert any("source.tar.gz" in error for error in errors)
