# 绘图要素经验手册

各类图形元素的绘制规则、参数公式、防坑指南。

---

## 1. 节点（Node）

### 1.1 形状选择

```latex
% ✅ 正确：rectangle + rounded corners（跨版本稳定）
\node[rectangle, rounded corners=4pt,
      minimum width=3cm, minimum height=0.9cm,
      align=center, font=\normalsize] ...

% ❌ 禁止：rounded rectangle（TikZ 版本差异导致尺寸异常、文字溢出）
\node[rounded rectangle, minimum width=3cm] ...
```

### 1.2 字体大小

```latex
% ✅ 与正文对齐（小四 = \normalsize ≈ 12pt）
inputnode/.style={..., font=\normalsize}

% ❌ 禁止（印刷后模糊不可读）
font=\small          % 9pt
font=\footnotesize   % 8pt
```

### 1.3 长文字节点

```latex
% 凡是长文字，必须加 text width + align，否则文字溢出边框
\node[text width=4.5cm, align=left] at (x, y) {长文字内容};
```

### 1.4 标注文字间距

```latex
% 用带距离的 above/below，不要裸用 above
\node[above=0.15cm of target_node] {标注文字};
% 或
\node at (x, y+0.3) {标注文字};
```

### 1.5 节点间最小安全间距

| 节点类型 | 相邻中心距 |
|---|---|
| 圆形（radius=r） | ≥ 2r + 0.3cm |
| 矩形（width=w） | ≥ w + 0.3cm |
| 标注文字到节点边缘 | ≥ 0.15cm |

### 1.6 常用节点样式组合

```latex
% 输入节点（椭圆）
inputnode/.style={
    ellipse, fill=blueinput, draw=blueborder, thick,
    minimum width=3.6cm, minimum height=1.0cm,
    align=center, font=\normalsize}

% 处理节点（圆角矩形，渐变）
procnode/.style={
    rectangle, rounded corners=4pt,
    draw=blueborder!55, very thick,
    top color=white, bottom color=blueinput,
    minimum width=3.4cm, minimum height=0.9cm,
    align=center, font=\normalsize}

% 融合/汇聚节点
fusionbox/.style={
    rectangle, rounded corners=4pt,
    fill=purplefusion, draw=purpleborder, very thick,
    minimum width=4.0cm, minimum height=1.0cm,
    align=center, font=\normalsize}

% 输出节点（椭圆）
outputnode/.style={
    ellipse, fill=greenoutput, draw=greenborder, thick,
    minimum width=3.4cm, minimum height=1.1cm,
    align=center, font=\normalsize}
```

---

## 2. 箭头与连接线

### 2.1 箭头样式定义

```latex
arr/.style={-Stealth, thick, draw=darkgray}

% 粗箭头（大图/雷达示意图）
arrow/.style={
    -{Stealth[length=12pt, width=10pt]},
    line width=3pt, color=colArrow}
```

### 2.2 折线符号速查

| 符号 | 含义 |
|---|---|
| `--` | 直线 |
| `-\|` | 先水平后垂直 |
| `\|-` | 先垂直后水平 |
| `++(dx,dy)` | 相对当前位置偏移后继续 |
| `-\|` + 绝对坐标 | 先水平到目标 x，再垂直到目标 y |

### 2.3 扇入箭头（多路 → 汇聚节点）

```latex
% 左/右侧支路先垂直下行再折向中央 Concat
\draw[arr] (feat_left.south)  -- ++(0,-0.35) -| (concat.north);
\draw[arr] (feat_center)      -- (concat);        % 中央直连
\draw[arr] (feat_right.south) -- ++(0,-0.35) -| (concat.north);

% ++(0,-0.35)：先下行 0.35cm 让折点低于节点底部即可
```

### 2.4 扇出箭头（汇聚节点 → 多路）

