#!/usr/bin/env bash
# scholar-kit 交互式安装脚本
# 确认安装目标后直接从 GitHub 下载到目标目录，无需预先克隆仓库
set -e

# ── OS detection ─────────────────────────────────────────────────────────────
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
  echo "ℹ️  检测到 Windows Git Bash 环境，安装路径对应 %USERPROFILE%（即 $HOME）"
elif grep -qi "microsoft" /proc/version 2>/dev/null; then
  echo "ℹ️  检测到 WSL 环境，安装到 Linux 家目录 $HOME"
  echo "   若 AI 工具安装在 Windows 端，路径可能在 /mnt/c/Users/$USER/ 下"
fi

REPO_BASE="https://raw.githubusercontent.com/sunyue/scholar-kit/main"
REPO_ARCHIVE="https://github.com/sunyue/scholar-kit/archive/refs/heads/main.tar.gz"

ALL_SKILLS=("academic-writing" "scientific-drawing" "writing-style-check")
SKILL_DESCS=(
  "academic-writing     — Markdown → docx / LaTeX 格式转换（pandoc 驱动）"
  "scientific-drawing   — TikZ / matplotlib 学术图表生成"
  "writing-style-check  — 学术正文风格检查与修改建议"
)

TOOL_NAMES=("Claude Code" "OpenCode" "Codex CLI" "GitHub Copilot")
TOOL_DESCS=(
  "Claude Code     → $HOME/.claude/skills/"
  "OpenCode        → $HOME/.opencode/skills/"
  "Codex CLI       → $HOME/.codex/instructions.md（追加内容）"
  "GitHub Copilot  → $HOME/.copilot/skills/（VS Code Copilot Chat 全局生效）"
)
TOOL_DETECT=(
  "command -v claude &>/dev/null || [ -d \"\$HOME/.claude\" ]"
  "command -v opencode &>/dev/null || [ -d \"\$HOME/.opencode\" ]"
  "command -v codex &>/dev/null || [ -d \"\$HOME/.codex\" ]"
  "command -v code &>/dev/null || [ -d \"\$HOME/.vscode\" ]"
)
TOOL_URLS=(
  "https://claude.ai/download"
  "https://opencode.ai"
  "https://platform.openai.com/docs/codex"
  "https://github.com/features/copilot"
)

# ── helpers ──────────────────────────────────────────────────────────────────

print_divider() { echo ""; echo "────────────────────────────────────────"; echo ""; }

# 返回某技能所需的依赖列表（空格分隔）
skill_deps() {
  case "$1" in
    academic-writing)     echo "curl tar pandoc python3" ;;
    scientific-drawing)   echo "curl tar python3" ;;
    writing-style-check)  echo "curl tar python3" ;;
    *)                    echo "curl tar" ;;
  esac
}

# 返回某依赖的安装参考提示
dep_hint() {
  case "$1" in
    curl)    echo "brew install curl  /  sudo apt install curl" ;;
    tar)     echo "通常随系统自带，请检查系统环境" ;;
    pandoc)  echo "brew install pandoc  /  sudo apt install pandoc  /  https://pandoc.org/installing.html" ;;
    python3) echo "brew install python  /  sudo apt install python3  /  https://python.org/downloads" ;;
    *)       echo "" ;;
  esac
}

# 返回自动安装命令（依赖包管理器检测）
auto_install_cmd() {
  local dep="$1"
  if command -v brew &>/dev/null; then
    case "$dep" in
      python3) echo "brew install python" ;;
      *)       echo "brew install $dep" ;;
    esac
  elif command -v apt-get &>/dev/null; then
    echo "sudo apt-get install -y $dep"
  elif command -v dnf &>/dev/null; then
    echo "sudo dnf install -y $dep"
  else
    echo ""
  fi
}

