#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import re
from pathlib import Path


DIMENSIONS = [
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
]


def classify_section(intent: str) -> str:
    mapping = {
        "Gap": "Introduction",
        "Contribution": "Method",
        "Result": "Results",
        "Limitation": "Discussion",
        "Background": "RelatedWork",
    }
    return mapping.get(intent, "Unknown")


def detect_move(sentence: str) -> str:
    s = sentence.lower()
    if any(k in s for k in ["however", "although", "but", "yet"]):
        return "contrast"
    if any(k in s for k in ["therefore", "thus", "hence"]):
        return "conclusion"
    if any(k in s for k in ["for example", "such as"]):
        return "exemplification"
    if any(k in s for k in ["we propose", "we present", "this paper"]):
        return "claim"
    return "background"


def detect_tense(sentence: str) -> str:
    s = sentence.lower()
    if re.search(r"\b(has|have)\s+\w+ed\b", s):
        return "present-perfect"
    if re.search(r"\b(was|were|did)\b", s):
        return "past"
    return "present"


def detect_voice(sentence: str) -> str:
    s = sentence.lower()
    if re.search(r"\b(is|are|was|were|be|been)\s+\w+ed\b", s):
        return "passive"
    return "active"


def detect_hedging(sentence: str) -> str:
    s = sentence.lower()
    if any(k in s for k in ["may", "might", "can", "could", "suggest", "indicate"]):
        return "hedged"
    return "assertive"


def safe_get(d: dict, key: str, default):
    v = d.get(key)
    return default if v is None else v


def build_full11(core5: dict):
    sentence_patterns = safe_get(core5, "sentence_patterns", [])
    paragraph_templates = safe_get(core5, "paragraph_templates", [])
    claim_bindings = safe_get(core5, "claim_evidence_bindings", [])
    innovation_patterns = safe_get(core5, "innovation_patterns", [])

    section_argument_structure = []
    rhetorical_moves = []
    terminology_collocation = {}
    tense_voice_hedging = []
    figure_text_linkage = []
    related_work_positioning = []
    macro_blueprint = []

    for sp in sentence_patterns:
        sentence = sp.get("pattern", "")
        intent = sp.get("intent", "Background")
        section = classify_section(intent)

        section_argument_structure.append(
            {
                "id": sp.get("id", ""),
                "section": section,
                "intent": intent,
                "argument_role": "claim" if intent in ["Contribution", "Result"] else "context",
            }
        )

        rhetorical_moves.append(
            {
                "id": sp.get("id", ""),
                "move": detect_move(sentence),
                "section": section,
                "intent": intent,
            }
        )

        tense_voice_hedging.append(
            {
                "id": sp.get("id", ""),
                "tense": detect_tense(sentence),
                "voice": detect_voice(sentence),
                "hedging": detect_hedging(sentence),
            }
        )

        words = [w.lower() for w in re.findall(r"[a-zA-Z][a-zA-Z-]{3,}", sentence)]
        for i in range(len(words) - 1):
            pair = words[i] + " " + words[i + 1]
            terminology_collocation[pair] = terminology_collocation.get(pair, 0) + 1

        if section in ["Results", "Discussion"] and any(k in sentence.lower() for k in ["benchmark", "improves", "outperforms", "error", "energy"]):
            figure_text_linkage.append(
                {
                    "id": sp.get("id", ""),
                    "linkage_type": "result_interpretation",
                    "pattern": sentence,
                }
            )

        if section == "RelatedWork" or intent == "Background":
            related_work_positioning.append(
                {
                    "id": sp.get("id", ""),
                    "positioning_type": "prior_work_context",
                    "pattern": sentence,
                }
            )

    macro_blueprint = [
        {"stage": "problem", "description": "Define robust control and guidance problem under uncertainty."},
        {"stage": "gap", "description": "Identify limits in disturbance handling and decision consistency."},
        {"stage": "method", "description": "Present adaptive guidance-control architecture with constraints."},
        {"stage": "results", "description": "Report tracking and energy improvements over baselines."},
        {"stage": "boundary", "description": "State failure modes and scope limits."},
        {"stage": "contribution", "description": "Claim robust, practical, and reproducible performance gains."},
    ]

    top_collocations = sorted(terminology_collocation.items(), key=lambda x: x[1], reverse=True)[:80]
    terminology_collocation_list = [
        {"pair": p, "count": c} for p, c in top_collocations
    ]

    full11 = {
        "run_manifest": core5.get("run_manifest", {}),
        "metrics": core5.get("metrics", {}),
        "dimension_coverage": {
            "dimensions": DIMENSIONS,
            "counts": {
                "macro_blueprint": len(macro_blueprint),
                "section_argument_structure": len(section_argument_structure),
                "rhetorical_moves": len(rhetorical_moves),
                "paragraph_templates": len(paragraph_templates),
                "sentence_patterns": len(sentence_patterns),
                "terminology_collocation": len(terminology_collocation_list),
                "tense_voice_hedging": len(tense_voice_hedging),
                "claim_evidence_binding": len(claim_bindings),
                "figure_text_linkage": len(figure_text_linkage),
                "related_work_positioning": len(related_work_positioning),
                "innovation_argument_phrasing": len(innovation_patterns),
            },
        },
        "macro_blueprint": macro_blueprint,
        "section_argument_structure": section_argument_structure,
        "rhetorical_moves": rhetorical_moves,
        "paragraph_templates": paragraph_templates,
        "sentence_patterns": sentence_patterns,
        "terminology_collocation": terminology_collocation_list,
        "tense_voice_hedging": tense_voice_hedging,
        "claim_evidence_binding": claim_bindings,
        "figure_text_linkage": figure_text_linkage,
        "related_work_positioning": related_work_positioning,
        "innovation_argument_phrasing": innovation_patterns,
    }

    return full11


def build_gap_report(full11: dict) -> str:
    counts = full11["dimension_coverage"]["counts"]
    lines = [
        "# Full-11 Coverage Report",
        "",
        f"- generated_at: {dt.datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Dimension Counts",
    ]
    for dim in DIMENSIONS:
        lines.append(f"- {dim}: {counts.get(dim, 0)}")

    lines.extend([
        "",
        "## Suggested Patch Priorities",
    ])

    if counts.get("figure_text_linkage", 0) < 15:
        lines.append("- figure_text_linkage is sparse; add explicit result-to-figure sentence templates.")
    if counts.get("related_work_positioning", 0) < 20:
        lines.append("- related_work_positioning is sparse; distill more contrastive related-work paragraphs.")
    if counts.get("terminology_collocation", 0) < 40:
        lines.append("- terminology_collocation needs more corpus pages or broader extraction window.")
    if counts.get("innovation_argument_phrasing", 0) < 25:
        lines.append("- innovation_argument_phrasing needs more strong claim samples from intro and abstract.")

    lines.append("- keep human review mandatory for all strong-claim innovation entries.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Expand core5 package to full 11 dimensions.")
    parser.add_argument("--core5-package", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    core5 = json.loads(Path(args.core5_package).read_text(encoding="utf-8"))
    full11 = build_full11(core5)

    (out_dir / "full11-distill-package.json").write_text(
        json.dumps(full11, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "full11-coverage-report.md").write_text(
        build_gap_report(full11), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
