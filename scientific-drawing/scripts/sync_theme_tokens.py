#!/usr/bin/env python3
"""
sync_theme_tokens.py — 从 theme-tokens.json 同步生成 TikZ 主题文件
====================================================================
执行方式（在仓库任意目录均可）：
    python scientific-drawing/scripts/sync_theme_tokens.py

或在 scientific-drawing/scripts/ 目录下：
    python sync_theme_tokens.py

幂等：重复运行结果一致，不会产生副作用。

生成文件：
    scientific-drawing/references/tikz-theme.tex
        — TikZ \\definecolor 与 \\tikzset 样式定义
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from typing import Any

# ── 路径解析 ─────────────────────────────────────────────────────────────────
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_SKILL_ROOT  = os.path.dirname(_SCRIPT_DIR)   # scientific-drawing/
_REFS_DIR    = os.path.join(_SKILL_ROOT, "references")
_TOKEN_FILE  = os.path.join(_REFS_DIR, "theme-tokens.json")
_TIKZ_OUT    = os.path.join(_REFS_DIR, "tikz-theme.tex")


def load_tokens(path: str = _TOKEN_FILE) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def hex_to_html(hex_color: str) -> str:
    """将 '#RRGGBB' 转为 LaTeX \\definecolor HTML 参数（去掉 #）。"""
    return hex_color.lstrip("#").upper()


