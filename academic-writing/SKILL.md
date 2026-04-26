---
name: academic-writing
description: 学术论文写作技能：Markdown（内嵌 LaTeX 公式）撰写，通过 pandoc 转换为符合模版的 docx 或 LaTeX。触发场景：用户提供 docx/tex 模版要求创建转换脚本、说"帮我把 md 转成 docx/tex"、要求检查转换结果与模版的格式差异、建立项目目录结构、或在 Ulysses/Obsidian 写作后需要导出最终格式。
---

# 学术写作技能

## 0. 核心约束

| 约束 | 规范 |
|---|---|
| **转换器** | 必须 pandoc；禁止手动 Word 操作或 python-docx 大幅修改 |
| **模版设置** | 必须在 pandoc 调用之前完成，不得作为后处理补丁 |
| **格式调整** | 优先 `--lua-filter=format_filter.lua`；patch 脚本仅作最后手段（≤1个） |
| **格式检查** | 必须开启独立审查 agent，用 `look_at` / 文本 diff 逐项核对模版与输出 |
| **迭代退出** | 审查 agent 返回 PASS 或 3 轮内无法消解差异时，报告用户决策 |
| **图表格式** | 图题居中、表题在表格上方、表格满页宽是**必备步骤**，每次转换必须执行（见 §8） |
| **模版修改边界** | 如 reference.docx 缺少图表样式定义，**只允许修改样式定义（styles.xml）**，禁止修改模版的格式数据（正文内容、页面布局数据等） |

---

## 1. 目录结构（项目初始化）

每项写作任务对应一个独立文件夹，结构如下：

```
项目根目录/
├── docx_tex/           ← 最终输出（docx 或 tex）
│   └── figures/        ← 生成好的图片（由 scientific-drawing 技能生成）
├── md/                 ← 源 md 文件（与文稿同名，如"低空反无.md"）
│   └── figures/        ← 图片源文件（.py/.tex 绘图脚本，由 scientific-drawing 生成）
└── script/             ← 所有脚本（convert.sh、辅助脚本、监控脚本）
    ├── convert.sh
    ├── extract_template_styles.py
    ├── format_filter.lua
    ├── patch_fonts.py  （最后手段）
    └── watch.sh        （自动监控）
```

**初始化命令（主 Agent 执行）：**
```bash
PROJECT_NAME="低空反无"
WORK_DIR="./${PROJECT_NAME}"

mkdir -p "${WORK_DIR}/docx_tex/figures" \
         "${WORK_DIR}/md/figures" \
         "${WORK_DIR}/script"
echo "目录结构已创建：${WORK_DIR}/"
```

> **经验总结**：所有脚本集中在 `script/` 避免散落在根目录，便于管理、批量修改和版本控制。

---

## 2. 转换脚本生成流程（必须按此顺序）

### Step 1 — 主 Agent 分析模版

读取用户提供的 `.docx` 或 `.tex` 模版，提取：
- 样式定义（标题层级、章节编号、字体、行距、页边距）
- 公式编号规则（若有）
- 图表题注格式
- 参考文献格式（若有）

### Step 2 — 主 Agent 创建转换脚本

转换脚本必须满足以下顺序结构，**禁止打乱**：

```bash
#!/bin/bash
# convert.sh — 由 academic-writing 技能自动生成，请勿手动修改
set -e

# ── 0. 配置区 ──
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"   # 所有脚本在 script/ 目录下
TEMPLATE="${SCRIPT_DIR}/../template.docx"      # 模版在项目根目录
INPUT_MD="${SCRIPT_DIR}/../md/低空反无.md"
OUTPUT_DOCX="${SCRIPT_DIR}/../docx_tex/低空反无.docx"
OUTPUT_TEX="${SCRIPT_DIR}/../docx_tex/低空反无.tex"

# ── 1. 模版预处理（在 pandoc 之前！） ──
echo "提取模版样式..."
python3 "${SCRIPT_DIR}/extract_template_styles.py" "${TEMPLATE}" \
  > /tmp/tpl_styles.json

# ── 2. pandoc 转换 ──
echo "转换 md → docx..."
pandoc "${INPUT_MD}" \
  --reference-doc="${TEMPLATE}" \
  --lua-filter="${SCRIPT_DIR}/format_filter.lua" \
  --extract-media="${SCRIPT_DIR}/../docx_tex/figures" \
  -o "${OUTPUT_DOCX}"

echo "转换 md → tex..."
pandoc "${INPUT_MD}" \
  -f markdown+tex_math_dollars \
  --lua-filter="${SCRIPT_DIR}/format_filter.lua" \
  --top-level-division=chapter \
  -o "${OUTPUT_TEX}"

echo "完成：${OUTPUT_DOCX} ${OUTPUT_TEX}"
```

