# 主题体系说明（Theme System）

本文档说明 `scientific-drawing` 技能的统一主题体系，涵盖文件结构、使用方式、新增/切换主题的操作流程，以及向后兼容说明。

---

## 目录

1. [设计目标](#1-设计目标)
2. [文件结构](#2-文件结构)
3. [主题文件结构（theme-tokens.json）](#3-主题文件结构theme-tokensjson)
4. [TikZ 端使用方式](#4-tikz-端使用方式)
5. [Python 端使用方式](#5-python-端使用方式)
6. [如何新增主题](#6-如何新增主题)
7. [如何切换默认主题](#7-如何切换默认主题)
8. [如何同步到-TikZ](#8-如何同步到-tikz)
9. [向后兼容说明](#9-向后兼容说明)

---

## 1. 设计目标

| 目标 | 说明 |
|------|------|
| **单一颜色源** | 所有颜色、线型、字体、布局参数统一存储于 `theme-tokens.json`，TikZ 与 Python 均从此读取 |
| **一改全生效** | 修改 `theme-tokens.json` 后运行同步脚本，TikZ/Python 即可使用新主题 |
| **规则与数据解耦** | `SKILL.md` 只保留选色规则和逻辑，不内置具体 hex 值 |
| **向后兼容** | 已有脚本的 `from color_palette import ...` 导入无需修改 |

---

## 2. 文件结构

```
scientific-drawing/
├── references/
│   ├── theme-tokens.json          ← 唯一颜色源（Single Source of Truth）
│   ├── tikz-theme.tex             ← 由同步脚本生成，TikZ \input 此文件
│   ├── color-palettes.json        ← 历史配色库（保留作参考）
│   └── color-standards.md        ← 选色规则与原则文档
├── figures/
│   ├── theme_tokens.py            ← Python 主题加载模块（动态读取 JSON）
│   └── color_palette.py           ← 向后兼容包装层（内部调用 theme_tokens）
└── scripts/
    └── sync_theme_tokens.py       ← 同步脚本（JSON → tikz-theme.tex）
```

---

## 3. 主题文件结构（theme-tokens.json）

```json
{
  "default_theme": "schematic_general",

  "shared": {
    "typography": { "font_family_sans": "...", "font_size_pt": 13, ... },
    "strokes":    { "axis_width": 2.0, "line_width_main": 2.4, ... },
    "line_styles":{ "solid": "solid", "dashed": "dashed", ... },
    "markers":    { "circle": "o", "square": "s", "marker_size": 6 },
    "layout":     { "grid_alpha": 0.12, "legend_frame_alpha": 0.85, ... }
  },

  "themes": {
    "schematic_general": {
      "type":    "schematic",
      "goal":    "...",
      "colors":  { "background": "#FFFFFF", "primary": "#0072B2", ... },
      "usage":   { ... },
      "rules":   [ "..." ]
    },
    ...
  }
}
```

### 字段说明

| 字段 | 说明 |
|------|------|
| `default_theme` | 默认使用的主题名，Python `get_theme(None)` 和 TikZ 生成均使用此值 |
| `shared.typography` | 字体族、各级字号（pt） |
| `shared.strokes` | 各类线宽（pt，供 Python/TikZ 换算） |
| `shared.line_styles` | 线型名称别名 |
| `shared.markers` | matplotlib marker 字符与默认尺寸 |
| `shared.layout` | grid alpha、图例透明度、DPI、边距等 |
| `themes.<name>.colors` | 主题中所有语义化颜色（hex 字符串） |
| `themes.<name>.usage` | 颜色的推荐使用场景（文档性，非代码依赖） |
| `themes.<name>.rules` | 该主题的选色规则（文档性） |

### 内置主题

| 主题键 | 类型 | 适用场景 |
|--------|------|----------|
| `schematic_general` | schematic | 通用示意图、流程图、架构图（**默认**） |
| `biomedical_mechanism` | schematic | 生物医学、机制图 |
| `engineering_schematic` | schematic | 工程系统、流程图 |
| `line_chart_general` | data | 折线图、曲线图（多系列） |
| `continuous_data` | data | 连续数据热图、强度图 |
| `diverging_data` | data | 正负偏差图、相关性图 |
| `categorical_comparison` | data | 分类比较图、柱状图、箱线图 |

---

## 4. TikZ 端使用方式

### 步骤

1. 在 preamble 中加入 `\input`：

```latex
\documentclass[border={15pt 10pt 10pt 10pt}]{standalone}
\usepackage{xeCJK}
\setCJKmainfont{PingFang SC}
\usepackage{tikz}
\usetikzlibrary{positioning, shapes.geometric, arrows.meta, fit, calc, backgrounds}
\usepackage{xcolor}

% 引入统一主题（路径相对于 .tex 文件位置调整）
\input{../../references/tikz-theme.tex}
```

2. 直接使用预定义颜色命令与样式：

```latex
% 颜色命令（来自 schematic_general 默认主题）
\draw[draw=themePrimary, line width=\themeLineWidthMain] (0,0) -- (3,0);
\node[themeNodePrimary] at (1.5,1) {主路径节点};
\draw[themeArrow] (A) -- (B);
\draw[themeArrowWarning] (B) -- (C);
```

### 可用命令速查

**颜色命令**（`\definecolor` 定义，可直接用于 `draw=`、`fill=`、`text=`）：

| 命令 | 语义 |
|------|------|
| `\themeBackground` | 背景白色 |
| `\themeText` | 正文黑色 |
| `\themeSecondaryText` | 次级文字深灰 |
| `\themeOutline` | 轮廓深灰 |
| `\themeFillNeutral` | 中性填充浅灰 |
| `\themePrimary` | 主色蓝 |
| `\themeAccentOne` | 强调橙 |
| `\themeAccentTwo` | 强调绿 |
| `\themeAccentThree` | 强调紫 |
| `\themeWarning` | 警示红橙 |
| `\themeSeriesNumOne` … `\themeSeriesNumSix` | 数据图系列色 |
| `\themeSeqLow` … `\themeSeqMax` | 顺序色板（6级） |
| `\themeDivNegStrong` … `\themeDivPosStrong` | 发散色板（7级） |

**线宽命令**（`\newcommand` 定义，用于 `line width=`）：

| 命令 | 值 |
|------|----|
| `\themeLineWidthMain` | 2.4pt |
| `\themeLineWidthMinor` | 1.6pt |
| `\themeLineWidthThin` | 1.0pt |
| `\themeAxisWidth` | 2.0pt |
| `\themeArrowWidth` | 1.8pt |
| `\themeNodeBorderWidth` | 1.6pt |

**节点/箭头样式**（`\tikzset` 定义，直接作为 style 使用）：

| 样式 | 说明 |
|------|------|
| `themeNode` | 圆角矩形，深灰轮廓 |
| `themeNodePrimary` | 圆角矩形，蓝色轮廓，浅蓝填充 |
| `themeNodeAccent` | 圆角矩形，橙色轮廓 |
| `themeArrow` | Stealth 箭头，黑色 |
| `themeArrowPrimary` | Stealth 箭头，蓝色 |
| `themeArrowWarning` | Stealth 箭头，警示色 |
| `themeDashed` | 虚线，深灰 |
| `themeDotted` | 点线，深灰 |
| `themeBox` | 虚线框，浅灰半透明填充（fit 背景框） |
| `themeEllipse` | 椭圆，浅蓝填充（流程图开始/结束） |

---

## 5. Python 端使用方式

### 推荐方式（新脚本）

```python
import os, sys
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_SCRIPT_DIR, ".."))   # 指向 figures/

from theme_tokens import get_theme, get_color, apply_matplotlib_theme, apply_axes_style

# 一行完成字体注册 + rcParams + 颜色 cycle
apply_matplotlib_theme()                          # 默认主题（schematic_general）
# apply_matplotlib_theme("line_chart_general")   # 数据图

_theme = get_theme()                              # 获取主题字典
primary = get_color(_theme, "primary")            # 取单色
```

### API 说明

| 函数 | 说明 |
|------|------|
| `get_theme(name=None)` | 返回指定主题字典，None 使用 default_theme |
| `get_shared()` | 返回 shared token（typography/strokes/layout/markers/line_styles） |
| `get_color(theme, key)` | 从主题 colors 字典中安全取色 |
| `get_palette(theme)` | 返回有序系列色列表（适合 matplotlib color cycle） |
| `apply_matplotlib_theme(name=None)` | 设置 rcParams + 注册中文字体 + 颜色 cycle |
| `apply_axes_style(ax, name=None)` | 对 Axes 对象应用 spines/grid/tick 规范样式 |

---

## 6. 如何新增主题

1. 打开 `references/theme-tokens.json`
2. 在 `themes` 对象中新增一个条目：

```json
"my_new_theme": {
  "type":   "schematic",
  "goal":   "描述该主题的视觉目标",
  "colors": {
    "background": "#FFFFFF",
    "text":       "#000000",
    "primary":    "#your_hex",
    ...
  },
  "usage": { ... },
  "rules": [ "..." ]
}
```

3. 运行同步脚本更新 TikZ 文件（若新主题为默认主题）：

```bash
python scientific-drawing/scripts/sync_theme_tokens.py
```

4. Python 端无需额外操作（动态读取 JSON）。

---

## 7. 如何切换默认主题

1. 修改 `theme-tokens.json` 中的 `default_theme` 字段：

```json
{
  "default_theme": "line_chart_general",
  ...
}
```

2. 运行同步脚本，让 TikZ 文件使用新默认主题的颜色：

```bash
python scientific-drawing/scripts/sync_theme_tokens.py
```

3. Python 端调用 `apply_matplotlib_theme()` 或 `get_theme()` 时自动使用新默认。

---

## 8. 如何同步到 TikZ

```bash
# 在仓库任意目录执行：
python scientific-drawing/scripts/sync_theme_tokens.py

# 或在 scientific-drawing/scripts/ 目录下：
python sync_theme_tokens.py
```

脚本会读取 `references/theme-tokens.json`，用当前 `default_theme` 的颜色值重新生成 `references/tikz-theme.tex`。操作幂等，可重复执行。

> **注意**：`tikz-theme.tex` 由脚本自动生成，请不要手动编辑，否则下次运行同步脚本时会被覆盖。

---

## 9. 向后兼容说明

| 场景 | 状态 | 说明 |
|------|------|------|
| `from color_palette import BLUE, RED, BLACK, GRID_COLOR, GRID_ALPHA, SPINE_COLOR, SPINE_WIDTH` | ✅ 兼容 | `color_palette.py` 已改为内部调用 `theme_tokens`，常量值来自 `theme-tokens.json` |
| `from color_palette import PALETTE` | ✅ 兼容 | 返回 schematic_general 主题的调色板 |
| TikZ 内手写 `\definecolor` | ⚠️ 不推荐 | 可继续工作，但更新主题时不会自动同步；建议改用 `\input{tikz-theme.tex}` |
| `references/color-palettes.json` | ✅ 保留 | 原始配色库仍可查阅，主题 token 语义与其保持一致 |
