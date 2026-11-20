---
name: ppt-svg-designer
description: 按 PowerPoint 模板批量制作可编辑 SVG 配图。用于要求复用参考页字体、颜色、分栏、图文版式或把 SVG 放入指定 PPT 页的任务，由 Agent 直接复制模板并编写 SVG。
---

# 按模板绘制 PowerPoint 配图

1. 对齐页码、参考页、图框位置、文案和交付形式。批量任务先列出每页的参考页、图意、版式和输出文件名。已有模板时复制参考页，保留母版、页眉页脚和图框外的元素。
2. 直接查看参考页与源素材。已有 SVG 时打开源码，复制最接近的分组、文字属性、边框和间距。PPTX 可用归档查看器或 `unzip -p` 读取原始部件。按 presentation.xml 的页面顺序及其关系定位幻灯片，再沿该页的 .rels 找到布局、母版、主题和嵌入的 SVG。以实际占位符和文本运行为准，缺省属性再查布局、母版和主题。只有截图时，按可见样式近似，并向用户说明哪些样式未经源文件确认。
3. 使用目标图框的尺寸。PowerPoint 的 1 cm 为 360000 EMU。无指定图框时采用 33.87 cm × 12.72 cm、白底和微软雅黑。用户指定字体优先，否则沿用模板明确指定的字体，中文缺省用 Microsoft YaHei。保持 viewBox 与图框等比。参考字号从 pt 换算为横向用户单位的公式为 `字号 × 2.54 / 72 × viewBox宽 / 图框宽(cm)`。
4. Agent 直接复制并编辑 SVG 标记。按图意选择下表中的源码，将标题、图元、连接关系和分组改为当前内容。每个逻辑模块用带 id 的 g 分组，文字保留 text/tspan。优先复制几何和文字属性，遇到图片、外部样式、滤镜或阴影时用基本图元与显式属性重绘。保留原始 SVG 作为可编辑交付件。
5. 逐图运行校验并渲染预览。检查中文字体替换、换行、裁切、箭头方向、文字重叠及与模板相邻文字的相对字号。结构校验只覆盖项目约定的静态 SVG 子集，几何与排版需查看预览。
6. 要求回填时，用演示文稿编辑器在模板副本中将 SVG 作为矢量图片插入目标图框，锁定宽高比并对齐原位置。重新打开副本核对页序、显示尺寸和模板其余元素。交付 PPTX 与对应 SVG 源文件，预览图按需附上。Python 仅限校验及预览。

## 可直接复制的源码

| 布局 | 文件（相对本目录） | 适用内容 |
|---|---|---|
| 左字右图 | [01-text-left.svg](assets/01-text-left.svg) | 概念与原理图 |
| 上字下图 | [02-text-top.svg](assets/02-text-top.svg) | 结论与示意曲线 |
| 双栏 | [03-two-columns.svg](assets/03-two-columns.svg) | 两种方法对照 |
| 三栏 | [04-three-columns.svg](assets/04-three-columns.svg) | 三个并列要点 |
| 两列两行 | [05-grid-2x2.svg](assets/05-grid-2x2.svg) | 四类信息 |
| 三列两行 | [06-grid-3x2.svg](assets/06-grid-3x2.svg) | 六个模块 |
| 横向流程 | [07-process.svg](assets/07-process.svg) | 顺序与里程碑 |
| 反馈闭环 | [08-feedback.svg](assets/08-feedback.svg) | 循环与改进 |
| 分层架构 | [09-layers.svg](assets/09-layers.svg) | 层级与职责 |

## 校验与预览

在技能目录运行以下命令。校验只依赖 Python 3 标准库。PNG 预览另需 PATH 中的 Inkscape 1.x，预览环境需有中文字体。

```sh
python3 scripts/check_svg.py assets/01-text-left.svg
python3 scripts/check_svg.py assets/01-text-left.svg --preview preview.png --width 1280
```