> **经验总结**：
> - `SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"` 让脚本从任意路径调用都能找到同目录下的辅助脚本
> - `set -e` 使任何命令失败立即退出，避免静默跳过后续步骤
> - 图片媒体包 ` --extract-media` 输出到 `docx_tex/figures`，避免散落根目录
> - Lua filter 路径用绝对路径（`${SCRIPT_DIR}/...`），不依赖 cwd

### Step 3 — 生成辅助脚本

所有脚本写入 `script/` 子目录：

| 脚本 | 用途 | 触发条件 |
|---|---|---|
| `script/extract_template_styles.py` | 从 docx/odt 模版提取样式参数到 JSON | 模版为 docx/odt 时必须 |
| `script/format_filter.lua` | 格式微调（字体、字号、公式渲染方式） | **默认生成**，优先使用 |
| `script/patch_fonts.py` | 极细微字体替换 | Lua filter 无法实现时（最后手段） |
| `script/watch.sh` | 自动监控 md 目录变化，自动触发 convert.sh | 需要实时预览时启用 |

### Step 4 — 自动监控方案（三选一）

#### 方案 A：watchdog（推荐，功能最完整）

`script/watch.sh` 即为 watchdog 实现：

| 特性 | 说明 |
|---|---|
| 防抖 | `threading.Timer` 延迟 2s，编辑器保存多次触发只执行一次 |
| subprocess 调用 | 调用 `pandoc_convert.py`，保持与 convert.sh 一致的转换逻辑 |
| 静默运行 | 无 GUI，打印简洁日志，Ctrl+C 退出 |

```
python3 scripts/convert/watch_and_convert.py
```

#### 方案 B：AppleScript Folder Action（macOS 原生）

macOS 内置的 Folder Action，通过 `adding folder items to` 事件触发脚本。

```applescript
-- script/watch_folder.applescript
-- 保存到 ~/Library/Scripts/Folder Action Scripts/，然后右键文件夹 → 附加文件夹动作
on adding folder items to theAttachedFolder after receiving theNewItems
    repeat with anItem in theNewItems
        set ext to do shell script "basename " & quoted form of POSIX path of anItem & " | sed 's/.*\\.//'"
        if ext is "md" then
            do shell script "cd " & quoted form of POSIX path of theAttachedFolder & "
                /usr/local/bin/python3 ../script/convert.sh"
        end if
    end repeat
end adding folder items to
```

**附加步骤**：
1. 保存上述脚本到 `~/Library/Scripts/Folder Action Scripts/watch_md.applescript`
2. 右键 `md/` 文件夹 → **文件夹动作设置** → 勾选**启用文件夹动作**
3. 附加 `watch_md.applescript`

> **局限**：无原生防抖；事件触发粒度粗（整个文件夹变化才触发）；无法运行复杂预处理逻辑。

#### 方案 C：Shortcuts 自动化（macOS Tahoe+，零代码）

macOS Shortcuts 的**文件夹内容变化**触发器，纯 GUI 配置。

1. 打开 **Shortcuts** → **自动化** → **创建个人自动化**
2. 选择 **文件夹** → 选取 `md/` 文件夹
3. 勾选 **已添加**（文件进入时触发）
4. 添加操作：**运行 Shell 脚本**：`bash ../script/convert.sh`
5. 取消勾选 **显示忽略通知**，勾选 **立即运行**
6. 保存

> **局限**：过滤条件简单；不支持子文件夹精确过滤。

#### 方案对比

