---
name: paper-style-distiller
description: 论文风格蒸馏技能：从顶刊/顶会论文中抽取语言习惯、词汇偏好、句型模板、论证结构与时态偏好，产出可复用的风格画像与仿写规则。触发词："蒸馏论文风格"、"提取写作风格"、"做风格画像"、"style distill"。
---

# 论文风格蒸馏技能

## 目标

从给定论文样本中提炼可执行风格资产，用于后续写作对齐。

核心目标分为两部分：

1. 蒸馏质量：结论可复现、可解释、可执行。
2. 结果可检索：写作时能在 10 秒内定位到可用句型和段落模板。

治理与执行基线：

- 统一契约：references/style-distill-schema-v1.json
- 治理规则：references/distillation-governance-v1.md
- 核心闭环：references/core5-execution-playbook.md

## 输入

- 论文文本或段落样本（建议 >= 3 篇）
- 目标领域与期刊/会议
- 可选：仅分析章节（如 Introduction / Discussion）
- 可选：目标文体约束（保守/中性/激进）
- 可选：输出语言（中文/英文）

## 输出

- style-profile.json：风格画像主文件（供下游技能加载）
- style-rules.md：Do / Avoid 规则（带证据和反例）
- sentence-patterns.jsonl：句型库（逐条可检索）
- paragraph-templates.json：段落模板库（按章节和意图索引）
- retrieval-index.md：人工可读索引（快速查找）

必须保证每条句型/模板都带索引字段，至少包含：

- id：唯一编号（如 S-Intro-Gap-001）
- section：章节（Introduction/RelatedWork/Method/Results/Discussion/Conclusion）
- intent：意图（背景/缺口/贡献/方法/结果/局限/展望）
- tense：主要时态（past/present/present-perfect）
- pattern：抽象模板（必须带槽位）
- slots：槽位说明（如 problem, method, gain）
- evidence：来源证据（论文编号 + 段落编号）
- confidence：可信度（0-1）

## 工作流

### Step 0 — PDF 预处理（必须先于蒸馏执行）

将原始 PDF 转换为去噪的结构化 Markdown，供蒸馏脚本消费。

```bash
python3 scripts/preprocess_pdf_to_md.py \
  --sample-dir samples/papers \
  --out-dir    samples/preprocessed_md
```

预处理完成后输出 `samples/preprocessed_md/preprocess_report.md`，确认：
- 处理篇数与预期相符
- 无期望论文被跳过（检查 filter_journals 白名单）
- 字符数 > 5000（低于此值说明该 PDF 为损坏文件）

### Step 1–8 — 蒸馏主流程

1. 样本准入：检查样本数量、领域一致性、章节完整性。
2. 样本清洗：去除参考文献、公式噪声、图注噪声、无关脚注（Step 0 已完成）。
3. 结构分层：按段落功能打标签（背景/缺口/方法/结果/结论）。
4. 语言统计：术语、搭配、时态、句长、连接词、hedging 强度。
5. 句型归纳：抽取高频稳定句式并转为槽位模板。
6. 段落抽象：抽取常见段落推进路径并转为模板块。
7. 证据绑定：每条结论都绑定来源段落与出现频次（`source_paragraph_id` 必须为 `body:…`）。
8. 结果固化：输出画像、规则、句型库、段落库和检索索引。

蒸馏命令（加 `--preprocessed-dir` 读取 Step 0 输出）：

```bash
python3 scripts/run_core5_bootstrap.py \
  --sample-dir   samples/papers \
  --preprocessed-dir samples/preprocessed_md \
  --out-dir      runs
```

### Step 9 — 生成人工审查表（每次蒸馏后必须执行）

```bash
python3 scripts/generate_review_doc.py \
  --pkg runs/<run-id>/core5-distill-package.json \
  --out runs/<run-id>/distill-review.md
```

审查表位于 `runs/<run-id>/distill-review.md`，包含：
- 术语搭配（高频词组，可核查）
- 句型模板（带来源段落 ID）
- 创新论证条目（带 ✅/⚠️/❌ 评审列）
- 相关工作定位句式
- 段落推进路径模板
- 语料贡献统计（哪篇论文贡献了多少句型）