```latex
\draw[arr] (mlp.south) -- ++(0,-0.9) -| (out_left.north);
\draw[arr] (mlp)       -- (out_center);
\draw[arr] (mlp.south) -- ++(0,-0.9) -| (out_right.north);

% ⚠️ 关键坑：折点 0.9cm 必须低于所有输出节点 north 锚点
% 若输出层距 mlp < 2.0cm → 折线与节点 north 重合 → 箭头不可见
% 解法：增大两层间距至 ≥ 2.0cm
```

### 2.5 交叉虚线标注防重叠

```latex
% 两条虚线箭头交叉时，标注左右分置
% 左→右箭头：标注置于左侧（above left）
\draw[dashed, -Stealth, color=colBeam]
  (ant_tx) -- node[above left, font=\normalsize\bfseries,
                   text=colBeam, xshift=2pt, yshift=-16pt] {发射波束} (target);

% 右→左箭头：标注置于右侧（above right）
\draw[dashed, -Stealth, color=colEcho]
  (target) -- node[above right, font=\normalsize\bfseries,
                   text=colEcho, xshift=-2pt, yshift=-16pt] {回波信号} (ant_rx);

% 禁止两条都用 above 或都放同一侧
```

**yshift 参考：**

| yshift 值 | 视觉效果 |
|---|---|
| `yshift=4pt` | 紧贴箭头上方 |
| `yshift=-8pt` | 中部偏下 |
| `yshift=-16pt` | 靠近目标节点 |

---

## 3. 层标签（纵向流程图左侧）

```latex
% ✅ 水平放置，不旋转
layerlabel/.style={font=\bfseries\normalsize, color=darkgray, align=center}

\node[layerlabel] at (1.5,  0.0)   {输入层};
\node[layerlabel] at (1.5, -1.85)  {特征提取层};
\node[layerlabel] at (1.5, -3.7)   {特征层};
\node[layerlabel] at (1.5, -6.2)   {融合层};
\node[layerlabel] at (1.5, -10.3)  {输出层};

% 层标签 x = 固定值（比 col1_x 小 2–3cm）
% 层标签 y = 对应行代表节点的 y 坐标（直接从节点定义处取）

% ❌ 禁止 \rotatebox{90}：standalone 中竖排文字易被裁剪
```

必须在 preamble 加大左边距：`\documentclass[border={15pt 10pt 10pt 10pt}]{standalone}`

---

## 4. fit 包围框与背景层

### 4.1 定义顺序（必须）

```latex
% ✅ 正确：先定义节点，再定义 fit 框
\node (n1) at (x1, y1) {...};
\node (n2) at (x2, y2) {...};
\begin{scope}[on background layer]    % 必须加载 \usetikzlibrary{backgrounds}
    \node[draw=blueborder!25, dashed, rounded corners=7pt, thick,
          fill=blue!3, fit=(n1)(n2), inner sep=8pt] (box) {};
\end{scope}
\node[branchlabel, above=0.3cm of box] {标签};   % 标签在 scope 外定义

% ❌ 错误：fit 在被包含节点前定义 → 框尺寸为 0
```

### 4.2 fit 框重叠检查

各列中心 x 之差 ≥ fit 内最宽节点宽度 + inner sep×2 + 0.5cm

调整方法：减小 `inner sep`（从 `12pt` 改为 `8pt`），或增大列间距。

### 4.3 背景 Band（分层架构图）

```latex
% 无填充 + 虚线边框（背景层分隔带）
databand/.style={
    rectangle, rounded corners=6pt,
    fill=none, draw=colBlueDark,
    line width=2pt, dashed,
    minimum width=12cm, minimum height=2.2cm,
    text centered, align=center}

\begin{scope}[on background layer]
    \node[databand] (databand) at (0, 3.8) {};
\end{scope}
```

---

## 5. 扇形图

### 5.1 标准模板（环形扇形）

