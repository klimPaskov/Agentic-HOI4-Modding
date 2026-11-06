"""Repository-owned HOI4 3D pipeline support library."""

import sys

# The tools write files with `newline=` (Python 3.10) and measure with numpy. An older default Python
# (3.9 on some machines) otherwise fails deep inside a tool with an unrelated error.
if sys.version_info < (3, 10):
    raise SystemExit("The 3D pipeline needs Python 3.10 or later with numpy. Run it with `py -3.13 -B <tool>` on Windows or `python3.13 <tool>` elsewhere.")
try:
    import numpy  # noqa: F401
except ImportError:
    raise SystemExit("The 3D pipeline needs numpy: `py -3.13 -m pip install numpy`, then run the tool again.") from None