| 特性 | watchdog（方案A） | AppleScript（方案B） | Shortcuts（方案C） |
|---|---|---|---|
| 防抖 | ✅ 2s Timer | ❌ 需额外脚本 | ❌ 无 |
| 预处理能力 | ✅ 完整 Python | ⚠️ limited | ❌ 无 |
| 安装复杂度 | 中（pip install watchdog） | 低（保存脚本+附加动作） | 低（GUI 点选） |
| 跨平台 | ❌ macOS only | ❌ macOS only | ❌ macOS only |
| 后台运行 | ✅ 终端/nohup | ✅ 开机自启 | ✅ 后台 |

**推荐**：方案 A（watchdog），功能完整。

### Step 5 — 用户验收

启动审查 agent 逐条核查（见 §3），循环迭代直到 PASS 或 3 轮上限。

---

## 3. 多 Agent 审查迭代工作流（必须遵守）

> 核心原则：审查 agent 独立检查，主 agent 不得跳过或自行判断"差不多"

### 3.1 Agent 分工

| Agent | 职责 | 允许工具 |
|---|---|---|
| **主 Agent** | 分析模版、生成脚本、协调迭代 | Bash, Write, Edit, task() |
| **绘图 Agent**（可选） | 生成/转换 md 中的图片（调用 scientific-drawing） | Write, Edit, Bash |
| **审查 Agent** | 检查转换后文件与模版的格式差异，返回 PASS/FAIL + 问题列表 | look_at（若 docx 有图片）、文本比对工具 |

### 3.2 审查 Agent 检验清单（每次逐条核查）

```
【文档结构】
□ 标题层级是否与模版一致（# → Heading 1，## → Heading 2）？
□ 章节编号格式是否正确（若模版有编号）？
□ 目录是否自动生成（若模版有目录）？

【字体与字号】
□ 正文字号是否与模版一致（小四/12pt）？
□ 标题字号是否逐级增大（与模版对照）？
□ 字体族是否正确（宋体/正文 vs Times New Roman）？

【公式】
□ 公式是否正常渲染（非原始 LaTeX 源码）？
□ 公式编号是否在右侧（若模版有编号规则）？
□ 行内公式与上下文间距是否正确？

【图表题注】
□ 图题注位置（下方 vs 上方）与模版一致？
□ 表头样式是否加粗（与模版对照）？

【参考文献】
□ 引用格式是否符合模版（作者年/顺序编码）？
□ 缩进格式是否与模版一致（悬挂缩进）？
```

### 3.3 标准迭代流程

```
Step 1 — 主 Agent 创建/更新 convert.sh 和辅助脚本（位于 script/）
Step 2 — 主 Agent 执行 bash script/convert.sh
Step 3 — 主 Agent 启动审查 Agent，逐条核查清单
         → PASS：完成
         → FAIL：主 Agent 按问题列表修改脚本（回 Step 1），最多 3 轮
Step 4 — 3 轮仍 FAIL：主 Agent 报告具体未匹配项，用户决策是否接受当前结果
Step 5（可选）— 主 Agent 启动监控：
- watchdog（推荐）：`python3 script/watch.sh`
- AppleScript（备选）：按方案 B 说明附加 Folder Action
```

---

## 4. 模版分析要点

### 4.1 docx 模版（优先）

使用 `python-docx` 或直接解压 `word/styles.xml` 分析：

```
关键样式：
- Normal / Body Text → 正文
- Heading 1/2/3 → 一/二/三级标题
- List Paragraph → 列表
- Table Normal → 表格
- Caption → 题注
```

### 4.2 LaTeX 模版

直接读取 `.tex` 文件，提取：
- `\documentclass{...}` 确定文档类
- `\usepackage{}` 确定宏包依赖
- `\title{}`、`\author{}`、`\chapter{}`、`\section{}` 层级
- `\bibliography{}` 参考文献方式

### 4.3 常见差异与解法

| 差异 | 根因 | pandoc 参数解法 |
|---|---|---|
| 标题级别不对 | md # vs 模版 Heading | `--base-levels=1` 或在 md 中调整 `#` 数量 |
| 图表题注位置 | 模版在上/下 | 修改 md 中 `![alt](path)` 前后题注位置 |
| 公式渲染为源码 | 未开启 math 渲染 | `-f markdown+tex_math_dollars` |
| 字体不对 | 模版字体缺失 | 通过 reference-doc 传递样式 |
| 行距不对 | 模版行距非单倍 | 在 reference-doc 中设置，或用 patch 脚本微调 |

