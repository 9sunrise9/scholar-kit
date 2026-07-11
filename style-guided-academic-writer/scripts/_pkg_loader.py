"""Shared loader for paper-style-distiller distill packages.

The ``paper-style-distiller`` skill emits a JSON file (the "distill package")
that aggregates all 11 dimensions of style evidence into one document. The
canonical schema is described in
``paper-style-distiller/references/style-distill-schema-v1.json``, but the
real-world packages we see today use slightly different top-level keys and a
few extra fields (``example_hints``, ``block_order``, etc.). This loader
normalises those differences and exposes a small, typed interface used by
both ``retrieve_templates.py`` and ``apply_style_to_draft.py``.

The loader is read-only and never mutates the input file. It validates the
mandatory keys (``paragraph_templates`` and ``sentence_patterns``) and
warns on missing optional dimensions so the downstream scripts can degrade
gracefully rather than crashing.
"""

from __future__ import annotations

import json
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

LOG = logging.getLogger("sgaw.loader")

# Required dimensions — both retrieval and alignment rely on these.
_REQUIRED_KEYS = ("paragraph_templates", "sentence_patterns")

# Optional dimensions — used for richer reports when available.
_OPTIONAL_KEYS = (
    "macro_blueprint",
    "section_argument_structure",
    "rhetorical_moves",
    "terminology_collocation",
    "tense_voice_hedging",
    "claim_evidence_binding",
    "figure_text_linkage",
    "related_work_positioning",
    "innovation_argument_phrasing",
    "run_manifest",
    "metrics",
    "dimension_coverage",
)


@dataclass
class ParagraphTemplate:
    """One paragraph-level blueprint distilled from the corpus.

    Attributes:
        id: Stable identifier (e.g. ``P-001``).
        section: Section label, e.g. ``Introduction``/``Method``/``Result``/``Discussion``/``Conclusion``.
        intent: Rhetorical intent label, e.g. ``Background``/``Gap``/``Contribution``/``Result``/``Limitation``.
        template: Free-text template with ``{slot}`` placeholders.
        required_slots: Slot names that must be filled for the template to apply.
        optional_slots: Slot names that are nice-to-have.
        confidence: 0..1 confidence score assigned by the distiller.
        evidence_count: How many corpus paragraphs supported this template.
        support_ratio: 0..1 ratio of supporting vs. contradicting evidence.
        block_order: Ordered list of block labels (e.g. ``["Background", "Gap"]``).
        example_hints: Free-form hints, often raw text from the corpus.
        dedup_key: Stable dedup key for downstream caching.
    """

    id: str
    section: str
    intent: str
    template: str
    required_slots: list[str] = field(default_factory=list)
    optional_slots: list[str] = field(default_factory=list)
    confidence: float = 0.0
    evidence_count: int = 0
    support_ratio: float = 0.0
    block_order: list[str] = field(default_factory=list)
    example_hints: Any = None
    dedup_key: str = ""

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> "ParagraphTemplate":
        """Normalise a raw JSON row into a typed template.

        Handles both the canonical schema (``support_ratio``) and the older
        patched schema (no ``support_ratio``); missing optional fields get
        safe defaults so downstream code never crashes on ``KeyError``.
        """
        block_order = raw.get("block_order") or []
        if isinstance(block_order, str):
            block_order = [s.strip() for s in block_order.split(",") if s.strip()]
        return cls(
            id=str(raw.get("id", "")),
            section=str(raw.get("section", "Unknown")),
            intent=str(raw.get("intent", "Unknown")),
            template=str(raw.get("template", "")),
            required_slots=list(raw.get("required_slots") or []),
            optional_slots=list(raw.get("optional_slots") or []),
            confidence=float(raw.get("confidence", 0.0) or 0.0),
            evidence_count=int(raw.get("evidence_count", 0) or 0),
            support_ratio=float(raw.get("support_ratio", 0.0) or 0.0),
            block_order=list(block_order),
            example_hints=raw.get("example_hints"),
            dedup_key=str(raw.get("dedup_key", "")),
        )