```latex
\def\R{3.0}   % 外径
\def\r{1.2}   % 内径（0 则为实心扇形）

\foreach \startA/\endA/\clr in {
  45/135/clrGreen, 135/225/clrBlue,
  225/315/clrPurple, 315/405/clrWarm
}{
  \fill[\clr]
    ({cos(\startA)*\r},{sin(\startA)*\r}) --
    ({cos(\startA)*\R},{sin(\startA)*\R})
    arc[start angle=\startA, end angle=\endA, radius=\R] --
    ({cos(\endA)*\r},{sin(\endA)*\r})
    arc[start angle=\endA, end angle=\startA, radius=\r, reverse] -- cycle;
}

% 细白分隔线（相邻扇形间加 1–1.5pt 白线，防粘连）
\foreach \ang in {45, 135, 225, 315}{
  \draw[white, line width=1.2pt]
    ({cos(\ang)*\r},{sin(\ang)*\r}) -- ({cos(\ang)*\R},{sin(\ang)*\R});
}
```

### 5.2 标签放置规则

```latex
% 外侧标签：颜色与扇区一致，位置在 R+间距 处
\node[color=clrGreen, font=\bfseries\normalsize]
  at ({cos(90)*(\R+0.6)},{sin(90)*(\R+0.6)}) {观察};

% 扇区内文字：白色，位置在环中心 (r+R)/2 处
\node[white, font=\normalsize]
  at ({cos(90)*(\r+(\R-\r)/2)},{sin(90)*(\r+(\R-\r)/2)}) {子文本};
```

### 5.3 arc 角度陷阱

```latex
% TikZ arc 默认逆时针：
%   end = start + θ  → 逆时针 θ°
%   end = start - θ  → 顺时针 θ°

% ⚠️ 常见错误：
%   start=-135, end=135  → 逆时针 270°（不是 90°！）

% 正确（逆时针 90°）：
arc[start angle=-135, end angle=-45, radius=\R]

% 正确（顺时针 90°）：
arc[start angle=-45, end angle=-135, radius=\R]  % 配合 clockwise 选项
```

---

## 6. 同心圆

### 6.1 绘制顺序（外→内，后绘覆盖前绘）

```latex
% 绘制步骤：外层 → 白色覆盖 → 中层 → 白色覆盖 → 内层
\fill[LayerBlueFill, draw=LayerBlueDraw, line width=1.5pt] (0,0) circle (\Rthree);
\fill[white] (0,0) circle (\Rtwo);
\fill[LayerAmberFill, draw=LayerAmberDraw, line width=1.5pt] (0,0) circle (\Rtwo);
\fill[white] (0,0) circle (\Rone);
\fill[LayerRedFill, draw=LayerRedDraw, line width=1.5pt] (0,0) circle (\Rone);
\fill[white] (0,0) circle (\Rcenter);
\fill[LayerRedFill, draw=LayerRedDraw, line width=1.5pt] (0,0) circle (\Rcenter);
```

### 6.2 层名 y 坐标公式

```
层名 y = (外半径 + 内半径) / 2，略偏内更安全

外蓝环 (5.0+3.5)/2 = 4.25  → 实际用 4.0
中黄环 (3.5+2.0)/2 = 2.75
内红环 (2.0+0.85)/2 ≈ 1.43 → 实际用 1.5

距离标注 y = -(外半径 + 0.15)
```

### 6.3 文字防遮挡原则

- 层名 y 坐标严格在圆环内侧（≥0.5cm 距圆弧）
- 技术项列表**不放圆内**，改用圆外独立色框 + 虚线连接
- 标注框加 `fill=white`，防止圆环穿过文字

```latex
% 圆外独立图例框
\node[draw=LayerBlueDraw, fill=LayerBlueFill, rounded corners=4pt,
      text=LayerBlueDraw, font=\bfseries\normalsize, align=left, inner sep=4pt]
  at (6.8, 4.8) {
    \begin{tabular}{l}
      远程预警层 \\ \hline
      长程雷达 \quad 频谱监测 \quad 通信干扰
    \end{tabular}};
\draw[LayerBlueDraw, thin, dashed] (6.1, 4.8) -- (5.5, 4.8);  % 虚线连到圆环

% 来袭箭头标注（带白色背景框，防被圆环穿过）
\node[draw=LayerRedDraw, fill=white, rounded corners=2pt,
      text=LayerRedDraw, font=\bfseries\normalsize, inner sep=2pt]
  at (8.0, 3.7) {无人机集群来袭};
```

