from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "skills" / "snapnote" / "templates" / "default" / "scripts" / "snapnote_packet_helper.py"
FIXTURES = ROOT / "tests" / "fixtures"


def decoded_path(stdout: str) -> Path:
    for line in stdout.splitlines():
        if line.startswith("Decoded source.image: "):
            return Path(line.split(": ", 1)[1])
    raise AssertionError(f"missing decoded image path in output:\n{stdout}")


class SnapNotePacketHelperTests(unittest.TestCase):
    def run_helper(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(HELPER), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_decodes_v0_1_0_source_image_data(self) -> None:
        fixture = FIXTURES / "valid-v0.1.0-image-data.snapnote.json"

        result = self.run_helper("--decode", str(fixture))

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Valid SnapNote: valid-v0-1-0-image-data", result.stdout)
        self.assertNotIn("legacy", result.stderr.lower())
        output_path = decoded_path(result.stdout)
        self.assertTrue(output_path.exists())
        self.assertGreater(output_path.stat().st_size, 0)

    def test_warns_when_decoding_legacy_source_image_string(self) -> None:
        fixture = FIXTURES / "legacy-image-string.snapnote.json"

        result = self.run_helper("--decode", str(fixture))

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("WARNING: source.image is a legacy string shape", result.stderr)
        output_path = decoded_path(result.stdout)
        self.assertTrue(output_path.exists())
        self.assertGreater(output_path.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
