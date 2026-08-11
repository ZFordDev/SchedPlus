import pytest

from startup.flags import VALID_FLAGS, determine_startup_mode
from startup.modes import StartupMode


def test_supported_startup_flags_are_explicit():
    assert VALID_FLAGS == {
        "--py": StartupMode.PYQT,
        "--tk": StartupMode.TK,
        "--raw": StartupMode.CLI,
    }


def test_removed_dev_flag_is_invalid(capsys):
    assert determine_startup_mode(["--dev"]) is StartupMode.INVALID
    assert "--dev" not in capsys.readouterr().out


@pytest.mark.parametrize("command", ["add", "list", "edit", "delete", "--help"])
def test_direct_commands_route_to_cli(command):
    assert determine_startup_mode([command]) is StartupMode.CLI
