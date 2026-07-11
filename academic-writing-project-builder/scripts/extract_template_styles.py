#!/usr/bin/env python3
"""从 docx/odt 模版提取样式信息，用于 pandoc reference-doc 生成。"""

import sys, json, zipfile, xml.etree.ElementTree as ET
from pathlib import Path


def extract_styles(template_path: str) -> dict:
    """
    提取 docx/odt 模版中的样式信息。
    返回 dict: { styleId: { 'sz': 字号半点值, 'font': '中文字体' }, ... }
    """
    styles = {}
    ns_w = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    ns_odt = "urn:oasis:names:tc:opendocument:xmlns:style:1.0"

    tpl = Path(template_path)
    if not tpl.exists():
        print(
            json.dumps({"error": f"Template not found: {template_path}"}),
            file=sys.stderr,
        )
        sys.exit(1)

    if tpl.suffix.lower() == ".docx":
        with zipfile.ZipFile(template_path) as z:
            if "word/styles.xml" not in z.namelist():
                print(
                    json.dumps({"error": "No word/styles.xml in docx"}), file=sys.stderr
                )
                sys.exit(1)
            with z.open("word/styles.xml") as f:
                tree = ET.parse(f)
        for style in tree.findall(f".//{{{ns_w}}}style"):
            sid = style.get(f"{{{ns_w}}}styleId")
            sz_el = style.find(f".//{{{ns_w}}}sz")
            sz2_el = style.find(f".//{{{ns_w}}}szCs")
            font_el = style.find(f".//{{{ns_w}}}rFonts")
            sz_val = None
            if sz_el is not None:
                v = sz_el.get(f"{{{ns_w}}}val")
                if v:
                    sz_val = int(v)
            elif sz2_el is not None:
                v = sz2_el.get(f"{{{ns_w}}}val")
                if v:
                    sz_val = int(v)
            font_val = None
            if font_el is not None:
                font_val = (
                    font_el.get(f"{{{ns_w}}}eastAsia")
                    or font_el.get(f"{{{ns_w}}}ascii")
                    or font_el.get(f"{{{ns_w}}}hAnsi")
                )
            if sid:
                styles[sid] = {"sz": sz_val, "font": font_val}

    elif tpl.suffix.lower() == ".odt":
        with zipfile.ZipFile(template_path) as z:
            if "styles.xml" not in z.namelist():
                print(json.dumps({"error": "No styles.xml in odt"}), file=sys.stderr)
                sys.exit(1)
            with z.open("styles.xml") as f:
                tree = ET.parse(f)
        for style in tree.findall(f".//{{{ns_odt}}}style"):
            sid = style.get(f"{{{ns_odt}}}name")
            sz_el = style.find(f".//{{{ns_odt}}}font-size")
            font_el = style.find(f".//{{{ns_odt}}}font-family")
            sz_val = None
            if sz_el is not None:
                v = sz_el.get(f"{{{ns_odt}}}font-size")
                if v:
                    sz_val = int(float(v) * 2)  # odt 用 cm, 转半点
            font_val = None
            if font_el is not None:
                font_val = font_el.get(f"{{{ns_odt}}}generic-family") or " ".join(
                    e.text for e in font_el if e.text
                )
            if sid:
                styles[sid] = {"sz": sz_val, "font": font_val}

    else:
        print(
            json.dumps({"error": f"Unsupported format: {tpl.suffix}"}), file=sys.stderr
        )
        sys.exit(1)

    print(json.dumps(styles, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    tpl = sys.argv[1] if len(sys.argv) > 1 else "template.docx"
    extract_styles(tpl)
