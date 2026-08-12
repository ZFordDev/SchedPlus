from pathlib import Path

from scripts import build_debian_package
from scripts.build_debian_package import EDITIONS, _control, _copyright, _lintian_overrides


def test_debian_editions_are_mutually_exclusive():
    for edition in EDITIONS.values():
        control = _control(edition, "0.8.0", "amd64")

        assert f"Package: {edition.name}" in control
        assert f"Architecture: amd64" in control
        assert "Conflicts: " + ", ".join(edition.conflicts) in control
        assert "Replaces: " + ", ".join(edition.conflicts) in control


def test_debian_package_control_uses_current_branding():
    control = _control(EDITIONS["standard"], "0.8.0", "amd64")

    assert "local-first scheduler" in control
    assert "KeyPlus" not in control


def test_debian_metadata_uses_common_apache_license_and_explicit_runtime_overrides():
    assert "/usr/share/common-licenses/Apache-2.0" in _copyright()

    overrides = _lintian_overrides("schedplus-cli")
    assert "schedplus-cli: custom-library-search-path" in overrides
    assert "schedplus-cli: unstripped-binary-or-object" in overrides


def test_command_line_arguments_are_passed_to_the_debian_builder(monkeypatch, capsys):
    received = {}
    expected = Path("artifacts/debian/schedplus-cli_0.8.0_amd64.deb")
    monkeypatch.setattr(
        build_debian_package,
        "build",
        lambda **options: received.update(options) or expected,
    )
    monkeypatch.setattr(
        build_debian_package.sys,
        "argv",
        [
            "build_debian_package.py",
            "--edition",
            "cli",
            "--frozen-dir",
            "dist/SchedPlusCli",
            "--output-dir",
            "artifacts/debian",
            "--version",
            "0.8.0",
        ],
    )

    assert build_debian_package.main() == 0
    assert received == {
        "edition": "cli",
        "frozen_dir": Path("dist/SchedPlusCli"),
        "output_dir": Path("artifacts/debian"),
        "version": "0.8.0",
    }
    assert capsys.readouterr().out == f"{expected}\n"