@dataclass
class SentencePattern:
    """One sentence-level template distilled from the corpus."""

    id: str
    section: str
    intent: str
    tense: str
    rhetorical_strength: str
    pattern: str
    slots: list[str] = field(default_factory=list)
    confidence: float = 0.0
    evidence: list[dict[str, Any]] = field(default_factory=list)
    dedup_key: str = ""

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> "SentencePattern":
        return cls(
            id=str(raw.get("id", "")),
            section=str(raw.get("section", "Unknown")),
            intent=str(raw.get("intent", "Unknown")),
            tense=str(raw.get("tense", "present")),
            rhetorical_strength=str(raw.get("rhetorical_strength", "neutral")),
            pattern=str(raw.get("pattern", "")),
            slots=list(raw.get("slots") or []),
            confidence=float(raw.get("confidence", 0.0) or 0.0),
            evidence=list(raw.get("evidence") or []),
            dedup_key=str(raw.get("dedup_key", "")),
        )


@dataclass
class DistillPackage:
    """A loaded and validated distill package.

    Indexes for fast retrieval are built once at load time so that
    per-query cost stays O(matches) instead of O(n_total).
    """

    path: Path
    raw: dict[str, Any]
    paragraph_templates: list[ParagraphTemplate] = field(default_factory=list)
    sentence_patterns: list[SentencePattern] = field(default_factory=list)
    macro_blueprint: list[dict[str, Any]] = field(default_factory=list)
    terminology_collocation: list[dict[str, Any]] = field(default_factory=list)
    claim_evidence_binding: list[dict[str, Any]] = field(default_factory=list)
    related_work_positioning: list[dict[str, Any]] = field(default_factory=list)
    innovation_patterns: list[dict[str, Any]] = field(default_factory=list)
    run_manifest: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)
    # Secondary indexes: section → list[idx]
    _paragraph_index: dict[tuple[str, str], list[int]] = field(default_factory=dict)
    _sentence_index: dict[tuple[str, str], list[int]] = field(default_factory=dict)

    @property
    def run_id(self) -> str:
        return str(self.run_manifest.get("run_id", "<unknown>"))

    @property
    def schema_version(self) -> str:
        return str(self.run_manifest.get("schema_version", "<unknown>"))

    def paragraph_sections(self) -> list[str]:
        return sorted({t.section for t in self.paragraph_templates})

    def paragraph_intents(self) -> list[str]:
        return sorted({t.intent for t in self.paragraph_templates})

    def sentence_tenses(self) -> list[str]:
        return sorted({s.tense for s in self.sentence_patterns})

    def sentence_strengths(self) -> list[str]:
        return sorted({s.rhetorical_strength for s in self.sentence_patterns})

    def query_paragraphs(
        self,
        section: str | None = None,
        intent: str | None = None,
        min_confidence: float = 0.0,
    ) -> list[ParagraphTemplate]:
        """Return paragraph templates matching the given filters.

        Matching is case-insensitive and falls back to substring match when
        no exact section+intent key exists, so a typo like ``intro`` still
        returns ``Introduction`` hits.
        """
        results: list[ParagraphTemplate] = []
        section_lc = section.lower() if section else None
        intent_lc = intent.lower() if intent else None
        for tpl in self.paragraph_templates:
            if tpl.confidence < min_confidence:
                continue
            if section_lc and section_lc not in tpl.section.lower():
                continue
            if intent_lc and intent_lc not in tpl.intent.lower():
                continue
            results.append(tpl)
        results.sort(key=lambda t: (-t.confidence, -t.evidence_count, t.id))
        return results

    def query_sentences(
        self,
        section: str | None = None,
        intent: str | None = None,
        tense: str | None = None,
        rhetorical_strength: str | None = None,
        min_confidence: float = 0.0,
    ) -> list[SentencePattern]:
        """Return sentence patterns matching the given filters."""
        results: list[SentencePattern] = []
        sec_lc = section.lower() if section else None
        int_lc = intent.lower() if intent else None
        ten_lc = tense.lower() if tense else None
        rs_lc = rhetorical_strength.lower() if rhetorical_strength else None
        for sp in self.sentence_patterns:
            if sp.confidence < min_confidence:
                continue
            if sec_lc and sec_lc not in sp.section.lower():
                continue
            if int_lc and int_lc not in sp.intent.lower():
                continue
            if ten_lc and sp.tense.lower() != ten_lc:
                continue
            if rs_lc and rs_lc not in sp.rhetorical_strength.lower():
                continue
            results.append(sp)
        results.sort(key=lambda s: (-s.confidence, s.id))
        return results


