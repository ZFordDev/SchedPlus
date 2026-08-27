from pathlib import Path
import tomllib


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_ci_runs_for_code_changes_but_ignores_docs_and_workflow_edits():
    workflow = (PROJECT_ROOT / ".github" / "workflows" / "ci.yml").read_text(
        encoding="utf-8"
    )

    assert "branches:\n      - main" in workflow
    assert workflow.count("paths-ignore:") == 2
    for pattern in ("'**.md'", "'**.yml'", "'**.yaml'"):
        assert workflow.count(pattern) == 2


def test_ci_installs_pyqt_runtime_before_running_offscreen_tests():
    workflow = (PROJECT_ROOT / ".github" / "workflows" / "ci.yml").read_text(
        encoding="utf-8"
    )

    assert "Install PyQt runtime libraries" in workflow
    assert "sudo apt-get install --yes libegl1 libgl1" in workflow
    assert "QT_QPA_PLATFORM=offscreen python -m pytest -q" in workflow


def test_mypy_is_available_to_the_ci_typecheck_job():
    project = tomllib.loads(
        (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    )
    development_dependencies = project["project"]["optional-dependencies"]["dev"]
    workflow = (PROJECT_ROOT / ".github" / "workflows" / "ci.yml").read_text(
        encoding="utf-8"
    )

    assert "mypy" in development_dependencies
    assert "python -m mypy src" in workflow
