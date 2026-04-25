# Scientific Drawing Skill

学术论文科学绘图技能。适用于创建所有类型的学术图表，包含 TikZ/matplotlib 完整规则与配色方案。

## 目录

* [功能概述](#功能概述)
* [核心约束](#0-核心约束不可违反)
* [技术决策树](#1-技术决策树)
* [配色原则](#2-配色原则)
* [TikZ 绘图规范](#3-tikz-绘图规范)
* [matplotlib 绘图规范](#4-matplotlib-绘图规范)
* [多Agent 审查工作流](#5-多agent-审查工作流)
* [参考文件索引](#6-参考文件索引)
* [环境依赖](#7-环境依赖)
* [安装与兼容性](#8-安装与兼容性)
* [仓库结构](#9-仓库结构)

---

## 功能概述

本技能适用于创建以下类型的学术图表：

| 图表类型 | 技术栈 | 说明 |
|----------|--------|------|
| 架构图、流程图、示意图、原理图、机制图 | TikZ (xelatex) | 矢量图，精确控制 |
| 扇形图、同心圆图、网络拓扑图 | TikZ (xelatex) | 复杂布局支持 |
| 曲线图、折线图、散点图、热图、雷达图、柱状图 | Python matplotlib | 数据可视化 |
| 算法伪代码 | LaTeX algorithm2e | 学术规范格式 |

---

## 0. 核心约束（不可违反）

| 约束 | 规范 | 违规后果 |
|------|------|----------|
| **字体大小** | 正文字体小四（12pt）= `\normalsize` (TikZ) = `font.size=13` (matplotlib) | 禁止 `\small` 、 `\footnotesize` |
| **留白** | standalone border `10–15pt` ；matplotlib `bbox_inches="tight"` | 过大/过小/被裁剪 |
| **遮挡** | 所有内容不得遮挡；文字与圆弧/节点严格分离 | 最高优先级，任意一项 ✗ 即 FAIL |
| **配色** | 顶刊克制风；示意图 ≤ 5 色相，数据图 ≤ 3–4 色相 | 禁止浅灰、rainbow、纯原色 |
| **编译器** | TikZ 必须 **xelatex**（禁用 pdflatex） | 中文/特殊符号乱码 |
| **输出格式** | matplotlib 始终输出 SVG；TikZ 输出 PDF → 导出 SVG | 位图分辨率损失 |

---

## 1. 技术决策树

```
需要画什么？
│
├─ 示意图 / 原理图 / 机制图 / 架构图 / 流程图 / 网络拓扑图 / 扇形图 / 同心圆
│   └─→ TikZ（xelatex 编译）
│
├─ 数据图：曲线、折线、散点、热图、雷达、柱状、ROC
│   └─→ Python matplotlib
│
└─ 算法伪代码
    └─→ LaTeX article + algorithm2e
```

---

## 2. 配色原则

### 2.1 核心规则

| 规则 | 说明 |
|------|------|
| **信息优先** | 配色服务于结构、层级、分类和趋势；不添加无意义的渐变、阴影、3D 效果 |
| **少色原则** | 示意图 ≤ 5 色；曲线图 2–4 色；多组最多 6–8 色但必须配合线型/marker |
| **饱和度** | 低饱和（HSL 饱和度 20–40%）；避免纯 RGB 原色 |
| **一致性** | 同一论文中相同对象/变量必须使用相同颜色语义 |
| **可读性** | 灰度打印可区分；色盲可区分；缩小到版面后仍清晰 |

### 2.2 禁止事项

| 禁止 | 原因 |
|------|------|
| rainbow / jet 色带 | 制造虚假视觉边界，误导连续数据读者 |
| `#999999` / `#CCCCCC` / `#EEEEEE` | 印刷不清晰，低对比度 |
| 纯原色 `#FF0000` 、 `#00FF00` 、 `#0000FF` | 过于刺眼，非学术风格 |
| 红绿唯一对比 | 色盲不友好，灰度下失效 |
| 4+ 色相混用（示意图） | 视觉混乱，学术感丧失 |
| 浅灰作为文字颜色 | 印刷后几乎不可读 |

### 2.3 推荐配色方案

#### 方案 A：IEEE/Springer（工科论文首选）

```latex
\definecolor{colPrimary}{RGB}{31,73,125}    % IEEE 深蓝
\definecolor{colSecondary}{RGB}{64,64,64}   % 深灰
\definecolor{colArrow}{RGB}{30,30,30}       % 近黑箭头
```

#### 方案 B：顶刊通用定性色（色盲友好，推荐优先）

```latex
\definecolor{clrBlue}   {HTML}{0072B2}
\definecolor{clrOrange} {HTML}{E69F00}
\definecolor{clrGreen2}{HTML}{009E73}
\definecolor{clrPurple2}{HTML}{CC79A7}
\definecolor{clrRed2}   {HTML}{D55E00}
\definecolor{clrSkyBlue}{HTML}{56B4E9}
```

#### 方案 C：Nature 低饱和（生物/材料/综合类期刊）

```latex
\definecolor{clrGreen}{HTML}{8FBCB2}    % 灰绿
\definecolor{clrBlue} {HTML}{8AAAC8}    % 灰蓝
\definecolor{clrPurple}{HTML}{A99DC4}   % 灰紫
\definecolor{clrWarm} {HTML}{C8AD8A}     % 灰暖
```

#### 方案 D：同心圆防御层专用（蓝/黄/红三层）

```latex
\definecolor{LayerBlueFill}{HTML}{DBEAFE}
\definecolor{LayerBlueDraw}{HTML}{1D4ED8}
\definecolor{LayerAmberFill}{HTML}{FEF3C7}
\definecolor{LayerAmberDraw}{HTML}{D97706}
\definecolor{LayerRedFill}{HTML}{FEE2E2}
\definecolor{LayerRedDraw}{HTML}{DC2626}
```

### 2.4 按图形类型选色

| 图形类型 | 配色目标 | 推荐色板 |
|----------|----------|----------|
| 示意图 / 原理图 / 流程图 | 突出模块关系、表达流程方向 | `schemes.schematic_general` |
| 生物医学 / 机制图 | 暖色调，紫红强调，绿色辅助 | `schemes.biomedical_mechanism` |
| 算法 / 计算 / 深度学习 | 紫 + 青 + 橙，强调计算层次 | `schemes.algorithm_computation` |
| 连续数据（热图） | 单色相由浅到深 | `schemes.continuous_data` |
| 发散数据（正负偏差） | 双端对称，中间白/灰 | `schemes.diverging_data` |
| 分类比较 | 彼此差异明显，色盲友好 | `schemes.categorical_comparison` |

### 2.5 标注文字配色

```
规则：标注文字颜色 = 对应图形元素颜色

✅ 正确：蓝色箭头 + 蓝色标注文字
        红色圆环 + 红色标注文字
❌ 禁止：蓝色箭头 + 黑色标注文字（视觉割裂）
```

---

## 3. TikZ 绘图规范

### 3.1 必须包含的 Preamble

```latex
\documentclass[border={15pt 10pt 10pt 10pt}]{standalone}
% border 顺序：left bottom right top（非 CSS 顺序！）
\usepackage{xeCJK}
\setCJKmainfont{PingFang SC}
\usepackage{tikz}
\usetikzlibrary{positioning, shapes.geometric, arrows.meta, fit, calc, backgrounds}
\usepackage{xcolor}
```

### 3.2 编译与导出流程

```bash
# 1. 新建 figures/子目录/fig.tex
# 2. 编译
cd figures/子目录/ && xelatex -interaction=nonstopmode fig.tex

# 3. 预览 PNG（200 DPI）
pdftoppm -r 200 -png fig.pdf fig_preview && mv fig_preview-1.png fig.png

# 4. 确认无遮挡后导出 SVG
pdftocairo -svg fig.pdf fig.svg

# 5. 清理中间文件
rm -f *.aux *.log *.fls *.fdb_latexmk fig_preview*.png
```

### 3.3 字体规范

| 用途 | TikZ 命令 | 大小 |
|------|-----------|------|
| 正文章内文字 | `\normalsize` 或留空 | 12pt（小四） |
| 节点内文字 | `\normalsize` | 12pt |
| 标注文字 | `\normalsize` 或 `\small` （仅标注） | 12pt |
| 禁止使用 | `\small` 、 `\footnotesize` 、 `\tiny` | — |

---

## 4. matplotlib 绘图规范

### 4.1 文件头部模板

```python
import matplotlib.pyplot as plt
import matplotlib.font_manager as _fm
import os, sys

# TODO: 修改为你的中文字体路径
_SANS_PATH = "/Users/sunyue/Library/Fonts/SourceHanSansCN-Regular.ttf"
_fm.fontManager.addfont(_SANS_PATH)  # 必须在 rcParams 之前

plt.rcParams['font.family']        = 'sans-serif'
plt.rcParams['font.sans-serif']    = ['Source Han Sans CN', 'PingFang SC', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size']          = 13       # 小四 ≈ 13pt（正文对齐）
plt.rcParams['axes.titlesize']     = 20
plt.rcParams['axes.labelsize']     = 16
plt.rcParams['xtick.labelsize']    = 13
plt.rcParams['ytick.labelsize']    = 13
plt.rcParams['legend.fontsize']    = 13
plt.rcParams['figure.dpi']         = 150

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_SCRIPT_DIR, ".."))
from color_palette import BLUE, RED, BLACK, GRID_COLOR, GRID_ALPHA, SPINE_COLOR, SPINE_WIDTH
```

### 4.2 axes 标准样式

```python
ax.spines[["top", "right"]].set_visible(False)
for sp in ["left", "bottom"]:
    ax.spines[sp].set_color(SPINE_COLOR)
    ax.spines[sp].set_linewidth(SPINE_WIDTH)
ax.tick_params(axis="both", width=2.0, length=6, colors=BLACK, pad=5)
ax.grid(True, ls=":", lw=2.0, color=GRID_COLOR, alpha=GRID_ALPHA)
```

### 4.3 保存格式

```python
plt.tight_layout()
plt.savefig(os.path.join(_SCRIPT_DIR, "fig.svg"), format="svg", bbox_inches="tight")
```

### 4.4 Legend 规范

```python
# 禁止同时传 prop 和 fontsize
ax.legend(loc="upper right", frameon=True, framealpha=0.85,
          edgecolor=BLACK, prop={'size': 13})  # 只用 prop，不加 fontsize=
```

---

## 5. 多Agent 审查工作流

> **核心原则**：每张图必须经过独立审查 Agent 用 `look_at` 读取 PNG 并逐条确认通过，才算完成。主 Agent **禁止自审自查**。

### 5.1 Agent 分工

| Agent 角色 | 职责 | 允许工具 |
|------------|------|----------|
| **绘图 Agent** | 编写 .tex/.py、编译/运行、生成 PNG 预览 | Write, Edit, Bash, look_at |
| **审查 Agent** | 调用 `look_at` 读取 PNG，逐条核查检验清单 | look_at |
| **主 Agent** | 分发任务、接收结果、协调迭代；收到 PASS 后导出 SVG | Task, BackgroundTask |

### 5.2 审查检验清单

**每次 look_at 后逐条核查，输出 □✓ / □✗：**

```
【字体】
□ 所有文字是否清晰可读（与正文字号相当）？
□ 是否存在疑似 \small / \footnotesize 的过小字号？
□ 中文是否正常显示（无方块乱码）？

【遮挡】（最高优先级，任意一项 ✗ 即 FAIL）
□ 是否有文字压在圆弧/线条/节点边框上？
□ 是否有节点互相重叠（非刻意）？
□ 是否有箭头穿过文字或节点内容？
□ legend/图例是否遮挡关键数据区域？

【布局与留白】
□ 图形边距是否合适（standalone border 10–15pt）？
□ 各列/各行间距是否均匀？
□ 是否有内容超出图形边框被裁剪？

【配色】
□ 是否使用了浅灰（#999999 / #CCCCCC）？
□ 色相数量是否在限制内（示意图 ≤5，数据图 ≤4）？
□ 标注文字颜色是否与对应线条/元素保持一致？

【整体】
□ 图的信息是否清晰传达？
□ 图形整体是否对称/平衡？
```

### 5.3 执行流程

```
Step 1 ── 主 Agent 启动绘图 Agent → 生成 fig.png
Step 2 ── 主 Agent 启动审查 Agent → 逐条核查
Step 3 ── 若 PASS → 主 Agent 导出 SVG
          若 FAIL → 续接绘图 Agent 修改
Step 4 ── 续接审查 Agent 重新审查
Step 5 ── 重复 Step 4–5，最多 3 轮
Step 6 ── 超过 3 轮仍 FAIL → 主 Agent 介入判断是否需要架构重设计
```

---

## 6. 参考文件索引

| 文件 | 内容 | 何时读 |
|------|------|--------|
| `references/tikz-rules.md` | TikZ 布局与模板、多列布局、y 坐标管理、调试网格 | 多列布局 / 布局级 Bug |
| `references/elements.md` | 节点形状、箭头（fan-in/fan-out）、层标签、fit框、扇形图、同心圆 | 要素级绘制规则 |
| `references/matplotlib-rules.md` | 字体注册、legend、spines、输出、踩坑修复 | matplotlib 全面问题 |
| `references/color-standards.md` | 选色原则、图形类型选色、TikZ 色板、Python 降饱和工具 | 配色问题 |
| `references/color-palettes.json` | 具体 hex 值、主题色板数组 | 需要具体颜色时 |
| `references/compile-export.md` | 编译命令、PDF→SVG、macOS cairo 问题 | 编译/导出问题 |

---

## 7. 环境依赖

### 7.1 TikZ 依赖

| 依赖 | 版本要求 | 说明 |
|------|----------|------|
| **LaTeX 发行版** | TeX Live 2020+ / MacTeX 2020+ | 必须支持 xelatex |
| **xeCJK** | 最新版本 | 中文支持 |
| **fontspec** | 最新版本 | 字体配置 |
| **poppler-utils** | 最新版本 | pdftoppm、pdftocairo（PDF 转 PNG/SVG） |

**安装命令：**

```bash
# macOS (Homebrew)
brew install --cask mactex  # 或 smalltex
brew install poppler

# Ubuntu/Debian
sudo apt install texlive-xetex texlive-latex-extra poppler-utils

# Windows
# 安装 TeX Live 并勾选 xelatex 组件
```

**验证安装：**

```bash
xelatex --version
pdftocairo --version
```

### 7.2 Python matplotlib 依赖

| 依赖 | 版本要求 | 说明 |
|------|----------|------|
| **Python** | 3.8+ | — |
| **matplotlib** | 3.5+ | 绘图库 |
| **numpy** | 1.20+ | 数据处理（可选） |
| **pandas** | 1.3+ | 数据处理（可选） |

**安装命令：**

```bash
pip install matplotlib numpy pandas
```

### 7.3 中文字体

**必需字体：**
* `Source Han Sans CN`（思源黑体）或
* `PingFang SC`（macOS 系统字体）

**字体安装：**

```bash
# macOS
# 系统自带 PingFang SC，无需额外安装
# 如需思源黑体：
brew install font-source-han-sans-cn

# Linux (Ubuntu)
sudo apt install fonts-noto-cjk

# Windows
# 从 https://fonts.google.com/noto 使用 Noto Sans CJK
```

**字体路径配置（Python 脚本中）：**

```python
# 根据你的系统修改字体路径
_SANS_PATH = "/Users/sunyue/Library/Fonts/SourceHanSansCN-Regular.ttf"  # macOS
# _SANS_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"  # Linux
# _SANS_PATH = "C:/Windows/Fonts/SourceHanSansCN-Regular.ttf"  # Windows
```

### 7.4 可选工具

| 工具 | 用途 | 安装 |
|------|------|------|
| `latexmk` | 自动 LaTeX 编译 | TeX Live 自带 |
| `ImageMagick` | 图片转换 | `brew install imagemagick` |
| `Ghostscript` | PDF 处理 | `brew install ghostscript` |

### 7.5 依赖检查脚本

```bash
#!/bin/bash
# 检查所有依赖

echo "=== LaTeX ==="
xelatex --version | head -1

echo "=== Poppler ==="
pdftocairo --version | head -1

echo "=== Python ==="
python3 --version

echo "=== matplotlib ==="
python3 -c "import matplotlib; print(f'matplotlib {matplotlib.__version__}')"

echo "=== 字体检查 ==="
ls -la ~/Library/Fonts/SourceHanSansCN*.ttf 2>/dev/null || echo "Source Han Sans CN 未找到"
```

---

## 8. 安装与兼容性

### 8.1 OpenCode

**方式一：内置命令（推荐）**

```
/skill-from-github 9sunrise9/scientific-drawing
```

**方式二：通过 skill-creator**

```
/skill-creator
# 按照提示指向仓库 URL
```

### 8.2 Claude Code

**方式一：agent-skills-cli（推荐）**

```bash
npx agent-skills-cli add 9sunrise9/scientific-drawing --agent claude
```

**方式二：手动安装**

```bash
# Clone 到 Claude Code 的 skills 目录
git clone https://github.com/9sunrise9/scientific-drawing.git ~/.claude/skills/scientific-drawing
```

### 8.3 其他 AI 编码工具

**Cursor / VS Code / Copilot：**

```bash
npx agent-skills-cli add 9sunrise9/scientific-drawing
```

**手动安装：**

```bash
# 克隆到对应平台的 skills 目录
git clone https://github.com/9sunrise9/scientific-drawing.git ~/.cursor/skills/scientific-drawing
```

### 8.4 离线安装

如果无法访问 GitHub，可以下载 ZIP 包后手动安装：

```bash
# 下载并解压到 skills 目录
unzip scientific-drawing.zip -d ~/.claude/skills/scientific-drawing
```

### 8.5 安装验证

安装后，在项目中创建测试文件并验证：

```bash
# 创建测试目录
mkdir -p figures/test
cd figures/test

# 测试 matplotlib（如果已安装 Python 依赖）
python3 -c "
import matplotlib.pyplot as plt
plt.figure()
plt.plot([1,2,3],[1,2,3])
plt.savefig('test.svg')
print('matplotlib OK')
"

# 测试 LaTeX（如果已安装 LaTeX 依赖）
xelatex -interaction=nonstopmode -halt-on-error <<'EOF'
\documentclass[border=10pt]{standalone}
\usepackage{tikz}
\begin{document}
Hello World!
\end{document}
EOF
echo "LaTeX OK"
```

---

## 9. 仓库结构

```
scientific-drawing/
├── SKILL.md                    # OpenCode 版本（主）
├── README.md                   # 本文件
├── references/                 # 参考文档
│   ├── color-palettes.json    # 配色 JSON 参考库
│   ├── color-standards.md     # 配色规范
│   ├── compile-export.md      # 编译与导出
│   ├── elements.md            # 各要素绘制规则
│   ├── matplotlib-rules.md    # matplotlib 全规则
│   └── tikz-rules.md          # TikZ 布局与模板
└── claude/
    └── skills/
        └── scientific-drawing/
            └── SKILL.md       # Claude Code 兼容版本
```

### 双平台支持说明

| 平台 | SKILL.md 位置 | 参考文件路径 |
|------|---------------|-------------|
| OpenCode | `./SKILL.md` | `references/*` |
| Claude Code | `./claude/skills/scientific-drawing/SKILL.md` | `../../references/*` |

---

## 迭代流程

```bash
# 1. 本地修改后提交
git add .
git commit -m "描述你的修改"

# 2. 推送到 GitHub
git push

# 3. 其他环境重新安装
/skill-from-github 9sunrise9/scientific-drawing
```

---

## 致谢

本技能整合了以下来源的最佳实践：

* IEEE/Springer 配色标准
* Nature 色盲友好色板
* LaTeX TikZ 官方文档
* matplotlib 数据可视化规范

---

*最后更新：2026-04-25*