---

## 5. Ulysses Markdown 写作规范

用户使用 Ulysses 写作时，遵守以下约定以便顺利转换：

```
# 一级标题          → 对应章/大节
## 二级标题         → 子节
### 三级标题        → 子子节
---                → 手动分页符（对应 Word 分页）
$$e=mc^2$$          → 行内公式（tex_math_dollars）
$$
E = mc^2           → 独立公式块
$$
![图注](figures/pic.png)  → 图片（路径相对于 md 文件位置）
| 表头 | 表头 |     → 表格
```

> **警告**：Ulysses 的 `<!--Comments-->` 注释在转换时默认被 strip，需要保留的注释改为 md `[//]: # (注释内容)` 格式。

---

## 5a. 中文 LaTeX：ctex + xelatex 专属事项

> 适用场景：文稿包含中文正文（专著、教材、中文期刊）。

### 文档类选择

| 用途 | 文档类 |
|---|---|
| 专著 / 技术报告 | `ctexrep` |
| 期刊 / 短文 | `ctexart` |
| 书籍 | `ctexbook` |

**禁止**在中文文稿中使用通用 `report`/`article` 文档类（字体/字符支持不完整）。

### convert.sh 中文 tex 路径模板

```bash
pandoc "$INPUT_MD" \
  -f markdown+tex_math_dollars \
  --standalone \
  --lua-filter="$SCRIPT_DIR/format_filter.lua" \
  --top-level-division=chapter \
  -V documentclass=ctexrep \
  -o "$OUTPUT_TEX"

# 后处理：移除 xelatex 下不兼容包、冗余 pandoc 宏、修正图片路径
sed -i.bak \
  -e '/\\usepackage\[T1\]{fontenc}/d' \
  -e '/\\usepackage{newtxtext/d' \
  -e '/\\usepackage{newtxmath/d' \
  -e '/\\newtheorem{problem}/d' \
  -e '/\\setcounter{secnumdepth}{0}/d' \
  -e 's|{\.\.\/docx_tex\/figures\/|{figures/|g' \
  "$OUTPUT_TEX"
rm -f "${OUTPUT_TEX}.bak"
```

> **注意**：
> - **禁止**传 `-V lang=zh-CN`，这会触发 pandoc 调用 polyglossia 并生成 `\setmainlanguage[]{}` 空参命令，导致 xelatex 报错 `End of environment '' already defined`。
> - ctexrep 已自动处理中文字体与断行，无需手动配置 xeCJK。

### pandoc `--standalone` 注入的冗余宏（需清理）

pandoc 的默认 LaTeX 模板每次都会在 tex 开头注入以下内容，专著/嵌入场景下必须清理：

| 宏 | 问题 |
|---|---|
| `\usepackage[T1]{fontenc}` | 与 xelatex 不兼容，导致中文字符无法渲染 |
| `\usepackage{newtxtext}` / `newtxmath` | Latin 字体包，xelatex 下冲突 |
| `\newtheorem{problem}{Problem}` | 嵌入专著时若主文件已定义 `problem` 环境则报错 |
| `\setcounter{secnumdepth}{0}` | 关闭全文章节编号，嵌入专著会破坏主文件编号 |

上述 `sed -i.bak` 命令已包含对所有四类宏的清理。

### 图片路径规范

tex 文件在 `docx_tex/` 目录，图片在 `docx_tex/figures/`。  
md 中图片路径**必须**写为相对于 tex 文件位置：`figures/fig_1/fig.pdf`。  
**禁止**从 md 目录相对引用（`../docx_tex/figures/...`）——虽然偶尔因编译 cwd 巧合正确，但路径语义是错的。

若历史 md 已使用 `../docx_tex/` 前缀，上述 `sed -i.bak` 中的最后一条规则已统一替换。

### 编译命令

