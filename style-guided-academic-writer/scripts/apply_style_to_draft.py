#!/usr/bin/env python3
"""Compute paragraph-level style alignment between a draft and a distill package.

Given a draft (Markdown file) and a distill package produced by
``paper-style-distiller``, this script walks each paragraph of the draft and
asks four questions:

1. Which section does this paragraph belong to? (auto-detected from the
   nearest preceding ``#`` / ``##`` heading, or set manually with
   ``--section-hints``)
2. Which paragraph templates from the package best fit that section+intent?
3. Which sentence patterns from the package best fit the surface text?
4. Where does the draft diverge from the distilled style — and what
   concrete revisions would close the gap?

The output is a Markdown report (default) or a JSON record (when
``--format json``) that can be reviewed by a human writer or piped into a
follow-up revision script.

Examples
---------

Run against a draft and a distill package, output the report to stdout::

    python3 apply_style_to_draft.py \\
        --pkg paper-style-distiller/runs/full11-core5-20260518-230538/full11-distill-package.json \\
        --draft samples/draft-introduction.md

Save the report to a file and skip paragraphs with no templates::

    python3 apply_style_to_draft.py \\
        --pkg runs/full11-distill-package.json \\
        --draft my-paper.md \\
        --output runs/my-paper-alignment.md \\
        --min-paragraph-templates 1

Use an explicit section hint when headings are ambiguous::

    python3 apply_style_to_draft.py \\
        --pkg runs/full11-distill-package.json \\
        --draft my-paper.md \\
        --section-hints "0=Introduction,3=Method,7=Discussion"
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from _pkg_loader import (  # noqa: E402
    DistillPackage,
    ParagraphTemplate,
    SentencePattern,
    load_distill_package,
)

LOG = logging.getLogger("sgaw.apply")

# Headings that count as "section" markers in academic Markdown drafts.
_SECTION_HEADING_PATTERN = re.compile(r"^\s{0,3}(#{1,3})\s+(.+?)\s*$")
# Headings deeper than ### are treated as subsections of the most recent
# section and inherit its name.
_MAX_HEADING_DEPTH = 3

# Fallback mapping for common English section titles used in academic
# papers.  Maps the canonical section name (used in distill packages) to a
# list of substrings we accept as a heading.  Matching is case-insensitive
# substring, so a heading of "1. Introduction" or "INTRODUCTION" both work.
_SECTION_ALIASES: dict[str, tuple[str, ...]] = {
    "Introduction": ("introduction", "intro", "background"),
    "Method": ("method", "approach", "methodology", "framework"),
    "Result": ("result", "experiment", "evaluation", "experimental"),
    "Discussion": ("discussion", "analysis", "ablation"),
    "Conclusion": ("conclusion", "summary", "concluding"),
    "RelatedWork": ("related work", "related-work", "literature review", "prior work"),
}


# ---------------------------------------------------------------------------
# Draft parsing
# ---------------------------------------------------------------------------


@dataclass
class DraftParagraph:
    """One paragraph extracted from the draft.

    ``index`` is the 0-based paragraph index across the whole document so
    the report can reference ``#3`` etc.  ``section`` is auto-detected
    from the most recent heading unless overridden by a section hint.
    """

    index: int
    text: str
    heading: str | None = None
    section: str = "Unknown"
    explicit_section: bool = False  # True when overridden by --section-hints

    @property
    def word_count(self) -> int:
        return len(self.text.split())

    @property
    def sentence_count(self) -> int:
        # Cheap sentence counter: split on '.', '!', '?', ';' followed by
        # whitespace.  Good enough for "did this paragraph drift short or
        # long" heuristics; not a linguistic parser.
        return len([s for s in re.split(r"[.!?;]+\s+", self.text.strip()) if s])


def _parse_section_hints(spec: str | None) -> dict[int, str]:
    """Parse ``"0=Introduction,3=Method,7=Discussion"`` into ``{0: "Introduction", ...}``."""
    if not spec:
        return {}
    out: dict[int, str] = {}
    for chunk in spec.split(","):
        chunk = chunk.strip()
        if not chunk or "=" not in chunk:
            LOG.warning("ignoring malformed section-hint chunk: %r", chunk)
            continue
        idx_s, name = chunk.split("=", 1)
        try:
            out[int(idx_s.strip())] = name.strip()
        except ValueError:
            LOG.warning("ignoring non-integer section-hint index: %r", idx_s)
    return out


def _normalise_section(heading: str | None) -> str:
    """Map a free-form heading to one of the canonical section names.

    Returns ``"Unknown"`` when no alias matches — the report will then fall
    back to "package-wide" templates so the writer still gets suggestions.
    """
    if not heading:
        return "Unknown"
    h_lc = heading.lower()
    for canonical, aliases in _SECTION_ALIASES.items():
        for alias in aliases:
            if alias in h_lc:
                return canonical
    return "Unknown"


def split_draft_into_paragraphs(text: str) -> list[DraftParagraph]:
    """Split a Markdown draft into paragraphs and detect section per paragraph.

    The algorithm walks the file line-by-line:

    * blank lines separate paragraphs;
    * lines starting with ``#`` / ``##`` / ``###`` update the current
      section via the alias table above;
    * lists, blockquotes and code blocks are flattened into the
      surrounding paragraph because the alignment heuristic works on
      natural prose, not bullet points.
    """
    paragraphs: list[DraftParagraph] = []
    buf: list[str] = []
    current_heading: str | None = None
    current_section = "Unknown"

    def flush() -> None:
        nonlocal buf
        if not buf:
            return
        joined = " ".join(s.strip() for s in buf if s.strip()).strip()
        if joined:
            paragraphs.append(
                DraftParagraph(
                    index=len(paragraphs),
                    text=joined,
                    heading=current_heading,
                    section=current_section,
                )
            )
        buf = []

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            flush()
            continue
        m = _SECTION_HEADING_PATTERN.match(line)
        if m and len(m.group(1)) <= _MAX_HEADING_DEPTH:
            flush()
            current_heading = m.group(2).strip()
            current_section = _normalise_section(current_heading)
            continue
        buf.append(stripped)
    flush()

    return paragraphs


# ---------------------------------------------------------------------------
# Alignment scoring
# ---------------------------------------------------------------------------


def _score_paragraph_match(text: str, tpl: ParagraphTemplate) -> float:
    """Compute a 0..1 heuristic alignment score for one paragraph template.

    The score blends three cheap signals:

    * **template coverage**: how many of the required slot names appear as
      phrases in the paragraph text;
    * **block-order match**: do the paragraph's first/last sentences align
      with the template's block_order?
    * **section alignment bonus**: 0.1 boost when the paragraph's section
      matches the template's section.

    This is intentionally heuristic — the goal is "is this template worth
    showing the writer", not "did the writer perfectly use this template".
    """
    text_lc = text.lower()
    required = tpl.required_slots or []
    if not required:
        slot_coverage = 0.0
    else:
        # Slot names often look like "gap_text" or "method" or "task".
        # Strip suffixes and split on '_' so a slot of "gap_text" matches
        # when the paragraph mentions "gap".
        slot_hits = 0
        for slot in required:
            candidates = {slot.lower()}
            for token in re.split(r"[_\-]+", slot):
                if len(token) > 2:
                    candidates.add(token.lower())
            if any(c in text_lc for c in candidates):
                slot_hits += 1
        slot_coverage = slot_hits / len(required)

    block_order = tpl.block_order or []
    block_bonus = 0.0
    if block_order:
        first_token = block_order[0].lower()
        last_token = block_order[-1].lower()
        # Use simple lexical presence as a proxy for block alignment; full
        # block-tagged parsing is out of scope for this script.
        sentences = [s.strip() for s in re.split(r"[.!?]+\s+", text) if s.strip()]
        if sentences:
            head_lc = sentences[0].lower()
            tail_lc = sentences[-1].lower()
            if any(first_token in s.lower() for s in (head_lc,)):
                block_bonus += 0.15
            if any(last_token in s.lower() for s in (tail_lc,)):
                block_bonus += 0.10

    return min(1.0, slot_coverage * 0.7 + block_bonus + tpl.confidence * 0.1)


def _score_sentence_match(sentence: str, sp: SentencePattern) -> float:
    """Heuristic 0..1 score for one sentence vs one sentence pattern."""
    s_lc = sentence.lower()
    # Penalise patterns whose raw text is much longer than the sentence
    # (those are clearly background exemplars, not reuse candidates).
    len_ratio = min(len(s_lc), 200) / max(len(s_lc), 1)
    pattern_keywords = set(re.findall(r"[a-z]{4,}", sp.pattern.lower()))
    sentence_keywords = set(re.findall(r"[a-z]{4,}", s_lc))
    if not pattern_keywords:
        kw_overlap = 0.0
    else:
        kw_overlap = len(pattern_keywords & sentence_keywords) / len(
            pattern_keywords | sentence_keywords
        )
    return min(1.0, 0.4 * kw_overlap + 0.3 * len_ratio + 0.3 * sp.confidence)


def _guess_intent(text: str) -> str:
    """Heuristic intent guess for a paragraph when no template matches.

    Looks for keywords that are strongly associated with each intent in the
    corpus.  This is intentionally conservative — when in doubt, returns
    ``"Background"`` because that is by far the most common intent.
    """
    lc = text.lower()
    if any(k in lc for k in ("however,", "limitation", "drawback", "fail to", "cannot")):
        return "Limitation"
    if any(k in lc for k in ("however", "remains", "open", "lack", "missing", "gap")):
        return "Gap"
    if any(k in lc for k in ("we propose", "we present", "contribution", "novel")):
        return "Contribution"
    if any(k in lc for k in ("outperform", "improves", "achieves", "results show", "experiment")):
        return "Result"
    return "Background"


def _best_sentence_matches(
    paragraph_text: str, candidates: list[SentencePattern], limit: int
) -> list[tuple[SentencePattern, float]]:
    """Return the top ``limit`` sentence patterns scored against ``paragraph_text``."""
    sentences = [s for s in re.split(r"[.!?]+\s+", paragraph_text) if len(s.split()) >= 4]
    if not sentences:
        return []
    scored: list[tuple[SentencePattern, float]] = []
    for sp in candidates:
        best = max(_score_sentence_match(s, sp) for s in sentences)
        scored.append((sp, best))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:limit]


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


@dataclass
class ParagraphReport:
    """One row in the alignment report."""

    index: int
    section: str
    section_source: str  # "auto" / "hint" / "default"
    word_count: int
    sentence_count: int
    guessed_intent: str
    matched_templates: list[dict[str, Any]] = field(default_factory=list)
    matched_sentences: list[dict[str, Any]] = field(default_factory=list)
    gap_suggestions: list[str] = field(default_factory=list)
    preview: str = ""


def build_report(
    paragraphs: list[DraftParagraph],
    pkg: DistillPackage,
    min_paragraph_templates: int,
    sentence_top_k: int,
) -> list[ParagraphReport]:
    """Walk every paragraph and produce one :class:`ParagraphReport`."""
    reports: list[ParagraphReport] = []
    for p in paragraphs:
        sec_lc = p.section.lower() if p.section != "Unknown" else None
        # Find candidate paragraph templates for this section.
        if sec_lc:
            paragraph_candidates = pkg.query_paragraphs(section=p.section)
        else:
            paragraph_candidates = pkg.query_paragraphs()
        # Score and rank.
        scored = [
            (tpl, _score_paragraph_match(p.text, tpl))
            for tpl in paragraph_candidates
        ]
        scored.sort(key=lambda x: (x[1], x[0].confidence), reverse=True)
        top_templates = scored[: min_paragraph_templates]
        # Find candidate sentence patterns for the same section.
        if sec_lc:
            sentence_candidates = pkg.query_sentences(section=p.section)
        else:
            sentence_candidates = pkg.query_sentences()
        top_sentences = _best_sentence_matches(p.text, sentence_candidates, sentence_top_k)
        # Identify gap suggestions.
        gap_suggestions: list[str] = []
        if not top_templates:
            gap_suggestions.append(
                f"No paragraph template matched section={p.section!r}."
                " Consider re-tagging this paragraph or expanding the section."
            )
        if len(p.text.split()) < 40:
            gap_suggestions.append(
                f"Paragraph is short ({p.word_count} words). "
                "Consider adding evidence / detail / hedging per the skill's "
                "writing constraints."
            )
        if not top_sentences:
            gap_suggestions.append(
                "No sentence patterns matched. Try retrieving with "
                "retrieve_templates.py --kind sentence --section <guess>."
            )
        reports.append(
            ParagraphReport(
                index=p.index,
                section=p.section,
                section_source="hint" if p.explicit_section else "auto",
                word_count=p.word_count,
                sentence_count=p.sentence_count,
                guessed_intent=_guess_intent(p.text),
                matched_templates=[
                    {
                        "id": tpl.id,
                        "section": tpl.section,
                        "intent": tpl.intent,
                        "template": tpl.template,
                        "score": round(score, 3),
                        "confidence": tpl.confidence,
                        "evidence_count": tpl.evidence_count,
                        "required_slots": tpl.required_slots,
                        "block_order": tpl.block_order,
                    }
                    for tpl, score in top_templates
                ],
                matched_sentences=[
                    {
                        "id": sp.id,
                        "section": sp.section,
                        "intent": sp.intent,
                        "tense": sp.tense,
                        "rhetorical_strength": sp.rhetorical_strength,
                        "score": round(score, 3),
                        "confidence": sp.confidence,
                        "pattern_snippet": (sp.pattern[:160] + "…")
                        if len(sp.pattern) > 160
                        else sp.pattern,
                    }
                    for sp, score in top_sentences
                ],
                gap_suggestions=gap_suggestions,
                preview=p.text[:200],
            )
        )
    return reports


def render_markdown_report(
    reports: list[ParagraphReport], pkg: DistillPackage, draft_path: Path
) -> str:
    """Format the report as Markdown suitable for human review."""
    out: list[str] = []
    out.append(f"# Style Alignment Report")
    out.append("")
    out.append(f"- draft: `{draft_path}`")
    out.append(f"- distill package: `{pkg.path}`")
    out.append(f"- run_id: `{pkg.run_id}` (schema {pkg.schema_version})")
    if pkg.metrics:
        cov = pkg.metrics.get("coverage")
        cons = pkg.metrics.get("consistency")
        leak = pkg.metrics.get("leakage_risk")
        if cov is not None:
            out.append(f"- coverage: {cov}")
        if cons is not None:
            out.append(f"- consistency: {cons}")
        if leak is not None:
            out.append(f"- leakage_risk: {leak}")
    out.append(f"- paragraphs analysed: {len(reports)}")
    out.append("")

    # Summary table.
    out.append("## Summary")
    out.append("")
    out.append(
        "| # | Section | Src | Words | Sents | Guessed intent | "
        "Paragraph matches | Sentence matches |"
    )
    out.append("|---|---------|-----|------:|------:|----------------|-------------------:|-------------------:|")
    for r in reports:
        out.append(
            f"| {r.index} | {r.section} | {r.section_source} | "
            f"{r.word_count} | {r.sentence_count} | {r.guessed_intent} | "
            f"{len(r.matched_templates)} | {len(r.matched_sentences)} |"
        )
    out.append("")

    # Per-paragraph detail.
    for r in reports:
        out.append(f"## Paragraph {r.index}  —  section: `{r.section}`")
        out.append("")
        out.append(f"> {r.preview}{'…' if len(r.preview) == 200 else ''}")
        out.append("")
        out.append(f"- guessed intent: **{r.guessed_intent}**")
        out.append(f"- word count: {r.word_count}  ·  sentence count: {r.sentence_count}")
        out.append("")
        if r.matched_templates:
            out.append("**Paragraph template matches:**")
            out.append("")
            for m in r.matched_templates:
                out.append(
                    f"- `{m['id']}` ({m['section']}/{m['intent']}, "
                    f"score={m['score']}, conf={m['confidence']}, evidence={m['evidence_count']})"
                )
                out.append(f"    template: `{m['template']}`")
                if m["required_slots"]:
                    out.append(
                        f"    required slots: {', '.join(m['required_slots'])}"
                    )
                if m["block_order"]:
                    out.append(f"    block order: {' -> '.join(m['block_order'])}")
            out.append("")
        else:
            out.append("**No paragraph template matched.**")
            out.append("")
        if r.matched_sentences:
            out.append("**Sentence pattern matches:**")
            out.append("")
            for s in r.matched_sentences:
                out.append(
                    f"- `{s['id']}` ({s['section']}/{s['intent']}, "
                    f"tense={s['tense']}, rh={s['rhetorical_strength']}, "
                    f"score={s['score']}, conf={s['confidence']})"
                )
                out.append(f"    `{s['pattern_snippet']}`")
            out.append("")
        else:
            out.append("**No sentence pattern matched.**")
            out.append("")
        if r.gap_suggestions:
            out.append("**Gap suggestions:**")
            out.append("")
            for g in r.gap_suggestions:
                out.append(f"- {g}")
            out.append("")

    return "\n".join(out)


def render_json_report(
    reports: list[ParagraphReport], pkg: DistillPackage, draft_path: Path
) -> str:
    """Format the report as JSON for downstream tooling."""
    payload = {
        "draft": str(draft_path),
        "pkg": str(pkg.path),
        "run_id": pkg.run_id,
        "schema_version": pkg.schema_version,
        "paragraphs": [asdict(r) for r in reports],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="apply_style_to_draft.py",
        description=(
            "Compute paragraph-level style alignment between a draft and a "
            "paper-style-distiller distill package. Used by "
            "style-guided-academic-writer to produce alignment reports."
        ),
    )
    parser.add_argument(
        "--pkg", required=True, type=Path, help="Path to the distill package JSON."
    )
    parser.add_argument(
        "--draft", required=True, type=Path, help="Path to the draft Markdown file."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Where to write the report. Defaults to stdout.",
    )
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="Output format. 'markdown' (default) or 'json'.",
    )
    parser.add_argument(
        "--section-hints",
        type=str,
        default=None,
        help=(
            "Comma-separated list of paragraph-index=section overrides, e.g. "
            "'0=Introduction,3=Method,7=Discussion'. Useful when the draft's "
            "headings are ambiguous or absent."
        ),
    )
    parser.add_argument(
        "--min-paragraph-templates",
        type=int,
        default=3,
        help="Maximum number of paragraph templates to report per paragraph (default 3).",
    )
    parser.add_argument(
        "--sentence-top-k",
        type=int,
        default=3,
        help="Maximum number of sentence patterns to report per paragraph (default 3).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable DEBUG-level logging.",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_arg_parser().parse_args(list(argv) if argv is not None else None)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    try:
        pkg = load_distill_package(args.pkg)
    except (FileNotFoundError, ValueError) as exc:
        LOG.error("failed to load distill package: %s", exc)
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if not args.draft.exists():
        LOG.error("draft file not found: %s", args.draft)
        print(f"error: draft file not found: {args.draft}", file=sys.stderr)
        return 2

    draft_text = args.draft.read_text(encoding="utf-8")
    paragraphs = split_draft_into_paragraphs(draft_text)
    if not paragraphs:
        LOG.error("no paragraphs extracted from draft %s", args.draft)
        print(f"error: no paragraphs extracted from draft {args.draft}", file=sys.stderr)
        return 2

    hints = _parse_section_hints(args.section_hints)
    for idx, section in hints.items():
        if 0 <= idx < len(paragraphs):
            paragraphs[idx].section = section
            paragraphs[idx].explicit_section = True
        else:
            LOG.warning(
                "section-hint index %d is out of range (have %d paragraphs)",
                idx,
                len(paragraphs),
            )

    LOG.info(
        "analysing %d paragraphs from %s with %d explicit section hints",
        len(paragraphs),
        args.draft,
        len(hints),
    )

    reports = build_report(
        paragraphs=paragraphs,
        pkg=pkg,
        min_paragraph_templates=max(0, args.min_paragraph_templates),
        sentence_top_k=max(0, args.sentence_top_k),
    )

    if args.format == "json":
        rendered = render_json_report(reports, pkg, args.draft)
    else:
        rendered = render_markdown_report(reports, pkg, args.draft)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        LOG.info("wrote report to %s", args.output)
    else:
        print(rendered)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())