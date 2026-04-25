# 学术配色规范手册

本文档整合自 `tikz-drawing-guide.md` 与 `reference.md`，涵盖配色原则、色板选择、Python/TikZ 工具。

---

## 目录

1. [核心原则](#1-核心原则)
2. [禁止事项](#2-禁止事项)
3. [按图形类型选色](#3-按图形类型选色)
4. [TikZ 推荐色板](#4-tikz-推荐色板)
5. [Python 共享色板](#5-python-共享色板)
6. [标注文字配色规范](#6-标注文字配色规范)
7. [Python 降饱和工具](#7-python-降饱和工具)
8. [SVG 颜色验证](#8-svg-颜色验证)
9. [灰度验证步骤（导出前必做）](#85-灰度验证步骤导出前必做)
10. [禁止色速查表](#9-禁止色速查表)

---

## 1. 核心原则

| 原则 | 规范 |
|---|---|
| **信息优先** | 配色服务于结构、层级、分类和趋势；不添加无意义的渐变、阴影、3D 效果 |
| **少色原则** | 示意图 ≤ 5 色；曲线图 2–4 色，多组最多 6–8 色并配线型/点型 |
| **饱和度** | 低饱和（HSL 饱和度 20–40%）；避免纯 RGB 原色 |
| **一致性** | 同一论文中相同对象/变量必须使用相同颜色语义，不得跨图改变 |
| **可读性** | 灰度打印可区分；色盲可区分；缩小到版面后仍清晰 |
| **可出版** | 避免荧光色、过饱和色、彩虹色带；保证线上阅读与印刷均稳定 |

> **行为规则（skill 执行层）**：
> 示意图用低饱和定性色板；数据图根据连续/发散/分类属性选顺序、发散或定性色板。
> 以黑/灰/蓝为结构基础，少量强调色突出关键对象。
> 严禁 rainbow/jet、荧光色、过饱和色、红绿唯一对比。
> 同一论文颜色语义必须保持一致。

---

## 2. 禁止事项

| 禁止行为 | 原因 |
|---|---|
| 使用 rainbow / jet 色带 | 制造虚假视觉边界，误导连续数据读者 |
| 红绿作为唯一对比 | 色盲不友好，灰度下失效 |
| 只靠颜色区分类别 | 必须同时使用线型、marker、形状、框线或编号标签 |
| 过多高饱和颜色 | 抢夺视觉注意力，削弱重点信息 |
| 深色/复杂背景 | 显著降低专业感和可读性 |
| 同组数据频繁变换颜色语义 | 严重破坏图的可理解性 |
| 不做灰度检查 | 很多彩色图转黑白后完全失效 |
| `#999999`/`#CCCCCC`/`#EEEEEE` 浅灰 | 印刷不清晰，低对比度 |
| 4 种以上不同色相 | 视觉混乱，学术感丧失 |
| 浅灰作为文字颜色 | 印刷后几乎不可读 |

---

## 3. 按图形类型选色

> **设计工作流原则**：
> 1. **先定结构，再定颜色** — 先确定图的骨架（节点/层/流程/轴），确认逻辑无误后再选色；不要边画边选色
> 2. **先判断数据类型** — 进入数据图配色前，必须先分类：连续数据？发散数据？分类比较？三类对应三种截然不同的色板

### 3.1 示意图 / 原理图 / 流程图

**配色目标**：突出模块关系、表达流程方向、强调关键节点、建立视觉层次。

| 角色 | 颜色 |
|---|---|
| 中性底色 | 白（禁用浅灰作底色） |
| 轮廓 / 文字 | 黑 `#111827` / 深灰 `#374151` |
| 主流程 / 主路径 | 蓝 `#0072B2` |
| 次级步骤 | 橙 `#E69F00` |
| 辅助模块 | 绿 `#009E73` / 紫 `#CC79A7` |
| 警示 / 抑制 | 红 `#D55E00`（不大面积使用） |

**颜色上限**：示意图/原理图总色相数 ≤ 5（含背景和文字色）；超出时先合并同类再选色。

**常见错误**：模块颜色过多像商业海报；颜色过亮显得不学术；不同面板颜色不统一；只靠颜色无箭头辅助。

**主题参考**：见 `color-palettes.json` → `themes.schematic_general` / `engineering_schematic` / `biomedical_mechanism`

### 3.2 曲线图 / 数据图

**配色目标**：区分数据系列、保持趋势可读、图例简单清楚、黑白色盲环境可识别。

**步骤 1：先判断数据类型**

| 数据类型 | 判断标准 | 色板类型 | 参考 |
|---|---|---|---|
| 连续数据（强度/趋势） | 数值有自然大小顺序，如热图、置信度 | 顺序色板（单色相由浅到深） | `themes.continuous_data` |
| 正负偏差 / 相关性 | 数值有正负含义，0 为自然中心 | 发散色板（双端对称，中间白/灰） | `themes.diverging_data` |
| 分类比较 | 各类别无自然顺序关系 | 定性色板（彼此差异明显） | `themes.categorical_comparison` / `themes.line_chart_general` |

**步骤 2：按类型选色，注意上限**

- 优先 2–4 色；多组图最多 6–8 色
- 多条曲线结合线型、marker、透明度编码
- **灰度验证**：配色完成后，用 `desaturate(color, 0)` 将所有颜色转灰度，检查各系列在灰度下仍可区分（亮度差 ≥ 30）；否则用线型/marker 补充区分
- 不使用 rainbow 色带

### 3.3 领域专用配色主题

从 `color-palettes.json` 选对应主题，不要跨主题混用：

| 领域 | 主题键 | 特点 |
|---|---|---|
| 通用示意图 / 工程 | `themes.schematic_general` | 黑 + 蓝 + 橙 三色核心 |
| 生物医学 / 机制图 | `themes.biomedical_mechanism` | 暖色调，紫红强调，绿色辅助 |
| 工程系统 / 流程图 | `themes.engineering_schematic` | 深蓝主，冷色调，对比清晰 |
| 算法 / 计算 / 深度学习 | `themes.algorithm_computation` | 紫 + 青 + 橙，强调计算层次 |
| 环境 / 生态 / 地理 | `themes.environment_ecology` | 绿色主，蓝辅，地球感 |
| 化学 / 分子 / 材料 | `themes.chemistry_molecular` | 暖橙 + 蓝 + 灰，元素感 |
| 连续数据热图 | `themes.continuous_data` | 蓝→白→红 或 白→蓝 顺序色 |
| 发散数据 | `themes.diverging_data` | 红←白→蓝，零点居中 |
| 分类比较 | `themes.categorical_comparison` | 最多 8 色，色盲友好 |

---

## 4. TikZ 推荐色板

### 方案 A：IEEE/Springer（多数工科论文首选）

```latex
\definecolor{colPrimary}{RGB}{31,73,125}    % IEEE 深蓝
\definecolor{colSecondary}{RGB}{64,64,64}   % 深灰
\definecolor{colArrow}{RGB}{30,30,30}       % 近黑（箭头）
\definecolor{colBeam}{RGB}{31,73,125}       % 发射波束（与主色一致）
\definecolor{colEcho}{RGB}{90,90,90}        % 回波（深灰，提高可读性）
```

```python
# Python 等效
BLUE_IEEE = "#1F497D"
GRAY_DARK  = "#3D3D3D"
```

### 方案 B：灰度系（黑白印刷优先）

```latex
\definecolor{colDark}{HTML}{333333}
\definecolor{colMid}{HTML}{666666}
\definecolor{colLight}{HTML}{999999}   % 注意：仅用于辅助元素，禁用于文字
```

### 方案 C：Nature 低饱和（生物/材料/综合类期刊）

```latex
\definecolor{clrGreen}{HTML}{8FBCB2}   % 灰绿
\definecolor{clrBlue} {HTML}{8AAAC8}   % 灰蓝
\definecolor{clrPurple}{HTML}{A99DC4}  % 灰紫
\definecolor{clrWarm} {HTML}{C8AD8A}   % 灰暖
```

```python
# Python 等效
NATURE_GREEN  = "#8FBCB2"
NATURE_BLUE   = "#8AAAC8"
NATURE_PURPLE = "#A99DC4"
NATURE_WARM   = "#C8AD8A"
```

### 方案 D：双色强调对比

```latex
\definecolor{colMain}{HTML}{2E86AB}    % 冷蓝
\definecolor{colAccent}{HTML}{A23B72}  % 玫红
```

### 方案 E：同心圆防御层专用（蓝/黄/红三层）

```latex
\definecolor{LayerBlueFill}{HTML}{DBEAFE}
\definecolor{LayerBlueDraw}{HTML}{1D4ED8}
\definecolor{LayerAmberFill}{HTML}{FEF3C7}
\definecolor{LayerAmberDraw}{HTML}{D97706}
\definecolor{LayerRedFill}{HTML}{FEE2E2}
\definecolor{LayerRedDraw}{HTML}{DC2626}
```

### 方案 F：顶刊通用定性色（色盲友好，推荐优先使用）

```latex
\definecolor{clrBlue}   {HTML}{0072B2}
\definecolor{clrOrange} {HTML}{E69F00}
\definecolor{clrGreen2} {HTML}{009E73}
\definecolor{clrPurple2}{HTML}{CC79A7}
\definecolor{clrRed2}   {HTML}{D55E00}
\definecolor{clrSkyBlue}{HTML}{56B4E9}
```

> **选色原则**：方案 F 色盲友好、顶刊经过验证，默认优先。方案 A 适合国内工科标准，方案 C 适合综合/材料类期刊。

---

## 5. Python 共享色板（`figures/color_palette.py`）

```python
# figures/color_palette.py
# ── 主色（数据系列）──
BLUE   = "#1D4ED8"
RED    = "#DC2626"
GREEN  = "#16A34A"
AMBER  = "#F59E0B"
PURPLE = "#7C3AED"
TEAL   = "#0891B2"

PALETTE = [BLUE, RED, GREEN, AMBER, PURPLE, TEAL]

# ── 填充色（浅色半透明）──
BLUE_FILL   = "#DBEAFE"
RED_FILL    = "#FEE2E2"
GREEN_FILL  = "#D1FAE5"
AMBER_FILL  = "#FEF3C7"
PURPLE_FILL = "#EDE9FE"
TEAL_FILL   = "#CFFAFE"

# ── 中性色 ──
BLACK      = "#111827"
DARK_GRAY  = "#374151"
MID_GRAY   = "#6B7280"
LIGHT_GRAY = "#D1D5DB"   # 仅用于边框/网格，禁用于文字
WHITE      = "#FFFFFF"

# ── 网格/边框 ──
GRID_COLOR  = BLACK
GRID_ALPHA  = 0.12
SPINE_COLOR = BLACK
SPINE_WIDTH = 2.0

# ── 文字 ──
TEXT_COLOR = BLACK
```

> **注**：需要顶刊色盲友好色时，直接用 `color-palettes.json` → `qualitative` 中的颜色值替换 `PALETTE`。

---

## 6. 标注文字配色规范

```
规则：标注文字颜色 = 对应图形元素颜色

✅ 正确：
  蓝色箭头 + 蓝色标注文字
  红色圆环 + 红色标注文字

❌ 禁止：
  蓝色箭头 + 黑色/灰色标注文字（视觉割裂）
  所有标注统一用黑色（失去层次感）
```

扇形图外侧标签：颜色 = 对应扇区颜色；扇区内文字：白色。

---

## 7. Python 降饱和工具

```python
import matplotlib.colors as mc
import colorsys

def desaturate(hex_color, factor=0.6):
    """降低颜色饱和度。factor=1 原色，factor=0 灰色。"""
    rgb = mc.to_rgb(hex_color)
    h, l, s = colorsys.rgb_to_hls(*rgb)
    return colorsys.hls_to_rgb(h, l, s * factor)

# Nature 风格基础色 → 降饱和后使用
BASE_PALETTE = {
    'blue':   '#4878CF',
    'green':  '#6ACC65',
    'red':    '#D65F5F',
    'purple': '#B47CC7',
    'gold':   '#C4AD66',
}
COLORS_DESATURATED = {k: desaturate(v, 0.6) for k, v in BASE_PALETTE.items()}
```

---

## 8. SVG 颜色验证

```bash
# SVG 用 rgb(百分比%) 存色，不能用 hex grep！
grep "rgb(" figure.svg | head -10
grep -c "fill\|stroke" figure.svg    # 统计颜色节点数
```

---

## 8.5 灰度验证步骤（导出前必做）

```python
import matplotlib.colors as mc

def to_grayscale_luminance(hex_color):
    """返回 0–100 的灰度亮度值。相邻系列差值 ≥ 30 才可打印区分。"""
    r, g, b = mc.to_rgb(hex_color)
    # ITU-R BT.601 加权灰度
    return round((0.299*r + 0.587*g + 0.114*b) * 100, 1)

# 用法：检查数据图各系列颜色
palette = ["#0072B2", "#E69F00", "#009E73", "#D55E00"]
grays = [to_grayscale_luminance(c) for c in palette]
print(grays)   # 例：[27.3, 64.8, 44.2, 36.1]
# 相邻两值差 < 30 → 该组合黑白印刷失效，需改色或加线型/marker 补充区分
```

> **验证通过标准**：所有数据系列亮度差 ≥ 30，或通过线型/marker 辅助区分后免检。

---

## 9. 禁止色速查表

| 颜色 | 禁止原因 |
|---|---|
| `#999999` / `#CCCCCC` / `#EEEEEE` | 印刷不清晰，低对比度 |
| `#FF0000` / `#00FF00` / `#0000FF` | 过于刺眼，非学术风格 |
| rainbow / jet 色带 | 制造虚假视觉边界 |
| 荧光色 / 过饱和色 | 不可出版，印刷失真 |
| 示意图超过 5 色相 / 数据图超过 4 色相 | 视觉混乱，学术感丧失 |
| 浅灰作为文字颜色 | 印刷后几乎不可读 |
| 红绿唯一对比 | 色盲不友好，灰度下失效 |
