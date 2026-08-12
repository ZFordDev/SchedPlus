from scripts.build_debian_package import EDITIONS, _control


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
