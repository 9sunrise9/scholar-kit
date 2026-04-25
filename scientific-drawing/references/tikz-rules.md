# TikZ 布局与模板手册

布局原则、完整可运行模板、调试方法。各图形要素的绘制规则见 [elements.md](elements.md)。

---

## 1. 基础 preamble

```latex
\documentclass[border={15pt 10pt 10pt 10pt}]{standalone}
% border 顺序：left bottom right top（非 CSS 顺序！）
% 有左侧层标签时 left=15pt；无标签可用 border=10pt

\usepackage{xeCJK}
\setCJKmainfont{PingFang SC}
\usepackage{tikz}
\usetikzlibrary{positioning, shapes.geometric, arrows.meta, fit, calc, backgrounds}
\usepackage{xcolor}
```

---

## 2. 布局：多列对比图

**核心原则：全部用绝对坐标，禁止相对偏移叠加（累积漂移）。**

### 列间距计算公式

```
节点最大宽度 W ≈ 4.0cm，列间隙 G = 1.5cm
col1_x = 4.5   （左边距留给层标签）
col2_x = col1_x + W + G ≈ 10.0
col3_x = col2_x + W + G ≈ 15.5

分隔线 x = 左列右边界 + 间距/2
外框宽度 ≥ 最右列 x + 列宽/2 + 0.5cm
```

### 三列对比图模板

```latex
% ========== 参数设置区 ==========
% 列宽 W=4.0cm，列间距 G=1.5cm
% col1=4.5, col2=10.0, col3=15.5
% 外框: (0,0) rectangle (19.0, 9.0)

\begin{tikzpicture}[
  box/.style={draw, rectangle, rounded corners=4pt,
              minimum width=3.5cm, minimum height=0.9cm,
              align=center, font=\normalsize},
]
\draw[thick] (0,0) rectangle (19.0, 9.0);
\draw[dashed] (7.25, 0.2) -- (7.25, 8.8);     % 分隔线1
\draw[dashed] (13.75, 0.2) -- (13.75, 8.8);   % 分隔线2

\node[font=\bfseries\normalsize] at (3.5,  8.5) {集中式};
\node[font=\bfseries\normalsize] at (10.5, 8.5) {分布式};
\node[font=\bfseries\normalsize] at (17.0, 8.5) {混合式};

\node[box] (c1n1) at (3.5,  7.0) {节点A};
\node[box] (c2n1) at (10.5, 7.0) {节点A};
\node[box] (c3n1) at (17.0, 7.0) {节点A};
\end{tikzpicture}
```

---

## 3. 布局：纵向流程图（三列标准模板）

来自 `figures/nn_structure/nn_structure.tex`，完整可运行。

