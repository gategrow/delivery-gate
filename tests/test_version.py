"""Version queries must not execute the stop hook or dashboard."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class VersionTests(unittest.TestCase):
    def test_version_is_side_effect_free(self):
        root = Path(__file__).resolve().parents[1]
        for script in ("config-health", "quality-gate"):
            for flags in (["--version"], ["--hook", "--version"], ["--check", "--version"]):
                with self.subTest(script=script, flags=flags), tempfile.TemporaryDirectory() as directory:
                    result = subprocess.run(
                        [sys.executable, str(root / (script + ".py")), *flags],
                        input="",
                        capture_output=True,
                        text=True,
                        timeout=5,
                        cwd=directory,
                        env={**os.environ, "HOME": directory, "CLAUDE_PROJECT_DIR": directory},
                    )
                    self.assertEqual(result.returncode, 0)
                    self.assertEqual(result.stdout, script + " 1.0.0\n")
                    self.assertEqual(result.stderr, "")
                    self.assertEqual(list(Path(directory).iterdir()), [])
