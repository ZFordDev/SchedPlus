"""Keep build-profile dependencies small, explicit, and non-overlapping."""

import ast
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _project_metadata():
    with (PROJECT_ROOT / "pyproject.toml").open("rb") as source:
        return tomllib.load(source)["project"]


def test_core_profile_contains_no_desktop_dependencies():
    dependencies = _project_metadata()["dependencies"]
    normalized = " ".join(dependencies).lower()

    assert dependencies == ["cryptography>=44.0.0"]
    assert "pyqt" not in normalized
    assert "tkcalendar" not in normalized
    assert "babel" not in normalized


def test_interface_profiles_have_only_their_required_frameworks():
    extras = _project_metadata()["optional-dependencies"]

    assert extras["lite"] == ["tkcalendar>=1.6.1"]
    assert extras["standard"] == ["PyQt6>=6.11.0"]
    assert extras["full"] == ["PyQt6>=6.11.0", "tkcalendar>=1.6.1"]


def test_development_profile_includes_full_runtime_and_tools():
    extras = set(_project_metadata()["optional-dependencies"]["dev"])

    assert {"PyQt6>=6.11.0", "tkcalendar>=1.6.1"} <= extras
    assert {"pytest", "black", "ruff"} <= extras


def _external_import_roots(directory: Path) -> set[str]:
    roots = set()
    for source_path in directory.rglob("*.py"):
        tree = ast.parse(source_path.read_text(encoding="utf-8"), source_path.name)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots.update(alias.name.partition(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                roots.add(node.module.partition(".")[0])
    return roots


def test_core_and_cli_source_do_not_import_desktop_frameworks():
    imports = set()
    for package in ("logic", "cli", "updater"):
        imports.update(_external_import_roots(PROJECT_ROOT / "src" / package))

    assert "PyQt6" not in imports
    assert "tkcalendar" not in imports


def test_interface_source_does_not_cross_gui_frameworks():
    pyqt_imports = _external_import_roots(PROJECT_ROOT / "src" / "ui" / "pyqt")
    pyqt_imports.update(
        _external_import_roots(PROJECT_ROOT / "src" / "ui").intersection({"PyQt6"})
    )
    tkinter_tree = ast.parse(
        (PROJECT_ROOT / "src" / "ui" / "tkinter_ui.py").read_text(encoding="utf-8")
    )
    tkinter_imports = {
        node.module.partition(".")[0]
        for node in ast.walk(tkinter_tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    tkinter_imports.update(
        alias.name.partition(".")[0]
        for node in ast.walk(tkinter_tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    )

    assert "tkcalendar" not in pyqt_imports
    assert "PyQt6" not in tkinter_imports