```latex
\documentclass[border={15pt 10pt 10pt 10pt}]{standalone}
\usepackage{xeCJK}
\setCJKmainfont{PingFang SC}
\usepackage{tikz}
\usetikzlibrary{positioning, shapes.geometric, arrows.meta, fit, calc, backgrounds}
\usepackage{xcolor}

\definecolor{blueinput}{HTML}{DBEAFE}
\definecolor{blueborder}{HTML}{1D4ED8}
\definecolor{purplefusion}{HTML}{EDE9FE}
\definecolor{purpleborder}{HTML}{7C3AED}
\definecolor{greenoutput}{HTML}{D1FAE5}
\definecolor{greenborder}{HTML}{065F46}
\definecolor{darkgray}{HTML}{374151}

\tikzset{
  arr/.style={-Stealth, thick, draw=darkgray},
  inputnode/.style={ellipse, fill=blueinput, draw=blueborder, thick,
      minimum width=3.6cm, minimum height=1.0cm, align=center, font=\normalsize},
  procnode/.style={rectangle, rounded corners=4pt,
      draw=blueborder!55, very thick, top color=white, bottom color=blueinput,
      minimum width=3.4cm, minimum height=0.9cm, align=center, font=\normalsize},
  featnode/.style={rectangle, rounded corners=4pt,
      draw=blueborder, thick, top color=white, bottom color=blueinput,
      minimum width=3.2cm, minimum height=0.9cm, align=center, font=\normalsize},
  fusionbox/.style={rectangle, rounded corners=4pt,
      fill=purplefusion, draw=purpleborder, very thick,
      minimum width=4.0cm, minimum height=1.0cm, align=center, font=\normalsize},
  outputnode/.style={ellipse, fill=greenoutput, draw=greenborder, thick,
      minimum width=3.4cm, minimum height=1.1cm, align=center, font=\normalsize},
  layerlabel/.style={font=\bfseries\normalsize, color=darkgray, align=center},
  branchlabel/.style={font=\bfseries\normalsize, color=darkgray},
}

\begin{document}
% Columns: left=4.5, center=10.0, right=15.5 (gap=5.5cm)
% Row spacing: 1.1cm between rows
% Layer labels: x=1.5（水平，无需旋转）

\begin{tikzpicture}

  % ── 层标签（水平放置）──
  \node[layerlabel] at (1.5,  0.0)   {输入层};
  \node[layerlabel] at (1.5, -1.85)  {特征提取层};
  \node[layerlabel] at (1.5, -3.7)   {特征层};
  \node[layerlabel] at (1.5, -6.2)   {融合层};
  \node[layerlabel] at (1.5, -10.3)  {输出层};

  % Row 1: 输入
  \node[inputnode] (in1) at (4.5,  0.0) {输入A};
  \node[inputnode] (in2) at (10.0, 0.0) {输入B};
  \node[inputnode] (in3) at (15.5, 0.0) {输入C};

  % Row 2: 特征提取
  \node[procnode, below=1.1cm of in1] (proc1) {特征提取1};
  \node[procnode, below=1.1cm of in2] (proc2) {特征提取2};
  \node[procnode, below=1.1cm of in3] (proc3) {特征提取3};

  % Row 3: 特征层
  \node[featnode, below=1.1cm of proc1] (feat1) {特征向量1};
  \node[featnode, below=1.1cm of proc2] (feat2) {特征向量2};
  \node[featnode, below=1.1cm of proc3] (feat3) {特征向量3};

  % Concat（绝对坐标）
  \node[fusionbox] (concat) at (10.0, -5.7) {特征拼接 Concat};
  \node[fusionbox, below=1.0cm of concat] (mlp) {MLP / Attention 融合};

  % 输出层（绝对坐标，距 mlp ≥ 2cm）
  \node[outputnode] (out1) at (4.5,  -10.3) {输出A};
  \node[outputnode] (out2) at (10.0, -10.3) {输出B};
  \node[outputnode] (out3) at (15.5, -10.3) {输出C};

  % 直连箭头
  \draw[arr] (in1)--(proc1); \draw[arr] (in2)--(proc2); \draw[arr] (in3)--(proc3);
  \draw[arr] (proc1)--(feat1); \draw[arr] (proc2)--(feat2); \draw[arr] (proc3)--(feat3);

  % 扇入
  \draw[arr] (feat1.south) -- ++(0,-0.35) -| (concat.north);
  \draw[arr] (feat2) -- (concat);
  \draw[arr] (feat3.south) -- ++(0,-0.35) -| (concat.north);
  \draw[arr] (concat) -- (mlp);

  % 扇出（折点 0.9cm，输出层距 mlp ≥ 2cm）
  \draw[arr] (mlp.south) -- ++(0,-0.9) -| (out1.north);
  \draw[arr] (mlp) -- (out2);
  \draw[arr] (mlp.south) -- ++(0,-0.9) -| (out3.north);

  % 背景 fit 框（必须在节点之后！）
  \begin{scope}[on background layer]
    \node[draw=blueborder!25, dashed, rounded corners=7pt, thick,
          fill=blue!3, fit=(in1)(proc1)(feat1), inner sep=8pt] (box1) {};
    \node[draw=blueborder!25, dashed, rounded corners=7pt, thick,
          fill=blue!3, fit=(in2)(proc2)(feat2), inner sep=8pt] (box2) {};
    \node[draw=blueborder!25, dashed, rounded corners=7pt, thick,
          fill=blue!3, fit=(in3)(proc3)(feat3), inner sep=8pt] (box3) {};
  \end{scope}
  \node[branchlabel, above=0.3cm of box1] {支路A};
  \node[branchlabel, above=0.3cm of box2] {支路B};
  \node[branchlabel, above=0.3cm of box3] {支路C};

\end{tikzpicture}
\end{document}
```

**关键参数：**

| 参数 | 值 | 说明 |
|---|---|---|
| 列 x | 4.5 / 10.0 / 15.5 | 列间距 5.5cm，左留 3cm 给层标签 |
| 行间距 | `below=1.1cm` | 同列统一用 `below=` 定位 |
| Concat y | −5.7 | 绝对坐标，低于 feat 约 1.6cm |
| 扇入折点 | `++(0,−0.35)` | 先下 0.35cm 再折向 Concat |
| 扇出折点 | `++(0,−0.9)` | 先下 0.9cm；输出层距 mlp ≥ 2.0cm |
| 左边距 | `border={15pt 10pt 10pt 10pt}` | 防层标签被裁剪 |

---

## 4. 布局：纵向坐标统一管理（分层架构图）

```latex
% ─── 简单流程图（单 y 值版本）───────────────────────────────
\def\ySensor{0}
\def\yDataFusion{2.8}    % 传感器层 → 数据融合层
\def\yFeatFusion{5.8}    % 数据融合 → 特征融合层
\def\yDecisFusion{8.8}   % 特征融合 → 决策融合层
\def\yOutput{11.5}       % 最终输出

% ─── 多级融合架构图（Low/High 双 y 值版本）────────────────
% 每层有两行：Low = 子节点行（多个并列节点）；High = 融合中心行（单个节点）
% fusion center to sub-nodes: 2.0（固定，保证融合中心容纳内容）
% 行间 Low 到下一层 Low 距离：4.0（= High - Low + 2.0）
\def\ySensor{0}
\def\yDataLow{2.8}       % 数据融合层：子节点 y（与传感器层相差 2.8）
\def\yDataHigh{4.8}      % 数据融合层：融合中心 y（= Low + 2.0）
\def\yFeatLow{6.8}       % 特征融合层：子节点 y（= DataHigh + 2.0）
\def\yFeatHigh{8.8}      % 特征融合层：融合中心 y（= FeatLow + 2.0）
\def\yDecisLow{10.8}     % 决策融合层：子节点 y
\def\yDecisHigh{12.8}    % 决策融合层：融合中心 y
\def\yOutput{15.0}       % 最终输出（= DecisHigh + 2.2）
```

