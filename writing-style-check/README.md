# writing-style-check

学术写作风格检查技能。用于自动检测正文中的风格违规，并给出可执行的修改建议。

---

## 功能概述

基于 WSS-1 规范，脚本会检查以下四类问题：

- L：语言基调（宏大叙事、文学化比喻、代词误用、无来源数据等）
- P：段落结构（段首背景铺垫、列表引出不规范、并列标点错误等）
- T：技术内容组织（重点提示词不规范等）
- F：符号格式（引号/括号/缩写格式/加粗/破折号分节等）
- LX：词汇替换建议（基于词汇映射表给出口语到学术表达替换建议）

输出包含：规则编号、违规行号、原文片段、问题说明、修改建议与改写参考。

---

## 目录结构

```
writing-style-check/
├── README.md
├── SKILL.md
├── references/
│   ├── WritingStyle.md
│   └── lexicon-substitutions.zh-CN.json
└── scripts/
    └── writingstylecheck.py
```

---

## 环境要求

- Python 3.9+
- 无第三方依赖（仅使用 Python 标准库）

---

## 快速开始

在本目录下运行：

```bash
cd writing-style-check
python3 scripts/writingstylecheck.py --demo
```

---

## 使用方式

### 1) 检查文件

```bash
python3 scripts/writingstylecheck.py path/to/your.md
```

### 2) 检查一段文本

```bash
python3 scripts/writingstylecheck.py --text "你的文本"
```

### 3) 从标准输入读取

```bash
cat path/to/your.md | python3 scripts/writingstylecheck.py --stdin
```

### 4) 运行内置示例

```bash
python3 scripts/writingstylecheck.py --demo
```

### 5) 结构化 JSON 输出

```bash
python3 scripts/writingstylecheck.py path/to/your.md --format json
```

### 6) 低风险自动修复

```bash
python3 scripts/writingstylecheck.py path/to/your.md --fix
python3 scripts/writingstylecheck.py path/to/your.md --fix --format json
python3 scripts/writingstylecheck.py path/to/your.md --fix-dry-run
```

---

## 结果解读

报告中每条违规均包含规则编号（如 L1.2、P3、F2）。建议按以下顺序处理：

1. 先修复 L（语言基调）和 P（结构）问题，避免全文风格偏差。
2. 再修复 F（符号）问题，统一版式与术语表达。
3. 最后逐段复读，确认改写后语义未偏移。

输出采用 pep8 风格（便于快速定位与批量修复）：

```text
<path>:<line>:<col>: <code> 条目:<rule_id> <message>
```

代码含义：

- `E-*`：Error，对应 MUST 级规则
- `W-*`：Warning，对应 SHOULD 级建议（如词汇替换 LX）

`--format json` 时输出包含：

- `summary`：总数/错误数/警告数/代码统计
- `fix`：是否启用自动修复、修复统计、是否写回文件
- `violations`：逐条问题（含 code、rule_id、line、col、message、suggestion）

`--fix` 当前仅执行低风险修复：

- ASCII 引号替换为中文引号
- 半角括号替换为全角括号
- 去除 Markdown 加粗标记
- 常见提示短语规范化
- 词汇映射中的短词保守替换

`--fix-dry-run` 会执行同样的修复计算与复检，但不会写回文件。

示例：

```text
chapter3.md:42:1: E-L1.1 条目:L1.1 段落不得以感叹式/背景铺垫开头（L1.1）
chapter3.md:77:15: W-LX1 条目:LX1 检测到可替换表达：可落地
```

---

## 相关文件

- `SKILL.md`：技能定义与触发说明
- `references/WritingStyle.md`：完整规范条款
- `references/lexicon-substitutions.zh-CN.json`：词汇替换与说法替换映射表
- `scripts/writingstylecheck.py`：检查脚本
