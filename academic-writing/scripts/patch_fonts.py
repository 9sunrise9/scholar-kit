#!/usr/bin/env python3
"""对 docx 输出做极细微字体替换（仅当 pandoc 参数无法解决时启用）。"""

import sys, zipfile, shutil, os


def patch_fonts(docx_path: str, font_map: dict):
    tmp = docx_path + ".tmp"
    with (
        zipfile.ZipFile(docx_path, "r") as zin,
        zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout,
    ):
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename.endswith(".xml"):
                text = data.decode("utf-8")
                for old, new in font_map.items():
                    text = text.replace(old, new)
                data = text.encode("utf-8")
            zout.writestr(item, data)
    shutil.move(tmp, docx_path)
    print(f"Patched: {docx_path}")


if __name__ == "__main__":
    docx = sys.argv[1] if len(sys.argv) > 1 else "output.docx"
    font_map = {"Calibri": "Times New Roman", "Arial": "Helvetica"}
    patch_fonts(docx, font_map)