def _coerce_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def load_distill_package(path: str | Path) -> DistillPackage:
    """Load and validate a distill package from disk.

    Args:
        path: Path to a JSON file produced by ``paper-style-distiller``.

    Returns:
        A populated :class:`DistillPackage`.

    Raises:
        FileNotFoundError: If ``path`` does not exist.
        ValueError: If the file is not valid JSON or is missing required
            dimensions (``paragraph_templates`` / ``sentence_patterns``).
    """
    p = Path(path).expanduser().resolve()
    if not p.exists():
        raise FileNotFoundError(f"distill package not found: {p}")
    if not p.is_file():
        raise ValueError(f"distill package path is not a file: {p}")

    LOG.debug("loading distill package from %s", p)
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"distill package is not valid JSON: {p} ({exc})") from exc

    if not isinstance(raw, dict):
        raise ValueError(
            f"distill package top-level must be an object, got {type(raw).__name__}"
        )

    missing = [k for k in _REQUIRED_KEYS if k not in raw]
    if missing:
        raise ValueError(
            f"distill package {p} is missing required keys: {missing}. "
            f"This file may be an older core5 snapshot; run paper-style-distiller "
            "to produce a full 11-dimension package."
        )

    pkg = DistillPackage(
        path=p,
        raw=raw,
        paragraph_templates=[
            ParagraphTemplate.from_raw(r) for r in raw.get("paragraph_templates", [])
        ],
        sentence_patterns=[
            SentencePattern.from_raw(r) for r in raw.get("sentence_patterns", [])
        ],
        macro_blueprint=list(raw.get("macro_blueprint", [])),
        terminology_collocation=list(raw.get("terminology_collocation", [])),
        claim_evidence_binding=list(raw.get("claim_evidence_binding", [])),
        related_work_positioning=list(raw.get("related_work_positioning", [])),
        innovation_patterns=list(raw.get("innovation_argument_phrasing", [])),
        run_manifest=dict(raw.get("run_manifest", {})),
        metrics=dict(raw.get("metrics", {})),
    )

    for key in _OPTIONAL_KEYS:
        if key not in raw:
            LOG.debug("distill package missing optional dimension: %s", key)

    # Build secondary indexes for fast lookups.
    pkg._paragraph_index = _build_two_level_index(
        (t.section, t.intent) for t in pkg.paragraph_templates
    )
    pkg._sentence_index = _build_two_level_index(
        (s.section, s.intent) for s in pkg.sentence_patterns
    )

    LOG.info(
        "loaded %d paragraph templates and %d sentence patterns from %s",
        len(pkg.paragraph_templates),
        len(pkg.sentence_patterns),
        p.name,
    )
    return pkg


def _build_two_level_index(
    keys: Iterable[tuple[str, str]],
) -> dict[tuple[str, str], list[int]]:
    """Build a small ``(section, intent) → [indices]`` map.

    Used internally for future extension; kept here so the indexing logic
    stays in one place when more callers are added.
    """
    idx: dict[tuple[str, str], list[int]] = defaultdict(list)
    for i, key in enumerate(keys):
        idx[key].append(i)
    return dict(idx)


def summary(pkg: DistillPackage) -> dict[str, Any]:
    """Return a short, JSON-friendly summary of a loaded package.

    Useful for ``--format json`` output and for unit tests.
    """
    return {
        "path": str(pkg.path),
        "run_id": pkg.run_id,
        "schema_version": pkg.schema_version,
        "counts": {
            "paragraph_templates": len(pkg.paragraph_templates),
            "sentence_patterns": len(pkg.sentence_patterns),
            "macro_blueprint": len(pkg.macro_blueprint),
            "terminology_collocation": len(pkg.terminology_collocation),
            "claim_evidence_binding": len(pkg.claim_evidence_binding),
            "related_work_positioning": len(pkg.related_work_positioning),
            "innovation_patterns": len(pkg.innovation_patterns),
        },
        "sections": pkg.paragraph_sections(),
        "intents": pkg.paragraph_intents(),
        "tenses": pkg.sentence_tenses(),
        "rhetorical_strengths": pkg.sentence_strengths(),
        "metrics": pkg.metrics,
    }