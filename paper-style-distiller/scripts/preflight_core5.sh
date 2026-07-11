#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPTS_DIR="$ROOT_DIR/scripts"
REF_DIR="$ROOT_DIR/references"
SAMPLES_DIR="${SAMPLES_DIR:-$ROOT_DIR/samples/papers}"
PREPROCESSED_DIR="${PREPROCESSED_DIR:-$ROOT_DIR/samples/preprocessed_md}"
RUNS_DIR="${RUNS_DIR:-$ROOT_DIR/runs}"

echo "=== paper-style-distiller: 完整流程启动 ==="
echo "  样本目录:       $SAMPLES_DIR"
echo "  预处理输出目录: $PREPROCESSED_DIR"
echo "  Run 输出目录:   $RUNS_DIR"
echo ""

# ── 一、治理文件检查 ───────────────────────────────────────────────

required_files=(
  "$REF_DIR/distillation-governance-v1.md"
  "$REF_DIR/style-distill-schema-v1.json"
  "$REF_DIR/core5-execution-playbook.md"
  "$REF_DIR/human-review-checklist.md"
  "$REF_DIR/run-manifest-template.json"
)

missing=0
for file in "${required_files[@]}"; do
  if [[ ! -f "$file" ]]; then
    echo "MISSING: $file"
    missing=1
  fi
done

if [[ "$missing" -ne 0 ]]; then
  echo "Preflight failed: required governance files are missing."
  exit 1
fi

REF_DIR="$REF_DIR" python3 - <<'PY'
import json, os
from pathlib import Path
root = Path(os.environ["REF_DIR"])
for p in ["style-distill-schema-v1.json", "run-manifest-template.json"]:
    with open(root / p, "r", encoding="utf-8") as f:
        json.load(f)
print("JSON validation passed")
PY

echo "✅ 治理文件检查通过"

# ── 二、Step 0：PDF 预处理 ─────────────────────────────────────────

echo ""
echo "=== Step 0: PDF 预处理 ==="

if [[ ! -d "$SAMPLES_DIR" ]]; then
  echo "ERROR: 样本目录不存在: $SAMPLES_DIR"
  exit 1
fi

python3 "$SCRIPTS_DIR/preprocess_pdf_to_md.py" \
  --sample-dir "$SAMPLES_DIR" \
  --out-dir    "$PREPROCESSED_DIR"

echo "✅ Step 0 完成: 预处理结果位于 $PREPROCESSED_DIR"

# ── 三、Step 1–8：核心蒸馏 ────────────────────────────────────────

echo ""
echo "=== Step 1–8: 核心蒸馏 (Core-5 Bootstrap) ==="

python3 "$SCRIPTS_DIR/run_core5_bootstrap.py" \
  --sample-dir       "$SAMPLES_DIR" \
  --preprocessed-dir "$PREPROCESSED_DIR" \
  --out-dir          "$RUNS_DIR"

# 找到最新 run 目录
LATEST_RUN=$(ls -td "$RUNS_DIR"/core5-* 2>/dev/null | head -1)
if [[ -z "$LATEST_RUN" ]]; then
  echo "ERROR: 找不到蒸馏输出目录"
  exit 1
fi
PKG_FILE="$LATEST_RUN/core5-distill-package.json"
if [[ ! -f "$PKG_FILE" ]]; then
  echo "ERROR: 蒸馏包文件不存在: $PKG_FILE"
  exit 1
fi

echo "✅ Step 1–8 完成: 蒸馏包位于 $PKG_FILE"

# ── 四、Step 9：生成人工审查表 ────────────────────────────────────

echo ""
echo "=== Step 9: 生成人工审查表 ==="

REVIEW_FILE="$LATEST_RUN/distill-review.md"
python3 "$SCRIPTS_DIR/generate_review_doc.py" \
  --pkg "$PKG_FILE" \
  --out "$REVIEW_FILE"

echo "✅ 审查表已生成: $REVIEW_FILE"
echo ""
echo "=== 全流程完成 ==="
echo "下一步: 打开 $REVIEW_FILE，完成人工审查（§3 创新论证列填写 ✅/⚠️/❌）后进入 A/B 盲测。"