# 检查单个依赖；缺失时询问是否安装
# 返回 0 表示可用，返回 1 表示仍缺失
check_dep() {
  local dep="$1"
  if command -v "$dep" &>/dev/null; then
    echo "  ✓ $dep"
    return 0
  fi

  local hint install_cmd
  hint=$(dep_hint "$dep")
  install_cmd=$(auto_install_cmd "$dep")

  echo ""
  echo "  ⚠️  未找到依赖：$dep"
  [[ -n "$hint" ]] && echo "     参考：$hint"

  if [[ -n "$install_cmd" ]]; then
    read -r -p "  是否现在自动安装 $dep？($install_cmd) [y/N] " ans
    if [[ "$ans" =~ ^[Yy]$ ]]; then
      echo "  → 执行：$install_cmd"
      eval "$install_cmd"
      if command -v "$dep" &>/dev/null; then
        echo "  ✓ $dep 安装成功"
        return 0
      else
        echo "  ✗ $dep 安装失败，请手动安装后重试"
        return 1
      fi
    fi
  else
    echo "  未找到可用包管理器，无法自动安装，请手动安装 $dep 后重新运行安装脚本。"
  fi
  return 1
}

ask_multiselect() {
  # Sets REPLY_INDICES to selected 0-based indices
  local prompt="$1"; shift
  local -a items=("$@")
  REPLY_INDICES=()

  echo "$prompt"
  echo "  (输入序号，多个用空格分隔；直接回车 = 全选)"
  echo ""
  for i in "${!items[@]}"; do
    printf "  %d) %s\n" "$((i+1))" "${items[$i]}"
  done
  echo ""
  read -r -p "  > " input

  if [[ -z "$input" ]]; then
    for i in "${!items[@]}"; do REPLY_INDICES+=("$i"); done
  else
    for token in $input; do
      if [[ "$token" =~ ^[0-9]+$ ]] && (( token >= 1 && token <= ${#items[@]} )); then
        REPLY_INDICES+=("$((token-1))")
      fi
    done
  fi
}

detect_tool() {
  eval "${TOOL_DETECT[$1]}" 2>/dev/null
}

# 下载单个技能目录到目标路径（通过 tar 解压）
install_skill_dir() {
  local skill="$1" target_dir="$2"
  mkdir -p "$target_dir"
  echo "  ↓ 下载 $skill ..."
  curl -sL "$REPO_ARCHIVE" \
    | tar -xz --strip-components=2 \
         -C "$target_dir" \
         "scholar-kit-main/$skill"
  echo "  ✓ $skill → $target_dir/$skill"
}

# 下载 SKILL.md 并追加到目标文件
install_skill_append() {
  local skill="$1" target_file="$2"
  mkdir -p "$(dirname "$target_file")"
  echo "  ↓ 下载 $skill/SKILL.md ..."
  printf '\n<!-- scholar-kit: %s -->\n' "$skill" >> "$target_file"
  curl -sL "$REPO_BASE/$skill/SKILL.md" >> "$target_file"
  echo "  ✓ $skill → $target_file（已追加）"
}

# ── main ─────────────────────────────────────────────────────────────────────

echo ""
echo "scholar-kit 安装向导"
echo "===================="

# ── 核心依赖检查（curl / tar）────────────────────────────────────────────────
print_divider
echo "检查核心依赖..."
echo ""
CORE_OK=true
for _dep in curl tar; do
  check_dep "$_dep" || CORE_OK=false
done
if [[ "$CORE_OK" == "false" ]]; then
  echo ""
  echo "❌  缺少必要工具，安装中止。请安装上述依赖后重新运行脚本。"
  exit 1
fi

# Step 1: 选技能
print_divider
ask_multiselect "Step 1 — 选择要安装的技能：" "${SKILL_DESCS[@]}"
SELECTED_SKILLS=()
for idx in "${REPLY_INDICES[@]}"; do
  SELECTED_SKILLS+=("${ALL_SKILLS[$idx]}")
done

if [[ ${#SELECTED_SKILLS[@]} -eq 0 ]]; then
  echo "未选择任何技能，退出。"; exit 0
fi
echo ""
echo "已选技能：${SELECTED_SKILLS[*]}"

# Step 1.5: 检查技能依赖
print_divider
echo "Step 1.5 — 检查技能所需依赖..."
echo ""

# 收集所有已选技能的不重复依赖（排除已检查的 curl / tar）
SKILL_DEP_LIST=()
for _skill in "${SELECTED_SKILLS[@]}"; do
  for _dep in $(skill_deps "$_skill"); do
    [[ "$_dep" == "curl" || "$_dep" == "tar" ]] && continue
    _already=false
    for _d in "${SKILL_DEP_LIST[@]}"; do [[ "$_d" == "$_dep" ]] && _already=true && break; done
    [[ "$_already" == "false" ]] && SKILL_DEP_LIST+=("$_dep")
  done
done

if [[ ${#SKILL_DEP_LIST[@]} -eq 0 ]]; then
  echo "  所有技能依赖均已满足。"
else
  SKILL_DEPS_OK=true
  for _dep in "${SKILL_DEP_LIST[@]}"; do
    check_dep "$_dep" || SKILL_DEPS_OK=false
  done
  if [[ "$SKILL_DEPS_OK" == "false" ]]; then
    echo ""
    read -r -p "  部分依赖缺失，技能功能可能受限。是否仍继续安装？[y/N] " _ans
    if [[ ! "$_ans" =~ ^[Yy]$ ]]; then
      echo "安装中止。"
      exit 0
    fi
  fi
fi

# Step 2: 选工具（循环直到有至少一个可用）
while true; do
  print_divider
  ask_multiselect "Step 2 — 选择要安装到的 AI 工具：" "${TOOL_DESCS[@]}"
  SELECTED_TOOL_INDICES=("${REPLY_INDICES[@]}")

  if [[ ${#SELECTED_TOOL_INDICES[@]} -eq 0 ]]; then
    echo "未选择任何工具，退出。"; exit 0
  fi

  # 检测可用性
  VALID_TOOL_INDICES=()
  echo ""
  for idx in "${SELECTED_TOOL_INDICES[@]}"; do
    name="${TOOL_NAMES[$idx]}"
    if detect_tool "$idx"; then
      echo "  ✓ $name 已检测到"
      VALID_TOOL_INDICES+=("$idx")
    else
      echo "  ⚠️  未检测到 $name，已跳过"
      echo "     安装方式：${TOOL_URLS[$idx]}"
    fi
  done

  if [[ ${#VALID_TOOL_INDICES[@]} -gt 0 ]]; then
    break
  fi

  echo ""
  echo "❌  所选工具均未检测到，无法安装。"
  echo "    请重新选择已安装的工具，或按 Ctrl+C 退出。"
done

# Step 3: 执行安装
print_divider
echo "开始安装..."
echo ""

for idx in "${VALID_TOOL_INDICES[@]}"; do
  name="${TOOL_NAMES[$idx]}"
  echo "→ $name"
  for skill in "${SELECTED_SKILLS[@]}"; do
    case "$idx" in
      0) install_skill_dir "$skill" "$HOME/.claude/skills" ;;
      1) install_skill_dir "$skill" "$HOME/.opencode/skills" ;;
      2) install_skill_append "$skill" "$HOME/.codex/instructions.md" ;;
      3) install_skill_dir "$skill" "$HOME/.copilot/skills" ;;
    esac
  done
  echo ""
done

# Step 4: 完成
echo "安装完成！请重启对应的 AI 工具以激活技能。"
echo ""
echo "技能激活后，直接在对话中说出触发词即可使用："
echo "  - academic-writing：   \"帮我把 md 转成 docx\""
echo "  - scientific-drawing： \"帮我画一张架构图\""
echo "  - writing-style-check：\"帮我检查写作风格\""
