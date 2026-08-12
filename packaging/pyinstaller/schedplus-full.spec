import sys

sys.path.insert(0, SPECPATH)

from common import build


app = build(
    edition="SchedPlusFull",
    entry_point="full.py",
    excludes=[],
    console=False,
)