```bash
# 优先 latexmk（自动处理交叉引用轮次）
(cd "$PROJECT_ROOT/docx_tex" && latexmk -xelatex -interaction=nonstopmode -halt-on-error "$TEX_BASENAME")

# 备用（需运行两次处理交叉引用）
(cd "$PROJECT_ROOT/docx_tex" && xelatex -interaction=nonstopmode -halt-on-error "$TEX_BASENAME")
(cd "$PROJECT_ROOT/docx_tex" && xelatex -interaction=nonstopmode -halt-on-error "$TEX_BASENAME")
```

### `sed -i` 跨平台说明

macOS 的 `sed -i ''` 与 Linux 的 `sed -i` 语法不兼容。统一写法：

```bash
# 跨平台安全写法（macOS 和 Linux 均适用）
sed -i.bak -e '...' FILE && rm -f FILE.bak
```

**禁止**直接使用 `sed -i ''`（macOS only，Linux 下报错）。

---

## 6. 辅助脚本参考

### 6.4 watch.sh（watchdog，推荐）

watchdog 实现，防抖 2 秒。完整代码见 `script/watch.sh`。

### 6.1 format_filter.lua（默认生成，优先使用）

Lua filter 是 pandoc 原生支持的格式调整手段，运行在 AST 层面，比补丁脚本更可靠。

```lua
-- format_filter.lua
-- 用法：pandoc --lua-filter=format_filter.lua input.md -o output.docx
-- 用途：公式渲染、字体覆盖、标题层级调整

local filter = {}

-- 公式块：强制使用 displaymath 而非 math
function Math(elem)
  if elem.mathtype == "InlineMath" then
    return elem
  end
  return pandoc.Math({mathmode = "DisplayMath"}, elem.text)
end

-- 标题：强制指定样式（覆盖 reference-doc 默认）
function Header(elem)
  local level = elem.level
  local style = {
    [1] = "Heading 1",
    [2] = "Heading 2",
    [3] = "Heading 3",
  }
  if style[level] then
    return elem
  end
  return elem
end

-- 代码块：设置等宽字体
function CodeBlock(elem)
  return pandoc.Para({
    pandoc.Str(elem.text)
  })
end

-- 读取模版样式 JSON（由 extract_template_styles.py 生成）
local function load_tpl_styles()
  local f = io.open("/tmp/tpl_styles.json", "r")
  if not f then return {} end
  local content = f:read("*all")
  f:close()
  local ok, dec = pcall(JSON.parse, content)
  if ok then return dec else return {} end
end

return filter
```

**常用 Lua filter 场景**：

| 场景 | Lua filter 实现 |
|---|---|
| LaTeX 公式渲染 | `Math` element 改 `mathmode = "DisplayMath"` |
| 强制中文字体 | 遍历 `Str` 设置 `Span` 属性 |
| 图片题注位置 | 调换 `Para` 中 `Image` 和 `Str` 顺序 |
| 标题加编号 | `Header` 中插入 `Strong` 编号前缀 |

### 6.2 extract_template_styles.py（必须，模版分析）

```python
#!/usr/bin/env python3
import sys, json, zipfile, xml.etree.ElementTree as ET
from pathlib import Path

def extract_styles(template_path: str) -> dict:
    styles = {}
    ns_w = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    tpl = Path(template_path)
    if tpl.suffix.lower() == '.docx':
        with zipfile.ZipFile(template_path) as z:
            with z.open('word/styles.xml') as f:
                tree = ET.parse(f)
        for style in tree.findall(f'.//{{{ns_w}}}style'):
            sid = style.get(f'{{{ns_w}}}styleId')
            sz_el = style.find(f'.//{{{ns_w}}}sz')
            font_el = style.find(f'.//{{{ns_w}}}rFonts')
            sz_val = None
            if sz_el is not None:
                v = sz_el.get(f'{{{ns_w}}}val')
                if v: sz_val = int(v)
            font_val = None
            if font_el is not None:
                font_val = font_el.get(f'{{{ns_w}}}eastAsia') or font_el.get(f'{{{ns_w}}}ascii')
            if sid and (sz_val or font_val):
                styles[sid] = {'sz': sz_val, 'font': font_val}
    print(json.dumps(styles, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    extract_styles(sys.argv[1] if len(sys.argv) > 1 else 'template.docx')
```

### 6.3 patch_fonts.py（最后手段）

