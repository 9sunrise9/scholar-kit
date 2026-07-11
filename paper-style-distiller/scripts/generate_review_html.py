#!/usr/bin/env python3
"""
生成蒸馏结果 HTML 人工审查报告
输入: core5-distill-package.json
输出: distill-review.html  ← 可在浏览器打开的交互式审查页面

特性：
  - 标签页导航（§1–§7）
  - §3 创新论证带内联打分复选框（可保存到 localStorage）
  - 质量指标可视化（进度条）
  - 全文检索句型
  - 语料分布条形图
  - 按类型过滤创新模式
"""

import argparse
import json
import re
import html as htmllib
from collections import Counter
from pathlib import Path


# ── 工具函数 ──────────────────────────────────────────────────────────────

def h(text: str) -> str:
    """HTML 转义"""
    return htmllib.escape(str(text), quote=True)

def paper_short(paper_id: str) -> str:
    name = Path(paper_id).stem
    parts = name.split("_", 2)
    if len(parts) >= 3:
        year = parts[0]
        words = parts[2].replace("_", " ").split()[:4]
        return f"{year} · {' '.join(words)}"
    return name[:60]

def innovation_badge(itype: str) -> str:
    cfg = {
        "theory":    ("badge-theory",    "📐 theory"),
        "algorithm": ("badge-algo",      "⚙️ algorithm"),
        "observer":  ("badge-observer",  "👁 observer"),
        "learning":  ("badge-learning",  "🧠 learning"),
        "method":    ("badge-method",    "🔧 method"),
    }
    cls, label = cfg.get(itype, ("badge-method", f"🔧 {itype}"))
    return f'<span class="badge {cls}">{h(label)}</span>'

def clean_pattern(pat: str) -> str:
    if len(pat) > 400:
        return pat[:397] + "…"
    return pat


def prettify_formula_text(text: str) -> str:
  """仅用于前端展示的轻量公式修复，不修改原始蒸馏数据。"""
  s = clean_pattern(text or "")

  # 常见占位符
  s = s.replace("{num}", "n")

  # Big-O 常见表达
  s = re.sub(r"O\(\s*T\s*\^?\s*n\s*\)", r"$O(T^n)$", s)
  s = re.sub(r"O\(\s*T\s*\)", r"$O(T)$", s)

  # 常见离散索引表达
  s = re.sub(r"\bxk\+n\b", r"$x_{k+n}$", s)
  s = re.sub(r"\buk\b", r"$u_k$", s)
  s = re.sub(r"\bdk\b", r"$d_k$", s)

  # 常见导数 OCR 写法
  s = s.replace("_x(t)", "$\\dot{x}(t)$")
  s = s.replace("_mt", "$\\dot{m}(t)$")

  # 向量空间写法
  s = re.sub(r"\bIRn\b", r"$\\mathbb{R}^n$", s)

  return s


def render_review_buttons(review_id: str) -> str:
  """为任意卡片渲染统一的 ✅/⚠️/❌ 评审按钮组。"""
  rid = h(review_id)
  return f"""
<div class="review-btn-group" data-review-id="{rid}">
  <button class="review-btn" data-verdict="ok" title="可直接用" onclick="setReview(this,'ok')">✅</button>
  <button class="review-btn" data-verdict="warn" title="需小幅修改" onclick="setReview(this,'warn')">⚠️</button>
  <button class="review-btn" data-verdict="bad" title="噪声，删除" onclick="setReview(this,'bad')">❌</button>
</div>"""

def extract_bigrams(patterns: list) -> Counter:
    counter: Counter = Counter()
    for p in patterns:
        text = p.get("pattern", "")
        text = re.sub(r"\{[^}]+\}", " ", text)
        words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
        for i in range(len(words) - 1):
            counter[f"{words[i]} {words[i+1]}"] += 1
    return counter

def paper_contribution_stats(patterns: list) -> Counter:
    counter: Counter = Counter()
    for p in patterns:
        src = p.get("evidence", [{}])[0].get("source_paper_id", "unknown")
        counter[src] += 1
    return counter

def group_by_section_intent(patterns: list) -> dict:
    from collections import defaultdict
    g: dict = defaultdict(lambda: defaultdict(list))
    for p in patterns:
        raw_sec = p.get("section", "Unknown")
        sec = re.sub(r"^(I{1,3}V?|V?I{0,3}|\d+)\.\s*", "", raw_sec).strip()
        sec = sec.title() if sec else "Unknown"
        g[sec][p.get("intent", "Background")].append(p)
    return {k: dict(v) for k, v in g.items()}


# ── CSS ────────────────────────────────────────────────────────────────────