### 6.4 完整防御层模板

```latex
\documentclass[border=10pt]{standalone}
\usepackage{xeCJK}
\setCJKmainfont{PingFang SC}
\usepackage{tikz}
\usetikzlibrary{positioning, shapes.geometric, arrows.meta, calc}
\usepackage{xcolor}

\definecolor{LayerRedFill}{HTML}{FEE2E2}
\definecolor{LayerRedDraw}{HTML}{DC2626}
\definecolor{LayerAmberFill}{HTML}{FEF3C7}
\definecolor{LayerAmberDraw}{HTML}{D97706}
\definecolor{LayerBlueFill}{HTML}{DBEAFE}
\definecolor{LayerBlueDraw}{HTML}{1D4ED8}

\begin{document}
\begin{tikzpicture}[font=\sffamily]
  \def\Rthree{5.0}
  \def\Rtwo{3.5}
  \def\Rone{2.0}
  \def\Rcenter{0.85}

  \fill[LayerBlueFill, draw=LayerBlueDraw, line width=1.5pt] (0,0) circle (\Rthree);
  \fill[white] (0,0) circle (\Rtwo);
  \fill[LayerAmberFill, draw=LayerAmberDraw, line width=1.5pt] (0,0) circle (\Rtwo);
  \fill[white] (0,0) circle (\Rone);
  \fill[LayerRedFill, draw=LayerRedDraw, line width=1.5pt] (0,0) circle (\Rone);
  \fill[white] (0,0) circle (\Rcenter);
  \fill[LayerRedFill, draw=LayerRedDraw, line width=1.5pt] (0,0) circle (\Rcenter);

  \node[color=LayerBlueDraw, font=\bfseries\normalsize] at (0, 4.0)  {远程预警与软杀伤层};
  \node[color=LayerAmberDraw, font=\bfseries\normalsize] at (0, 2.75) {中程机动防御层};
  \node[color=LayerRedDraw, font=\bfseries\normalsize]  at (0, 1.5)  {近程终端防御层};

  \node[color=LayerBlueDraw, font=\bfseries\normalsize]  at (0,-4.15) {3\;km+};
  \node[color=LayerAmberDraw, font=\bfseries\normalsize] at (0,-2.75) {1\textasciitilde 3\;km};
  \node[color=LayerRedDraw, font=\bfseries\normalsize]   at (0,-1.55) {0\textasciitilde 1\;km};

  \draw[-{Stealth[length=3mm,width=2mm]}, line width=1.3pt, draw=LayerRedDraw]
    (7.5, 3.2) -- (5.5, 2.7);
  \draw[-{Stealth[length=3mm,width=2mm]}, line width=1.3pt, draw=LayerRedDraw]
    (7.5, 0.0) -- (5.5, 0.0);
  \draw[-{Stealth[length=3mm,width=2mm]}, line width=1.3pt, draw=LayerRedDraw]
    (7.5,-2.8) -- (5.5,-2.5);
  \node[draw=LayerRedDraw, fill=white, rounded corners=2pt,
        text=LayerRedDraw, font=\bfseries\normalsize, inner sep=2pt]
    at (8.0, 3.7) {无人机集群来袭};

  \node[draw=LayerBlueDraw, fill=white, rounded corners=3pt,
        text=LayerBlueDraw, font=\bfseries\normalsize, inner sep=2pt]
    at (4.2, 3.5) {软杀伤};
  \node[draw=LayerRedDraw, fill=white, rounded corners=3pt,
        text=LayerRedDraw, font=\bfseries\normalsize, inner sep=2pt]
    at (3.2, 1.5) {硬杀伤};
\end{tikzpicture}
\end{document}
```

