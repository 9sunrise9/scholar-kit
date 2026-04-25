"""
theme_tokens.py — 统一主题加载模块
=====================================
从 references/theme-tokens.json 读取配色与视觉样式，
为 matplotlib 绘图脚本提供主题 API。

用法示例：
    from theme_tokens import get_theme, get_color, apply_matplotlib_theme

    theme = get_theme()                    # 使用 default_theme
    theme = get_theme("line_chart_general")

    primary = get_color(theme, "primary")  # 从主题颜色字典中取色

    apply_matplotlib_theme()               # 一行设置 plt.rcParams
"""

from __future__ import annotations

import json
import os
from typing import Any

# ── 路径解析（无论从哪个目录运行脚本均可找到 JSON）────────────────────────────
_THIS_DIR   = os.path.dirname(os.path.abspath(__file__))
_REFS_DIR   = os.path.join(_THIS_DIR, "..", "references")
_TOKEN_FILE = os.path.join(_REFS_DIR, "theme-tokens.json")


def _load_tokens() -> dict[str, Any]:
    """加载并返回 theme-tokens.json 的完整内容（带缓存）。"""
    if not hasattr(_load_tokens, "_cache"):
        with open(_TOKEN_FILE, "r", encoding="utf-8") as f:
            _load_tokens._cache = json.load(f)  # type: ignore[attr-defined]
    return _load_tokens._cache  # type: ignore[attr-defined]


# ── 公开 API ──────────────────────────────────────────────────────────────────

def get_theme(name: str | None = None) -> dict[str, Any]:
    """
    返回指定主题的完整字典（colors / usage / rules 等字段）。

    Parameters
    ----------
    name : str | None
        主题名称，如 "schematic_general"、"line_chart_general"。
        传 None 时使用 JSON 中的 default_theme。

    Returns
    -------
    dict
        主题字典，包含 colors、usage、rules 等键。
        shared token（typography / strokes / layout 等）通过
        get_shared() 单独获取。
    """
    tokens = _load_tokens()
    if name is None:
        name = tokens["default_theme"]
    themes = tokens["themes"]
    if name not in themes:
        available = list(themes.keys())
        raise KeyError(f"主题 '{name}' 不存在。可用主题：{available}")
    return themes[name]


def get_shared() -> dict[str, Any]:
    """返回共享视觉 token（typography / strokes / line_styles / markers / layout）。"""
    return _load_tokens()["shared"]


def get_color(theme: dict[str, Any], key: str) -> str:
    """
    从主题颜色字典中安全取色。

    Parameters
    ----------
    theme : dict
        由 get_theme() 返回的主题字典。
    key : str
        颜色键名，如 "primary"、"series_1"、"background"。

    Returns
    -------
    str
        十六进制颜色字符串，如 "#0072B2"。
    """
    colors = theme.get("colors", {})
    if key not in colors:
        available = list(colors.keys())
        raise KeyError(f"颜色键 '{key}' 不在当前主题中。可用键：{available}")
    return colors[key]


def get_palette(theme: dict[str, Any]) -> list[str]:
    """
    返回主题中所有数据系列颜色，按 series_1 … series_N 顺序排列。
    对于 categorical_comparison 主题，返回 cat_1 … cat_N。

    适合直接传给 matplotlib color cycle。
    """
    colors = theme.get("colors", {})
    result: list[str] = []
    # 尝试 series_N
    for i in range(1, 10):
        if f"series_{i}" in colors:
            result.append(colors[f"series_{i}"])
    if result:
        return result
    # 尝试 cat_N
    for i in range(1, 10):
        if f"cat_{i}" in colors:
            result.append(colors[f"cat_{i}"])
    if result:
        return result
    # 回退：返回 primary / accent_*
    for key in ("primary", "accent_1", "accent_2", "accent_3"):
        if key in colors:
            result.append(colors[key])
    return result


def apply_matplotlib_theme(theme_name: str | None = None) -> None:
    """
    将主题 token 应用到 matplotlib rcParams，并注册中文字体。

    调用后无需手动设置 plt.rcParams，即可获得符合规范的默认样式。

    Parameters
    ----------
    theme_name : str | None
        同 get_theme(name)。None 表示使用 default_theme。
    """
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as _fm

    shared = get_shared()
    typo   = shared["typography"]
    layout = shared["layout"]

    # ── 中文字体注册 ─────────────────────────────────────────────────────────
    _candidates = [
        os.path.expanduser("~/Library/Fonts/SourceHanSansCN-Regular.ttf"),
        os.path.expanduser("~/Library/Fonts/SourceHanSansSC-Regular.otf"),
        "/Library/Fonts/SourceHanSansCN-Regular.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/noto-cjk/NotoSansCJKsc-Regular.otf",
        "/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc",
        os.path.expandvars(r"%WINDIR%\Fonts\msyh.ttc"),
        os.path.expandvars(r"%WINDIR%\Fonts\simhei.ttf"),
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
    ]
    for _p in _candidates:
        if os.path.isfile(_p):
            _fm.fontManager.addfont(_p)
            break

    # ── rcParams ─────────────────────────────────────────────────────────────
    font_stack = [typo["font_family_sans"]] + typo["font_family_sans_fallback"]
    plt.rcParams["font.family"]        = "sans-serif"
    plt.rcParams["font.sans-serif"]    = font_stack
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["font.size"]          = typo["font_size_pt"]
    plt.rcParams["axes.titlesize"]     = typo["title_size_pt"]
    plt.rcParams["axes.labelsize"]     = typo["label_size_pt"]
    plt.rcParams["xtick.labelsize"]    = typo["tick_size_pt"]
    plt.rcParams["ytick.labelsize"]    = typo["tick_size_pt"]
    plt.rcParams["legend.fontsize"]    = typo["legend_size_pt"]
    plt.rcParams["figure.dpi"]         = layout["figure_dpi"]

    # ── 颜色 cycle ────────────────────────────────────────────────────────────
    theme   = get_theme(theme_name)
    palette = get_palette(theme)
    if palette:
        from cycler import cycler
        plt.rcParams["axes.prop_cycle"] = cycler(color=palette)


def apply_axes_style(ax: Any, theme_name: str | None = None) -> None:
    """
    对单个 Axes 对象应用规范样式（spines / grid / ticks）。

    Parameters
    ----------
    ax : matplotlib.axes.Axes
    theme_name : str | None
    """
    shared = get_shared()
    layout = shared["layout"]
    strokes = shared["strokes"]
    theme  = get_theme(theme_name)
    colors = theme.get("colors", {})

    axis_color = colors.get("axis", colors.get("text", "#000000"))
    grid_color = colors.get("grid", "#E5E5E5")

    ax.spines[["top", "right"]].set_visible(False)
    for sp in ["left", "bottom"]:
        ax.spines[sp].set_color(axis_color)
        ax.spines[sp].set_linewidth(strokes["axis_width"])
    ax.tick_params(axis="both", width=strokes["axis_width"],
                   length=6, colors=axis_color, pad=5)
    ax.grid(True, ls=":", lw=strokes["line_width_thin"],
            color=grid_color, alpha=layout["grid_alpha"])
