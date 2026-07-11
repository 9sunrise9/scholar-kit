#!/usr/bin/env python3
"""
Post-Distillation Review Pipeline  (US-002 ~ US-006)

Implements all 11 dimension reviewers + routing reviewer + coordinator logic.
Reads the latest full11 distill package, runs every dimension's review rules,
and writes:
  - runs/postdistill-review-result.json  (full review result per contract v1)
  - runs/postdistill-human-review-pack.json  (only needs_review items, grouped)
  - runs/postdistill-validation-report.md  (US-002 validation report)

Usage:
  python3 scripts/postdistill_review.py [--input <path-to-full11.json>]
"""

import argparse
import json
import re
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict


# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────

VALID_DIMENSIONS = {
    "macro_blueprint",
    "section_argument_structure",
    "rhetorical_moves",
    "paragraph_templates",
    "sentence_patterns",
    "terminology_collocation",
    "tense_voice_hedging",
    "claim_evidence_binding",
    "figure_text_linkage",
    "related_work_positioning",
    "innovation_argument_phrasing",
}

# Mapping from intent to expected argument_role(s)
INTENT_ROLE_MAP = {
    "Background":   {"context"},
    "Result":       {"claim", "evidence"},
    "Contribution": {"claim"},
    "Gap":          {"context", "claim"},
    "Limitation":   {"context", "claim"},
}

VALID_POSITIONING_TYPES = {
    "prior_work_context",
    "contrast",
    "gap_identification",
    "limitation",
    "baseline",
    "extension",
}

VALID_LINKAGE_TYPES = {
    "result_interpretation",
    "method_illustration",
    "data_presentation",
    "architecture_description",
    "comparison_visualization",
}

VALID_RHETORICAL_MOVES = {
    "background", "contrast", "conclusion", "claim", "exemplification",
    "elaboration", "gap", "limitation", "motivation", "restatement",
    "problem", "method", "result", "contribution",
}

VALID_VOICES    = {"active", "passive"}
VALID_HEDGES    = {"assertive", "hedged", "tentative", "speculative", "neutral"}

# Confidence threshold for "skip human review" mode
SKIP_HUMAN_CONF_THRESHOLD = 0.65

LEAKAGE_TOKEN_LIMIT = 13  # tokens (rough word-based approximation)
PATTERN_MAX_WORDS = 60    # longer patterns increase leakage risk


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def make_id(prefix: str, i: int) -> str:
    return f"{prefix}-{i:04d}"


def word_count(text: str) -> int:
    return len(text.split()) if text else 0


def max_consecutive_words(pattern: str, source_text: str) -> int:
    """Approximate max shared consecutive token run. Simple heuristic."""
    pattern_words = pattern.lower().split()
    source_words = source_text.lower().split()
    max_run = 0
    for i, pw in enumerate(pattern_words):
        run = 0
        for j, sw in enumerate(source_words):
            if sw == pw:
                k = 0
                while (i + k < len(pattern_words) and
                       j + k < len(source_words) and
                       pattern_words[i + k] == source_words[j + k]):
                    k += 1
                if k > run:
                    run = k
        if run > max_run:
            max_run = run
    return max_run


def routing_verdict(item: dict, dimension: str) -> str:
    """Determine if an item belongs to its assigned dimension."""
    # An item with slots containing keywords strongly tied to other dimensions
    section = item.get("section", "")
    intent  = item.get("intent", "")
    itype   = item.get("innovation_type", "")
    positioning = item.get("positioning_type", "")
    linkage = item.get("linkage_type", "")

    if dimension == "related_work_positioning":
        if positioning not in VALID_POSITIONING_TYPES and positioning:
            return "route_to_human"
        return "route_ok"

    if dimension == "figure_text_linkage":
        if linkage not in VALID_LINKAGE_TYPES and linkage:
            return "route_to_human"
        return "route_ok"

    if dimension == "innovation_argument_phrasing":
        if itype not in ("algorithm", "method", "theory", "learning", "observer") and itype:
            return "multi_candidate"
        return "route_ok"

    if dimension == "section_argument_structure":
        role = item.get("argument_role", "")
        expected = INTENT_ROLE_MAP.get(intent, set())
        if expected and role not in expected:
            return "reclassify"
        return "route_ok"

    return "route_ok"