CSS = """
:root {
  --bg: #f8fafc;
  --surface: #ffffff;
  --surface2: #f8fafc;
  --border: #e2e8f0;
  --text: #1e293b;
  --muted: #64748b;
  --accent: #1e40af;
  --accent2: #3b82f6;
  --green: #16a34a;
  --red: #dc2626;
  --yellow: #ca8a04;
  --orange: #ea580c;
  --cyan: #0284c7;
  --font: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --mono: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: var(--font);
  background: var(--bg);
  color: var(--text);
  font-size: 14px;
  line-height: 1.6;
}

body.theme-dark {
  --bg: #0f172a;
  --surface: #111827;
  --surface2: #1f2937;
  --border: #374151;
  --text: #e5e7eb;
  --muted: #9ca3af;
  --accent: #60a5fa;
  --accent2: #93c5fd;
  --green: #22c55e;
  --red: #ef4444;
  --yellow: #f59e0b;
  --orange: #fb923c;
  --cyan: #67e8f9;
}

.layout { display: flex; min-height: 100vh; }

.layout.sidebar-hidden .sidebar {
  width: 0;
  padding: 0;
  border-right: 0;
  overflow: hidden;
}

.layout.sidebar-hidden .main {
  max-width: 1280px;
}

/* ── SIDEBAR ── */
.sidebar {
  width: 220px;
  background: var(--surface);
  border-right: 1px solid var(--border);
  padding: 24px 0;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  flex-shrink: 0;
}

.sidebar,
.metric-card,
.guide-card,
.pattern-card,
.tmpl-card,
.rw-card,
.review-tip,
.innov-table-wrap,
.bigram-item,
.save-bar {
  box-shadow: 0 1px 3px rgba(0,0,0,.06);
}

.sidebar h1 {
  font-size: 13px;
  font-weight: 700;
  letter-spacing: .06em;
  text-transform: uppercase;
  color: var(--accent);
  padding: 0 20px 16px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 8px;
}

.nav-item {
  display: block;
  padding: 8px 20px;
  color: var(--muted);
  text-decoration: none;
  font-size: 13px;
  border-left: 3px solid transparent;
  transition: all .15s;
  cursor: pointer;
}
.nav-item:hover { color: var(--text); background: var(--surface2); }
.nav-item.active { color: var(--accent); border-left-color: var(--accent); background: var(--surface2); font-weight: 600; }

.sidebar-meta { padding: 16px 20px; font-size: 11px; color: var(--muted); border-top: 1px solid var(--border); margin-top: auto; }

/* ── MAIN ── */
.main {
  flex: 1;
  padding: 32px 40px;
  max-width: 1100px;
}

.sidebar-toggle {
  position: sticky;
  top: 10px;
  z-index: 30;
  margin-bottom: 12px;
  background: var(--surface2);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 7px 12px;
  font-size: 12px;
  cursor: pointer;
}
.sidebar-toggle:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.theme-toggle {
  position: sticky;
  top: 10px;
  z-index: 30;
  margin-left: 8px;
  margin-bottom: 12px;
  background: var(--surface2);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 7px 12px;
  font-size: 12px;
  cursor: pointer;
}
.theme-toggle:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.section { display: none; }
.section.active { display: block; }

/* ── HEADER ── */
.page-header {
  margin-bottom: 32px;
}
.page-header h2 {
  font-size: 22px;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 6px;
}
.page-header .run-id {
  font-family: var(--mono);
  font-size: 12px;
  color: var(--muted);
}
.page-header .warning {
  margin-top: 10px;
  padding: 10px 14px;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 6px;
  font-size: 13px;
  color: #1e3a8a;
}

/* ── METRIC CARDS ── */
.metric-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
  margin: 20px 0;
}
.metric-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px;
}
.metric-card .label { font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: .06em; }
.metric-card .value { font-size: 28px; font-weight: 700; font-family: var(--mono); margin: 4px 0; }
.metric-card .sub { font-size: 12px; color: var(--muted); }
.metric-card.pass .value { color: var(--green); }
.metric-card.fail .value { color: var(--red); }
.metric-card.info .value { color: var(--accent); }

.progress-row {
  margin: 8px 0;
}
.progress-label {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--muted);
  margin-bottom: 4px;
}
.progress-label span:last-child { font-family: var(--mono); color: var(--text); }
.progress-bar {
  height: 6px;
  background: var(--border);
  border-radius: 3px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  border-radius: 3px;
  transition: width .4s ease;
}
.fill-green { background: var(--green); }
.fill-red   { background: var(--red); }
.fill-accent { background: var(--accent); }
.fill-yellow { background: var(--yellow); }

/* ── INFO TABLE ── */
.info-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  margin: 16px 0;
}
.info-table td {
  padding: 8px 12px;
  border-bottom: 1px solid var(--border);
}
.info-table td:first-child { color: var(--muted); width: 180px; }
.info-table code {
  font-family: var(--mono);
  font-size: 12px;
  background: var(--surface2);
  padding: 2px 6px;
  border-radius: 4px;
  color: var(--cyan);
}

/* ── SECTION HEADING ── */
.section-heading {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 6px;
  color: var(--text);
  display: flex;
  align-items: center;
  gap: 10px;
}
.section-heading .sect-num {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: var(--accent);
  border-radius: 6px;
  font-size: 13px;
  font-weight: 800;
  color: #fff;
}

.review-tip {
  background: var(--surface);
  border: 1px solid var(--border);
  border-left: 3px solid var(--accent2);
  border-radius: 6px;
  padding: 12px 16px;
  margin: 12px 0 20px;
  font-size: 13px;
  color: var(--muted);
  line-height: 1.7;
}
.review-tip strong { color: var(--text); }

/* ── BIGRAM TABLE ── */
.bigram-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 8px;
  margin: 16px 0;
}
.bigram-item {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 10px 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.bigram-item .phrase {
  font-family: var(--mono);
  font-size: 12px;
  color: var(--cyan);
}
.bigram-item .count {
  font-size: 11px;
  font-weight: 700;
  color: var(--muted);
  background: var(--surface2);
  padding: 2px 7px;
  border-radius: 10px;
}

/* ── SEARCH ── */
.search-bar {
  position: relative;
  margin-bottom: 16px;
}
.search-bar input {
  width: 100%;
  padding: 10px 14px 10px 38px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text);
  font-size: 14px;
  outline: none;
  font-family: var(--font);
}
.search-bar input:focus { border-color: var(--accent); }
.search-bar .icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--muted);
  pointer-events: none;
}

/* ── FILTER PILLS ── */
.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}
.pill {
  padding: 4px 12px;
  border-radius: 20px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--muted);
  font-size: 12px;
  cursor: pointer;
  transition: all .15s;
  user-select: none;
}
.pill:hover { border-color: var(--accent); color: var(--text); }
.pill.active { background: var(--accent); border-color: var(--accent); color: #fff; font-weight: 600; }

/* ── PATTERN CARDS ── */
.pattern-section { margin-bottom: 28px; }
.pattern-section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--accent2);
  margin-bottom: 12px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--border);
}
.pattern-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 14px 16px;
  margin-bottom: 8px;
  transition: border-color .15s;
}
.pattern-card:hover { border-color: var(--accent); }
.pattern-card.hidden { display: none; }
.pattern-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}
.pattern-id {
  font-family: var(--mono);
  font-size: 11px;
  color: var(--muted);
  background: var(--surface2);
  padding: 2px 7px;
  border-radius: 4px;
}
.pattern-text {
  font-family: var(--font);
  font-size: 16px;
  line-height: 1.85;
  background: linear-gradient(180deg, rgba(59,130,246,.06), rgba(59,130,246,.02));
  border: 1px solid rgba(59,130,246,.2);
  border-left: 4px solid var(--accent2);
  border-radius: 10px;
  padding: 12px 14px;
  white-space: pre-wrap;
  word-break: break-word;
  color: var(--text);
  margin: 8px 0;
}
.pattern-meta {
  display: flex;
  gap: 16px;
  font-size: 11px;
  color: var(--muted);
  flex-wrap: wrap;
}
.pattern-meta span { display: flex; align-items: center; gap: 4px; }

/* ── BADGE ── */
.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
}
.badge-theory   { background: rgba(108,142,247,.2); color: #6c8ef7; border: 1px solid rgba(108,142,247,.4); }
.badge-algo     { background: rgba(167,139,250,.2); color: #a78bfa; border: 1px solid rgba(167,139,250,.4); }
.badge-observer { background: rgba(251,146,60,.2);  color: #fb923c; border: 1px solid rgba(251,146,60,.4); }
.badge-learning { background: rgba(52,211,153,.2);  color: #34d399; border: 1px solid rgba(52,211,153,.4); }
.badge-method   { background: rgba(148,163,184,.15); color: #94a3b8; border: 1px solid rgba(148,163,184,.3); }

.badge-pass   { background: rgba(52,211,153,.2); color: #34d399; border: 1px solid rgba(52,211,153,.4); }
.badge-fail   { background: rgba(248,113,113,.2); color: #f87171; border: 1px solid rgba(248,113,113,.4); }
.badge-review { background: rgba(251,191,36,.2);  color: #fbbf24; border: 1px solid rgba(251,191,36,.4); }
.badge-ok     { background: rgba(52,211,153,.2); color: #34d399; border: 1px solid rgba(52,211,153,.4); }
.badge-warn   { background: rgba(251,191,36,.2);  color: #fbbf24; border: 1px solid rgba(251,191,36,.4); }

.conf-bar {
  display: inline-block;
  height: 4px;
  border-radius: 2px;
  background: var(--accent);
  vertical-align: middle;
}

/* ── INNOVATION TABLE ── */
.innov-table-wrap { overflow-x: auto; }
.innov-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  min-width: 900px;
}
.innov-table th {
  background: var(--surface2);
  color: var(--muted);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: .06em;
  padding: 10px 12px;
  text-align: left;
  position: sticky;
  top: 0;
  border-bottom: 2px solid var(--border);
}
.innov-table td {
  padding: 10px 12px;
  border-bottom: 1px solid var(--border);
  vertical-align: top;
}
.innov-table tr:hover td { background: rgba(108,142,247,.04); }
.innov-table tr.hidden { display: none; }
.innov-table td.claim-cell {
  font-size: 12px;
  color: var(--text);
  max-width: 280px;
}
.innov-table td.pattern-cell {
  font-family: var(--font);
  font-size: 14px;
  line-height: 1.7;
  color: var(--text);
  max-width: 200px;
}

.innov-table td.claim-cell {
  font-size: 14px;
  line-height: 1.75;
}

/* ── REVIEW BUTTONS ── */
.review-btn-group { display: flex; gap: 4px; }
.review-btn {
  padding: 4px 10px;
  border-radius: 5px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--muted);
  font-size: 13px;
  cursor: pointer;
  transition: all .12s;
}
.review-btn:hover { border-color: var(--accent); color: var(--text); }
.review-btn.selected-ok   { background: rgba(52,211,153,.2); border-color: #34d399; color: #34d399; }
.review-btn.selected-warn { background: rgba(251,191,36,.2);  border-color: #fbbf24; color: #fbbf24; }
.review-btn.selected-bad  { background: rgba(248,113,113,.2); border-color: #f87171; color: #f87171; }

/* ── RELATED WORK ── */
.rw-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-left: 3px solid var(--accent2);
  border-radius: 8px;
  padding: 14px 16px;
  margin-bottom: 8px;
}

/* ── PARAGRAPH TEMPLATE ── */
.tmpl-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 12px;
}
.tmpl-card .tmpl-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}
.tmpl-body {
  font-family: var(--font);
  font-size: 16px;
  line-height: 1.85;
  background: linear-gradient(180deg, rgba(59,130,246,.06), rgba(59,130,246,.02));
  border: 1px solid rgba(59,130,246,.2);
  border-left: 4px solid var(--accent2);
  border-radius: 10px;
  padding: 12px 14px;
  white-space: pre-wrap;
  color: var(--text);
  margin: 10px 0;
}

/* KaTeX in reading blocks */
.pattern-text .katex,
.tmpl-body .katex,
.innov-table .katex {
  font-size: 1.03em;
}
.slot-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}
.slot-tag {
  font-family: var(--mono);
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  background: rgba(108,142,247,.15);
  border: 1px solid rgba(108,142,247,.3);
  color: var(--accent);
}
.slot-tag.optional {
  background: rgba(148,163,184,.1);
  border-color: rgba(148,163,184,.25);
  color: var(--muted);
}

/* ── BAR CHART ── */
.bar-chart { margin: 16px 0; }
.bar-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
  font-size: 12px;
}
.bar-row .bar-label {
  width: 240px;
  flex-shrink: 0;
  color: var(--muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.bar-row .bar-track {
  flex: 1;
  height: 8px;
  background: var(--border);
  border-radius: 4px;
  overflow: hidden;
}
.bar-row .bar-fill {
  height: 100%;
  border-radius: 4px;
  background: var(--accent);
}
.bar-row .bar-val {
  width: 60px;
  text-align: right;
  font-family: var(--mono);
  font-size: 11px;
  color: var(--text);
}

/* ── REVIEW GUIDE ── */
.guide-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin: 16px 0;
}
.guide-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px;
}
.guide-card h4 { font-size: 13px; font-weight: 600; margin-bottom: 8px; }
.guide-card ul { padding-left: 16px; }
.guide-card li { font-size: 12px; color: var(--muted); margin-bottom: 4px; line-height: 1.5; }
.guide-card li strong { color: var(--text); }

/* ── SAVE BUTTON ── */
.save-bar {
  position: fixed;
  bottom: 24px;
  right: 32px;
  z-index: 100;
}
.save-btn {
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 10px 20px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(108,142,247,.4);
  transition: all .15s;
}
.save-btn:hover { background: #5a7ef5; transform: translateY(-1px); }
.save-notification {
  position: fixed;
  bottom: 72px;
  right: 32px;
  background: var(--green);
  color: #0f1117;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  opacity: 0;
  transition: opacity .3s;
  pointer-events: none;
}
.save-notification.show { opacity: 1; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

/* ── RESPONSIVE ── */
@media (max-width: 900px) {
  .sidebar { display: none; }
  .main { padding: 20px; }
  .guide-grid { grid-template-columns: 1fr; }
}

.toc-counter {
  font-family: var(--mono);
  font-size: 11px;
  color: var(--muted);
  background: var(--surface2);
  padding: 1px 6px;
  border-radius: 10px;
  margin-left: 6px;
}
"""

