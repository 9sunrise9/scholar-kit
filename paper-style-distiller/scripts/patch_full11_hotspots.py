#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Patch weak dimensions in full11 package.")
    parser.add_argument("--full11-package", required=True)
    parser.add_argument("--out-file", required=True)
    args = parser.parse_args()

    p = Path(args.full11_package)
    data = json.loads(p.read_text(encoding="utf-8"))

    figure_templates = [
        "Figure {fig_id} shows that the proposed method consistently reduces {metric} under {condition}.",
        "As illustrated in Figure {fig_id}, performance gain mainly comes from {module} rather than parameter scaling.",
        "The trend in Figure {fig_id} confirms that robustness is preserved when {disturbance} increases.",
        "Compared with {baseline} in Figure {fig_id}, our method achieves lower {metric} with similar control effort.",
        "Figure {fig_id} and Table {table_id} jointly indicate improved stability-efficiency trade-off.",
    ]

    innovation_boosters = [
        {
            "id": "I-BOOST-001",
            "innovation_type": "method",
            "claim_pattern": "We introduce a disturbance-aware guidance-control co-design that explicitly aligns decision quality with tracking robustness.",
            "mechanism_pattern": "The key mechanism is coupling adaptive guidance update with constraint-consistent control allocation under uncertainty.",
            "gain_pattern": "Relative to classical MPC and backstepping baselines, the method improves tracking robustness under wave-current coupling.",
            "boundary_pattern": "The gain may shrink under extremely sparse sensing and abrupt maneuver switches.",
            "confidence": 0.81,
            "human_review_required": True,
        },
        {
            "id": "I-BOOST-002",
            "innovation_type": "system",
            "claim_pattern": "We provide an end-to-end decision-guidance-control pipeline with interpretable evidence binding for each strong claim.",
            "mechanism_pattern": "The pipeline enforces claim strength calibration against evidence type and confidence thresholds.",
            "gain_pattern": "This design reduces over-claim risk while preserving actionable writing templates for deployment scenarios.",
            "boundary_pattern": "The framework depends on sufficient benchmark diversity for stable calibration.",
            "confidence": 0.79,
            "human_review_required": True,
        },
    ]

    ft = data.get("figure_text_linkage", [])
    for i, t in enumerate(figure_templates, start=1):
        ft.append(
            {
                "id": f"F-LINK-{i:03d}",
                "linkage_type": "result_interpretation",
                "pattern": t,
            }
        )
    data["figure_text_linkage"] = ft

    ip = data.get("innovation_argument_phrasing", [])
    ip.extend(innovation_boosters)
    data["innovation_argument_phrasing"] = ip

    counts = data.get("dimension_coverage", {}).get("counts", {})
    counts["figure_text_linkage"] = len(data["figure_text_linkage"])
    counts["innovation_argument_phrasing"] = len(data["innovation_argument_phrasing"])

    out = Path(args.out_file)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
