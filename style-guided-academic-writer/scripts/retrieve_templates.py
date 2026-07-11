#!/usr/bin/env python3
"""Retrieve paragraph templates and sentence patterns from a distill package.

This CLI is the entry point that ``style-guided-academic-writer`` uses to
pull reusable style assets out of a paper-style-distiller JSON package. It
supports the four-axis retrieval hierarchy described in the skill's
``## 快速检索规则`` section:

1. ``section``     (Introduction / Method / Result / Discussion / Conclusion)
2. ``intent``      (Background / Gap / Contribution / Result / Limitation)
3. ``tense``       (past / present / present-perfect) — sentence patterns only
4. ``rhetorical-strength`` (soft / neutral / strong) — sentence patterns only

Filters are combined with logical AND. When a query returns no rows, the
script applies the skill's documented fallback strategy: relax
``rhetorical-strength``, then ``tense``, then fall back to section+intent
only. Each fallback step is reported so the caller can see why the output
looks the way it does.

Examples
---------

Look up paragraph templates for an Introduction gap statement::

    python3 retrieve_templates.py \\
        --pkg paper-style-distiller/runs/full11-core5-20260518-230538/full11-distill-package.json \\
        --section Introduction --intent Gap --format table

Same query but constrained to sentence patterns with ``present`` tense and
``strong`` rhetoric::

    python3 retrieve_templates.py \\
        --pkg runs/full11-distill-package.json \\
        --section Introduction --intent Gap --tense present --rhetorical-strength strong \\
        --min-confidence 0.8 --limit 5

Dump everything as JSON for piping into another tool::

    python3 retrieve_templates.py \\
        --pkg runs/full11-distill-package.json --kind sentence --format json \\
        --section Method --intent Contribution > method-contribution.json

Print a top-level summary of the package without any filtering::

    python3 retrieve_templates.py --pkg runs/full11-distill-package.json --summary
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Iterable

# Allow ``python3 scripts/retrieve_templates.py`` from any cwd by adding the
# scripts directory to sys.path when invoked directly.
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from _pkg_loader import (  # noqa: E402  (import after sys.path tweak)
    DistillPackage,
    ParagraphTemplate,
    SentencePattern,
    load_distill_package,
    summary as package_summary,
)

LOG = logging.getLogger("sgaw.retrieve")


# ---------------------------------------------------------------------------
# CLI plumbing
# ---------------------------------------------------------------------------


def build_arg_parser() -> argparse.ArgumentParser:
    """Build the argument parser for this CLI."""
    parser = argparse.ArgumentParser(
        prog="retrieve_templates.py",
        description=(
            "Query paragraph templates and sentence patterns in a "
            "paper-style-distiller distill package. Used by "
            "style-guided-academic-writer to look up reusable style assets."
        ),
    )
    parser.add_argument(
        "--pkg",
        required=True,
        type=Path,
        help="Path to the distill package JSON file.",
    )
    parser.add_argument(
        "--kind",
        choices=("paragraph", "sentence", "both"),
        default="both",
        help=(
            "Which template family to retrieve. "
            "'paragraph' returns paragraph_templates; "
            "'sentence' returns sentence_patterns; "
            "'both' (default) returns both side by side."
        ),
    )
    parser.add_argument(
        "--section",
        type=str,
        default=None,
        help=(
            "Filter by section (substring, case-insensitive). "
            "Examples: Introduction, Method, Result, Discussion, Conclusion."
        ),
    )
    parser.add_argument(
        "--intent",
        type=str,
        default=None,
        help=(
            "Filter by intent (substring, case-insensitive). "
            "Examples: Background, Gap, Contribution, Result, Limitation."
        ),
    )
    parser.add_argument(
        "--tense",
        choices=("past", "present", "present-perfect"),
        default=None,
        help="Sentence-level tense filter. Ignored when --kind=paragraph.",
    )
    parser.add_argument(
        "--rhetorical-strength",
        choices=("soft", "neutral", "strong"),
        default=None,
        help="Sentence-level rhetorical strength filter. Ignored when --kind=paragraph.",
    )
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.0,
        help="Drop rows with confidence below this threshold (0..1).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Cap the number of rows returned per kind (after sorting).",
    )
    parser.add_argument(
        "--format",
        choices=("table", "json"),
        default="table",
        help="Output format. 'table' prints a human-readable summary; "
        "'json' prints the structured records for downstream tooling.",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print a one-shot summary of the package and exit. "
        "Useful for verifying the package is well-formed before querying.",
    )
    parser.add_argument(
        "--no-fallback",
        action="store_true",
        help="Disable the relaxed-search fallback. By default the script "
        "follows the skill's documented fallback order (relax strength, "
        "then tense, then section+intent).",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable DEBUG-level logging.",
    )
    return parser


# ---------------------------------------------------------------------------
# Filtering with the skill's documented fallback strategy
# ---------------------------------------------------------------------------


def _filter_paragraphs(
    pkg: DistillPackage,
    section: str | None,
    intent: str | None,
    min_confidence: float,
) -> list[ParagraphTemplate]:
    return pkg.query_paragraphs(
        section=section, intent=intent, min_confidence=min_confidence
    )


def _filter_sentences(
    pkg: DistillPackage,
    section: str | None,
    intent: str | None,
    tense: str | None,
    rhetorical_strength: str | None,
    min_confidence: float,
) -> list[SentencePattern]:
    return pkg.query_sentences(
        section=section,
        intent=intent,
        tense=tense,
        rhetorical_strength=rhetorical_strength,
        min_confidence=min_confidence,
    )


def retrieve_with_fallback(
    pkg: DistillPackage,
    kind: str,
    section: str | None,
    intent: str | None,
    tense: str | None,
    rhetorical_strength: str | None,
    min_confidence: float,
    limit: int | None,
    use_fallback: bool,
) -> dict[str, Any]:
    """Run the query and (optionally) apply the skill's fallback strategy.

    Returns a dict with two lists (``paragraphs`` and ``sentences``) and a
    ``fallback_trace`` describing which relaxations were applied so the
    caller can explain why they got what they got.
    """
    trace: list[str] = []
    paragraphs: list[ParagraphTemplate] = []
    sentences: list[SentencePattern] = []

    if kind in ("paragraph", "both"):
        paragraphs = _filter_paragraphs(pkg, section, intent, min_confidence)
        if not paragraphs and use_fallback:
            # Fallback: drop section+intent, only keep section
            if section is not None and intent is not None:
                trace.append(
                    "no paragraphs matched section+intent — relaxing to section only"
                )
                paragraphs = _filter_paragraphs(pkg, section, None, min_confidence)
            # Next fallback: drop section+intent entirely
            if not paragraphs and (section is not None or intent is not None):
                trace.append(
                    "still empty — relaxing to package-wide top-confidence paragraphs"
                )
                paragraphs = _filter_paragraphs(pkg, None, None, min_confidence)

    if kind in ("sentence", "both"):
        sentences = _filter_sentences(
            pkg, section, intent, tense, rhetorical_strength, min_confidence
        )
        if not sentences and use_fallback:
            # Fallback 1: relax rhetorical strength
            if rhetorical_strength is not None:
                trace.append(
                    "no sentences matched strength — relaxing rhetorical-strength"
                )
                sentences = _filter_sentences(
                    pkg, section, intent, tense, None, min_confidence
                )
            # Fallback 2: relax tense
            if not sentences and tense is not None:
                trace.append("still empty — relaxing tense")
                sentences = _filter_sentences(
                    pkg, section, intent, None, rhetorical_strength, min_confidence
                )
                if not sentences:
                    sentences = _filter_sentences(
                        pkg, section, intent, None, None, min_confidence
                    )
            # Fallback 3: only section+intent
            if not sentences and (section is not None or intent is not None):
                trace.append(
                    "still empty — relaxing to section+intent only"
                )
                sentences = _filter_sentences(
                    pkg, section, intent, None, None, min_confidence
                )
            # Fallback 4: package-wide
            if not sentences:
                trace.append(
                    "still empty — relaxing to package-wide top-confidence sentences"
                )
                sentences = _filter_sentences(pkg, None, None, None, None, min_confidence)

    if limit is not None:
        if paragraphs:
            paragraphs = paragraphs[:limit]
        if sentences:
            sentences = sentences[:limit]

    return {
        "paragraphs": paragraphs,
        "sentences": sentences,
        "fallback_trace": trace,
    }


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def _render_table(records: dict[str, Any]) -> str:
    """Render retrieved records as a human-readable plain-text report."""
    out: list[str] = []
    paragraphs = records["paragraphs"]
    sentences = records["sentences"]
    trace = records["fallback_trace"]

    out.append("=" * 72)
    out.append("style-guided-academic-writer :: retrieve_templates")
    out.append("=" * 72)
    if trace:
        out.append("Fallback applied:")
        for step in trace:
            out.append(f"  - {step}")
        out.append("-" * 72)

    out.append(
        f"Paragraph templates matched: {len(paragraphs)}    "
        f"Sentence patterns matched: {len(sentences)}"
    )
    out.append("-" * 72)

    if paragraphs:
        out.append("PARAGRAPH TEMPLATES")
        out.append("-" * 72)
        for tpl in paragraphs:
            out.append(
                f"[{tpl.id}] {tpl.section} / {tpl.intent}  "
                f"(conf={tpl.confidence:.2f}, evidence={tpl.evidence_count})"
            )
            out.append(f"  template : {tpl.template}")
            if tpl.required_slots:
                out.append(f"  required : {', '.join(tpl.required_slots)}")
            if tpl.optional_slots:
                out.append(f"  optional : {', '.join(tpl.optional_slots)}")
            if tpl.block_order:
                out.append(f"  order    : {' -> '.join(tpl.block_order)}")
            if tpl.dedup_key:
                out.append(f"  dedup    : {tpl.dedup_key}")
            out.append("")

    if sentences:
        out.append("SENTENCE PATTERNS")
        out.append("-" * 72)
        for sp in sentences:
            header = (
                f"[{sp.id}] {sp.section} / {sp.intent}  "
                f"tense={sp.tense}  rh={sp.rhetorical_strength}  "
                f"conf={sp.confidence:.2f}"
            )
            out.append(header)
            snippet = sp.pattern.strip()
            if len(snippet) > 220:
                snippet = snippet[:217] + "..."
            out.append(f"  pattern : {snippet}")
            if sp.slots:
                out.append(f"  slots   : {', '.join(sp.slots)}")
            if sp.evidence:
                src = sp.evidence[0].get("source_paper_id", "<unknown>")
                pid = sp.evidence[0].get(
                    "source_paragraph_id",
                    sp.evidence[0].get("source_paragrap_id", "<unknown>"),
                )
                out.append(f"  source  : {src} @ {pid}")
            out.append("")

    if not paragraphs and not sentences:
        out.append(
            "No rows matched the query. Try relaxing --section/--intent, "
            "lowering --min-confidence, or removing --no-fallback."
        )

    return "\n".join(out)


def _render_json(records: dict[str, Any]) -> str:
    """Render retrieved records as JSON for downstream tooling."""
    payload = {
        "paragraphs": [
            {
                "id": t.id,
                "section": t.section,
                "intent": t.intent,
                "template": t.template,
                "required_slots": t.required_slots,
                "optional_slots": t.optional_slots,
                "confidence": t.confidence,
                "evidence_count": t.evidence_count,
                "support_ratio": t.support_ratio,
                "block_order": t.block_order,
                "dedup_key": t.dedup_key,
            }
            for t in records["paragraphs"]
        ],
        "sentences": [
            {
                "id": s.id,
                "section": s.section,
                "intent": s.intent,
                "tense": s.tense,
                "rhetorical_strength": s.rhetorical_strength,
                "pattern": s.pattern,
                "slots": s.slots,
                "confidence": s.confidence,
                "evidence": s.evidence,
                "dedup_key": s.dedup_key,
            }
            for s in records["sentences"]
        ],
        "fallback_trace": records["fallback_trace"],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main(argv: Iterable[str] | None = None) -> int:
    """CLI entry point; returns a process exit code."""
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

    if args.summary:
        if args.format == "json":
            print(json.dumps(package_summary(pkg), ensure_ascii=False, indent=2))
        else:
            s = package_summary(pkg)
            print(f"package       : {s['path']}")
            print(f"run_id        : {s['run_id']}")
            print(f"schema_version: {s['schema_version']}")
            print("counts:")
            for k, v in s["counts"].items():
                print(f"  {k:30s} {v}")
            print(f"sections      : {', '.join(s['sections']) or '(none)'}")
            print(f"intents       : {', '.join(s['intents']) or '(none)'}")
            print(f"tenses        : {', '.join(s['tenses']) or '(none)'}")
            print(
                f"rhetoric      : {', '.join(s['rhetorical_strengths']) or '(none)'}"
            )
            if s["metrics"]:
                print("metrics       :")
                for k, v in s["metrics"].items():
                    print(f"  {k:30s} {v}")
        return 0

    if args.min_confidence < 0.0 or args.min_confidence > 1.0:
        LOG.error("--min-confidence must be between 0 and 1")
        return 2
    if args.limit is not None and args.limit <= 0:
        LOG.error("--limit must be a positive integer")
        return 2

    records = retrieve_with_fallback(
        pkg=pkg,
        kind=args.kind,
        section=args.section,
        intent=args.intent,
        tense=args.tense,
        rhetorical_strength=args.rhetorical_strength,
        min_confidence=args.min_confidence,
        limit=args.limit,
        use_fallback=not args.no_fallback,
    )

    if args.format == "json":
        print(_render_json(records))
    else:
        print(_render_table(records))

    # Exit code 0 if anything matched (or the query was empty by design),
    # 3 if the caller asked for something specific and we got nothing back.
    total = len(records["paragraphs"]) + len(records["sentences"])
    specific = bool(args.section or args.intent or args.tense or args.rhetorical_strength)
    if total == 0 and specific and not args.no_fallback:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())