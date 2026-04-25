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