```python
#!/usr/bin/env python3
import sys, zipfile, shutil
def patch_fonts(docx_path, font_map):
    tmp = docx_path + '.tmp'
    with zipfile.ZipFile(docx_path, 'r') as zin, zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename.endswith('.xml'):
                text = data.decode('utf-8')
                for old, new in font_map.items():
                    text = text.replace(old, new)
                data = text.encode('utf-8')
            zout.writestr(item, data)
    shutil.move(tmp, docx_path)
if __name__ == '__main__':
    patch_fonts(sys.argv[1], {'Calibri': 'Times New Roman'})
```

---

## 8. 图表格式处理（必备步骤）

> **每次 md→docx 转换必须完成本节所有步骤。** 图题居中、表题在表格上方、表格满页宽是硬性要求，不得省略。

### 8.1 原则

- **reference.docx 是唯一的样式来源**：图/表样式必须在 reference.docx 的 styles.xml 中定义好，pandoc 通过 `custom-style` 匹配 styleId 来应用样式。
- **pandoc `custom-style` 必须用 styleId 名**，不能用中文显示名（中文显示名会触发 pandoc 新建空白样式，导致样式失效）。
- **pandoc 对自定义样式只复制存根（stub）**，不复制完整 pPr/rPr。因此后处理脚本必须将 reference.docx 中的完整样式定义注入到输出 docx 的 styles.xml（见 §8.4）。

### 8.2 reference.docx 必备样式

在 reference.docx 的 styles.xml 中，以下样式必须存在且正确配置（用 `patch_reference_styles.py` 写入）：

| StyleId | 显示名 | 必要配置 |
|---|---|---|
| `FigurePara` | 图片 | `jc=center`，`ind firstLine="0" firstLineChars="0"` |
| `FigureCaption` | 图题 | `jc=center`，`ind firstLine="0" firstLineChars="0"` |
| `TableCaption` | 表题 | `jc=center`，`ind firstLine="0" firstLineChars="0"` |
| `TableBody` | 表格正文 | `ind firstLine="0" firstLineChars="0"`，`spacing line="240" lineRule="auto"` |

**关键细节**：必须同时设 `firstLine="0"` 和 `firstLineChars="0"`，否则继承自正文样式（`a1`）的 `firstLineChars="200"` 会覆盖 `firstLine="0"`，导致首行缩进仍然出现。

```xml
<!-- TableBody 样式示例（reference.docx styles.xml，无 w: 前缀命名空间） -->
<style type="paragraph" styleId="TableBody">
  <name val="表格正文"/>
  <basedOn val="a1"/>
  <next val="TableBody"/>
  <pPr>
    <spacing before="0" after="0" line="240" lineRule="auto"/>
    <ind firstLine="0" firstLineChars="0"/>
    <jc val="both"/>
  </pPr>
  <rPr>
    <rFonts eastAsia="宋体" ascii="Times New Roman" hAnsi="Times New Roman"/>
    <sz val="21"/>
  </rPr>
</style>
```

### 8.3 format_filter.lua：图表节点的 custom-style 标注

Lua filter 的 `Pandoc()` document-level filter 负责将 md 中的图片段落、图题、表题标注为对应 styleId：

```lua
-- 关键规则（必须用 styleId，不能用中文显示名）
-- 图片段落 -> FigurePara
-- 图题（图片后紧跟的 Plain/Para，内容以"图"开头）-> FigureCaption  
-- 表题（表格前的 Para，内容以"表"开头）-> TableCaption
-- 表格内单元格段落 -> 后处理脚本替换（Compact -> TableBody）
```

### 8.4 后处理脚本：样式同步 + 表格宽度（convert.sh 内嵌 Python）

后处理分三个独立步骤，**顺序不可打乱**：

#### Step A：替换表格内段落样式（Compact → TableBody）

pandoc 对表格内容使用 `Compact` 样式，需替换为 `TableBody`：

```python
def replace_in_tc(m):
    return re.sub(r'(<w:pStyle w:val=")Compact(")', r'\1TableBody\2', m.group(0))
new_xml, n = re.subn(r'<w:tc>.*?</w:tc>', replace_in_tc, doc_xml, flags=re.DOTALL)
```

#### Step B：从 reference.docx 同步完整样式定义

pandoc 输出的自定义样式只有存根，必须从 reference.docx 复制完整定义：

