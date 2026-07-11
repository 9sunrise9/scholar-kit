#!/usr/bin/env python3
"""
生成蒸馏结果人工审查表
输入: core5-distill-package.json
输出: distill-review-{runid}.md  ← 人工可读、可评判的质量审查文档

审查表结构：
  §1  术语搭配    – 高频词组（含出处，可核查）
  §2  句型模板    – 按 section×intent 分组，每条带原文出处
  §3  创新论证    – claim + mechanism + gain + boundary（带来源句）
  §4  相关工作定位 – 已有研究描述模式
  §5  段落推进路径 – 段落层模板
  §6  覆盖统计    – 每篇论文贡献的句型数量
  §7  人工评审指引 – 告诉评审者看什么、打什么分
"""

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


# ── 辅助函数 ──────────────────────────────────────────────────────────────

def load_package(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def clean_pattern(pat: str) -> str:
    """将 {num} 还原为更可读的占位符，限长 300 字符。"""
    pat = re.sub(r"\{num\}", "[N]", pat)
    if len(pat) > 300:
        return pat[:297] + "..."
    return pat


def paper_short(paper_id: str) -> str:
    """从文件名中提取简短论文标识（年份+前4词）。"""
    name = Path(paper_id).stem
    # 例：2022_S9EDH2DH_Adaptive Prescribed-Time Control...
    parts = name.split("_", 2)
    if len(parts) >= 3:
        year = parts[0]
        words = parts[2].replace("_", " ").split()[:5]
        return f"{year} {' '.join(words)}"
    return name[:60]


def extract_bigrams(patterns: list[dict]) -> Counter:
    """从句型模板中统计高频词组（2-gram），用于术语搭配分析。"""
    counter: Counter = Counter()
    for p in patterns:
        text = p.get("pattern", "")
        # 去除槽位占位符
        text = re.sub(r"\{[^}]+\}", " ", text)
        words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
        for i in range(len(words) - 1):
            bg = f"{words[i]} {words[i+1]}"
            counter[bg] += 1
    return counter


def group_patterns_by_section_intent(patterns: list[dict]) -> dict:
    """按 section + intent 分组句型，返回嵌套 dict。"""
    grouped: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    for p in patterns:
        # 归一化 section 名（去掉罗马数字前缀）
        raw_sec = p.get("section", "Unknown")
        sec = re.sub(r"^(I{1,3}V?|V?I{0,3}|\d+)\.\s*", "", raw_sec).strip()
        if not sec or sec == "Unknown":
            # 尝试从 source_paragraph_id 中推断
            src = p.get("evidence", [{}])[0].get("source_paragraph_id", "")
            if "body:" in src:
                parts = src.split(":")
                sec = parts[1] if len(parts) > 1 else "Unknown"
        sec = sec.title() if sec else "Unknown"
        intent = p.get("intent", "Background")
        grouped[sec][intent].append(p)
    return {k: dict(v) for k, v in grouped.items()}


def paper_contribution_stats(patterns: list[dict]) -> Counter:
    """统计每篇论文贡献的句型数量。"""
    counter: Counter = Counter()
    for p in patterns:
        src = p.get("evidence", [{}])[0].get("source_paper_id", "unknown")
        counter[src] += 1
    return counter


def format_innovation_type_badge(itype: str) -> str:
    badges = {
        "theory":    "📐 theory",
        "algorithm": "⚙️ algorithm",
        "observer":  "👁️ observer",
        "learning":  "🧠 learning",
        "method":    "🔧 method",
    }
    return badges.get(itype, f"🔧 {itype}")


# ── 各章节生成 ────────────────────────────────────────────────────────────

def section_meta(pkg: dict) -> str:
    manifest = pkg.get("run_manifest", {})
    metrics  = pkg.get("metrics", {})
    lines = [
        "## 元信息\n",
        f"| 字段 | 值 |",
        f"|------|---|",
        f"| Run ID | `{manifest.get('run_id', 'N/A')}` |",
        f"| 时间戳 | {manifest.get('run_timestamp', 'N/A')} |",
        f"| 操作者 | {manifest.get('operator', 'N/A')} |",
        f"| 语料哈希 | `{pkg.get('run_manifest', {}).get('source_corpus_hash', 'N/A')[:16]}...` |",
        f"| 句型数 | {len(pkg.get('sentence_patterns', []))} |",
        f"| 创新模式数 | {len(pkg.get('innovation_patterns', []))} |",
        f"| Claim 绑定数 | {len(pkg.get('claim_evidence_bindings', []))} |",
        "",
        "### 质量指标\n",
        f"| 指标 | 值 | 阈值 | 状态 |",
        f"|------|-----|------|------|",
    ]
    thresholds = {
        "coverage": (0.70, ">="),
        "consistency": (0.60, ">="),
        "actionability": (0.60, ">="),
        "leakage_risk": (0.20, "<="),
    }
    for k, v in metrics.items():
        thr, op = thresholds.get(k, (None, None))
        if thr is not None:
            ok = (v >= thr) if op == ">=" else (v <= thr)
            status = "✅ pass" if ok else "❌ fail"
        else:
            status = "—"
        lines.append(f"| {k} | {v} | {thr or '—'} | {status} |")
    return "\n".join(lines)


def section_terminology(patterns: list[dict], top_n: int = 30) -> str:
    bigrams = extract_bigrams(patterns)
    lines = [
        "## §1 术语搭配\n",
        "> **评审要点**：词组是否是该领域真实高频搭配？有无明显噪声词组（如页眉残留）？\n",
        f"| 排名 | 词组 | 出现次数 |",
        f"|------|------|---------|",
    ]
    for i, (bg, cnt) in enumerate(bigrams.most_common(top_n), 1):
        lines.append(f"| {i} | `{bg}` | {cnt} |")
    return "\n".join(lines)


def section_sentence_patterns(patterns: list[dict]) -> str:
    grouped = group_patterns_by_section_intent(patterns)
    lines = [
        "## §2 句型模板（按章节×意图分组）\n",
        "> **评审要点**：  \n"
        "> 1. 模板是否保留了语义槽位而非抄写原句？  \n"
        "> 2. `section` 归属是否准确？  \n"
        "> 3. `intent` 分类是否正确（背景/缺口/贡献/结果/局限）？  \n"
        "> 4. 出处 `source_paragraph_id` 是否来自正文（body:…）而非 head_pages？\n",
    ]

    # 按优先章节顺序排列
    section_order = ["Introduction", "Related Work", "Relatedwork", "Method",
                     "Results", "Simulation", "Conclusion", "Discussion", "Unknown"]
    all_secs = list(grouped.keys())
    ordered = [s for s in section_order if s in all_secs]
    ordered += [s for s in all_secs if s not in ordered]

    for sec in ordered:
        intent_map = grouped[sec]
        lines.append(f"\n### 2.{sec}\n")
        for intent, plist in sorted(intent_map.items()):
            lines.append(f"#### {intent} ({len(plist)} 条)\n")
            for p in plist[:8]:  # 每组最多显示8条
                ev = p.get("evidence", [{}])[0]
                src_id  = ev.get("source_paragraph_id", "?")
                src_paper = paper_short(ev.get("source_paper_id", "?"))
                conf = p.get("confidence", 0)
                pat  = clean_pattern(p.get("pattern", ""))
                lines.append(f"**[{p['id']}]** conf={conf:.2f} | 来源: `{src_paper}`")
                lines.append(f"```")
                lines.append(pat)
                lines.append(f"```")
                lines.append(f"<sub>出处段落: `{src_id}`</sub>\n")
            if len(plist) > 8:
                lines.append(f"_… 还有 {len(plist)-8} 条，见 JSON 包_\n")
    return "\n".join(lines)


def section_innovation(innov: list[dict], claims: list[dict]) -> str:
    # 建立 claim_id → claim_text 映射
    claim_map = {c["claim_id"]: c["claim_text"] for c in claims}

    lines = [
        "## §3 创新论证表达\n",
        "> **评审要点**：  \n"
        "> 1. `claim_pattern` 是否是真实的贡献陈述句（非结构句、非页眉）？  \n"
        "> 2. `mechanism_pattern` 是否与该行的创新类型匹配？  \n"
        "> 3. `gain_pattern` / `boundary_pattern` 是否有领域特异性？  \n"
        "> ⚠️ 标记「需修改」的行请在审查列的 ✅/❌ 列填写。\n",
        "",
        "| ID | 类型 | claim（原文节选≤180字）| mechanism | gain | boundary | 审查 |",
        "|----|----|----------------------|-----------|------|----------|------|",
    ]

    for inn in innov:
        itype = format_innovation_type_badge(inn.get("innovation_type", "method"))
        claim = inn.get("claim_pattern", "")[:180].replace("|", "｜").replace("\n", " ")
        mech  = inn.get("mechanism_pattern", "")[:120].replace("|", "｜")
        gain  = inn.get("gain_pattern", "")[:100].replace("|", "｜")
        bnd   = inn.get("boundary_pattern", "")[:100].replace("|", "｜")
        lines.append(f"| **{inn['id']}** | {itype} | {claim} | {mech} | {gain} | {bnd} | □ |")

    return "\n".join(lines)


def section_related_work(patterns: list[dict]) -> str:
    """从句型中筛选相关工作定位类句式。"""
    rw_keywords = ["prior", "existing", "previous", "recent", "literature",
                   "have been", "have proposed", "have shown", "however",
                   "while", "although", "in contrast", "unlike"]

    rw_pats = []
    for p in patterns:
        text = p.get("pattern", "").lower()
        if any(k in text for k in rw_keywords):
            sec = p.get("section", "")
            if any(s in sec.lower() for s in ["intro", "relat", "background", "unknown"]):
                rw_pats.append(p)

    lines = [
        "## §4 相关工作定位\n",
        "> **评审要点**：句式是否体现了典型的「现有工作 -> 不足 -> 我方切入」推进逻辑？\n",
    ]
    if not rw_pats:
        lines.append("_（本次蒸馏未检测到相关工作定位模式，可能需要增加 Related Work 章节论文样本）_\n")
    else:
        for p in rw_pats[:10]:
            ev = p.get("evidence", [{}])[0]
            src = paper_short(ev.get("source_paper_id", "?"))
            pat = clean_pattern(p.get("pattern", ""))
            lines.append(f"**[{p['id']}]** 来源: `{src}`")
            lines.append(f"```")
            lines.append(pat)
            lines.append(f"```\n")
    return "\n".join(lines)


def section_paragraph_templates(tmpls: list[dict]) -> str:
    lines = [
        "## §5 段落推进路径（段落层模板）\n",
        "> **评审要点**：  \n"
        "> 1. 模板的槽位是否覆盖了该章节的核心写作要素？  \n"
        "> 2. 模板填入后能否直接生成可读段落（不需大幅改写）？\n",
    ]
    for t in tmpls:
        slots_str = ", ".join(f"`{{{s}}}`" for s in t.get("required_slots", []))
        opt_str   = ", ".join(f"`{{{s}}}`" for s in t.get("optional_slots", []))
        lines += [
            f"\n### [{t['id']}] {t.get('section','?')} — {t.get('intent','?')} (conf={t.get('confidence',0):.2f})\n",
            f"```",
            t.get("template", ""),
            f"```",
            f"- **必填槽位**: {slots_str or '（无）'}",
            f"- **可选槽位**: {opt_str or '（无）'}",
            f"- **证据样本数**: {t.get('evidence_count', '?')}",
        ]
    return "\n".join(lines)


def section_coverage_stats(patterns: list[dict]) -> str:
    stats = paper_contribution_stats(patterns)
    lines = [
        "## §6 语料贡献统计\n",
        "> 用于判断蒸馏是否「依赖单篇」——若某篇占比 > 40%，结果可能偏向该篇风格。\n",
        f"| 论文 | 贡献句型数 | 占比 |",
        f"|------|-----------|------|",
    ]
    total = sum(stats.values()) or 1
    for src, cnt in stats.most_common():
        short = paper_short(src)
        pct = cnt / total * 100
        bar = "█" * int(pct / 5)
        lines.append(f"| {short} | {cnt} | {pct:.1f}% {bar} |")
    return "\n".join(lines)


def section_review_guide() -> str:
    return """## §7 人工评审指引

### 快速判定标准

| 维度 | ✅ 合格 | ❌ 需修改 |
|------|--------|---------|
| **句型来源** | `source_paragraph_id` 包含 `body:` | 包含 `head_pages` |
| **claim 真实性** | 是论文贡献陈述句 | 是结构句 / 页眉残留 / 仅含 "in this paper" |
| **mechanism 特异性** | 包含领域关键词（convex/Lyapunov/adaptive…）| 完全通用模板（We achieve {objective}…）|
| **术语词组** | 是该领域真实搭配 | 含页码/作者名/OCR噪声 |
| **章节归属** | section 与实际内容匹配 | "Unknown" 占比 > 30% |

### 建议评分方式

对每个 §3 创新论证行，在「审查」列填：
- **✅** — 可直接用
- **⚠️** — 需小幅修改 claim 或 mechanism
- **❌** — 噪声，建议删除

### 修改后操作

1. 记录需删除/修改的 ID（如 I-013, S-004）
2. 在 `core5-distill-package.json` 中直接编辑对应条目
3. 重新运行 `generate_review_doc.py` 验证改动结果
"""


# ── 主函数 ────────────────────────────────────────────────────────────────

def build_review_doc(pkg_path: Path, out_path: Path) -> None:
    pkg = load_package(pkg_path)

    patterns = pkg.get("sentence_patterns", [])
    innov    = pkg.get("innovation_patterns", [])
    claims   = pkg.get("claim_evidence_bindings", [])
    tmpls    = pkg.get("paragraph_templates", [])
    manifest = pkg.get("run_manifest", {})
    run_id   = manifest.get("run_id", "unknown")

    doc_parts = [
        f"# 蒸馏结果人工审查表\n",
        f"> 自动生成 | Run: `{run_id}` | 包文件: `{pkg_path.name}`  \n",
        f"> ⚠️ 本文档仅供质量评判，不是写作输出物。请在 §3 审查列填写 ✅/⚠️/❌ 后反馈。\n",
        "",
        section_meta(pkg),
        "",
        "---\n",
        section_terminology(patterns),
        "",
        "---\n",
        section_sentence_patterns(patterns),
        "",
        "---\n",
        section_innovation(innov, claims),
        "",
        "---\n",
        section_related_work(patterns),
        "",
        "---\n",
        section_paragraph_templates(tmpls),
        "",
        "---\n",
        section_coverage_stats(patterns),
        "",
        "---\n",
        section_review_guide(),
    ]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(doc_parts), encoding="utf-8")
    print(f"[review-doc] → {out_path}  ({out_path.stat().st_size // 1024} KB)")


def main():
    parser = argparse.ArgumentParser(description="生成蒸馏结果人工审查 Markdown 文档")
    parser.add_argument("--pkg",     required=True, help="core5-distill-package.json 路径")
    parser.add_argument("--out",     required=True, help="输出审查表 .md 路径")
    args = parser.parse_args()
    build_review_doc(Path(args.pkg), Path(args.out))


if __name__ == "__main__":
    main()
