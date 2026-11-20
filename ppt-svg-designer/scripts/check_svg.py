"""Check an editable slide figure and optionally render a PNG with Inkscape."""
import argparse
import math
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

SVG = "{http://www.w3.org/2000/svg}"
ELEMENTS = set("svg title desc g text tspan rect circle ellipse path line polyline polygon".split())
ATTRIBUTES = set("""
    id x y dx dy x1 y1 x2 y2 cx cy r rx ry width height viewBox
    d points transform fill fill-opacity fill-rule stroke stroke-width
    stroke-opacity stroke-linecap stroke-linejoin stroke-dasharray opacity
    font-family font-size font-style font-weight text-anchor dominant-baseline
    letter-spacing preserveAspectRatio version
""".split())


def positive_length(value):
    match = re.fullmatch(r"(\d*\.?\d+)(?:cm|mm|in|pt|px)?", value)
    return bool(match and 0 < float(match[1]) < math.inf)


def check_svg(path):
    data = path.read_bytes()
    # The editable profile uses plain UTF-8 XML, without a DTD or processing instructions.
    source = data.decode("utf-8-sig")
    source = re.sub(r"^<\?xml\s+[^?]*\?>", "", source, count=1)
    if "<!DOCTYPE" in source or "<?" in source:
        raise ValueError("Use standalone SVG without a DTD or processing instructions")
    root = ET.fromstring(source)
    if root.tag != SVG + "svg":
        raise ValueError("Expected an SVG root in the SVG namespace")
    box = [float(n) for n in re.split(r"[\s,]+", root.get("viewBox", "").strip())]
    if len(box) != 4 or not all(map(math.isfinite, box)) or min(box[2:]) <= 0:
        raise ValueError("Invalid viewBox")
    if not all(positive_length(root.get(key, "")) for key in ("width", "height")):
        raise ValueError("Set positive explicit width and height")
    ids = set()
    for node in root.iter():
        if node.tag not in {SVG + name for name in ELEMENTS}:
            raise ValueError(f"Unsupported element: {node.tag}")
        for key, value in node.attrib.items():
            if key not in ATTRIBUTES or re.search(r"url\s*\(", value, re.I):
                raise ValueError(f"Unsupported attribute or resource reference: {key}")
        ident = node.get("id")
        if ident is not None:
            if not ident.strip() or ident in ids:
                raise ValueError(f"Empty or duplicate id: {ident}")
            ids.add(ident)
    if not any("".join(node.itertext()).strip() for node in root.iter(SVG + "text")):
        raise ValueError("Expected editable text")
    if not any(node.get("id") for node in root.iter(SVG + "g")):
        raise ValueError("Name at least one editable group")


def preview(path, target, width):
    if target.suffix.lower() != ".png" or path.resolve() == target.resolve():
        raise ValueError("Choose a separate .png output")
    if width <= 0:
        raise ValueError("Preview width must be positive")
    with tempfile.TemporaryDirectory(dir=target.parent) as tmp:
        image = Path(tmp) / "preview.png"
        subprocess.run(["inkscape", str(path.resolve()), f"--export-filename={image.resolve()}",
                        f"--export-width={width}"], check=True)
        if not image.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"):
            raise ValueError("Renderer did not produce a PNG")
        image.replace(target)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("svg", type=Path)
    parser.add_argument("--preview", type=Path, metavar="OUTPUT.png")
    parser.add_argument("--width", type=int, default=1280)
    args = parser.parse_args()
    try:
        check_svg(args.svg)
        if args.preview:
            preview(args.svg, args.preview, args.width)
    except (ValueError, ET.ParseError, OSError, subprocess.CalledProcessError) as error:
        print(f"{args.svg}: {error}", file=sys.stderr)
        return 1
    print(f"OK {args.svg}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