def gen_tikz_theme(tokens: dict[str, Any]) -> str:
    """生成完整的 tikz-theme.tex 内容字符串。"""
    default_name: str = tokens["default_theme"]
    shared: dict     = tokens["shared"]
    theme: dict      = tokens["themes"][default_name]
    colors: dict     = theme["colors"]
    strokes: dict    = shared["strokes"]
    now              = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # 颜色别名映射：(LaTeX 命令名, JSON 颜色键, 回退色)
    color_map: list[tuple[str, str, str]] = [
        ("themeBackground",    "background",    "#FFFFFF"),
        ("themeText",          "text",          "#000000"),
        ("themeSecondaryText", "secondary_text","#4D4D4D"),
        ("themeOutline",       "outline",       "#4D4D4D"),
        ("themeFillNeutral",   "fill_neutral",  "#D9D9D9"),
        ("themeGrid",          "grid",          "#E5E5E5"),
        ("themePrimary",       "primary",       "#0072B2"),
        ("themeAccentOne",     "accent_1",      "#E69F00"),
        ("themeAccentTwo",     "accent_2",      "#009E73"),
        ("themeAccentThree",   "accent_3",      "#CC79A7"),
        ("themeWarning",       "warning",       "#D55E00"),
        ("themeAxis",          "axis",          "#000000"),
    ]

    # 数据系列色（line_chart_general）
    series_theme_name = "line_chart_general"
    series_colors: dict = tokens["themes"].get(series_theme_name, {}).get("colors", {})

    # 顺序/发散色板
    cont = tokens["themes"].get("continuous_data", {}).get("colors", {})
    div  = tokens["themes"].get("diverging_data",  {}).get("colors", {})
    seq_map = [
        ("themeSeqLow",     cont.get("low",      "#EAF3FF")),
        ("themeSeqLowMid",  cont.get("low_mid",  "#CFE3FF")),
        ("themeSeqMid",     cont.get("mid",      "#9CC7FF")),
        ("themeSeqHighMid", cont.get("high_mid", "#5BA5FF")),
        ("themeSeqHigh",    cont.get("high",     "#2E7DFF")),
        ("themeSeqMax",     cont.get("max",      "#005BBB")),
    ]
    div_map = [
        ("themeDivNegStrong",  div.get("negative_strong", "#2166AC")),
        ("themeDivNegMid",     div.get("negative_mid",    "#67A9CF")),
        ("themeDivNegSoft",    div.get("negative_soft",   "#D1E5F0")),
        ("themeDivCenter",     div.get("center",          "#F7F7F7")),
        ("themeDivPosSoft",    div.get("positive_soft",   "#FDDBC7")),
        ("themeDivPosMid",     div.get("positive_mid",    "#EF8A62")),
        ("themeDivPosStrong",  div.get("positive_strong", "#B2182B")),
    ]

    lines: list[str] = []

    lines += [
        f"% tikz-theme.tex — 统一 TikZ 主题定义",
        f"% 自动生成于 {now}，由 scripts/sync_theme_tokens.py 从 references/theme-tokens.json 生成。",
        f"% 请勿手动编辑；修改 theme-tokens.json 后重新运行同步脚本。",
        f"%",
        f"% 当前默认主题：{default_name}",
        f"%",
        f"% 用法（在 TikZ 文档 preamble 中）：",
        f"%   \\input{{<skill-root>/scientific-drawing/references/tikz-theme.tex}}",
        "",
        "% ── 默认主题颜色 ─────────────────────────────────────────────────────────────",
    ]

    for cmd, key, fallback in color_map:
        if key.startswith("__series_"):
            val = fallback
        else:
            val = colors.get(key, fallback)
        lines.append(f"\\definecolor{{{cmd}}}{{HTML}}{{{hex_to_html(val)}}}")

    lines += [
        "",
        "% ── 数据图系列色（line_chart_general）───────────────────────────────────────",
    ]
    fallback_series = ["#0072B2","#E69F00","#009E73","#CC79A7","#D55E00","#56B4E9"]
    for i in range(1, 7):
        val = series_colors.get(f"series_{i}", fallback_series[i - 1])
        lines.append(f"\\definecolor{{themeSeriesNum{_number_to_word(i)}}}{{HTML}}{{{hex_to_html(val)}}}")

    lines += [
        "",
        "% ── 顺序色板（continuous_data）─────────────────────────────────────────────",
    ]
    for cmd, val in seq_map:
        lines.append(f"\\definecolor{{{cmd}}}{{HTML}}{{{hex_to_html(val)}}}")

    lines += [
        "",
        "% ── 发散色板（diverging_data）───────────────────────────────────────────────",
    ]
    for cmd, val in div_map:
        lines.append(f"\\definecolor{{{cmd}}}{{HTML}}{{{hex_to_html(val)}}}")

    lines += [
        "",
        "% ── 线宽常量 ─────────────────────────────────────────────────────────────────",
        f"\\newcommand{{\\themeLineWidthMain}}{{{strokes['line_width_main']}pt}}",
        f"\\newcommand{{\\themeLineWidthMinor}}{{{strokes['line_width_minor']}pt}}",
        f"\\newcommand{{\\themeLineWidthThin}}{{{strokes['line_width_thin']}pt}}",
        f"\\newcommand{{\\themeAxisWidth}}{{{strokes['axis_width']}pt}}",
        f"\\newcommand{{\\themeArrowWidth}}{{{strokes['arrow_width']}pt}}",
        f"\\newcommand{{\\themeNodeBorderWidth}}{{{strokes['node_border_width']}pt}}",
        "",
        "% ── TikZ 通用样式 ────────────────────────────────────────────────────────────",
        "\\tikzset{",
        "  themeNode/.style={",
        "    rectangle, rounded corners=4pt,",
        "    draw=themeOutline, line width=\\themeNodeBorderWidth,",
        "    fill=white, text=themeText,",
        "    font=\\normalsize, align=center,",
        "    minimum width=3.0cm, minimum height=0.8cm",
        "  },",
        "  themeNodePrimary/.style={",
        "    themeNode,",
        "    draw=themePrimary, fill=themeSeqLow, text=themeText",
        "  },",
        "  themeNodeAccent/.style={",
        "    themeNode,",
        "    draw=themeAccentOne, fill=white, text=themeText",
        "  },",
        "  themeArrow/.style={",
        "    -Stealth, line width=\\themeArrowWidth, draw=themeText",
        "  },",
        "  themeArrowPrimary/.style={",
        "    themeArrow, draw=themePrimary",
        "  },",
        "  themeArrowWarning/.style={",
        "    themeArrow, draw=themeWarning",
        "  },",
        "  themeDashed/.style={",
        "    dashed, line width=\\themeLineWidthMinor, draw=themeOutline",
        "  },",
        "  themeDotted/.style={",
        "    dotted, line width=\\themeLineWidthMinor, draw=themeOutline",
        "  },",
        "  themeBox/.style={",
        "    draw=themeOutline, dashed, line width=\\themeLineWidthThin,",
        "    fill=themeFillNeutral, fill opacity=0.3,",
        "    rounded corners=6pt",
        "  },",
        "  themeEllipse/.style={",
        "    ellipse, draw=themeOutline, line width=\\themeNodeBorderWidth,",
        "    fill=themeSeqLow, text=themeText,",
        "    font=\\normalsize, align=center,",
        "    minimum width=2.8cm, minimum height=0.9cm",
        "  }",
        "}",
    ]

    return "\n".join(lines) + "\n"


def _number_to_word(n: int) -> str:
    """将 1–9 转为英文序数词首字母大写（One, Two …）用于命令名。"""
    words = ["One","Two","Three","Four","Five","Six","Seven","Eight","Nine"]
    return words[n - 1] if 1 <= n <= 9 else str(n)


def main() -> None:
    print(f"[sync] 读取 {_TOKEN_FILE}")
    tokens = load_tokens()

    print(f"[sync] 生成 {_TIKZ_OUT}")
    tikz_content = gen_tikz_theme(tokens)
    with open(_TIKZ_OUT, "w", encoding="utf-8") as f:
        f.write(tikz_content)

    print("[sync] 完成。已更新：")
    print(f"  → {_TIKZ_OUT}")
    print()
    print("提示：Python 端通过 figures/theme_tokens.py 动态读取，无需额外生成步骤。")


if __name__ == "__main__":
    main()
