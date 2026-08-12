"""Entry point for the scriptable SchedPlus CLI."""

import sys

from cli.commands import run_command


def run_cli(scheduler, arguments=None):
    """Run command parsing with supplied arguments or the process arguments."""
    arguments = list(sys.argv[1:] if arguments is None else arguments)
    if arguments and arguments[0] == "--raw":
        arguments.pop(0)
    if not arguments:
        arguments = ["--help"]
    return run_command(arguments, scheduler)