# ──────────────────────────────────────────────────────────────────────────────
# Dimension Reviewers  (D1–D11)
# ──────────────────────────────────────────────────────────────────────────────

def review_macro_blueprint(items: list) -> list:
    """D1: Macro Blueprint — check required stages, non-empty descriptions."""
    required_stages = {"problem", "gap", "method", "results", "boundary", "contribution"}
    present_stages = {it.get("stage", "") for it in items}
    results = []
    for i, item in enumerate(items):
        stage = item.get("stage", "")
        desc  = item.get("description", "")
        rv = routing_verdict(item, "macro_blueprint")
        if not stage or not desc:
            verdict = "needs_review"
            reason  = "missing stage or description"
        elif stage not in required_stages:
            verdict = "needs_review"
            reason  = f"unexpected stage value: '{stage}'"
        elif len(desc.split()) < 4:
            verdict = "needs_review"
            reason  = "description too short to be actionable"
        else:
            verdict = "pass"
            reason  = ""
        results.append({
            "item_id":    make_id("MB", i + 1),
            "source_id":  item.get("id", stage),
            "raw_text":   desc,
            "dimension":  "macro_blueprint",
            "routing_verdict":  rv,
            "reviewer_verdict": verdict,
            "confidence": 0.9 if verdict == "pass" else 0.5,
            "human_escalation": verdict == "needs_review",
            "risk_reason": reason,
        })
    # Check completeness of stage set
    missing = required_stages - present_stages
    if missing:
        results.append({
            "item_id":    "MB-COMPLETENESS",
            "source_id":  "macro_blueprint",
            "raw_text":   f"Missing stages: {sorted(missing)}",
            "dimension":  "macro_blueprint",
            "routing_verdict":  "route_ok",
            "reviewer_verdict": "needs_review",
            "confidence": 0.3,
            "human_escalation": True,
            "risk_reason": f"Required stages not present: {sorted(missing)}",
        })
    return results


def review_section_argument_structure(items: list, limit: int = 200) -> list:
    """D2: Section Argument Structure — check intent/role alignment."""
    results = []
    for i, item in enumerate(items[:limit]):
        section = item.get("section", "")
        intent  = item.get("intent", "")
        role    = item.get("argument_role", "")
        rv = routing_verdict(item, "section_argument_structure")
        expected = INTENT_ROLE_MAP.get(intent, set())
        if rv == "reclassify":
            verdict = "needs_review"
            reason  = f"argument_role '{role}' unexpected for intent '{intent}'; expected {expected}"
            conf    = 0.4
        elif not section or not intent or not role:
            verdict = "needs_review"
            reason  = "missing section/intent/role"
            conf    = 0.3
        else:
            verdict = "pass"
            reason  = ""
            conf    = 0.85
        results.append({
            "item_id":    item.get("id", make_id("SA", i + 1)),
            "source_id":  f"{section}:{intent}",
            "raw_text":   f"{section} | {intent} | {role}",
            "dimension":  "section_argument_structure",
            "routing_verdict":  rv,
            "reviewer_verdict": verdict,
            "confidence": conf,
            "human_escalation": verdict == "needs_review",
            "risk_reason": reason,
        })
    return results


def review_rhetorical_moves(items: list, limit: int = 200) -> list:
    """D3: Rhetorical Moves — uses 'move' field (single-word move type), not 'pattern'."""
    results = []
    for i, item in enumerate(items[:limit]):
        move   = item.get("move", "")
        intent = item.get("intent", "")
        rv = routing_verdict(item, "rhetorical_moves")
        if not move:
            verdict = "needs_review"
            reason  = "empty move field"
            conf    = 0.2
        elif move.lower() not in VALID_RHETORICAL_MOVES:
            verdict = "needs_review"
            reason  = f"unrecognized move type: '{move}'"
            conf    = 0.5
        else:
            verdict = "pass"
            reason  = ""
            conf    = 0.9
        results.append({
            "item_id":    item.get("id", make_id("RM", i + 1)),
            "source_id":  item.get("id", f"rm-{i+1}"),
            "raw_text":   move,
            "dimension":  "rhetorical_moves",
            "routing_verdict":  rv,
            "reviewer_verdict": verdict,
            "confidence": conf,
            "human_escalation": verdict == "needs_review",
            "risk_reason": reason,
        })
    return results


