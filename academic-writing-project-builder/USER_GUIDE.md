# 用户指南

## 功能

将 Markdown（内嵌 LaTeX 公式）转换为 docx / LaTeX，符合指定模版。

## 环境准备

### 必需

```bash
# pandoc
brew install pandoc

# python-docx（辅助分析模版）
pip install python-docx
```

### 可选

```bash
# watchdog（自动监控，推荐）
pip install watchdog

# fswatch（AppleScript 备选方案）
brew install fswatch
```

## 快速使用

### 1. 创建项目目录

```
项目根/
├── template.docx     ← 你的模版
├── docx_tex/figures/
├── md/figures/
└── script/
```

### 2. 编写 md 源文件

在 `md/` 目录下编写，遵守 Ulysses 写作规范：

- `#` 一级标题 → `Heading 1`
- `$$...$$` 行内公式 / `$$...$$` 独立公式块
- `![图注](figures/pic.png)` 图片
- `| 表头 |` 表格

### 3. 运行转换

```bash
bash script/convert.sh
```

### 4. 自动监控（可选）

```bash
# watchdog（推荐）
pip install watchdog
python3 script/watch.sh

# AppleScript（备选）
# 将 watch_folder.applescript 保存到 ~/Library/Scripts/Folder Action Scripts/
# 右键 md/ → 附加文件夹动作
```

## 与 AI Agent 协作

全程由 AI Agent 自动完成：

1. **分析模版** — 读取样式定义
2. **生成脚本** — convert.sh + 辅助脚本
3. **执行转换** — pandoc 转 docx/tex
4. **审查迭代** — AI 审查 Agent 检查格式，最多 3 轮

用户只需提供模版和 md 源文件。
