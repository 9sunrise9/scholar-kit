# paper-style-distiller

从论文样本中提取“可仿写”的风格资产，输出结构化风格画像，供下游写作技能直接使用。

## 11维治理与执行入口

- references/distillation-governance-v1.md（治理规则，含去重、质检、回退、人审、安全边界）
- references/style-distill-schema-v1.json（统一数据契约 v1）
- references/core5-execution-playbook.md（核心5维最小闭环执行）
- references/human-review-checklist.md（人工审核清单）
- references/run-manifest-template.json（复现与版本记录模板）
- references/blind-eval-ab-template.md（盲测 A/B 评分模板）

## 产出物

- style-profile.json（风格画像主文件）
- style-rules.md（规则与反例）
- sentence-patterns.jsonl（句型库，逐条可检索）
- paragraph-templates.json（段落模板库）
- retrieval-index.md（人工可读快速索引）

## 输出字段最小规范

句型项必须至少包含：

- id
- section
- intent
- tense
- pattern
- slots
- evidence
- confidence

段落模板项必须至少包含：

- id
- section
- intent
- skeleton
- block_order
- required_slots
- example_outline

## 快速检索示例

当写作技能需要“引言中的研究缺口句”时，优先按以下键查询：

- section=Introduction
- intent=Gap
- tense=present

当写作技能需要“讨论中的局限性段落模板”时：

- section=Discussion
- intent=Limitation

## 配合关系

与 style-guided-academic-writer 配套使用：先蒸馏，再写作。

## 建议执行顺序

1. 先按 core5-execution-playbook.md 跑核心5维闭环
2. 通过盲测 A/B 后，再扩展到完整 11 维
3. 每次运行都写 run-manifest，保证可复现

## 一键启动核心5维首轮

在仓库根目录运行：

```bash
RUN_ID="core5-$(date +%Y%m%d-%H%M%S)"
OUT_DIR="paper-style-distiller/runs/$RUN_ID"
python3 paper-style-distiller/scripts/run_core5_bootstrap.py \
	--sample-dir paper-style-distiller/samples/zotero-control-guidance-decision-top-journals \
	--out-dir "$OUT_DIR" \
	--manifest-template paper-style-distiller/references/run-manifest-template.json
```