### 6.5 柔化边界：不透明度渐晕环

在圆环间绘制额外的半透明描边线，使层间边界更柔和、有渐变感：

```latex
% 在同心圆主绘制代码之后加入（与主圆使用相同颜色但降低不透明度）
\draw[LayerBlueDraw,  line width=0.8pt, opacity=0.4] (0,0) circle (\Rtwo);
\draw[LayerAmberDraw, line width=0.8pt, opacity=0.4] (0,0) circle (\Rone);

% 规则：
%   - opacity=0.4（40% 不透明）
%   - line width 比主圆描边细（主 1.5pt → 渐晕 0.8pt）
%   - 颜色与内侧圆相同，画在内侧圆上方形成渐晕效果
%   - 不使用 fill，只用 draw
```

### 6.6 中心图标（盾形/阵地标志）

```latex
% 放在同心圆绘制之后、层名标注之前
% shift=(0,0.06)：图标轻微上移；scale=0.7：缩小以适应 Rcenter 圆内
\begin{scope}[shift={(0,0.06)}, scale=0.7]
  % 盾形外轮廓
  \draw[LayerRedDraw, line width=1.5pt, fill=white]
    (0,0.75) -- (0.42,0.58) -- (0.48,0.05) -- (0,-0.55)
    -- (-0.48,0.05) -- (-0.42,0.58) -- cycle;
  % 盾面十字/标志（小三角）
  \draw[LayerRedDraw, line width=1.0pt]
    (-0.16,0.16) -- (0.16,0.16) -- (0,0.38) -- cycle;
  % 下方短横（阵地符号）
  \draw[LayerRedDraw, line width=1.0pt] (-0.10,-0.10) -- (0.10,0.10);
\end{scope}
% 图标下方文字标注
\node[align=center, text=LayerRedDraw, font=\bfseries\small] at (0,-0.95) {要地/阵地};

% 通用规则：
%   shift=(0, y_offset)：y_offset 约为圆形视觉重心偏移量，一般 0.03–0.10
%   scale：使图标宽度 ≤ 2*Rcenter - 0.1cm（确保不超出中心圆）
%   所有路径必须 fill=white 或与 Rcenter 圆填充一致，不遮挡中心圆边框
```

---

## 7. 分层架构图背景框

```latex
% 背景分隔带样式（虚线框，无填充）
% ⚠️ 边框颜色使用 rgb,255 语法指定精确 RGB 值
\tikzset{
  layerband/.style={
    rectangle, rounded corners=6pt,
    fill=none, draw=#1,
    line width=2pt, dashed,
    minimum width=12cm, minimum height=2.2cm,
    text centered, align=center},
}

% 具体使用：用 rgb,255:red,N;green,N;blue,N 语法传颜色
% 语法说明：rgb,255 → 0–255 分量；用分号隔开 r/g/b；整体放在 {} 中
\tikzset{
  databand/.style={layerband={rgb,255:red,29;green,78;blue,216}},   % 蓝 #1D4ED8
  featband/.style={layerband={rgb,255:red,124;green,58;blue,237}},  % 紫 #7C3AED
  decisband/.style={layerband={rgb,255:red,6;green,95;blue,70}},    % 绿 #065F46
}

% 融合中心样式（实线框，有填充）
% 填充色同样可用 rgb,255 语法
\tikzset{
  fusecenter/.style={
    rectangle, rounded corners=5pt,
    fill=white, line width=2pt,
    minimum width=3.5cm, minimum height=1.1cm,
    text centered, align=center},
}

% 具体节点：传入 fill 和 draw 两个 rgb,255 颜色
\node[fusecenter,
      fill={rgb,255:red,219;green,234;blue,254},
      draw={rgb,255:red,29;green,78;blue,216}]
  (fuse) at (0, 4.8) {\textbf{数据级融合中心}\\联合综合};
```

