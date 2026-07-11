#!/usr/bin/env python3
"""
export_for_writer.py — Split a distill-package.json into 4 downstream-consumable files.

The paper-style-distiller produces a single ``distill-package.json`` that bundles
sentence patterns, paragraph templates, terminology collocations, hedging
statistics, and supporting evidence. The downstream ``style-guided-academic-writer``
consumes these as four separate artifacts so it can index them independently.

Outputs (written to ``--out-dir``)::

    sentence-patterns.jsonl   one JSON object per line; loadable as a stream
    paragraph-templates.json  structured library + section index
    style-profile.json        high-level profile (tone, hedging, length, ...)
    retrieval-index.md        human-readable index grouped by section+intent

The script is pure stdlib (json, argparse, pathlib, logging, collections). It is
robust to schema drift: missing fields are logged as warnings and replaced with
sensible defaults; the CLI never aborts on a partial package.

Usage::

    python3 export_for_writer.py \\
        --pkg  runs/full11-core5-20260518-230538/full11-distill-package.json \\
        --out-dir /tmp/test-export/

Optional flags::

    --format json|yml   Reserved for future YAML output; only ``json`` is wired.
    --verbose           Enable DEBUG-level logging.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

LOG = logging.getLogger("export_for_writer")

# ---------------------------------------------------------------------------
# Constants — section / intent ordering used in retrieval index
# ---------------------------------------------------------------------------

CANONICAL_SECTIONS: Tuple[str, ...] = (
    "HeadPages",
    "Introduction",
    "RelatedWork",
    "Method",
    "Results",
    "Result",
    "Discussion",
    "Conclusion",
    "Abstract",
)

CANONICAL_INTENTS: Tuple[str, ...] = (
    "Background",
    "Gap",
    "Contribution",
    "Method",
    "Result",
    "Limitation",
    "FutureWork",
    "Claim",
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _safe_get(obj: Mapping[str, Any], *keys: str, default: Any = None) -> Any:
    """Return the first key that exists in ``obj``, else ``default``.

    Used to gracefully fall back across schema renames without crashing.
    """
    for k in keys:
        if k in obj:
            return obj[k]
    return default


def _load_package(path: Path) -> Dict[str, Any]:
    """Load a distill-package.json, exiting on JSON or IO errors."""
    if not path.is_file():
        LOG.error("Package file does not exist: %s", path)
        sys.exit(2)
    try:
        with path.open("r", encoding="utf-8") as fh:
            pkg = json.load(fh)
    except json.JSONDecodeError as exc:
        LOG.error("Package file is not valid JSON: %s (%s)", path, exc)
        sys.exit(2)
    if not isinstance(pkg, dict):
        LOG.error("Package root must be a JSON object, got %s", type(pkg).__name__)
        sys.exit(2)
    return pkg


def _ensure_out_dir(path: Path) -> None:
    """Create ``path`` (and parents) if missing."""
    path.mkdir(parents=True, exist_ok=True)
    LOG.info("Output directory ready: %s", path)


def _extract_slots(pattern: str, declared: Sequence[str]) -> Dict[str, str]:
    """Build a slot description dict from a pattern string and declared slots.

    The pattern uses ``{slot_name}``-style placeholders. We emit a dict so the
    writer can look up slot semantics (``slots["method"] = "..."``).
    Slots declared on the record but not present in the pattern are still
    emitted (with empty description) so the writer sees the full slot set.
    """
    found: List[str] = []
    cursor = 0
    text = pattern or ""
    while True:
        open_idx = text.find("{", cursor)
        if open_idx == -1:
            break
        close_idx = text.find("}", open_idx + 1)
        if close_idx == -1:
            break
        name = text[open_idx + 1:close_idx].strip()
        if name and name not in found:
            found.append(name)
        cursor = close_idx + 1

    declared_clean = [s for s in (declared or []) if isinstance(s, str)]
    all_slots = list(dict.fromkeys(found + declared_clean))  # dedup, preserve order

    return {slot: "" for slot in all_slots}


def _normalise_sentence(rec: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    """Validate and reshape a sentence-pattern record.

    Returns ``None`` for records that lack the minimum fields required to be
    useful to the writer (id and pattern). Logs a warning instead of aborting.
    """
    rec_id = rec.get("id")
    pattern = rec.get("pattern")
    if not rec_id or not isinstance(pattern, str):
        LOG.warning("Skipping sentence_pattern without id/pattern: %s", rec)
        return None

    declared_slots = rec.get("slots") or []
    if not isinstance(declared_slots, list):
        LOG.debug("Sentence %s: 'slots' not a list, coercing to empty", rec_id)
        declared_slots = []

    evidence = rec.get("evidence") or []
    if not isinstance(evidence, list):
        evidence = []

    return {
        "id": rec_id,
        "section": rec.get("section", "Unknown"),
        "intent": rec.get("intent", "Unknown"),
        "tense": rec.get("tense", "present"),
        "pattern": pattern,
        "slots": _extract_slots(pattern, declared_slots),
        "evidence": evidence,
        "confidence": rec.get("confidence", 0.0),
        # Optional enrichments kept for the writer; absent → omitted to keep JSONL tight.
        **(
            {"rhetorical_strength": rec["rhetorical_strength"]}
            if rec.get("rhetorical_strength")
            else {}
        ),
        **({"dedup_key": rec["dedup_key"]} if rec.get("dedup_key") else {}),
    }


def _normalise_paragraph(rec: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    """Validate and reshape a paragraph-template record."""
    rec_id = rec.get("id")
    template = rec.get("template")
    if not rec_id or not isinstance(template, str):
        LOG.warning("Skipping paragraph_template without id/template: %s", rec)
        return None

    block_order = rec.get("block_order") or []
    if not isinstance(block_order, list):
        block_order = []

    # If block_order missing, synthesise from template tags like "[Background]"
    if not block_order:
        block_order = _extract_block_order_from_template(template)

    required_slots = rec.get("required_slots") or []
    optional_slots = rec.get("optional_slots") or []
    if not isinstance(required_slots, list):
        required_slots = []
    if not isinstance(optional_slots, list):
        optional_slots = []

    merged_slots: Dict[str, str] = {}
    for slot in required_slots:
        if isinstance(slot, str):
            merged_slots[slot] = "required"
    for slot in optional_slots:
        if isinstance(slot, str):
            merged_slots.setdefault(slot, "optional")

    evidence = []
    if rec.get("evidence_count") is not None:
        evidence.append({
            "evidence_count": rec.get("evidence_count"),
            "support_ratio": rec.get("support_ratio", 0.0),
        })
    if rec.get("example_hints"):
        evidence.append({"example_hints": rec.get("example_hints")})

    return {
        "id": rec_id,
        "section": rec.get("section", "Unknown"),
        "intent": rec.get("intent", "Unknown"),
        "structure": block_order,
        "template": template,
        "slots": merged_slots,
        "evidence": evidence,
        "confidence": rec.get("confidence", 0.0),
        **({"dedup_key": rec["dedup_key"]} if rec.get("dedup_key") else {}),
    }


def _extract_block_order_from_template(template: str) -> List[str]:
    """Pull ``[BlockName]`` markers out of a paragraph template string."""
    blocks: List[str] = []
    cursor = 0
    while True:
        open_idx = template.find("[", cursor)
        if open_idx == -1:
            break
        close_idx = template.find("]", open_idx + 1)
        if close_idx == -1:
            break
        block = template[open_idx + 1:close_idx].strip()
        if block and block not in blocks:
            blocks.append(block)
        cursor = close_idx + 1
    return blocks


# ---------------------------------------------------------------------------
# Output builders
# ---------------------------------------------------------------------------


def build_sentence_patterns_jsonl(
    sentences: Sequence[Mapping[str, Any]]
) -> str:
    """Render the JSONL payload as a single string."""
    lines: List[str] = []
    for rec in sentences:
        lines.append(json.dumps(rec, ensure_ascii=False, sort_keys=False))
    return "\n".join(lines) + ("\n" if lines else "")


def build_paragraph_templates_json(
    templates: Sequence[Mapping[str, Any]]
) -> str:
    """Build the structured paragraph-template library with section index."""
    index: Dict[str, List[str]] = defaultdict(list)
    serialisable: List[Dict[str, Any]] = []

    for rec in templates:
        serialisable.append(dict(rec))
        section = rec.get("section", "Unknown")
        index[section].append(rec["id"])

    payload = {
        "templates": serialisable,
        "index_by_section": {section: ids for section, ids in index.items()},
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def _dominant(values: Iterable[Any]) -> Tuple[Any, int]:
    """Return the most-common value and its count."""
    counter = Counter(values)
    if not counter:
        return ("unknown", 0)
    value, count = counter.most_common(1)[0]
    return (value, count)


def _classify_tone(
    rhetorical_mix: Mapping[str, int], total: int
) -> str:
    """Map rhetorical-strength distribution to a coarse tone label."""
    if total == 0:
        return "neutral"
    strong_frac = rhetorical_mix.get("strong", 0) / total
    soft_frac = rhetorical_mix.get("soft", 0) / total
    if strong_frac >= 0.30:
        return "confident"
    if soft_frac >= 0.20:
        return "cautious"
    return "neutral"


def build_style_profile_json(pkg: Mapping[str, Any]) -> str:
    """Derive a high-level style profile from the package.

    The profile is the writer's first read; it must remain small and stable.
    """
    sentences = pkg.get("sentence_patterns") or []
    paragraphs = pkg.get("paragraph_templates") or []
    terminology = pkg.get("terminology_collocation") or []
    tving = pkg.get("tense_voice_hedging") or []

    sentence_total = len(sentences)
    paragraph_total = len(paragraphs)

    # Pattern length statistics (tokens)
    lengths = [
        len((s.get("pattern") or "").split())
        for s in sentences
        if isinstance(s, Mapping)
    ]
    length_stats = {
        "n_samples": len(lengths),
        "min": min(lengths) if lengths else 0,
        "max": max(lengths) if lengths else 0,
        "mean": round(mean(lengths), 2) if lengths else 0.0,
        "median": median(lengths) if lengths else 0.0,
    }

    # Tense mix
    tense_counter = Counter(
        s.get("tense", "unknown")
        for s in sentences
        if isinstance(s, Mapping)
    )
    dominant_tense, _ = _dominant(tense_counter)

    # Rhetorical strength mix
    rhetorical_counter = Counter(
        s.get("rhetorical_strength", "neutral")
        for s in sentences
        if isinstance(s, Mapping)
    )

    # Hedging strength from tense_voice_hedging sidecar
    hedging_counter = Counter(
        t.get("hedging", "unknown")
        for t in tving
        if isinstance(t, Mapping)
    )
    voice_counter = Counter(
        t.get("voice", "unknown")
        for t in tving
        if isinstance(t, Mapping)
    )

    hedging_strength = _classify_hedging(hedging_counter, sum(hedging_counter.values()))

    # Top terminology collocations (top 10)
    top_terms = [
        {
            "pair": item.get("pair"),
            "count": item.get("count", 0),
        }
        for item in terminology[:10]
        if isinstance(item, Mapping) and item.get("pair")
    ]

    tone = _classify_tone(rhetorical_counter, sentence_total)

    # Section coverage for the writer to know what is well-supported
    section_counter = Counter(
        s.get("section", "Unknown")
        for s in sentences
        if isinstance(s, Mapping)
    )
    intent_counter = Counter(
        s.get("intent", "Unknown")
        for s in sentences
        if isinstance(s, Mapping)
    )

    metrics = pkg.get("metrics") or {}

    profile = {
        "schema_version": "v1",
        "run_id": _safe_get(pkg.get("run_manifest") or {}, "run_id"),
        "tone": tone,
        "hedging_strength": hedging_strength,
        "rhetorical_strength_mix": dict(rhetorical_counter),
        "dominant_tense": dominant_tense,
        "tense_mix": dict(tense_counter),
        "voice_mix": dict(voice_counter),
        "typical_sentence_length": length_stats,
        "terminology_preferences": top_terms,
        "section_coverage": dict(section_counter.most_common()),
        "intent_coverage": dict(intent_counter.most_common()),
        "counts": {
            "sentence_patterns": sentence_total,
            "paragraph_templates": paragraph_total,
            "terminology_collocation": len(terminology),
        },
        "metrics": metrics,
    }
    return json.dumps(profile, ensure_ascii=False, indent=2) + "\n"


def _classify_hedging(counter: Mapping[str, int], total: int) -> str:
    """Bucket hedging frequency into strong / medium / weak labels."""
    if total == 0:
        return "unknown"
    hedged_frac = counter.get("hedged", 0) / total
    if hedged_frac >= 0.30:
        return "strong"
    if hedged_frac >= 0.10:
        return "medium"
    return "weak"


def build_retrieval_index_md(
    sentences: Sequence[Mapping[str, Any]],
    templates: Sequence[Mapping[str, Any]],
    profile: Mapping[str, Any],
) -> str:
    """Render a human-readable index grouped by section + intent."""
    lines: List[str] = []
    lines.append("# Style Distillation — Retrieval Index")
    lines.append("")
    lines.append(
        "Auto-generated by `export_for_writer.py`. Use this index to find sentence "
        "patterns and paragraph templates by section and intent within seconds."
    )
    lines.append("")

    # Profile summary at the top
    lines.append("## Profile at a Glance")
    lines.append("")
    lines.append(f"- **Tone**: {profile.get('tone', 'unknown')}")
    lines.append(f"- **Hedging strength**: {profile.get('hedging_strength', 'unknown')}")
    lines.append(f"- **Dominant tense**: {profile.get('dominant_tense', 'unknown')}")
    length = profile.get("typical_sentence_length") or {}
    lines.append(
        f"- **Typical sentence length**: {length.get('mean', 0)} tokens "
        f"(min={length.get('min', 0)}, max={length.get('max', 0)}, "
        f"median={length.get('median', 0)})"
    )
    lines.append(f"- **Run ID**: {profile.get('run_id', 'unknown')}")
    counts = profile.get("counts") or {}
    lines.append(
        f"- **Counts**: {counts.get('sentence_patterns', 0)} sentence patterns, "
        f"{counts.get('paragraph_templates', 0)} paragraph templates"
    )
    lines.append("")

    # Group sentences by section then intent
    lines.append("## Sentence Patterns by Section × Intent")
    lines.append("")
    section_map: Dict[str, Dict[str, List[Mapping[str, Any]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for rec in sentences:
        section_map[rec.get("section", "Unknown")][rec.get("intent", "Unknown")].append(rec)

    ordered_sections = sorted(
        section_map.keys(),
        key=lambda s: (
            CANONICAL_SECTIONS.index(s) if s in CANONICAL_SECTIONS else len(CANONICAL_SECTIONS),
            s,
        ),
    )

    for section in ordered_sections:
        lines.append(f"### {section}")
        lines.append("")
        intents = section_map[section]
        ordered_intents = sorted(
            intents.keys(),
            key=lambda i: (
                CANONICAL_INTENTS.index(i) if i in CANONICAL_INTENTS else len(CANONICAL_INTENTS),
                i,
            ),
        )
        for intent in ordered_intents:
            patterns = intents[intent]
            lines.append(f"#### {section} · {intent} ({len(patterns)} patterns)")
            lines.append("")
            # Show top-5 by confidence for quick scanning
            shown = sorted(patterns, key=lambda p: p.get("confidence", 0), reverse=True)[:5]
            for rec in shown:
                excerpt = (rec.get("pattern") or "").strip().replace("\n", " ")
                if len(excerpt) > 140:
                    excerpt = excerpt[:137] + "..."
                anchor = rec.get("id", "?")
                confidence = rec.get("confidence", 0)
                lines.append(f"- `{anchor}` _(conf={confidence:.2f})_: {excerpt}")
            if len(patterns) > len(shown):
                lines.append(f"- _…and {len(patterns) - len(shown)} more_")
            lines.append("")

    # Paragraph templates index
    lines.append("## Paragraph Templates by Section")
    lines.append("")
    pt_section: Dict[str, List[Mapping[str, Any]]] = defaultdict(list)
    for rec in templates:
        pt_section[rec.get("section", "Unknown")].append(rec)

    ordered_pt_sections = sorted(
        pt_section.keys(),
        key=lambda s: (
            CANONICAL_SECTIONS.index(s) if s in CANONICAL_SECTIONS else len(CANONICAL_SECTIONS),
            s,
        ),
    )

    for section in ordered_pt_sections:
        templates_here = pt_section[section]
        lines.append(f"### {section} ({len(templates_here)} templates)")
        lines.append("")
        for rec in templates_here:
            anchor = rec.get("id", "?")
            intent = rec.get("intent", "Unknown")
            structure = rec.get("structure") or []
            structure_str = " → ".join(structure) if structure else "(unstructured)"
            confidence = rec.get("confidence", 0)
            lines.append(
                f"- `{anchor}` — {section} · {intent} _(conf={confidence:.2f})_: "
                f"{structure_str}"
            )
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(
        "Generated by `paper-style-distiller/scripts/export_for_writer.py`. "
        "Re-run after any distill-package update to refresh this index."
    )
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def _collect_sentences(pkg: Mapping[str, Any]) -> List[Mapping[str, Any]]:
    raw = pkg.get("sentence_patterns") or []
    out: List[Mapping[str, Any]] = []
    skipped = 0
    for rec in raw:
        if not isinstance(rec, Mapping):
            skipped += 1
            continue
        normalised = _normalise_sentence(rec)
        if normalised is None:
            skipped += 1
            continue
        out.append(normalised)
    if skipped:
        LOG.warning("Skipped %d malformed sentence-pattern records", skipped)
    LOG.info("Normalised %d sentence patterns", len(out))
    return out


def _collect_paragraphs(pkg: Mapping[str, Any]) -> List[Mapping[str, Any]]:
    raw = pkg.get("paragraph_templates") or []
    out: List[Mapping[str, Any]] = []
    skipped = 0
    for rec in raw:
        if not isinstance(rec, Mapping):
            skipped += 1
            continue
        normalised = _normalise_paragraph(rec)
        if normalised is None:
            skipped += 1
            continue
        out.append(normalised)
    if skipped:
        LOG.warning("Skipped %d malformed paragraph-template records", skipped)
    LOG.info("Normalised %d paragraph templates", len(out))
    return out


def export(pkg_path: Path, out_dir: Path) -> Dict[str, Path]:
    """Top-level export. Returns a dict of output path → on-disk location."""
    LOG.info("Loading package: %s", pkg_path)
    pkg = _load_package(pkg_path)

    sentences = _collect_sentences(pkg)
    paragraphs = _collect_paragraphs(pkg)

    profile_str = build_style_profile_json(pkg)
    sentences_str = build_sentence_patterns_jsonl(sentences)
    templates_str = build_paragraph_templates_json(paragraphs)

    # We need the profile back as a dict for the retrieval index
    profile_dict = json.loads(profile_str)

    index_md = build_retrieval_index_md(sentences, paragraphs, profile_dict)

    _ensure_out_dir(out_dir)

    outputs: Dict[str, Path] = {}
    targets = {
        "sentence-patterns.jsonl": sentences_str,
        "paragraph-templates.json": templates_str,
        "style-profile.json": profile_str,
        "retrieval-index.md": index_md,
    }
    for name, payload in targets.items():
        path = out_dir / name
        path.write_text(payload, encoding="utf-8")
        LOG.info("Wrote %s (%d bytes)", path, path.stat().st_size)
        outputs[name] = path

    return outputs


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="export_for_writer.py",
        description=(
            "Split a paper-style-distiller distill-package.json into 4 "
            "downstream-consumable files for the style-guided-academic-writer."
        ),
    )
    parser.add_argument(
        "--pkg",
        required=True,
        type=Path,
        help="Path to the distill-package.json produced by run_core5_bootstrap.py.",
    )
    parser.add_argument(
        "--out-dir",
        required=True,
        type=Path,
        help="Directory to write the 4 output files into (created if missing).",
    )
    parser.add_argument(
        "--format",
        choices=("json", "yml"),
        default="json",
        help=(
            "Output format family. Only 'json' is wired today; 'yml' is reserved "
            "for a future YAML emitter. Default: json."
        ),
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable DEBUG-level logging.",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s export_for_writer: %(message)s",
    )

    if args.format != "json":
        LOG.warning(
            "Format '%s' is reserved but not yet implemented; falling back to JSON.",
            args.format,
        )

    try:
        outputs = export(args.pkg, args.out_dir)
    except OSError as exc:
        LOG.error("I/O error during export: %s", exc)
        return 1

    LOG.info(
        "Done. Wrote %d files to %s",
        len(outputs),
        args.out_dir,
    )
    for name, path in outputs.items():
        LOG.info("  • %s", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())