# ── JavaScript ──────────────────────────────────────────────────────────────

JS = """
const SIDEBAR_STORAGE_KEY = 'distill-review-sidebar-hidden-v1';
const THEME_STORAGE_KEY = 'distill-review-theme-v1';

function showSection(id) {
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  const sec = document.getElementById(id);
  if (sec) sec.classList.add('active');
  const nav = document.querySelector('[data-target="' + id + '"]');
  if (nav) nav.classList.add('active');
}

// Search for sentence patterns
function filterPatterns(val) {
  const q = val.toLowerCase();
  document.querySelectorAll('.pattern-card').forEach(card => {
    const text = card.textContent.toLowerCase();
    card.classList.toggle('hidden', q.length > 0 && !text.includes(q));
  });
}

// Filter innovations by type
let activeFilter = 'all';
function filterInnovations(type) {
  activeFilter = type;
  document.querySelectorAll('.pill[data-filter]').forEach(p => {
    p.classList.toggle('active', p.dataset.filter === type);
  });
  document.querySelectorAll('.innov-table tr[data-type]').forEach(row => {
    row.classList.toggle('hidden', type !== 'all' && row.dataset.type !== type);
  });
}

// Review buttons
const STORAGE_KEY = 'distill-review-v1';
function loadReviews() {
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}'); } catch { return {}; }
}
function saveReviews() {
  const reviews = {};
  document.querySelectorAll('.review-btn.selected-ok, .review-btn.selected-warn, .review-btn.selected-bad').forEach(btn => {
    const host = btn.closest('[data-review-id]');
    if (!host) return;
    const id = host.dataset.reviewId;
    if (btn.classList.contains('selected-ok')) reviews[id] = 'ok';
    else if (btn.classList.contains('selected-warn')) reviews[id] = 'warn';
    else reviews[id] = 'bad';
  });
  localStorage.setItem(STORAGE_KEY, JSON.stringify(reviews));
  const notif = document.getElementById('save-notif');
  notif.classList.add('show');
  setTimeout(() => notif.classList.remove('show'), 2000);
}

function setReview(btn, verdict) {
  const group = btn.closest('.review-btn-group');
  group.querySelectorAll('.review-btn').forEach(b => b.classList.remove('selected-ok', 'selected-warn', 'selected-bad'));
  const cls = verdict === 'ok' ? 'selected-ok' : verdict === 'warn' ? 'selected-warn' : 'selected-bad';
  btn.classList.add(cls);
}

function applySidebarState(hidden) {
  const layout = document.getElementById('layout');
  const btn = document.getElementById('sidebar-toggle');
  if (!layout || !btn) return;
  layout.classList.toggle('sidebar-hidden', hidden);
  btn.textContent = hidden ? '显示目录' : '隐藏目录';
}

function toggleSidebar() {
  const layout = document.getElementById('layout');
  if (!layout) return;
  const hidden = !layout.classList.contains('sidebar-hidden');
  applySidebarState(hidden);
  localStorage.setItem(SIDEBAR_STORAGE_KEY, hidden ? '1' : '0');
}

function applyTheme(theme) {
  const body = document.body;
  const btn = document.getElementById('theme-toggle');
  if (!body || !btn) return;
  const dark = theme === 'dark';
  body.classList.toggle('theme-dark', dark);
  btn.textContent = dark ? '切换浅色' : '切换深色';
}

function toggleTheme() {
  const dark = document.body.classList.contains('theme-dark');
  const next = dark ? 'light' : 'dark';
  applyTheme(next);
  localStorage.setItem(THEME_STORAGE_KEY, next);
}

window.addEventListener('DOMContentLoaded', () => {
  const savedTheme = localStorage.getItem(THEME_STORAGE_KEY) || 'light';
  applyTheme(savedTheme);
  const sidebarHidden = localStorage.getItem(SIDEBAR_STORAGE_KEY) === '1';
  applySidebarState(sidebarHidden);
  showSection('sec-meta');
  const saved = loadReviews();
  Object.entries(saved).forEach(([id, verdict]) => {
    const host = document.querySelector('[data-review-id="' + id + '"]');
    if (!host) return;
    const btn = host.querySelector('.review-btn[data-verdict="' + verdict + '"]');
    if (btn) {
      const cls = verdict === 'ok' ? 'selected-ok' : verdict === 'warn' ? 'selected-warn' : 'selected-bad';
      btn.classList.add(cls);
    }
  });
  // update counters
  updateReviewCounters();

  // Render LaTeX math if KaTeX auto-render is available
  if (window.renderMathInElement) {
    window.renderMathInElement(document.body, {
      delimiters: [
        {left: '$$', right: '$$', display: true},
        {left: '$', right: '$', display: false},
        {left: '\\(', right: '\\)', display: false},
        {left: '\\[', right: '\\]', display: true}
      ],
      throwOnError: false
    });
  }
});

function updateReviewCounters() {
  // done in CSS via counting
}
"""


