"""
color_palette.py — 向后兼容包装层
===================================
此文件保留原有常量导出接口，内部从 theme_tokens 模块读取。
已有绘图脚本无需修改即可继续使用：
    from color_palette import BLUE, RED, BLACK, GRID_COLOR, GRID_ALPHA, SPINE_COLOR, SPINE_WIDTH

推荐新脚本改用：
    from theme_tokens import get_theme, get_color, apply_matplotlib_theme
"""

from __future__ import annotations

import os
import sys

# 确保 theme_tokens 可被导入（无论从哪个目录运行）
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from theme_tokens import get_theme, get_color, get_shared, get_palette  # noqa: E402

_theme  = get_theme()          # 使用 default_theme（schematic_general）
_colors = _theme["colors"]
_shared = get_shared()
_layout = _shared["layout"]
_strokes = _shared["strokes"]

# ── 主色（数据系列）——与原 color_palette.py 常量对齐 ─────────────────────────
BLUE   = _colors.get("primary",  "#0072B2")
RED    = _colors.get("warning",  "#D55E00")
GREEN  = _colors.get("accent_2", "#009E73")
AMBER  = _colors.get("accent_1", "#E69F00")
PURPLE = _colors.get("accent_3", "#CC79A7")
TEAL   = "#56B4E9"

PALETTE = get_palette(_theme) or [BLUE, RED, GREEN, AMBER, PURPLE, TEAL]

# ── 中性色 ────────────────────────────────────────────────────────────────────
BLACK      = _colors.get("text",           "#000000")
DARK_GRAY  = _colors.get("secondary_text", "#4D4D4D")
MID_GRAY   = _colors.get("outline",        "#4D4D4D")
LIGHT_GRAY = _colors.get("fill_neutral",   "#D9D9D9")
WHITE      = _colors.get("background",     "#FFFFFF")

# ── 网格/边框 ─────────────────────────────────────────────────────────────────
GRID_COLOR  = _colors.get("grid", "#E5E5E5")
GRID_ALPHA  = _layout["grid_alpha"]
SPINE_COLOR = BLACK
SPINE_WIDTH = _strokes["axis_width"]

# ── 文字 ──────────────────────────────────────────────────────────────────────
TEXT_COLOR = BLACK
