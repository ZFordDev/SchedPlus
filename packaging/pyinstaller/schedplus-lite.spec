import sys

sys.path.insert(0, SPECPATH)

from common import build


app = build(
    edition="SchedPlusLite",
    entry_point="lite.py",
    excludes=["PyQt6"],
    console=False,
)
