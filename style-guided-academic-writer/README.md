# style-guided-academic-writer

根据蒸馏结果执行学术写作或改写，强调“结构逻辑 + 语言风格”双对齐。

## 输入要求

- 任务说明
- 来自 `paper-style-distiller` 的蒸馏包 JSON（必需，至少包含 `paragraph_templates` 与 `sentence_patterns`）
- 可选：已有草稿（Markdown），用于改写与对齐校验

## 快速查找推荐

优先按以下键检索模板：

- section
- intent
- tense
- rhetorical-strength

示例：

- Introduction + Gap + present
- Method + Contribution + present
- Discussion + Limitation + present

## 配套脚本

`scripts/` 目录下提供两个 CLI 工具，均仅依赖 Python 标准库：

- `scripts/retrieve_templates.py` — 按 section/intent/tense/strength 检索段落模板与句型。
- `scripts/apply_style_to_draft.py` — 对 Markdown 草稿逐段做风格对齐，输出对齐报告。
- `scripts/_pkg_loader.py` — 共用的蒸馏包加载与归一化模块。

```bash
# 1) 检索：找 Introduction/Gap 段落模板
python3 scripts/retrieve_templates.py \
  --pkg ../paper-style-distiller/runs/full11-core5-20260518-230538/full11-distill-package.json \
  --section Introduction --intent Gap --kind paragraph --format table

# 2) 对齐：对草稿生成对齐报告
python3 scripts/apply_style_to_draft.py \
  --pkg ../paper-style-distiller/runs/full11-core5-20260518-230538/full11-distill-package.json \
  --draft samples/draft-illustration.md --format markdown
```

每个脚本支持 `--help` 与 `--verbose`。详细工作流与示例见 `SKILL.md`。

## 配合关系

建议先运行 paper-style-distiller，再运行本技能。