# ── HTML 生成 ────────────────────────────────────────────────────────────

def render_meta(pkg: dict) -> str:
    manifest = pkg.get("run_manifest", {})
    metrics  = pkg.get("metrics", {})

    n_mb = len(pkg.get("macro_blueprints", []))
    n_sp = len(pkg.get("sentence_patterns", []))
    n_ip = len(pkg.get("innovation_patterns", []))
    n_cb = len(pkg.get("claim_evidence_bindings", []))
    n_pt = len(pkg.get("paragraph_templates", []))
    n_rw = len(pkg.get("related_work_patterns", []))

    # summary cards
    cards_html = f"""
<div class="metric-grid">
  <div class="metric-card info">
    <div class="label">D1 宏观蓝图</div>
    <div class="value">{n_mb}</div>
    <div class="sub">macro blueprints</div>
  </div>
  <div class="metric-card info">
    <div class="label">句型模板</div>
    <div class="value">{n_sp}</div>
    <div class="sub">sentence patterns</div>
  </div>
  <div class="metric-card info">
    <div class="label">创新论证</div>
    <div class="value">{n_ip}</div>
    <div class="sub">innovation patterns</div>
  </div>
  <div class="metric-card info">
    <div class="label">Claim 绑定</div>
    <div class="value">{n_cb}</div>
    <div class="sub">claim-evidence bindings</div>
  </div>
  <div class="metric-card info">
    <div class="label">段落模板</div>
    <div class="value">{n_pt}</div>
    <div class="sub">paragraph templates</div>
  </div>
  <div class="metric-card info">
    <div class="label">D4 相关工作定位</div>
    <div class="value">{n_rw}</div>
    <div class="sub">related-work patterns</div>
  </div>
</div>"""

    # metrics progress bars
    thresholds = {
        "coverage":     (0.70, ">=", "fill-green"),
        "consistency":  (0.60, ">=", "fill-green"),
        "actionability":(0.60, ">=", "fill-green"),
        "leakage_risk": (0.20, "<=", "fill-red"),
    }
    metric_bars = ""
    for k, v in metrics.items():
        thr, op, color = thresholds.get(k, (None, None, "fill-accent"))
        if thr is not None:
            ok = (v >= thr) if op == ">=" else (v <= thr)
            status_badge = f'<span class="badge badge-pass">✅ pass</span>' if ok else f'<span class="badge badge-fail">❌ fail</span>'
            fill_pct = min(100, v * 100) if op == ">=" else min(100, (1 - v) * 100)
        else:
            status_badge = ""
            fill_pct = min(100, v * 100)
            color = "fill-accent"
        metric_bars += f"""
        <div class="progress-row">
          <div class="progress-label">
            <span>{h(k)} {status_badge}</span>
            <span>{v}</span>
          </div>
          <div class="progress-bar"><div class="progress-fill {color}" style="width:{fill_pct:.1f}%"></div></div>
        </div>"""

    info_rows = f"""
<table class="info-table">
  <tr><td>Run ID</td><td><code>{h(manifest.get('run_id', 'N/A'))}</code></td></tr>
  <tr><td>时间戳</td><td>{h(manifest.get('run_timestamp', 'N/A'))}</td></tr>
  <tr><td>操作者</td><td>{h(manifest.get('operator', 'N/A'))}</td></tr>
  <tr><td>语料哈希</td><td><code>{h(manifest.get('source_corpus_hash', 'N/A')[:20])}…</code></td></tr>
</table>"""

    return f"""
<div class="page-header">
  <h2>蒸馏结果人工审查报告</h2>
  <div class="run-id">Run ID: {h(manifest.get('run_id', 'N/A'))} · {h(manifest.get('run_timestamp', 'N/A'))}</div>
  <div class="warning">⚠️ 本文档仅供质量评判。请在各模块卡片上打 ✅ / ⚠️ / ❌，完成后点右下角「保存审查」。</div>
</div>
{info_rows}
<div class="section-heading"><span class="sect-num">✦</span> 数量统计</div>
{cards_html}
<div class="section-heading" style="margin-top:24px"><span class="sect-num">✦</span> 质量指标</div>
{metric_bars}
"""