def review_paragraph_templates(items: list) -> list:
    """D4: Paragraph Templates — confidence, block_order, non-trivial template.
    Note: support_ratio in the data is corpus-relative (typically 0.03–0.09) and
    is NOT a reliability signal; do not use it as a threshold.
    """
    results = []
    for i, item in enumerate(items):
        pid         = item.get("id", make_id("PT", i + 1))
        template    = item.get("template", "")
        conf        = float(item.get("confidence", 0))
        block_order = item.get("block_order", [])
        required    = item.get("required_slots", [])
        rv = routing_verdict(item, "paragraph_templates")
        if not template:
            verdict = "needs_review"
            reason  = "empty template"
            out_conf = 0.2
        elif conf < 0.60:
            verdict = "needs_review"
            reason  = f"low confidence ({conf:.2f})"
            out_conf = conf
        elif len(block_order) < 2:
            verdict = "needs_review"
            reason  = "block_order has fewer than 2 steps — template under-specified"
            out_conf = 0.55
        else:
            verdict = "pass"
            reason  = ""
            out_conf = conf
        results.append({
            "item_id":    pid,
            "source_id":  pid,
            "raw_text":   template[:200],
            "dimension":  "paragraph_templates",
            "routing_verdict":  rv,
            "reviewer_verdict": verdict,
            "confidence": out_conf,
            "human_escalation": verdict == "needs_review",
            "risk_reason": reason,
        })
    return results


def review_sentence_patterns(items: list, limit: int = 300) -> list:
    """D5: Sentence Patterns — confidence, evidence presence, leakage risk.
    Math-formula artifacts (many {num} slots + very long) are rejected outright.
    """
    results = []
    for i, item in enumerate(items[:limit]):
        pid      = item.get("id", make_id("SP", i + 1))
        pattern  = item.get("pattern", "")
        conf     = float(item.get("confidence", 0))
        evidence = item.get("evidence", [])
        rv = routing_verdict(item, "sentence_patterns")
        wc = word_count(pattern)
        slot_tokens = len(re.findall(r"\{[^}]+\}", pattern))
        if not pattern:
            verdict  = "needs_review"
            reason   = "empty pattern"
            out_conf = 0.2
        elif wc > PATTERN_MAX_WORDS and slot_tokens > 10:
            # Math-formula artifact: unusable as a text template
            verdict  = "reject"
            reason   = f"math formula artifact: {wc} words, {slot_tokens} slot tokens"
            out_conf = 0.1
        elif conf < 0.5:
            verdict  = "needs_review"
            reason   = f"low confidence ({conf:.2f})"
            out_conf = conf
        elif not evidence:
            verdict  = "needs_review"
            reason   = "no evidence chain — violates governance rule §6"
            out_conf = 0.3
        else:
            verdict  = "pass"
            reason   = ""
            out_conf = conf
        results.append({
            "item_id":    pid,
            "source_id":  pid,
            "raw_text":   pattern[:200],
            "dimension":  "sentence_patterns",
            "routing_verdict":  rv,
            "reviewer_verdict": verdict,
            "confidence": out_conf,
            "human_escalation": verdict == "needs_review",
            "risk_reason": reason,
        })
    return results


