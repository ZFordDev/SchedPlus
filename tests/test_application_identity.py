from pathlib import Path

import pytest

from schedplus.identity import get_application_identity
from updater.config import BuildInfo


def test_identity_is_derived_from_build_info():
    identity = get_application_identity(
        BuildInfo(
            version="0.8.1",
            edition="standard",
            package_format="appimage",
            platform="linux",
            architecture="x86_64",
            channel="preview",
        )
    )

    assert identity.version_label == "SchedPlus v0.8.1"
    assert "Edition: Standard" in identity.details
    assert "Update channel: Preview" in identity.details
    assert "Package: appimage" in identity.details
    assert "Platform: linux (x86_64)" in identity.details


@pytest.mark.parametrize(
    "relative_path",
    (
        "src/ui/pyqt/window.py",
        "src/ui/tkinter_ui.py",
        "src/startup/selector.py",
        "src/cli/commands.py",
    ),
)
def test_every_interface_uses_shared_identity_provider(relative_path):
    project_root = Path(__file__).parents[1]
    source = (project_root / relative_path).read_text(encoding="utf-8")

    assert "from schedplus.identity import get_application_identity" in source
    assert "get_application_identity()" in source
    assert "pyproject.toml" not in source