def render_terminology(patterns: list) -> str:
    bigrams = extract_bigrams(patterns)
    items = ""
    for bg, cnt in bigrams.most_common(40):
        items += f'<div class="bigram-item"><span class="phrase">{h(bg)}</span><span class="count">{cnt}</span></div>\n'
    return f"""
<div class="section-heading"><span class="sect-num">1</span> 术语搭配</div>
<div class="review-tip">
  <strong>评审要点：</strong> 词组是否是该领域真实高频搭配？
  有无明显噪声词组（如页眉残留、作者名、"the reference" 等停用词组）？
  若某词组大量出现但明显无意义，说明预处理去噪仍需增强。
</div>
<div class="bigram-grid">{items}</div>
"""


def render_sentence_patterns(patterns: list) -> str:
    grouped = group_by_section_intent(patterns)

    section_order = ["Introduction", "Related Work", "Relatedwork", "Relatedworks",
                     "Preliminaries", "Method", "Methodology", "Algorithm",
                     "Results", "Simulation", "Simulations", "Conclusion", "Discussion", "Unknown"]
    all_secs = list(grouped.keys())
    ordered = [s for s in section_order if s in all_secs]
    ordered += [s for s in all_secs if s not in ordered]

    cards_html = ""
    for sec in ordered:
        intent_map = grouped[sec]
        for intent, plist in sorted(intent_map.items()):
            title = f"{sec} › {intent} ({len(plist)} 条)"
            cards = ""
            for p in plist[:6]:
                ev = p.get("evidence", [{}])[0]
                src_id = ev.get("source_paragraph_id", "?")
                src_paper = paper_short(ev.get("source_paper_id", "?"))
                conf = p.get("confidence", 0)
                conf_w = int(conf * 60)
                pat = prettify_formula_text(p.get("pattern", ""))
                tense = p.get("tense", "")
                strength = p.get("rhetorical_strength", "")
                review_id = f"sent::{p.get('id', '?')}"
                cards += f"""
<div class="pattern-card" data-text="{h(pat.lower())} {h(sec.lower())} {h(intent.lower())}" data-review-id="{h(review_id)}">
  <div class="pattern-header">
    <span class="pattern-id">{h(p['id'])}</span>
    <span class="badge badge-method">{h(intent)}</span>
    {'<span class="badge badge-theory">' + h(tense) + '</span>' if tense else ''}
    {'<span class="badge badge-observer">' + h(strength) + '</span>' if strength else ''}
    <span style="margin-left:auto; font-size:11px; color:var(--muted)">conf: {conf:.2f} <span class="conf-bar" style="width:{conf_w}px"></span></span>
  </div>
  <div class="pattern-text">{h(pat)}</div>
  <div class="pattern-meta">
    <span>📄 {h(src_paper)}</span>
    <span>🔖 <code style="font-size:10px;color:var(--muted)">{h(src_id)}</code></span>
    <span style="margin-left:auto">{render_review_buttons(review_id)}</span>
  </div>
</div>"""
            if len(plist) > 6:
                cards += f'<p style="font-size:12px;color:var(--muted);padding:4px 0">… 还有 {len(plist)-6} 条，见 JSON 包</p>'
            cards_html += f'<div class="pattern-section"><div class="pattern-section-title">{h(title)}</div>{cards}</div>'

    return f"""
<div class="section-heading"><span class="sect-num">2</span> 句型模板</div>
<div class="review-tip">
  <strong>评审要点：</strong><br>
  1. 模板是否保留了语义槽位（{{placeholder}}）而非抄写原句？<br>
  2. <code>section</code> 归属是否正确（Unknown 占比是否过高）？<br>
  3. <code>source_paragraph_id</code> 是否来自正文（<code>body:…</code>）而非 <code>head_pages</code>？
</div>
<div class="search-bar">
  <span class="icon">🔍</span>
  <input type="text" placeholder="搜索句型内容、章节、意图…" oninput="filterPatterns(this.value)">
</div>
{cards_html}
"""