**Low/High 命名规则**：
- `\yXxxLow` = 该层**子节点**行（水平排列的多个并列节点）
- `\yXxxHigh` = 该层**融合中心**行（在 Low 上方 2.0）
- 调整间距时只改 `\yXxxLow`，对应 `\yXxxHigh = \yXxxLow + 2.0`

---

## 4.1 背景 Band 样式速查表

| Band 类型 | 颜色 RGB | 十六进制 | 语义 |
|---|---|---|---|
| `databand` 数据融合 | `rgb,255:red,29;green,78;blue,216` | `#1D4ED8` 蓝 | 传感器/数据层 |
| `featband` 特征融合 | `rgb,255:red,124;green,58;blue,237` | `#7C3AED` 紫 | 特征提取/表示层 |
| `decisband` 决策融合 | `rgb,255:red,6;green,95;blue,70` | `#065F46` 绿 | 决策/输出层 |

**`rgb,255` 语法格式**：`draw={rgb,255:red,R;green,G;blue,B}` — 分号分隔三通道，整体放大括号内。

| 需求 | 样式参数 |
|---|---|
| 虚线框背景带（无填充） | `fill=none, dashed, line width=2pt` |
| 实线框融合中心 | `fill=white` 或 `fill={rgb,255:...}` 浅色，`line width=2pt`（无 dashed）|
| 前景节点在 band 上层 | band 放在 `\begin{scope}[on background layer]` 内 |
| band 覆盖所有子节点 | `minimum width ≥ 最右子节点 x - 最左子节点 x + 节点宽 + 1cm` |

調整间距时只改 `\def` 值，所有节点自动跟随。

---

## 5. 布局通用规则

| 场景 | 规则 |
|---|---|
| 多列对比图 | 全部绝对坐标；列 x 提前注释在文件顶部 |
| 纵向流程图 | 同列用 `below=Xcm of prev`；跨列汇聚节点用绝对坐标 |
| 分隔线 | x = 左列右边界 + 间距/2 |
| 外框 | 宽度 ≥ 最右列 x + 列宽/2 + 0.5cm |
| 层标签 | 水平放置，x 固定，y 取对应行节点 y |
| fit 框 | 必须在被包含节点之后定义 |

---

## 6. 调试网格与工作流

```latex
\begin{tikzpicture}
% 纵向流程图 y 为负，网格必须向下扩展
\draw[gray!30, very thin, step=0.5] (-1,-12) grid (20, 2);
\foreach \x in {0,1,...,20} \node[gray,font=\tiny] at (\x, 0) {\x};
\foreach \y in {-12,-11,...,2} \node[gray,font=\tiny] at (-0.5,\y) {\y};
% 正式内容 ...
\end{tikzpicture}
```

> 确认所有节点位置无误后删除网格。若节点全落在网格外（不可见），检查 y 范围是否未向下扩展。

**调试工作流原则（每次小改后都生成预览确认）**：

```bash
# 每次改动后立即执行预览，不攒多次改动再预览
xelatex -interaction=nonstopmode fig.tex \
  && pdftoppm -r 200 -png fig.pdf fig_preview \
  && open fig_preview-1.png

# 只有预览确认无误，才继续下一个修改点
# 不要连续改 5 处之后再预览 → 定位错误来源困难
```

**小改触发重编译的场景**：
- 移动一个节点坐标 → 马上确认其相邻节点/箭头无偏移
- 修改 `border=` 值 → 立即确认边距无裁剪
- 新增一条箭头 → 立即确认无遮挡/穿字

---

## 7. 布局坑速查

| 现象 | 根因 | 解法 |
|---|---|---|
| 相对坐标叠加漂移 | 多列用了 `+(x,y)` 相对定位 | 全部改绝对坐标 |
| 右列内容超出外框 | 外框宽度计算未含最右列 | `total_width = 最右列x + 列宽/2 + 0.5` |
| 分隔线与节点重叠 | 分隔线 x 未随 xshift 更新 | 重算：分隔线 x = 左列右边界 + 0.25 |
| 中文乱码/不显示 | 用了 pdflatex | 必须 `xelatex` |
| 调试网格看不到节点 | 纵向图 y 负，网格只覆盖正 y | 改为 `(-1,-12) grid (20,2)` |
| `backgrounds` 库未加载 | 忘记 `\usetikzlibrary{backgrounds}` | 加到 preamble |
