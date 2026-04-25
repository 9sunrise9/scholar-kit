---
name: scholar-kit-installer
description: scholar-kit 交互式安装向导。当用户说"安装 scholar-kit"、"install scholar-kit"、"帮我装技能"时使用。
---

# scholar-kit 安装向导（Agent 执行指令）

你是 scholar-kit 的安装向导。按照以下步骤引导用户完成安装。**不要一次性展示所有步骤，逐步交互。**

---

## Step 1 — 询问要安装的技能

向用户展示以下选项，**请用户选择要安装的技能**（可多选）：

```
可用技能：
  1) academic-writing     — Markdown → docx / LaTeX 格式转换（pandoc 驱动）
  2) scientific-drawing   — TikZ / matplotlib 学术图表生成
  3) writing-style-check  — 学术正文风格检查与修改建议

请输入序号（如 1 2 3），或直接回车安装全部：
```

等待用户回复后，记录选中的技能名称。

---

## Step 2 — 询问目标 AI 工具

向用户展示以下选项，**请用户选择要安装到哪个 AI 工具**（可多选）：

```
支持的 AI 工具：
  1) Claude Code     → ~/.claude/skills/
  2) OpenCode        → ~/.opencode/skills/
  3) Codex CLI       → ~/.codex/instructions.md（追加内容）
  4) GitHub Copilot  → ~/.copilot/skills/（VS Code Copilot Chat 全局生效）

  Windows 用户：~ 对应 %USERPROFILE%，路径分隔符用 \

请输入序号（如 1 3），或直接回车安装到全部：
```

等待用户回复后，**在执行安装前，先检测所选工具是否已安装**：

| 工具 | macOS / Linux | Windows |
|------|---------------|---------|
| Claude Code    | `command -v claude` 或 `~/.claude/` 存在 | `where claude` 或 `%USERPROFILE%\.claude\` 存在 |
| OpenCode       | `command -v opencode` 或 `~/.opencode/` 存在 | `where opencode` 或 `%USERPROFILE%\.opencode\` 存在 |
| Codex CLI      | `command -v codex` 或 `~/.codex/` 存在 | `where codex` 或 `%USERPROFILE%\.codex\` 存在 |
| GitHub Copilot | `command -v code` 或 `~/.vscode/` 存在 | `where code` 或 `%APPDATA%\Code\` 存在 |

* 若检测**通过**：继续安装。
* 若检测**未通过**：向用户提示该工具尚未安装，**跳过该工具，不执行任何安装操作**，例如：

  

```
  ⚠️  未检测到 Claude Code，已跳过。
  如需使用，请先安装：https://claude.ai/download

  其他已选工具将继续安装。
  ```

  若用户所选的**全部工具**均未检测到，则提示所有工具均不可用，并请用户重新选择：

  

```
  ❌  所选工具均未检测到，无法安装。
  请重新选择已安装的工具（输入序号）：
  ```

  等待用户重新输入后，再次检测并执行安装。

各工具安装方式说明：

| 工具 | 安装方式 | macOS / Linux | Windows |
|------|----------|---------------|---------|
| Claude Code    | 复制技能目录 | `~/.claude/skills/<skill>/` | `%USERPROFILE%\.claude\skills\<skill>\` |
| OpenCode       | 复制技能目录 | `~/.opencode/skills/<skill>/` | `%USERPROFILE%\.opencode\skills\<skill>\` |
| Codex CLI      | 追加 SKILL.md | `~/.codex/instructions.md` | `%USERPROFILE%\.codex\instructions.md` |
| GitHub Copilot | 复制技能目录 | `~/.copilot/skills/<skill>/` | `%USERPROFILE%\.copilot\skills\<skill>\` |

> Codex 不支持技能目录结构，改为将 SKILL.md 全文追加到指令文件，追加前插入分隔注释 `<!-- scholar-kit: <skill-name> -->` ，方便日后识别和卸载。
> GitHub Copilot 安装到 `~/.copilot/skills/` 后，VS Code Copilot Chat 全局自动生效，无需额外配置。

---

## Step 3 — 执行安装

在用户确认技能和工具选择后，**先检测操作系统**，然后直接下载到目标路径，无需预先克隆仓库。

### macOS / Linux（bash）

**Claude Code / OpenCode**（下载技能目录）：

```bash
# 以安装 academic-writing 到 Claude Code 为例：
mkdir -p ~/.claude/skills
curl -sL https://github.com/sunyue/scholar-kit/archive/refs/heads/main.tar.gz \
  | tar -xz --strip-components=2 -C ~/.claude/skills scholar-kit-main/academic-writing