def render_macro_blueprints(blueprints: list) -> str:
    if not blueprints:
        return """
<div class="section-heading"><span class="sect-num">3</span> D1 宏观蓝图</div>
<div class="review-tip"><strong>评审要点：</strong> 检查 problem → gap → method → result → contribution 链条是否完整、是否与论文主线一致。</div>
<p style='color:var(--muted);font-size:13px;padding:16px 0'>（当前包未包含 macro_blueprints）</p>
"""

    cards = ""
    for mb in blueprints:
        review_id = f"macro::{mb.get('id', '?')}"
        cards += f"""<div class="tmpl-card">
  <div class="tmpl-header">
    <span class="pattern-id">{h(mb.get('id', '?'))}</span>
    <span class="badge badge-method">{h(mb.get('source_paper', '?')[:40])}</span>
    <span style="margin-left:auto;font-size:11px;color:var(--muted)">completeness {mb.get('completeness', 0):.2f} · conf {mb.get('confidence', 0):.2f}</span>
  </div>
  <div style="padding: 0 14px 10px;">{render_review_buttons(review_id)}</div>
  <div class="tmpl-body"><strong>Problem:</strong> {h(prettify_formula_text(mb.get('problem_context', '')))}</div>
  <div class="tmpl-body"><strong>Gap:</strong> {h(prettify_formula_text(mb.get('research_gap', '')))}</div>
  <div class="tmpl-body"><strong>Method:</strong> {h(prettify_formula_text(mb.get('proposed_method', '')))}</div>
  <div class="tmpl-body"><strong>Result:</strong> {h(prettify_formula_text(mb.get('key_result', '')))}</div>
  <div class="tmpl-body"><strong>Contribution:</strong> {h(prettify_formula_text(mb.get('contribution_claim', '')))}</div>
</div>"""

    return f"""
<div class="section-heading"><span class="sect-num">3</span> D1 宏观蓝图</div>
<div class="review-tip">
  <strong>评审要点：</strong> 每条应体现完整论证链。若某字段长期是 <code>[not detected]</code>，说明章节映射或意图识别仍需改进。
</div>
{cards}
"""


def render_innovations(innov: list, claims: list) -> str:
    claim_map = {c["claim_id"]: c["claim_text"] for c in claims}

    type_counts: Counter = Counter(i.get("innovation_type", "method") for i in innov)
    filter_pills = '<span class="pill active" data-filter="all" onclick="filterInnovations(\'all\')">All</span>'
    for itype, cnt in type_counts.most_common():
        filter_pills += f'<span class="pill" data-filter="{h(itype)}" onclick="filterInnovations(\'{h(itype)}\')">{h(itype)} ({cnt})</span>'

    rows = ""
    for inn in innov:
        itype = inn.get("innovation_type", "method")
        claim = prettify_formula_text(inn.get("claim_pattern", "")[:200]).replace("|", "｜")
        mech  = prettify_formula_text(inn.get("mechanism_pattern", "")[:150]).replace("|", "｜")
        gain  = prettify_formula_text(inn.get("gain_pattern", "")[:120]).replace("|", "｜")
        bnd   = prettify_formula_text(inn.get("boundary_pattern", "")[:120]).replace("|", "｜")
        conf  = inn.get("confidence", 0)
        needs = inn.get("human_review_required", False)
        flag  = '<span class="badge badge-warn">⚠ review</span>' if needs else ''

        rows += f"""<tr data-id="{h(inn['id'])}" data-review-id="innov::{h(inn['id'])}" data-type="{h(itype)}">
  <td><span class="pattern-id">{h(inn['id'])}</span></td>
  <td>{innovation_badge(itype)}</td>
  <td class="claim-cell">{h(claim)} {flag}</td>
  <td class="pattern-cell">{h(mech)}</td>
  <td class="pattern-cell">{h(gain)}</td>
  <td class="pattern-cell">{h(bnd)}</td>
  <td style="font-family:var(--mono);font-size:11px;color:var(--muted)">{conf:.2f}</td>
  <td>{render_review_buttons(f"innov::{inn['id']}")}</td>
</tr>"""

    return f"""
  <div class="section-heading"><span class="sect-num">5</span> 创新论证表达</div>
<div class="review-tip">
  <strong>评审要点：</strong><br>
  1. <strong>claim</strong> 是否是真实贡献陈述（非 "in this paper…" 结构句、非页眉噪声）？<br>
  2. <strong>mechanism</strong> 是否与创新类型匹配（convex/Lyapunov/adaptive 等领域词）？<br>
  3. <strong>gain/boundary</strong> 是否有领域特异性（非纯通用模板）？<br>
  对每行点击 ✅/⚠️/❌，完成后点右下角「保存审查」，结果存入浏览器。
</div>
<div class="filter-row">{filter_pills}</div>
<div class="innov-table-wrap">
<table class="innov-table">
  <thead><tr>
    <th>ID</th><th>类型</th><th>Claim（≤200字）</th>
    <th>Mechanism 模板</th><th>Gain 模板</th><th>Boundary 模板</th>
    <th>Conf</th><th>审查</th>
  </tr></thead>
  <tbody>{rows}</tbody>
</table>
</div>
"""