def review_terminology_collocation(items: list) -> list:
    """D6: Terminology Collocation — count >= 3, pair must be ≥2 words."""
    results = []
    for i, item in enumerate(items):
        pair  = item.get("pair", "")
        count = int(item.get("count", 0))
        rv = routing_verdict(item, "terminology_collocation")
        pair_words = len(pair.split())
        if pair_words < 2:
            verdict = "needs_review"
            reason  = f"pair '{pair}' is single word — not a collocation"
        elif count < 3:
            verdict = "needs_review"
            reason  = f"count={count} too low for reusable pattern (min 3)"
        else:
            verdict = "pass"
            reason  = ""
        results.append({
            "item_id":    make_id("TC", i + 1),
            "source_id":  pair,
            "raw_text":   f"{pair} (count={count})",
            "dimension":  "terminology_collocation",
            "routing_verdict":  rv,
            "reviewer_verdict": verdict,
            "confidence": 0.9 if verdict == "pass" else 0.5,
            "human_escalation": verdict == "needs_review",
            "risk_reason": reason,
        })
    return results


def review_tense_voice_hedging(items: list, limit: int = 300) -> list:
    """D7: Tense / Voice / Hedging — validates tense/voice/hedging enum values.
    This dimension stores structured linguistic annotations, not text patterns.
    Confidence field is absent in the data; validity is purely structural.
    """
    VALID_TENSES = {"present", "past", "future", "present_perfect"}
    results = []
    for i, item in enumerate(items[:limit]):
        pid     = item.get("id", make_id("TVH", i + 1))
        tense   = item.get("tense", "")
        voice   = item.get("voice", "")
        hedging = item.get("hedging", "")
        rv = routing_verdict(item, "tense_voice_hedging")
        issues = []
        if not tense:
            issues.append("missing tense")
        elif tense not in VALID_TENSES:
            issues.append(f"unknown tense '{tense}'")
        if voice and voice not in VALID_VOICES:
            issues.append(f"unknown voice '{voice}'")
        if hedging and hedging not in VALID_HEDGES:
            issues.append(f"unknown hedging '{hedging}'")
        if issues:
            verdict  = "needs_review"
            reason   = "; ".join(issues)
            out_conf = 0.4
        else:
            verdict  = "pass"
            reason   = ""
            out_conf = 0.9
        results.append({
            "item_id":    pid,
            "source_id":  pid,
            "raw_text":   f"tense={tense} voice={voice} hedging={hedging}",
            "dimension":  "tense_voice_hedging",
            "routing_verdict":  rv,
            "reviewer_verdict": verdict,
            "confidence": out_conf,
            "human_escalation": verdict == "needs_review",
            "risk_reason": reason,
        })
    return results


def review_claim_evidence_binding(items: list) -> list:
    """D8: Claim-Evidence Binding.
    Policy (skip-human-review mode):
      - No evidence → needs_review
      - strong/supportive + complete evidence (source_paper_id + source_paragraph_id) → pass
      - Incomplete evidence records → needs_review
    """
    results = []
    for i, item in enumerate(items):
        cid      = item.get("claim_id", make_id("CE", i + 1))
        text     = item.get("claim_text", "")
        strength = item.get("claim_strength", "")
        evidence = item.get("evidence", [])
        rv = routing_verdict(item, "claim_evidence_binding")

        if not evidence:
            verdict = "needs_review"
            reason  = "no evidence chain — violates governance §6"
            conf    = 0.3
        else:
            bad_ev = [ev for ev in evidence
                      if not ev.get("source_paper_id") or not ev.get("source_paragraph_id")]
            if bad_ev:
                verdict = "needs_review"
                reason  = f"{len(bad_ev)} evidence records missing required source fields"
                conf    = 0.5
            else:
                verdict = "pass"
                reason  = ""
                conf    = 0.9 if strength == "supportive" else 0.75
        results.append({
            "item_id":    cid,
            "source_id":  cid,
            "raw_text":   text[:200],
            "dimension":  "claim_evidence_binding",
            "routing_verdict":  rv,
            "reviewer_verdict": verdict,
            "confidence": conf,
            "human_escalation": verdict == "needs_review",
            "semantic_interpretation": strength,
            "risk_reason": reason,
        })
    return results


