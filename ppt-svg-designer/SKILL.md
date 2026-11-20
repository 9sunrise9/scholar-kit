---
name: ppt-svg-designer
description: 按 PowerPoint 模板批量制作可编辑 SVG 配图。用于要求复用参考页字体、颜色、分栏、图文版式或把 SVG 放入指定 PPT 页的任务。Agent 查阅 catalog.json 选定版式，打开对应 SVG 文件并复制源码改写，不使用 Python 复制或生成图形。
---

# 按模板绘制 PowerPoint 配图

1. 对齐页码、参考页、图框位置、文案和交付形式。批量任务先列出每页的参考页、图意、版式和输出文件名。已有模板时复制参考页，保留母版、页眉页脚和图框外的元素。
2. 直接查看参考页与源素材。已有 SVG 时打开源码，复制最接近的分组、文字属性、边框和间距。PPTX 可用归档查看器或 `unzip -p` 读取原始部件。按 presentation.xml 的页面顺序及其关系定位幻灯片，再沿该页的 .rels 找到布局、母版、主题和嵌入的 SVG。以实际占位符和文本运行为准，缺省属性再查布局、母版和主题。只有截图时，按可见样式近似，并向用户说明哪些样式未经源文件确认。
3. 使用目标图框的尺寸。PowerPoint 的 1 cm 为 360000 EMU。无指定图框时采用 `catalog.json` 里 `defaults` 的 33.87 cm × 12.72 cm、白底和微软雅黑。用户指定字体优先，否则沿用模板明确指定的字体，中文缺省用 Microsoft YaHei。保持 viewBox 与图框等比。参考字号从 pt 换算为横向用户单位的公式为 `字号 × 2.54 / 72 × viewBox宽 / 图框宽(cm)`。
4. 打开本目录的 `catalog.json`。按图意选择 `when` 与 `name` 最匹配的一条版式，再打开该条目 `file` 指向的 SVG，复制其中的标记，改写标题、图元、连接关系和分组文字。每个逻辑模块用带 id 的 `g` 分组，文字保留 `text`/`tspan`。优先沿用几何和文字属性；遇到图片、外部样式、滤镜或阴影时，用基本图元与显式属性重绘。把结果直接写成 `.svg` 文件。不要编写脚本来复制、生成或变换模板。
5. 自行检查成品的中文字体、换行、裁切、箭头方向、文字重叠，以及与模板相邻文字的相对字号。几何与排版以看图为准。
6. 要求放入 PPTX 时，用演示文稿编辑器在模板副本中将 SVG 作为矢量图片插入目标图框，锁定宽高比并对齐原位置。重新打开副本核对页序、显示尺寸和模板其余元素。交付 PPTX 与对应 SVG 源文件；只有用户要求时才另附预览图。

## 版式索引

版式以 [`catalog.json`](catalog.json) 为准：先查表，再打开对应文件取源码。九个 id 与名称：

| id | 名称 |
|---|---|
| `text-left` | 左字右图 |
| `text-top` | 上字下图 |
| `two-columns` | 双栏 |
| `three-columns` | 三栏 |
| `grid-2x2` | 两列两行 |
| `grid-3x2` | 三列两行 |
| `process` | 横向流程 |
| `feedback` | 反馈闭环 |
| `layers` | 分层架构 |

## 样式库自测（可选，不用于制作配图）

`scripts/check_svg.py` 只供本仓库自测样式库，不参与配图制作。需要时在技能目录运行，且只依赖 Python 3 标准库。PNG 预览另需 PATH 中的 Inkscape 1.x，预览环境需有中文字体。

```sh
python3 scripts/check_svg.py assets/01-text-left.svg
python3 scripts/check_svg.py assets/01-text-left.svg --preview preview.png --width 1280
```