def render_related_work(d4_patterns: list) -> str:
    if not d4_patterns:
        content = "<p style='color:var(--muted);font-size:13px;padding:16px 0'>（本次蒸馏未检测到相关工作定位模式，建议增加含 Related Work 章节的论文样本）</p>"
    else:
        type_counts: Counter = Counter(p.get("positioning_type", "unknown") for p in d4_patterns)
        pills = "".join(
            f'<span class="pill">{h(t)} ({c})</span>' for t, c in type_counts.most_common()
        )
        cards = ""
        for p in d4_patterns[:120]:
            ev = p.get("evidence", [{}])[0] if p.get("evidence") else {}
            src = paper_short(ev.get("source_paper_id", "?"))
            pat = prettify_formula_text(p.get("pattern", ""))
            rid = f"rw::{p.get('id', '?')}"
            cards += f"""<div class="rw-card">
  <div class="pattern-header" data-review-id="{h(rid)}">
    <span class="pattern-id">{h(p.get('id', '?'))}</span>
    <span class="badge badge-method">{h(p.get('positioning_type', 'unknown'))}</span>
    <span class="badge badge-theory">{h(p.get('section', 'Unknown'))}</span>
    <span class="badge badge-observer">{h(p.get('trigger_marker', ''))}</span>
    <span style="font-size:11px;color:var(--muted)">📄 {h(src)}</span>
    <span style="margin-left:auto">{render_review_buttons(rid)}</span>
  </div>
  <div class="pattern-text">{h(pat)}</div>
</div>"""
        content = f'<div class="filter-row">{pills}</div>{cards}'

    return f"""
<div class="section-heading"><span class="sect-num">4</span> 相关工作定位</div>
<div class="review-tip">
  <strong>评审要点：</strong> 句式是否体现「现有工作 → 不足/比较 → 我方切入」推进逻辑？
  重点检查 <code>positioning_type</code> 与触发词 <code>trigger_marker</code> 是否匹配。
</div>
{content}
"""


def render_paragraph_templates(tmpls: list) -> str:
    cards = ""
    for t in tmpls:
        req_slots = "".join(f'<span class="slot-tag">{{{h(s)}}}</span>' for s in t.get("required_slots", []))
        opt_slots = "".join(f'<span class="slot-tag optional">{{{h(s)}}}</span>' for s in t.get("optional_slots", []))
        conf = t.get("confidence", 0)
        rid = f"tmpl::{t.get('id', '?')}"
        cards += f"""<div class="tmpl-card">
  <div class="tmpl-header" data-review-id="{h(rid)}">
    <span class="pattern-id">{h(t['id'])}</span>
    <span class="badge badge-method">{h(t.get('section','?'))}</span>
    <span class="badge badge-theory">{h(t.get('intent','?'))}</span>
    <span style="margin-left:auto;font-size:11px;color:var(--muted)">conf {conf:.2f} · {t.get('evidence_count','?')} 证据样本</span>
  </div>
  <div style="padding: 0 14px 10px;">{render_review_buttons(rid)}</div>
  <div class="tmpl-body">{h(prettify_formula_text(t.get('template','')))}</div>
  <div class="slot-list">
    <span style="font-size:11px;color:var(--muted);margin-right:4px">必填:</span> {req_slots}
    {'<span style="font-size:11px;color:var(--muted);margin-left:10px;margin-right:4px">可选:</span>' + opt_slots if opt_slots else ''}
  </div>
</div>"""

    return f"""
  <div class="section-heading"><span class="sect-num">6</span> 段落推进路径</div>
<div class="review-tip">
  <strong>评审要点：</strong> 模板的槽位是否覆盖了该章节的核心写作要素？
  填入槽位后能否直接生成可读段落（不需大幅改写）？
</div>
{cards}
"""


def render_coverage(patterns: list, claims: list) -> str:
    # claim_evidence_bindings 有完整多论文归因，优先用；fallback 到 sentence_patterns
    claim_stats = paper_contribution_stats(claims) if claims else Counter()
    pat_stats   = paper_contribution_stats(patterns)
    use_claims  = bool(claim_stats)
    stats  = claim_stats if use_claims else pat_stats
    source_label = "Claim 绑定" if use_claims else "句型模板"

    total = sum(stats.values()) or 1
    bars = ""
    max_cnt = max(stats.values()) if stats else 1
    for src, cnt in stats.most_common():
        short = paper_short(src)
        pct = cnt / total * 100
        bar_w = cnt / max_cnt * 100
        bars += f"""<div class="bar-row">
  <div class="bar-label" title="{h(src)}">{h(short)}</div>
  <div class="bar-track"><div class="bar-fill" style="width:{bar_w:.1f}%"></div></div>
  <div class="bar-val">{cnt} ({pct:.0f}%)</div>
</div>"""

    note = f'（数据来源：<code>{source_label}</code> evidence；sentence_patterns 仅追踪了 1 篇来源，属蒸馏 LLM 归因不全，不代表实际语料只有 1 篇）' if use_claims else ''
    return f"""
  <div class="section-heading"><span class="sect-num">7</span> 语料贡献统计</div>
<div class="review-tip">
  <strong>评审要点：</strong> 若某篇论文占比 &gt; 40%，蒸馏结果可能偏向该篇风格，
  建议补充同领域其他论文平衡语料。<br><small style="color:var(--muted)">{note}</small>
</div>
<div class="bar-chart">{bars}</div>
"""


