---
name: style-guided-academic-writer
description: 风格驱动学术写作技能：基于蒸馏得到的风格画像进行新稿写作或改写，输出高一致性的学术文本与对齐说明。触发词："按蒸馏风格写作"、"风格仿写"、"style-guided writing"。
---

# 风格驱动学术写作技能

## 目标

在保证内容准确的前提下，让新稿与目标论文群风格保持一致。

## 输入

- 写作任务（主题、受众、字数、章节）
- 来自 paper-style-distiller 的风格画像
- 来自 paper-style-distiller 的句型库与段落模板库
- 可选：已有草稿（用于改写）

## 输出

- 写作结果（新稿或改写稿）
- 风格对齐说明（段落级）
- 偏差清单（与风格画像不一致项）
- 模板命中清单（本次写作调用了哪些句型/段落模板）

## 写作约束

- 优先对齐论证逻辑，再对齐词句表层。
- 严禁逐句复刻源论文表达。
- 术语一致性优先于修辞变化。
- 保留学术可读性，避免模板化堆砌。

## 工作流

1. 读取风格画像与任务约束。
2. 基于 section + intent + tense 检索句型与段落模板。
3. 生成段落级写作蓝图。
4. 产出草稿并做风格一致性校验。
5. 输出终稿、对齐说明与模板命中清单。

### 配套脚本（`scripts/`）

技能自带两个 CLI 脚本，承担上述工作流中"检索"和"校验"两步，避免手工翻 JSON。

#### 1. `retrieve_templates.py` —— 检索段落模板与句型

按 `section` → `intent` → `tense` → `rhetorical-strength` 顺序检索蒸馏包，并按
"放宽 rhetorical-strength → 放宽 tense → 仅按 section+intent"的回退策略兜底。
支持表格与 JSON 两种输出。

```bash
# 摘要：确认蒸馏包完整、字段完整
python3 style-guided-academic-writer/scripts/retrieve_templates.py \
  --pkg paper-style-distiller/runs/full11-core5-20260518-230538/full11-distill-package.json \
  --summary

# 检索 Introduction + Gap 段落模板
python3 style-guided-academic-writer/scripts/retrieve_templates.py \
  --pkg paper-style-distiller/runs/full11-core5-20260518-230538/full11-distill-package.json \
  --section Introduction --intent Gap --kind paragraph --format table

# 检索高置信、强语气、现在时的句型（限制 5 条，JSON 输出便于管线消费）
python3 style-guided-academic-writer/scripts/retrieve_templates.py \
  --pkg runs/full11-distill-package.json \
  --section Method --intent Contribution \
  --tense present --rhetorical-strength strong \
  --min-confidence 0.8 --limit 5 --format json
```

#### 2. `apply_style_to_draft.py` —— 对草稿做段落级对齐

将草稿 Markdown 按段拆分，自动从最近的 `#`/`##`/`###` 标题识别
`section`，对每段做模板与句型匹配，并产出对齐报告（Markdown 或 JSON）。
报告包含每段的：识别到的章节、猜测的 intent、最匹配的段落模板与句型、
以及风格偏差与改进建议。

```bash
# 把对齐报告写到 stdout
python3 style-guided-academic-writer/scripts/apply_style_to_draft.py \
  --pkg runs/full11-distill-package.json \
  --draft style-guided-academic-writer/samples/draft-illustration.md

# 写入文件并用 --section-hints 修正歧义章节
python3 style-guided-academic-writer/scripts/apply_style_to_draft.py \
  --pkg runs/full11-distill-package.json \
  --draft my-paper.md \
  --output runs/my-paper-alignment.md \
  --section-hints "0=Introduction,3=Method,7=Discussion"

# JSON 报告便于自动化消费
python3 style-guided-academic-writer/scripts/apply_style_to_draft.py \
  --pkg runs/full11-distill-package.json \
  --draft my-paper.md --format json > alignment.json
```

两个脚本均：

* 仅依赖 Python 标准库（`argparse`、`json`、`logging`、`dataclasses`、`re`、`pathlib`）。
* 在解析失败或字段缺失时打印明确错误而非崩溃。
* 用 `--verbose` 打开 DEBUG 日志，用 `--help` 查看完整选项。

## 快速检索规则

默认检索顺序：

1. section
2. intent
3. tense
4. rhetorical-strength

检索失败时回退策略：

1. 放宽 rhetorical-strength
2. 放宽 tense
3. 仅按 section + intent 选择最高 confidence 模板

## 模板调用约束

- 优先使用 paragraph-templates.json 的骨架组织段落。
- 句子生成时优先调用 sentence-patterns.jsonl 的高置信模板。
- 每段至少命中 1 个段落模板或 2 个句型模板。
- 每个模板调用后记录 template_id，写入命中清单。

## 对齐报告要求

对齐说明至少包含：

- 段落编号
- 使用的模板 id 列表
- 对齐维度（逻辑/时态/词汇/句型）
- 偏差项与修正建议