> **`rgb,255` 语法要点**：
> - 格式：`{rgb,255:red,R;green,G;blue,B}` — 注意 `rgb,255:` 前缀（不是逗号后空格）
> - 与 `\definecolor` 等效，但可直接内联在 `draw=`/`fill=` 选项中
> - 适用场景：每个样式需要不同颜色时（如 `databand`/`featband`/`decisband` 各自颜色），避免定义大量 `\definecolor`

```latex
% 纵向坐标统一用 \def 管理
\def\ySensor{0}
\def\yDataLow{2.8}       % 传感器行 → 数据融合行（子节点）
\def\yDataHigh{4.8}      % 数据融合中心 y
\def\yFeatLow{6.8}       % 特征融合子节点 y
\def\yFeatHigh{8.8}      % 特征融合中心 y
\def\yDecisLow{10.8}     % 决策融合子节点 y
\def\yDecisHigh{12.8}    % 决策融合中心 y
\def\yOutput{15.0}       % 最终输出行
```

**Low/High 对命名规则**：每层有两个 y 坐标 — `\yXxxLow` 是该层子节点行，`\yXxxHigh` 是融合中心行（约高 Low + 2.0）。

---

## 8. 分隔线与外框

```latex
% 分隔线 x = 左列右边界 + 间距/2
\draw[dashed] (x_divider, y_top) -- (x_divider, y_bottom);
% 确保：左列右边界 < x_divider < 右列左边界

% 外框
\draw[thick] (0, 0) rectangle (total_width, total_height);
% total_width ≥ 最右列 x + 列宽/2 + 0.5cm
```

---

## 9. 要素级坑速查

| 要素 | 现象 | 根因 | 解法 |
|---|---|---|---|
| **节点** | `rounded rectangle` 尺寸异常 | TikZ 版本差异 | 改用 `rectangle, rounded corners=4pt` |
| **节点** | 文字溢出边框 | 未设 `text width` | 加 `text width=Xcm, align=left` |
| **节点** | 字体印刷后偏小 | 用了 `\small`/`\footnotesize` | 改用 `\normalsize` |
| **箭头** | 扇出箭头不可见 | 输出层间距 < 2cm | 增大两层节点中心距至 ≥ 2.0cm |
| **箭头** | 两条交叉标注重叠 | 都用 `above` | 左箭头 `above left`，右箭头 `above right` |
| **标签** | 层标签被 standalone 裁剪 | 左边距不足 | `border={15pt 10pt 10pt 10pt}` |
| **标签** | 标注与线色视觉割裂 | 文字用黑色但线为蓝色 | 标注色与线色保持一致 |
| **fit框** | 框尺寸为 0 | fit 在节点前定义 | scope 必须在所有子节点之后 |
| **fit框** | 相邻 fit 框重叠 | 列间距不足 | 列间距 ≥ 最宽节点 + inner sep×2 + 0.5cm |
| **扇形** | arc 覆盖 270° 而非 90° | 终止角算错 | end = start + 90（逆时针 90°） |
| **同心圆** | 文字压在圆弧线上 | y = 圆半径 | y 用 (r_out+r_in)/2 公式，严格在环内 |
| **同心圆** | 技术文字堆叠不可辨 | 塞进圆内 | 改用圆外独立色框 + 虚线连接 |
| **同心圆** | 标注框被圆环穿过 | 无白色背景 | 加 `fill=white` 背景框 |

---

## 10. 雷达系统方块图模板

完整可运行模板，含参数化 `block/.style`、`arrow/.style`、双虚线交叉标注（`above left` / `above right`）。

