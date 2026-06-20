import sys
from .raw_mode import run_raw_mode

def run_cli(scheduler):
    """
    Entry point for RAW CLI mode.
    """
    args = sys.argv[1:]

    # Remove the --raw flag itself
    if "--raw" in args:
        args.remove("--raw")

    run_raw_mode(args, scheduler)