def render_guide() -> str:
    return """
<div class="section-heading"><span class="sect-num">8</span> 人工评审指引</div>
<div class="guide-grid">
  <div class="guide-card">
    <h4 style="color:var(--green)">✅ 合格标准</h4>
    <ul>
      <li><strong>来源</strong>：source_paragraph_id 包含 <code>body:</code></li>
      <li><strong>claim</strong>：是论文贡献/方法陈述句</li>
      <li><strong>mechanism</strong>：包含领域关键词（Lyapunov/convex/adaptive…）</li>
      <li><strong>术语词组</strong>：是该领域真实搭配</li>
      <li><strong>章节归属</strong>：section 与实际内容匹配</li>
    </ul>
  </div>
  <div class="guide-card">
    <h4 style="color:var(--red)">❌ 需删除的噪声</h4>
    <ul>
      <li><strong>结构句</strong>："The organization of this paper is…"</li>
      <li><strong>Abstract 前缀</strong>：claim 以 "Abstract—" 开头</li>
      <li><strong>OCR 乱码</strong>：大量符号 IRn, tf, ge 等</li>
      <li><strong>资助声明</strong>："This work was supported by…"</li>
      <li><strong>泛化失败</strong>：mechanism 完全通用（无领域词）</li>
    </ul>
  </div>
  <div class="guide-card">
    <h4 style="color:var(--yellow)">⚠️ 需修改</h4>
    <ul>
      <li>claim 大体准确但含冗余前缀（需截断）</li>
      <li>mechanism 槽位命名不够精确</li>
      <li>section 归属偏差（body:Unknown 但内容是 Introduction）</li>
    </ul>
  </div>
  <div class="guide-card">
    <h4 style="color:var(--accent)">📋 审查后操作</h4>
    <ul>
      <li>记录 ❌ 条目 ID（如 I-013, S-004）</li>
      <li>在 <code>core5-distill-package.json</code> 中删除/修改对应条目</li>
      <li>重新运行 <code>generate_review_html.py</code> 验证修改结果</li>
      <li>若 Unknown 占比 &gt; 30%，检查 preprocess_pdf_to_md.py 章节检测逻辑</li>
    </ul>
  </div>
</div>
"""


def build_html(pkg_path: Path, out_path: Path) -> None:
    pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
    manifest = pkg.get("run_manifest", {})
    run_id = manifest.get("run_id", "unknown")

    macro    = pkg.get("macro_blueprints", [])
    patterns = pkg.get("sentence_patterns", [])
    innov    = pkg.get("innovation_patterns", [])
    claims   = pkg.get("claim_evidence_bindings", [])
    tmpls    = pkg.get("paragraph_templates", [])
    rw       = pkg.get("related_work_patterns", [])

    n_mb = len(macro)
    n_sp = len(patterns)
    n_ip = len(innov)
    n_rw = len(rw)

    nav = f"""
<a class="nav-item active" data-target="sec-meta" onclick="showSection('sec-meta')">概述 & 指标</a>
<a class="nav-item" data-target="sec-term" onclick="showSection('sec-term')">§1 术语搭配</a>
<a class="nav-item" data-target="sec-sent" onclick="showSection('sec-sent')">§2 句型模板 <span class="toc-counter">{n_sp}</span></a>
<a class="nav-item" data-target="sec-macro" onclick="showSection('sec-macro')">§3 D1 宏观蓝图 <span class="toc-counter">{n_mb}</span></a>
<a class="nav-item" data-target="sec-rw" onclick="showSection('sec-rw')">§4 D4 相关工作 <span class="toc-counter">{n_rw}</span></a>
<a class="nav-item" data-target="sec-innov" onclick="showSection('sec-innov')">§5 创新论证 <span class="toc-counter">{n_ip}</span></a>
<a class="nav-item" data-target="sec-tmpl" onclick="showSection('sec-tmpl')">§6 段落模板</a>
<a class="nav-item" data-target="sec-cov" onclick="showSection('sec-cov')">§7 语料贡献</a>
<a class="nav-item" data-target="sec-guide" onclick="showSection('sec-guide')">§8 评审指引</a>
"""

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>蒸馏审查 · {h(run_id)}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"></script>
<style>{CSS}</style>
</head>
<body>
<div class="layout" id="layout">
  <nav class="sidebar">
    <h1>蒸馏审查</h1>
    {nav}
    <div class="sidebar-meta">Run: {h(run_id)}</div>
  </nav>
  <main class="main">
    <button id="sidebar-toggle" class="sidebar-toggle" onclick="toggleSidebar()">隐藏目录</button>
    <button id="theme-toggle" class="theme-toggle" onclick="toggleTheme()">切换深色</button>
    <div id="sec-meta" class="section">{render_meta(pkg)}</div>
    <div id="sec-term" class="section">{render_terminology(patterns)}</div>
    <div id="sec-sent" class="section">{render_sentence_patterns(patterns)}</div>
    <div id="sec-macro" class="section">{render_macro_blueprints(macro)}</div>
    <div id="sec-rw" class="section">{render_related_work(rw)}</div>
    <div id="sec-innov" class="section">{render_innovations(innov, claims)}</div>
    <div id="sec-tmpl" class="section">{render_paragraph_templates(tmpls)}</div>
    <div id="sec-cov" class="section">{render_coverage(patterns, claims)}</div>
    <div id="sec-guide" class="section">{render_guide()}</div>
  </main>
</div>
<div class="save-bar">
  <button class="save-btn" onclick="saveReviews()">💾 保存审查</button>
</div>
<div class="save-notification" id="save-notif">✓ 审查结果已保存到浏览器</div>
<script>{JS}</script>
</body>
</html>"""

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    size_kb = out_path.stat().st_size // 1024
    print(f"[review-html] → {out_path}  ({size_kb} KB)")


def main():
    parser = argparse.ArgumentParser(description="生成蒸馏结果 HTML 审查报告")
    parser.add_argument("--pkg", required=True, help="core5-distill-package.json 路径")
    parser.add_argument("--out", required=True, help="输出 .html 路径")
    args = parser.parse_args()
    build_html(Path(args.pkg), Path(args.out))


if __name__ == "__main__":
    main()
