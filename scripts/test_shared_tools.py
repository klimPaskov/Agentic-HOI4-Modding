"""The shared tool copies match the hashes recorded from their upstream (scripts/shared_tools.json)."""
from __future__ import annotations

import contextlib
import io
import unittest

import check_shared_tools


class SharedTools(unittest.TestCase):
    def test_copies_match_the_lock(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = check_shared_tools.main([])
        self.assertEqual(status, 0, output.getvalue())


if __name__ == "__main__":
    unittest.main()