```latex
\documentclass[border=20pt]{standalone}
\usepackage{xeCJK}
\setCJKmainfont{PingFang SC}
\usepackage{tikz}
\usetikzlibrary{arrows.meta, positioning}
\usepackage{xcolor}

% ── 颜色定义（IEEE 深蓝 + 深灰）──
\definecolor{colPrimary}{RGB}{31,73,125}   % IEEE 深蓝（发射链路）
\definecolor{colArrow}  {RGB}{30,30,30}    % 近黑（箭头）
\definecolor{colBeam}   {RGB}{31,73,125}   % 发射波束（同主色）
\definecolor{colEcho}   {RGB}{90,90,90}    % 回波信号（深灰）

% colTx = colPrimary（发射/接收链路蓝）
% colProc = colSecondary（处理链路深灰，可直接用 RGB 64,64,64）
\definecolor{colTx}  {RGB}{31,73,125}
\definecolor{colProc}{RGB}{64,64,64}

\begin{document}
\begin{tikzpicture}[
  % ── 参数化方块样式：block=<颜色> ──
  % draw=#1 → 边框色；fill=#1!10 → 10% 浅填充（自动与边框同色系）
  block/.style={
    rectangle, rounded corners=6pt,
    draw=#1, fill=#1!10, line width=2pt,
    text width=4.5cm, align=center,
    font=\Large\bfseries,
    minimum height=1.8cm, inner sep=12pt
  },
  arrow/.style={
    -{Stealth[length=12pt, width=10pt]},
    line width=3pt, color=colArrow
  },
]

% ── 发射链路（上方一行）──
\node[block=colTx]   (tx)     at (0,    4) {信号发生器\\(发射机)};
\node[block=colTx]   (ant_tx) at (6.5,  4) {发射天线};
\node[block=colTx]   (ant_rx) at (15.5, 4) {接收天线};
\node[block=colTx]   (rx)     at (22,   4) {接收机};
\node[block=colProc] (proc)   at (28.5, 4) {信号处理\\(目标检测)};

\draw[arrow] (tx) -- (ant_tx);
\draw[arrow] (ant_tx) -- node[above, font=\large\bfseries,
                              text=colArrow, yshift=5pt] {电磁波辐射} (ant_rx);
\draw[arrow] (ant_rx) -- (rx);
\draw[arrow] (rx) -- (proc);

% ── 目标节点（中间偏下）──
\node[block=colPrimary] (target) at (11, -1.5) {低空无人机集群\\(目标反射)};

% ── 交叉虚线：发射波束 + 回波信号（左右分置标注）──
\draw[dashed, arrow, color=colBeam]
  (ant_tx) -- node[above left,  font=\large\bfseries,
                   text=colBeam, xshift=2pt,  yshift=-16pt] {发射波束} (target);
\draw[dashed, arrow, color=colEcho]
  (target) -- node[above right, font=\large\bfseries,
                   text=colEcho, xshift=-2pt, yshift=-16pt] {回波信号} (ant_rx);

% ── 控制链路（下方）──
\node[block=colProc] (ctrl) at (14.25, -6.5) {系统控制与\\数据处理};
\draw[arrow] (proc.south)  |- (ctrl.east);
\draw[arrow] (ctrl.west)   -| (tx.south);

% ── 链路标注 ──
\node[font=\Large\bfseries, text=colTx,      anchor=south]
  at (ant_tx.north) [yshift=15pt] {发射链路};
\node[font=\Large\bfseries, text=colPrimary, anchor=north]
  at (target.south) [yshift=-15pt] {目标反射链路};
\node[font=\Large\bfseries, text=colProc,    anchor=north]
  at (ctrl.south)   [yshift=-15pt] {控制与处理链路};

\end{tikzpicture}
\end{document}
```

**关键技巧**：

| 要点 | 规则 |
|---|---|
| `block=<color>` | 用 `#1` 接收颜色参数；`fill=#1!10` 自动生成 10% 浅色填充 |
| 双虚线交叉标注 | 一条 `above left`，另一条 `above right`；颜色各自与线同色 |
| `yshift=-16pt` | 使标注靠近目标节点而非居中，避免两标注重叠 |
| 控制链路折线 | `|- ` 先水平后垂直；`-|` 先垂直后水平 |
| `colPrimary` vs `colTx` | 两者可共用同一深蓝值；`colTx` 标识发射链路语义 |
