"""Edition launchers must start their intended mode without GUI cross-imports."""

import ast
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib

from startup import controller
from startup.modes import StartupMode


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_project_defines_dedicated_entry_points():
    with (PROJECT_ROOT / "pyproject.toml").open("rb") as source:
        scripts = tomllib.load(source)["project"]["scripts"]

    assert scripts == {
        "schedplus": "startup.controller:boot_full",
        "schedplus-full": "startup.controller:boot_full",
        "schedplus-standard": "startup.controller:boot_standard",
        "schedplus-lite": "startup.controller:boot_lite",
        "schedplus-cli": "startup.controller:boot_cli",
    }


def test_full_launcher_keeps_existing_flag_routing(monkeypatch):
    launched = []
    monkeypatch.setattr(
        controller, "consume_health_argument", lambda arguments: (arguments, None)
    )
    monkeypatch.setattr(
        controller,
        "_launch_mode",
        lambda mode, arguments: launched.append((mode, arguments)) or 0,
    )
    monkeypatch.setattr(controller.sys, "argv", ["schedplus", "--py"])

    assert controller.boot_full() == 0
    assert launched == [(StartupMode.PYQT, ["--py"])]


def test_full_launcher_uses_the_existing_selector_without_arguments(monkeypatch):
    from startup import selector

    launched = []

    class FakeSelector:
        def show(self):
            return StartupMode.TK

    monkeypatch.setattr(
        controller, "consume_health_argument", lambda arguments: (arguments, None)
    )
    monkeypatch.setattr(
        controller,
        "_launch_mode",
        lambda mode, arguments: launched.append((mode, arguments)) or 0,
    )
    monkeypatch.setattr(selector, "StartupSelector", FakeSelector)
    monkeypatch.setattr(controller.sys, "argv", ["schedplus-full"])

    assert controller.boot_full() == 0
    assert launched == [(StartupMode.TK, [])]


def test_dedicated_gui_launchers_force_their_edition_mode(monkeypatch):
    launched = []
    monkeypatch.setattr(
        controller, "consume_health_argument", lambda arguments: (arguments, None)
    )
    monkeypatch.setattr(
        controller,
        "_launch_mode",
        lambda mode, arguments: launched.append((mode, arguments)) or 0,
    )
    monkeypatch.setattr(controller.sys, "argv", ["schedplus-standard", "--tk"])

    assert controller.boot_standard() == 0
    assert controller.boot_lite() == 0
    assert launched == [
        (StartupMode.PYQT, ["--tk"]),
        (StartupMode.TK, ["--tk"]),
    ]


def test_cli_launcher_passes_commands_to_shared_command_parser(monkeypatch):
    launched = []
    monkeypatch.setattr(
        controller, "consume_health_argument", lambda arguments: (arguments, None)
    )
    monkeypatch.setattr(
        controller,
        "_launch_mode",
        lambda mode, arguments: launched.append((mode, arguments)) or 0,
    )
    monkeypatch.setattr(
        controller.sys, "argv", ["schedplus-cli", "list", "--sort", "time"]
    )

    assert controller.boot_cli() == 0
    assert launched == [(StartupMode.CLI, ["list", "--sort", "time"])]


def test_entry_point_modules_do_not_import_gui_frameworks():
    for source_path in (
        PROJECT_ROOT / "src" / "startup" / "controller.py",
        PROJECT_ROOT / "src" / "schedplus" / "__main__.py",
        PROJECT_ROOT / "src" / "cli" / "cli_main.py",
    ):
        tree = ast.parse(source_path.read_text(encoding="utf-8"), source_path.name)
        imports = set()
        for node in tree.body:
            if isinstance(node, ast.Import):
                imports.update(alias.name.partition(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                imports.add(node.module.partition(".")[0])
        assert "PyQt6" not in imports
        assert "tkcalendar" not in imports
