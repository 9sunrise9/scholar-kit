# Matplotlib 绘图完整规则手册

本文档提炼自 `tikz-drawing-guide.md` 第十三–二十一节，包含字体配置、颜色导入、图形输出、踩坑修复。

---

## 1. 标准文件头部模板（每个脚本复制此块）

```python
import matplotlib.pyplot as plt
import matplotlib.font_manager as _fm
import os, sys

# ── 字体路径（思源系列，本机路径）──
_SANS_PATH = "/Users/sunyue/Library/Fonts/SourceHanSansCN-Regular.ttf"
_SERIF_PATH = "/Users/sunyue/Library/Fonts/SourceHanSerifCN-Regular.ttf"

# ── 注册字体（必须在 rcParams 之前！）──
_fm.fontManager.addfont(_SANS_PATH)
_fm.fontManager.addfont(_SERIF_PATH)

# ── 全局 rcParams ──
plt.rcParams['font.family']        = 'sans-serif'
plt.rcParams['font.sans-serif']    = ['Source Han Sans CN', 'PingFang SC',
                                       'Heiti SC', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['font.serif']         = ['Source Han Serif CN', 'STSong',
                                       'SimSun', 'DejaVu Serif']
plt.rcParams['font.weight']        = 'normal'   # 不加粗
plt.rcParams['axes.unicode_minus'] = False       # 负号正常显示
plt.rcParams['text.usetex']        = False
plt.rcParams['mathtext.fontset']   = 'cm'        # Computer Modern 公式字体
plt.rcParams['figure.dpi']         = 150

# ── 字号（对应小四，与论文正文统一）──
plt.rcParams['font.size']          = 13
plt.rcParams['axes.titlesize']     = 20
plt.rcParams['axes.labelsize']     = 16
plt.rcParams['xtick.labelsize']    = 13
plt.rcParams['ytick.labelsize']    = 13
plt.rcParams['legend.fontsize']    = 13

# ── 脚本目录 & 颜色导入 ──
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_SCRIPT_DIR, ".."))   # 根据层级调整
from color_palette import (BLUE, RED, GREEN, AMBER, PURPLE, TEAL,
                            BLACK, DARK_GRAY, MID_GRAY,
                            GRID_COLOR, GRID_ALPHA, SPINE_COLOR, SPINE_WIDTH)
```

---

## 2. figsize 规范

| 场景 | figsize | 说明 |
|---|---|---|
| B5 单栏插图（标准） | `(9.5, 6.0)` | 最大宽度 12cm，不超出页面 |
| 宽幅双栏对比 | `(12.0, 5.0)` | 跨栏用，慎用 |
| 小图 / 子图 | `(6.0, 4.5)` | 行内小图 |

```python
fig, ax = plt.subplots(figsize=(9.5, 6.0))
```

---

## 3. Axes 标准样式（每个图必须）

```python
# 隐藏上/右边框
ax.spines[["top", "right"]].set_visible(False)

# 左/下边框样式
for spine in ["left", "bottom"]:
    ax.spines[spine].set_color(SPINE_COLOR)
    ax.spines[spine].set_linewidth(SPINE_WIDTH)   # SPINE_WIDTH=2.0

# 刻度样式
ax.tick_params(axis="both", which="major",
               width=2.0, length=6, colors=BLACK, pad=5)
ax.tick_params(axis="both", which="minor",
               width=2.0, length=4, colors=BLACK)

# 网格
ax.grid(True, ls=":", lw=2.0, color=GRID_COLOR, alpha=GRID_ALPHA, which="both")
```

---

## 4. Legend 规范

```python
# ✅ 正确：只用 prop={'size': N}
ax.legend(
    loc="upper right",
    frameon=True,
    framealpha=0.85,
    edgecolor=BLACK,
    handlelength=2.2,
    borderpad=0.5,
    prop={'size': 13},    # ← 唯一字体控制方式
)

# ❌ 禁止：同时传 prop 和 fontsize → duplicate keyword argument 报错
# ax.legend(prop=_fp_bold, fontsize=13, ...)
```

---

## 5. 输出规范

```python
# 始终输出 SVG，不输出 PNG（矢量，嵌入文档不失真）
plt.tight_layout()
plt.savefig(
    os.path.join(_SCRIPT_DIR, "output_name.svg"),
    format="svg",
    bbox_inches="tight",    # 防止内容被裁剪（同时控制留白）
)
print("✓ output_name.svg saved")
```

---

## 6. 颜色导入方式

```python
# 共享色板位于 figures/color_palette.py
import os, sys
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_SCRIPT_DIR, ".."))   # 调整层级
from color_palette import BLUE, RED, BLACK, GRID_COLOR, GRID_ALPHA, SPINE_COLOR, SPINE_WIDTH
```

**禁止**在脚本内硬编码颜色值（如 `'#1D4ED8'`），统一从 `color_palette.py` 导入。

---

## 7. 降饱和工具（Nature 风格）

```python
import matplotlib.colors as mc
import colorsys

def desaturate(hex_color, factor=0.6):
    """降低颜色饱和度。factor=1 原色，factor=0 灰色。"""
    rgb = mc.to_rgb(hex_color)
    h, l, s = colorsys.rgb_to_hls(*rgb)
    return colorsys.hls_to_rgb(h, l, s * factor)

# 用法
PALETTE = {
    'blue':   '#4878CF',
    'green':  '#6ACC65',
    'red':    '#D65F5F',
    'purple': '#B47CC7',
    'gold':   '#C4AD66',
}
colors = {k: desaturate(v, 0.6) for k, v in PALETTE.items()}
```

---

## 8. 踩坑修复表

| 坑 | 现象 | 解法 |
|---|---|---|
| `addfont` 未在 `rcParams` 前调用 | 中文显示为方块，回退 DejaVu | 调换顺序：`addfont` → `rcParams` |
| legend 同时传 `prop=` 和 `fontsize=` | `duplicate keyword argument` 报错 | 只保留 `prop={'size': N}` |
| 字体硬编码为 Bold 变体 | 字体加粗，与论文风格不符 | 改为 Regular，`font.weight='normal'` |
| `cairosvg` 报 `OSError: cannot load library 'libcairo'` | macOS SIP 阻止 Homebrew 库 | 命令前加 `DYLD_LIBRARY_PATH=/opt/homebrew/lib` |
| 图片宽度超出 B5 页面 | figsize 过大 | 上限 12cm → `figsize=(9.5, 6.0)` |
| 负号显示为方框 | `axes.unicode_minus` 未设置 | `plt.rcParams['axes.unicode_minus'] = False` |
| 上/右边框影响视觉 | 默认 4 边框 | `ax.spines[["top","right"]].set_visible(False)` |
| Python 中 cairo 异常未完全捕获 | 只捕获 `ImportError` | 改为 `except (ImportError, OSError):` |