```

**Codex CLI**（下载 SKILL.md 并追加到全局指令文件）：

```bash
mkdir -p ~/.codex
printf '\n<!-- scholar-kit: academic-writing -->\n' >> ~/.codex/instructions.md
curl -sL https://raw.githubusercontent.com/sunyue/scholar-kit/main/academic-writing/SKILL.md \
  >> ~/.codex/instructions.md
```

**GitHub Copilot**（下载技能目录）：

```bash
mkdir -p ~/.copilot/skills
curl -sL https://github.com/sunyue/scholar-kit/archive/refs/heads/main.tar.gz \
  | tar -xz --strip-components=2 -C ~/.copilot/skills scholar-kit-main/academic-writing
```

### Windows（PowerShell）

> Windows 10 build 17063+ 内置 `curl.exe` 和 `tar.exe` ，以下命令直接在 PowerShell 中运行。

**Claude Code / OpenCode**（下载技能目录）：

```powershell
# Claude Code：目标目录 $env:USERPROFILE\.claude\skills
# OpenCode：  目标目录 $env:USERPROFILE\.opencode\skills
# 以安装 academic-writing 到 Claude Code 为例：
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills" | Out-Null
$tmp = "$env:TEMP\scholar-kit.tar.gz"
Invoke-WebRequest -Uri "https://github.com/sunyue/scholar-kit/archive/refs/heads/main.tar.gz" -OutFile $tmp
tar -xz --strip-components=2 -C "$env:USERPROFILE\.claude\skills" -f $tmp "scholar-kit-main/academic-writing"
Remove-Item $tmp
```

**Codex CLI**：

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.codex" | Out-Null
Add-Content "$env:USERPROFILE\.codex\instructions.md" "`n<!-- scholar-kit: academic-writing -->"
$tmp_skill = "$env:TEMP\scholar-kit-skill.md"
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/sunyue/scholar-kit/main/academic-writing/SKILL.md" -OutFile $tmp_skill
Get-Content $tmp_skill | Add-Content "$env:USERPROFILE\.codex\instructions.md"
Remove-Item $tmp_skill
```

**GitHub Copilot**：

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.copilot\skills" | Out-Null
$tmp = "$env:TEMP\scholar-kit.tar.gz"
Invoke-WebRequest -Uri "https://github.com/sunyue/scholar-kit/archive/refs/heads/main.tar.gz" -OutFile $tmp
tar -xz --strip-components=2 -C "$env:USERPROFILE\.copilot\skills" -f $tmp "scholar-kit-main/academic-writing"
Remove-Item $tmp
```

对每个选中的（技能 × 工具）组合依次执行，执行完毕后向用户报告结果。

---

## Step 4 — 完成提示

安装结束后告知用户：

```
安装完成！请重启对应的 AI 工具以激活技能。

技能激活后，直接在对话中说出触发词即可使用：
  - academic-writing：   "帮我把 md 转成 docx"
  - scientific-drawing： "帮我画一张架构图"
  - writing-style-check："帮我检查写作风格"
```

---

## 注意事项

* 若目标目录中已存在同名技能，覆盖安装（`curl | tar` 解压会直接替换文件）。
* 若用户的系统路径与默认路径不同，询问用户确认实际路径后再执行。
* 不要自动推断或猜测用户意图，每一步都等待用户明确回复。