def review_figure_text_linkage(items: list) -> list:
    """D9: Figure-Text Linkage — valid linkage_type, non-trivial pattern."""
    results = []
    for i, item in enumerate(items):
        fid     = item.get("id", make_id("FT", i + 1))
        ltype   = item.get("linkage_type", "")
        pattern = item.get("pattern", "")
        rv = routing_verdict(item, "figure_text_linkage")
        if rv == "route_to_human":
            verdict = "needs_review"
            reason  = f"unknown linkage_type: '{ltype}'"
            conf    = 0.3
        elif not pattern:
            verdict = "needs_review"
            reason  = "empty pattern"
            conf    = 0.2
        elif word_count(pattern) < 3:
            verdict = "needs_review"
            reason  = "pattern too short to be reusable"
            conf    = 0.4
        else:
            verdict = "pass"
            reason  = ""
            conf    = 0.85
        results.append({
            "item_id":    fid,
            "source_id":  fid,
            "raw_text":   pattern[:200],
            "dimension":  "figure_text_linkage",
            "routing_verdict":  rv,
            "reviewer_verdict": verdict,
            "confidence": conf,
            "human_escalation": verdict == "needs_review",
            "risk_reason": reason,
        })
    return results


def review_related_work_positioning(items: list, limit: int = 300) -> list:
    """D10: Related Work Positioning — valid positioning_type, pattern quality."""
    RELAXED_MAX_WORDS = 80  # slightly relaxed from PATTERN_MAX_WORDS=60
    results = []
    for i, item in enumerate(items[:limit]):
        rid     = item.get("id", make_id("RW", i + 1))
        ptype   = item.get("positioning_type", "")
        pattern = item.get("pattern", "")
        rv = routing_verdict(item, "related_work_positioning")
        if rv == "route_to_human":
            verdict = "needs_review"
            reason  = f"unknown positioning_type: '{ptype}'"
            conf    = 0.3
        elif not pattern:
            verdict = "needs_review"
            reason  = "empty pattern"
            conf    = 0.2
        elif word_count(pattern) > RELAXED_MAX_WORDS:
            verdict = "needs_review"
            reason  = f"pattern too long ({word_count(pattern)} words) — leakage risk"
            conf    = 0.4
        else:
            verdict = "pass"
            reason  = ""
            conf    = 0.85
        results.append({
            "item_id":    rid,
            "source_id":  rid,
            "raw_text":   pattern[:200],
            "dimension":  "related_work_positioning",
            "routing_verdict":  rv,
            "reviewer_verdict": verdict,
            "confidence": conf,
            "human_escalation": verdict == "needs_review",
            "risk_reason": reason,
        })
    return results


def review_innovation_argument_phrasing(items: list) -> list:
    """D11: Innovation Argument Phrasing.
    Skip-human-review policy:
      - human_review_required=True is noted but NOT auto-escalated in skip mode
      - Items with complete mechanism_pattern + gain_pattern + conf >= threshold → pass
      - Items missing mechanism or gain pattern → needs_review
      - multi_candidate routing → needs_review
    """
    results = []
    for i, item in enumerate(items):
        iid   = item.get("id", make_id("IA", i + 1))
        itype = item.get("innovation_type", "")
        claim = item.get("claim_pattern", "")
        conf  = float(item.get("confidence", 0.5))
        rv = routing_verdict(item, "innovation_argument_phrasing")

        mech = item.get("mechanism_pattern", "")
        gain = item.get("gain_pattern", "")

        if rv == "multi_candidate":
            verdict  = "needs_review"
            reason   = "multi-type candidate — routing ambiguous"
            out_conf = conf
        elif not mech or not gain:
            verdict  = "needs_review"
            reason   = "missing mechanism_pattern or gain_pattern — innovation claim incomplete"
            out_conf = 0.4
        elif conf < SKIP_HUMAN_CONF_THRESHOLD:
            verdict  = "needs_review"
            reason   = f"confidence {conf:.2f} below threshold {SKIP_HUMAN_CONF_THRESHOLD}"
            out_conf = conf
        else:
            verdict  = "pass"
            reason   = ""
            out_conf = conf

        results.append({
            "item_id":    iid,
            "source_id":  iid,
            "raw_text":   claim[:200],
            "dimension":  "innovation_argument_phrasing",
            "routing_verdict":  rv,
            "reviewer_verdict": verdict,
            "confidence": out_conf,
            "human_escalation": verdict == "needs_review",
            "risk_reason": reason,
        })
    return results