**必须由人工完成审查表评审后，才可进入 A/B 盲测。**

核心5维先行策略：

1. 先跑 macro blueprint、paragraph templates、claim-evidence binding、related-work positioning、innovation patterns。
2. 生成并完成人工审查（`distill-review.md`），修正 ❌ 条目后方可继续。
3. 跑盲测 A/B，通过后再扩展 11 维全量蒸馏。
4. 每次运行都输出 run manifest，记录版本、预算和阈值。

### Step 10 — 导出给写作技能（下游消费，必须在审查通过后执行）

人工审查通过且盲测达标后，使用 `export_for_writer.py` 把单文件 `distill-package.json`
拆成 `style-guided-academic-writer` 直接消费的 4 个产物：

```bash
python3 scripts/export_for_writer.py \
  --pkg     runs/<run-id>/full11-distill-package.json \
  --out-dir runs/<run-id>/writer-export/
```

脚本签名：

```
python3 export_for_writer.py --pkg <distill-package.json> --out-dir <dir> [--format json|yml] [--verbose]
```

参数：

- `--pkg`（必填）：distill-package.json 路径（core5 或 full11 包均可）。
- `--out-dir`（必填）：输出目录（不存在会自动创建）。
- `--format`：仅 `json` 已实现，`yml` 预留。
- `--verbose`：开启 DEBUG 日志。

在 `--out-dir` 下生成 4 个文件：

- `sentence-patterns.jsonl` — 一行一条 JSON 对象，字段：`id, section, intent, tense, pattern, slots (dict), evidence, confidence`。writer 可流式逐条加载。
- `paragraph-templates.json` — 结构化模板库，根节点包含 `templates` 数组与 `index_by_section`（按章节快速索引 template id）。
- `style-profile.json` — 高层风格画像：`tone, hedging_strength, dominant_tense, typical_sentence_length, terminology_preferences, section_coverage, intent_coverage, counts, metrics`。
- `retrieval-index.md` — 人工可读索引，按 `section × intent` 分组，每组最多展示 5 条按 confidence 排序的句型摘要与 1 条段落模板入口。

鲁棒性：

- 仅依赖标准库（`json, argparse, pathlib, logging, collections, statistics`），无外部依赖。
- 对缺字段（如 `block_order`、`example_hints`、`slots`）做降级而非失败；缺字段时记录 WARNING 后继续。
- 同时支持 core5（5 维）与 full11（11 维）两类包，包括 schema 在 `run_core5_bootstrap.py` 演进过程中产生的字段差异。

快速校验：

```bash
# 必须以 0 退出
python3 scripts/export_for_writer.py --help
# 4 个产物非空
ls -la runs/<run-id>/writer-export/
wc -l runs/<run-id>/writer-export/sentence-patterns.jsonl
```

## 蒸馏质量评估

每次蒸馏必须输出以下指标：

- coverage：模板覆盖率（样本段落中可解释比例）
- consistency：跨论文一致性（模板在不同论文复现比例）
- specificity：模板特异性（避免过度通用）
- leakage-risk：原句泄漏风险（避免抄写）
- actionability：可执行度（写作可直接调用比例）

建议阈值：

- coverage >= 0.70
- consistency >= 0.60
- leakage-risk <= 0.20

若未达到阈值，必须回退并重做第 5-7 步。

## 质量门槛

- 规则必须可执行，避免空泛描述。
- 模板必须保留语义槽位，避免抄原句。
- 输出必须标注样本覆盖范围与局限。
- 每条模板必须可通过 section + intent 快速检索。
- 所有输出字段命名必须稳定，便于下游自动消费。

## 检索组织约定

为了让写作技能快速查找信息，按以下优先级组织索引：

1. 一级索引：section
2. 二级索引：intent
3. 三级索引：tense
4. 四级索引：rhetorical-strength（soft/neutral/strong）

推荐检索键示例：

- Introduction:Gap:present:neutral
- Method:Contribution:present:strong
- Discussion:Limitation:present:soft