```python
# 从 reference.docx 读取目标样式（无 w: 前缀）
# 转换为 w: 前缀命名空间（所有属性/标签加 w:）
# 替换输出 docx styles.xml 中的对应存根
```

namespace 转换要点（reference.docx 用无前缀，输出 docx 用 `w:` 前缀）：

```python
ref_style_w = ref_style \
    .replace('<style ', '<w:style ') \
    .replace(' styleId=', ' w:styleId=') \
    .replace('<pPr>', '<w:pPr>') \
    .replace('<ind ', '<w:ind ') \
    .replace(' firstLine=', ' w:firstLine=') \
    .replace(' firstLineChars=', ' w:firstLineChars=')
    # ... 同理处理所有属性和标签
```

#### Step C：表格满页宽 + autofit

计算页面可用宽度（从 `<w:pgSz>` 和 `<w:pgMar>` 读取）：

```python
# 可用宽度 = pgSz.w - pgMar.left - pgMar.right（单位：twips）
# 例：A4 竖向，左右边距各 1800 twips → 11907 - 1800 - 1800 = 8307 twips

PAGE_WIDTH = 8307  # 按实际文档计算

def fix_table(tbl):
    # 1. tblW -> PAGE_WIDTH dxa
    tbl = re.sub(r'<w:tblW\b[^/]*/>', f'<w:tblW w:type="dxa" w:w="{PAGE_WIDTH}" />', tbl)
    # 2. tblLayout -> autofit（让 Word 根据内容自动分配列宽，减少折行）
    tbl = re.sub(r'<w:tblLayout\b[^/]*/>', '<w:tblLayout w:type="autofit" />', tbl)
    # 3. tblGrid 各列按原比例等比缩放到 PAGE_WIDTH
    #    col_widths_scaled = [round(w * PAGE_WIDTH / total) for w in col_widths_orig]
    #    修正末列使总和精确等于 PAGE_WIDTH
    # 4. 各 tcW 同步更新（考虑 gridSpan 合并列）
    return tbl
```

**autofit 的意义**：`tblLayout type="autofit"` 让 Word 在打开文档时根据内容重新分配列宽，优先避免折行，比 `fixed` 宽度更合理。tblGrid 的初始列宽作为比例参考起点。

### 8.5 审查清单补充（图表专项）

在 §3.2 审查清单基础上，增加以下图表专项检查：

```
【图片格式】
□ 图片段落是否居中（无首行缩进）？
□ 图题是否在图片下方？
□ 图题是否居中（无首行缩进）？

【表格格式】
□ 表题是否在表格上方？
□ 表题是否居中？
□ 表格是否撑满页面宽度？
□ 表格内文字是否无首行缩进？
□ 表格内文字是否单倍行距？
```

### 8.6 常见问题排查

| 症状 | 根因 | 修复 |
|---|---|---|
| 图/表样式未生效，用空白样式 | `custom-style` 用了中文显示名而非 styleId | 改用 styleId（`FigurePara`、`TableCaption` 等） |
| 表格首行缩进仍存在 | 只设了 `firstLine="0"`，未清除 `firstLineChars` | 同时设 `firstLineChars="0"` |
| 表格首行缩进仍存在（样式已设正确） | pandoc 存根未包含 pPr，Word 从父样式继承 | 后处理从 reference.docx 同步完整样式定义（Step B） |
| 表格宽度不足 | tblW 为 `pct 5000`（50%）或 `auto` | 后处理设 `tblW dxa PAGE_WIDTH` + `tblLayout autofit` |

- **script/format_filter.lua** — 默认生成，优先于 patch；覆盖公式渲染/字体/标题层级
- **script/extract_template_styles.py** — 每次分析 docx 模版时必须
- **script/watch.sh** — watchdog Python 版（推荐）：防抖 2s，pip install watchdog 后直接运行
- **script/watch_folder.applescript** — AppleScript Folder Action 版（备选）：保存到 ~/Library/Scripts/Folder Action Scripts/，右键附加文件夹动作
- **script/patch_fonts.py** — 仅 Lua filter 无法实现时的最后手段
- 当前 SKILL.md — 覆盖完整流程；无需读额外引用文件