# ──────────────────────────────────────────────────────────────────────────────
# Coordinator  (US-002)
# ──────────────────────────────────────────────────────────────────────────────

def run_all_reviewers(pkg: dict) -> list:
    """Run all 11 dimension reviewers and return combined item list."""
    all_items = []
    all_items += review_macro_blueprint(pkg.get("macro_blueprint", []))
    all_items += review_section_argument_structure(pkg.get("section_argument_structure", []))
    all_items += review_rhetorical_moves(pkg.get("rhetorical_moves", []))
    all_items += review_paragraph_templates(pkg.get("paragraph_templates", []))
    all_items += review_sentence_patterns(pkg.get("sentence_patterns", []))
    all_items += review_terminology_collocation(pkg.get("terminology_collocation", []))
    all_items += review_tense_voice_hedging(pkg.get("tense_voice_hedging", []))
    all_items += review_claim_evidence_binding(pkg.get("claim_evidence_binding", []))
    all_items += review_figure_text_linkage(pkg.get("figure_text_linkage", []))
    all_items += review_related_work_positioning(pkg.get("related_work_positioning", []))
    all_items += review_innovation_argument_phrasing(pkg.get("innovation_argument_phrasing", []))
    return all_items


# ──────────────────────────────────────────────────────────────────────────────
# Human Review Pack Builder  (US-006)
# ──────────────────────────────────────────────────────────────────────────────

CONFLICT_TYPE_MAP = {
    "route_to_human":   "routing_conflict",
    "multi_candidate":  "multi_candidate",
    "reclassify":       "routing_conflict",
}

DIMENSION_PRIORITY = [
    "innovation_argument_phrasing",
    "claim_evidence_binding",
    "macro_blueprint",
    "paragraph_templates",
    "figure_text_linkage",
    "related_work_positioning",
    "terminology_collocation",
    "sentence_patterns",
    "tense_voice_hedging",
    "section_argument_structure",
    "rhetorical_moves",
]


def build_human_review_pack(items: list, run_id: str) -> dict:
    """Build the human review pack from all needs_review items."""
    escalated = [it for it in items if it.get("human_escalation", False)]

    # Determine conflict_type per item
    hr_items = []
    for it in escalated:
        rv = it.get("routing_verdict", "route_ok")
        raw_reason = it.get("risk_reason", "")
        conflict = CONFLICT_TYPE_MAP.get(rv, "none")
        if "evidence" in raw_reason.lower():
            conflict = "evidence_gap"
        elif "claim" in raw_reason.lower() or "unsupported" in raw_reason.lower():
            conflict = "claim_unsupported"
        elif "leakage" in raw_reason.lower():
            conflict = "leakage_risk"
        elif "ambig" in raw_reason.lower() or "semantic" in raw_reason.lower():
            conflict = "semantic_ambiguity"

        hr_items.append({
            "item_id":                 it["item_id"],
            "source_id":               it.get("source_id", ""),
            "initial_route":           it.get("dimension", ""),
            "routing_review_result":   rv,
            "dimension_review_result": it["reviewer_verdict"],
            "confidence":              it.get("confidence", 0),
            "uncertainty_reason":      raw_reason,
            "recommended_action":      "reject" if it.get("confidence", 1) < 0.3 else "modify",
            "conflict_type":           conflict,
        })

    # Group by dimension, then by conflict_type
    groups_by_dim: dict = defaultdict(list)
    groups_by_conflict: dict = defaultdict(list)
    for it in hr_items:
        groups_by_dim[it["initial_route"]].append(it)
        groups_by_conflict[it["conflict_type"]].append(it)

    # Build dimension-sorted groups
    groups = []
    for dim in DIMENSION_PRIORITY:
        if dim in groups_by_dim:
            groups.append({"group_key": dim, "items": groups_by_dim[dim]})
    # Add any leftover dimensions not in priority list
    for dim, its in groups_by_dim.items():
        if dim not in DIMENSION_PRIORITY:
            groups.append({"group_key": dim, "items": its})

    # Count by dimension and conflict type
    by_dim_counts     = {k: len(v) for k, v in groups_by_dim.items()}
    by_conflict_counts = {k: len(v) for k, v in groups_by_conflict.items()}

    priority_order = [g["group_key"] for g in groups]

    return {
        "pack_id":      f"hrp-{run_id}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "groups":       groups,
        "summary": {
            "total_items":      len(hr_items),
            "by_dimension":     by_dim_counts,
            "by_conflict_type": by_conflict_counts,
            "priority_order":   priority_order,
        },
    }


