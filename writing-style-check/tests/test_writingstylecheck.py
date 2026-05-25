import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "writingstylecheck.py"


class WritingStyleCheckCliTests(unittest.TestCase):
    def run_cmd(self, args):
        proc = subprocess.run(
            ["python3", str(SCRIPT)] + args,
            capture_output=True,
            text=True,
            check=True,
        )
        return proc.stdout

    def test_json_output_has_expected_shape(self):
        out = self.run_cmd(["--text", "值得注意的是，系统可落地。", "--format", "json"])
        payload = json.loads(out)
        self.assertEqual(payload["standard"], "WSS-1")
        self.assertIn("summary", payload)
        self.assertIn("violations", payload)
        self.assertFalse(payload["fix"]["enabled"])

    def test_fix_dry_run_does_not_write_back(self):
        original = '"边缘计算"是关键。\n**核心**能力提升。\n值得注意的是，系统可落地。\n'
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "sample.md"
            p.write_text(original, encoding="utf-8")

            out = self.run_cmd([str(p), "--fix-dry-run", "--format", "json"])
            payload = json.loads(out)

            self.assertTrue(payload["fix"]["enabled"])
            self.assertTrue(payload["fix"]["dry_run"])
            self.assertTrue(payload["fix"]["changed"])
            self.assertFalse(payload["fix"]["write_back"])

            after = p.read_text(encoding="utf-8")
            self.assertEqual(after, original)

    def test_fix_writes_back_for_file(self):
        original = '"边缘计算"是关键。\n**核心**能力提升。\n值得注意的是，系统可落地。\n'
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "sample.md"
            p.write_text(original, encoding="utf-8")

            out = self.run_cmd([str(p), "--fix", "--format", "json"])
            payload = json.loads(out)

            self.assertTrue(payload["fix"]["enabled"])
            self.assertFalse(payload["fix"]["dry_run"])
            self.assertTrue(payload["fix"]["changed"])
            self.assertTrue(payload["fix"]["write_back"])

            after = p.read_text(encoding="utf-8")
            self.assertNotEqual(after, original)
            self.assertIn("“边缘计算”", after)
            self.assertNotIn("**核心**", after)


if __name__ == "__main__":
    unittest.main()
