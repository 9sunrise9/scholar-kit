import json
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts/check_svg.py"
CATALOG = ROOT / "catalog.json"
ASSETS = sorted((ROOT / "assets").glob("*.svg"))
SVG = "{http://www.w3.org/2000/svg}"


def run(*args):
    return subprocess.run([sys.executable, str(CLI), *args], capture_output=True)


class TestSvg(unittest.TestCase):
    def test_layouts(self):
        self.assertEqual(len(ASSETS), 9)
        for svg in ASSETS:
            with self.subTest(svg=svg):
                result = run(svg)
                self.assertEqual(result.returncode, 0, result.stderr)

    @unittest.skipUnless(shutil.which("inkscape"), "PNG preview needs Inkscape")
    def test_previews(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "output.png"
            for svg in ASSETS:
                with self.subTest(svg=svg):
                    result = run(svg, "--preview", target, "--width", "960")
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(struct.unpack(">II", target.read_bytes()[16:24]), (960, 361))
                    target.unlink()

    def test_invalid(self):
        original = ASSETS[0].read_text(encoding="utf-8")
        bad_inputs = [
            "<broken",
            original.replace('0 0 960 360', '0 0 nan 360'),
            original.replace('id="summary"', 'id="loop"'),
            original.replace('</svg>', '<image href="photo.png"/></svg>'),
            original.replace('</svg>', '<script/></svg>'),
            original.replace('<text ', '<path ').replace('</text>', '</path>'),
            original.replace('33.87cm', '0cm'),
        ]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.svg"
            for data in bad_inputs:
                with self.subTest(data=data[:80]):
                    path.write_text(data, encoding="utf-8")
                    self.assertNotEqual(run(path).returncode, 0)

    def test_preserve_source(self):
        with tempfile.TemporaryDirectory() as folder:
            svg = Path(folder) / "source.svg"
            shutil.copy(ASSETS[0], svg)
            self.assertNotEqual(run(svg, "--preview", svg).returncode, 0)
            self.assertEqual(svg.read_bytes(), ASSETS[0].read_bytes())


class TestCatalog(unittest.TestCase):
    def test_index_lists_each_asset_once(self):
        data = json.loads(CATALOG.read_text(encoding="utf-8"))
        raw = CATALOG.read_text(encoding="utf-8")
        self.assertNotIn("<svg", raw.lower())
        self.assertEqual(data["defaults"], {
            "width": "33.87cm",
            "height": "12.72cm",
            "viewBox": "0 0 960 360",
            "fontFamily": "Microsoft YaHei",
            "fill": "#193952",
            "accent": "#25748a",
            "panel": "#e1eff5",
        })
        layouts = data["layouts"]
        self.assertEqual(len(layouts), 9)
        ids = [item["id"] for item in layouts]
        self.assertEqual(len(ids), len(set(ids)))
        listed = []
        for item in layouts:
            self.assertRegex(item["id"], r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
            self.assertTrue(item["name"].strip())
            self.assertTrue(item["when"].strip())
            relative = item["file"]
            self.assertIsInstance(relative, str)
            self.assertFalse(Path(relative).is_absolute())
            self.assertNotIn("..", Path(relative).parts)
            path = (ROOT / relative).resolve()
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(path.suffix, ".svg")
            self.assertEqual(path.parent, (ROOT / "assets").resolve())
            listed.append(path)
            groups = item["groups"]
            self.assertIsInstance(groups, list)
            self.assertEqual(len(groups), len(set(groups)))
            present = [
                node.get("id")
                for node in ET.parse(path).getroot().iter(SVG + "g")
                if node.get("id")
            ]
            self.assertEqual(groups, present)
        self.assertEqual(set(listed), {path.resolve() for path in ASSETS})
        self.assertEqual(len(listed), len(set(listed)))