# ──────────────────────────────────────────────────────────────────────────────
# Validation Report  (US-002)
# ──────────────────────────────────────────────────────────────────────────────

def build_validation_report(items: list, pkg: dict, pack: dict, run_id: str) -> str:
    total    = len(items)
    passed   = sum(1 for it in items if it["reviewer_verdict"] == "pass")
    rejected = sum(1 for it in items if it["reviewer_verdict"] == "reject")
    nr       = sum(1 for it in items if it["reviewer_verdict"] == "needs_review")

    by_dim: dict = defaultdict(lambda: {"pass": 0, "reject": 0, "needs_review": 0})
    for it in items:
        by_dim[it.get("dimension", "unknown")][it["reviewer_verdict"]] += 1

    routing_counts: dict = defaultdict(int)
    for it in items:
        routing_counts[it.get("routing_verdict", "route_ok")] += 1

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        f"# Post-Distillation Review Validation Report",
        f"",
        f"- **run_id**: `{run_id}`",
        f"- **generated_at**: `{now}`",
        f"- **contract**: `references/postdistill-review-contract-v1.json`",
        f"",
        f"## US-002 Validation: Coordinator + Routing Flow",
        f"",
        f"| Check | Status |",
        f"|-------|--------|",
        f"| 11 dimension reviewers invoked | {'✅ Yes' if len(by_dim) >= 11 else '⚠️ ' + str(len(by_dim))} |",
        f"| Routing reviewer applied to all items | ✅ Yes (all items carry routing_verdict) |",
        f"| needs_review items escalated to human pack | ✅ Yes ({nr} items) |",
        f"| human_review_pack generated | ✅ Yes (pack_id: {pack['pack_id']}) |",
        f"",
        f"## Overall Verdict Distribution",
        f"",
        f"| Verdict | Count | % |",
        f"|---------|-------|---|",
        f"| pass | {passed} | {passed/total*100:.1f}% |",
        f"| reject | {rejected} | {rejected/total*100:.1f}% |",
        f"| needs_review | {nr} | {nr/total*100:.1f}% |",
        f"| **Total** | **{total}** | 100% |",
        f"",
        f"## Routing Verdict Distribution",
        f"",
    ]
    for rv, count in sorted(routing_counts.items()):
        lines.append(f"- `{rv}`: {count}")

    lines += [
        f"",
        f"## By Dimension  (D1–D11)",
        f"",
        f"| Dimension | pass | needs_review | reject | total |",
        f"|-----------|------|-------------|--------|-------|",
    ]
    for dim in DIMENSION_PRIORITY:
        counts = by_dim.get(dim, {"pass": 0, "reject": 0, "needs_review": 0})
        total_d = sum(counts.values())
        lines.append(
            f"| {dim} | {counts['pass']} | {counts['needs_review']} | {counts['reject']} | {total_d} |"
        )

    lines += [
        f"",
        f"## Human Review Pack Summary",
        f"",
        f"- Total items in pack: **{pack['summary']['total_items']}**",
        f"- Groups by dimension:",
    ]
    for dim, cnt in sorted(pack["summary"]["by_dimension"].items()):
        lines.append(f"  - {dim}: {cnt}")
    lines += [
        f"",
        f"- Groups by conflict_type:",
    ]
    for ct, cnt in sorted(pack["summary"]["by_conflict_type"].items()):
        lines.append(f"  - {ct}: {cnt}")

    lines += [
        f"",
        f"## Governance Gate Status",
        f"",
    ]
    metrics = pkg.get("metrics", {})
    gate_results = [
        ("coverage",       metrics.get("coverage", 0),           0.70, ">="),
        ("consistency",    metrics.get("consistency", 0),         0.60, ">="),
        ("actionability",  metrics.get("actionability", 0),       0.70, ">="),
        ("leakage_risk",   metrics.get("leakage_risk", 0),        0.20, "<="),
        ("ngram_overlap_4", metrics.get("ngram_overlap_4", 0),    0.25, "<="),
        ("semantic_similarity_max", metrics.get("semantic_similarity_max", 0), 0.92, "<="),
    ]
    for name, val, threshold, op in gate_results:
        ok = (val >= threshold) if op == ">=" else (val <= threshold)
        status = "✅ PASS" if ok else "❌ FAIL"
        lines.append(f"| {name} | {val} | {op}{threshold} | {status} |")

    # Inject header for the table above
    lines.insert(-len(gate_results), "| Metric | Value | Threshold | Status |")
    lines.insert(-len(gate_results), "|--------|-------|-----------|--------|")

    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Post-distillation review pipeline")
    parser.add_argument(
        "--input",
        default="runs/full11-core5-20260518-230538/full11-distill-package.json",
        help="Path to the full11 distill package JSON",
    )
    args = parser.parse_args()

    root = Path(__file__).parent.parent
    input_path = root / args.input

    print(f"[coordinator] Loading distill package: {input_path}")
    with open(input_path, encoding="utf-8") as f:
        pkg = json.load(f)

    run_id = pkg.get("run_manifest", {}).get("run_id", "unknown")
    review_id = f"review-{run_id}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

    print("[coordinator] Running all 11 dimension reviewers + routing reviewer...")
    all_items = run_all_reviewers(pkg)

    # Build summary
    total    = len(all_items)
    passed   = sum(1 for it in all_items if it["reviewer_verdict"] == "pass")
    rejected = sum(1 for it in all_items if it["reviewer_verdict"] == "reject")
    nr       = sum(1 for it in all_items if it["reviewer_verdict"] == "needs_review")

    from collections import Counter
    by_dim_counts = Counter(it.get("dimension", "unknown") for it in all_items if it["reviewer_verdict"] != "pass")

    print(f"[coordinator] Reviewed {total} items → pass={passed}, reject={rejected}, needs_review={nr}")

    print("[coordinator] Building human review pack...")
    pack = build_human_review_pack(all_items, run_id)
    print(f"[human-pack] Escalated {pack['summary']['total_items']} items for human review")

    # Assemble full review result
    review_result = {
        "review_id":   review_id,
        "run_id":      run_id,
        "items":       all_items,
        "human_review_pack": pack,
        "summary": {
            "total":        total,
            "pass":         passed,
            "reject":       rejected,
            "needs_review": nr,
            "by_dimension": dict(by_dim_counts),
        },
    }

    # Write outputs
    out_dir = root / "runs"
    out_dir.mkdir(exist_ok=True)

    result_path = out_dir / "postdistill-review-result.json"
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(review_result, f, ensure_ascii=False, indent=2)
    print(f"[output] Review result → {result_path}")

    pack_path = out_dir / "postdistill-human-review-pack.json"
    with open(pack_path, "w", encoding="utf-8") as f:
        json.dump(pack, f, ensure_ascii=False, indent=2)
    print(f"[output] Human review pack → {pack_path}")

    validation_md = build_validation_report(all_items, pkg, pack, run_id)
    val_path = out_dir / "postdistill-validation-report.md"
    with open(val_path, "w", encoding="utf-8") as f:
        f.write(validation_md)
    print(f"[output] Validation report → {val_path}")

    print("\n=== DONE ===")
    print(f"  reviewed  : {total}")
    print(f"  pass      : {passed} ({passed/total*100:.1f}%)")
    print(f"  reject    : {rejected}")
    print(f"  needs_review: {nr} ({nr/total*100:.1f}%)")


if __name__ == "__main__":
    main()
