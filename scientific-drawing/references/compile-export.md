# 编译与导出流程手册

本文档提炼自 `tikz-drawing-guide.md` 第十、十七节，包含 TikZ 编译、PDF 转换、清理、macOS 特殊问题。

---

## 1. TikZ 标准编译命令

```bash
# 必须 xelatex（支持中文 xeCJK，不可用 pdflatex）
cd figures/子目录/
xelatex -interaction=nonstopmode fig.tex

# 有交叉引用时编译两次
xelatex fig.tex && xelatex fig.tex

# latexmk 方式（自动重编译）
latexmk -xelatex -interaction=nonstopmode fig.tex
```

---

## 2. PDF → PNG 预览

```bash
# macOS 内置 pdftoppm（无需安装）
pdftoppm -r 200 -png fig.pdf fig_preview
mv fig_preview-1.png fig.png

# pdftocairo 方式（需 poppler）
pdftocairo -r 200 -png fig.pdf fig_preview
mv fig_preview-1.png fig.png
```

> 用于在 look_at 工具中确认节点位置和遮挡情况。分辨率 200 DPI 足够预览。

---

## 3. PDF → SVG（期刊投稿推荐）

```bash
# ✅ 推荐：pdftocairo（跨平台，质量好）
pdftocairo -svg fig.pdf fig.svg

# 备选：pdf2svg（macOS 需 homebrew）
pdf2svg fig.pdf fig.svg

# 备选：Inkscape
inkscape fig.pdf --export-filename=fig.svg

# 备选：ImageMagick
magick -density 200 fig.pdf fig.svg
```

---

## 4. 中间文件清理

```bash
# 保留 tex / pdf / svg，删除所有中间文件
rm -f *.aux *.log *.fls *.fdb_latexmk indent.log *.bak* fig_preview*.png

# 最终目录应只含：
# fig.tex    ← 源文件
# fig.pdf    ← 编译输出
# fig.svg    ← 矢量图（docx/LaTeX 嵌入用）
# fig.png    ← 可选预览图（低分辨率，不作为最终图）
```

---

## 5. 调试流程（每次改坐标后必走）

```bash
# 1. 编译
cd figures/defense_layers && xelatex -interaction=nonstopmode fig.tex

# 2. 生成预览 PNG
pdftoppm -png -r 150 fig.pdf fig_preview

# 3. 用 look_at 工具查看 → 确认无遮挡、位置正确

# 4. 确认后导出 SVG
pdftocairo -svg fig.pdf fig.svg

# 5. 清理
rm -f fig.{aux,log,fls,fdb_latexmk,bak*}
rm -f fig_preview*.png
```

> **重要**：不要连续多次修改而不验证，叠加误差会掩盖问题根因。每次小改后都生成预览确认。

---

## 6. macOS 特殊问题

### cairosvg 找不到 cairo 动态库

```bash
# 错误：OSError: cannot load library 'libcairo.2.dylib'
# 原因：macOS SIP 阻止自动加载 Homebrew 库

# 解法：命令前加 DYLD_LIBRARY_PATH
DYLD_LIBRARY_PATH=/opt/homebrew/lib python3 scripts/convert/md_to_docx.py 正文.md 正文.docx

# Python 中捕获需同时捕获两种异常
try:
    import cairosvg
except (ImportError, OSError):   # ← 必须同时捕获！
    cairosvg = None
```

### pdf2svg 命令路径

```bash
# Homebrew 安装
brew install pdf2svg

# 或直接用 pdftocairo（poppler 包含，更推荐）
brew install poppler
```

---

## 7. SVG 内容更新注意

```
只编译 .tex 而没有重新执行导出步骤 → SVG 内容不会更新

每次改 .tex 后：
  Step 1: xelatex fig.tex
  Step 2: pdftocairo -svg fig.pdf fig.svg   ← 两步都要跑！
```

---

## 8. SVG 颜色验证（防止颜色失真）

```bash
# SVG 用 rgb(百分比%) 存色，不能用 hex grep
grep "rgb(" figure.svg | head -10

# PDF 预览颜色可能失真（pdftoppm/ghostscript bug）
# 以 SVG grep 结果为权威，不信 PNG 预览截图的颜色
```

---

## 9. 算法伪代码专用流程

```bash
# 编译
xelatex -interaction=nonstopmode algXX_name.tex

# 裁白边
pdfcrop --margins 5 algXX_name.pdf algXX_name_crop.pdf
mv algXX_name_crop.pdf algXX_name.pdf

# 转 PNG（300 DPI，清晰印刷）
pdftoppm -r 300 -png algXX_name.pdf algXX_name
mv algXX_name-1.png algXX_name.png

# 清理
rm -f algXX_name.{aux,log,fls,fdb_latexmk}
```
