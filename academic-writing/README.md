# academic-writing

学术 Markdown → docx / LaTeX 转换技能。使用 Markdown（内嵌 LaTeX 公式）撰写，通过 Pandoc 转换为符合模版的 docx 或 LaTeX 文档，全程由 AI Agent 协作生成、审查、迭代。

---

## 环境要求

### 必需

| 工具 | 版本 | 安装方式 |
|---|---|---|
| **pandoc** | ≥ 3.0 | `brew install pandoc` |
| **Python** | ≥ 3.9 | 系统自带或 `brew install python` |
| **docx 模版** | `.docx` | 用户提供，放项目根目录 |

### 可选（按需）

| 工具 | 用途 | 安装方式 |
|---|---|---|
| **watchdog** | 自动监控 md 变化 | `pip install watchdog` |
| **python-docx** | 辅助分析 docx 样式 | `pip install python-docx` |
| **fswatch** | macOS 文件监控（AppleScript 备选） | `brew install fswatch` |

> **注意**：Linux 用户用 `apt install inotify-tools` 替代 fswatch。Windows 用户建议使用 watchdog 方案。

---

## 快速开始

### 1. 创建项目目录结构

```bash
PROJECT_NAME="论文标题"
mkdir -p "${PROJECT_NAME}/docx_tex/figures" \
         "${PROJECT_NAME}/md/figures" \
         "${PROJECT_NAME}/script"
```

### 2. 放置模版

将你的 `.docx` 模版放入项目根目录：
```
项目根目录/
├── template.docx          ← 你的模版
├── docx_tex/
├── md/
└── script/
```

### 3. 编写 md 源文件

在 `md/` 目录下编写 Markdown 文件（见 §Ulysses 写作规范）。

### 4. 运行转换

```bash
cd 你的项目根目录
bash script/convert.sh
```

转换成功后在 `docx_tex/` 目录下生成 `.docx` 和 `.tex` 文件。

---

## 文件结构

```
项目根目录/
├── template.docx              ← 模版（用户提供）
├── docx_tex/                  ← 转换输出目录
│   ├── 论文标题.docx
│   ├── 论文标题.tex
│   └── figures/               ← 图片（pandoc 自动导出）
├── md/                        ← 源文件目录
│   ├── 论文标题.md            ← 主文件
│   └── figures/               ← 图片源文件（如 scientific-drawing 生成的 .py/.tex）
└── script/                    ← 脚本目录
    ├── convert.sh             ← 转换入口（自动生成）
    ├── extract_template_styles.py  ← 模版样式提取
    ├── format_filter.lua       ← Lua 格式过滤器
    ├── patch_fonts.py         ← 字体补丁（最后手段）
    ├── watch.sh                ← watchdog 监控（推荐）
    └── watch_folder.applescript  ← AppleScript 监控（备选）
```

---

## 工作流程

```
用户编写 md
    ↓
主 Agent 分析 docx/tex 模版
    ↓
主 Agent 生成 convert.sh + 辅助脚本
    ↓
主 Agent 执行 convert.sh
    ↓
主 Agent 启动审查 Agent
    ↓
审查 Agent 检查格式差异
    ↓
┌─ PASS → 完成
│
└─ FAIL → 主 Agent 修改脚本 → 重新执行（最多 3 轮）
              ↓
         3 轮仍 FAIL → 报告用户决策
```

审查 Agent 逐条核查以下项目：

- **文档结构**：标题层级、章节编号、目录
- **字体与字号**：正文/标题字号、字体族
- **公式**：渲染是否正常、编号位置、间距
- **图表题注**：位置、样式
- **参考文献**：引用格式、缩进

---

## 自动监控（可选）

编辑器保存后自动触发转换，无需每次手动运行。

### 方案 A：watchdog（推荐）

```bash
pip install watchdog
python3 script/watch.sh
```

防抖 2 秒，编辑器保存多次只触发一次转换。`Ctrl+C` 停止。

### 方案 B：AppleScript Folder Action（macOS 原生）

```bash
# 1. 将 watch_folder.applescript 保存到：
~/Library/Scripts/Folder Action Scripts/

# 2. 右键 md/ 文件夹 → 附加文件夹动作
# 3. 选择 watch_folder.applescript
```

> 无防抖，编辑器高频保存时会多次触发。

### 方案 C：Shortcuts（macOS Tahoe+）

1. 打开 **Shortcuts** → **自动化** → **创建个人自动化**
2. 选择 **文件夹** → 选取 `md/` 文件夹
3. 勾选 **已添加**，勾选 **立即运行**
4. 添加操作：**运行 Shell 脚本**：`bash ../script/convert.sh`

---

## Ulysses 写作规范

在 Ulysses 等编辑器中编写 md 时，遵守以下约定：

```
# 一级标题              → Heading 1
## 二级标题             → Heading 2
### 三级标题            → Heading 3
---                    → 分页符

$$e=mc^2$$            → 行内公式（tex_math_dollars）
$$
E = mc^2              → 独立公式块（display math）
$$

![图注](figures/pic.png)  → 图片（路径相对于 md 文件）

| 表头 | 表头 |      → 表格
|------|------|
| 内容 | 内容 |
```

> **注释**：Ulysses 的 `<!--Comments-->` 会被 pandoc 剥离。需要保留的注释改为 `[//]: # (注释内容)` 格式。

---

## 核心约束

| 约束 | 说明 |
|---|---|
| **转换器** | 必须 pandoc，禁止手动 Word 操作 |
| **模版设置** | 必须在 pandoc 调用之前完成，不得作为后处理补丁 |
| **格式调整** | 优先 Lua filter，patch 脚本仅最后手段（≤1 个） |
| **格式检查** | 必须由独立审查 Agent 逐条核查，主 Agent 不得跳过 |

---

## 相关资源

- **SKILL.md** — 完整技能说明，包含所有脚本详解、审查清单、迭代流程
- **scientific-drawing** — 配套图表绘制技能，生成 `md/figures/` 中的图片
