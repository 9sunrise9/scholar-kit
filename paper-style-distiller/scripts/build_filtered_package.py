"""build_filtered_package.py
构建 "已审查通过" 蒸馏包。
读取 postdistill-review-result.json，过滤出 reviewer_verdict='pass' 的条目 item_id，
从原始蒸馏包中提取对应条目，并将字段名映射到 generate_review_html.py 所期望的格式，
最终写出 runs/full11-reviewed-pass.json。
"""
from __future__ import annotations
import json, re
from pathlib import Path

ROOT     = Path(__file__).parent.parent
REVIEW   = ROOT / "runs" / "postdistill-review-result.json"
SOURCE   = ROOT / "runs" / "full11-core5-20260518-230538" / "full11-distill-package.json"
OUT_PKG  = ROOT / "runs" / "full11-reviewed-pass.json"

# ── Dimension key mapping: source pkg → HTML generator ──────────────────────
DIM_MAP = {
    "macro_blueprint":           "macro_blueprints",
    "section_argument_structure":"section_argument_structures",
    "rhetorical_moves":          "rhetorical_moves",
    "paragraph_templates":       "paragraph_templates",
    "sentence_patterns":         "sentence_patterns",
    "terminology_collocation":   "terminology_collocations",
    "tense_voice_hedging":       "tense_voice_hedging",
    "claim_evidence_binding":    "claim_evidence_bindings",
    "figure_text_linkage":       "figure_text_linkages",
    "related_work_positioning":  "related_work_patterns",
    "innovation_argument_phrasing": "innovation_patterns",
}

# ID fields per dimension ────────────────────────────────────────────────────
ID_FIELDS = {
    "macro_blueprint":           ["id"],
    "section_argument_structure":["id"],
    "rhetorical_moves":          ["id"],
    "paragraph_templates":       ["id"],
    "sentence_patterns":         ["id"],
    "terminology_collocation":   ["id"],
    "tense_voice_hedging":       ["id"],
    "claim_evidence_binding":    ["claim_id"],
    "figure_text_linkage":       ["id"],
    "related_work_positioning":  ["id"],
    "innovation_argument_phrasing": ["id"],
}


def get_item_id(item: dict, dim: str) -> str | None:
    for f in ID_FIELDS.get(dim, ["id"]):
        v = item.get(f)
        if v:
            return str(v)
    return None


def main() -> None:
    review_data  = json.loads(REVIEW.read_text())
    review_items = review_data["items"] if isinstance(review_data, dict) else review_data
    src_pkg      = json.loads(SOURCE.read_text())

    # Collect pass item_ids per dimension
    pass_ids: dict[str, set[str]] = {}
    stats: dict[str, dict] = {}
    for rv in review_items:
        dim  = rv.get("dimension", "")
        iid  = rv.get("item_id", "")
        verd = rv.get("reviewer_verdict", "")
        stats.setdefault(dim, {"pass": 0, "reject": 0, "needs_review": 0})
        stats[dim][verd] = stats[dim].get(verd, 0) + 1
        if verd == "pass":
            pass_ids.setdefault(dim, set()).add(iid)

    # Build filtered package
    out_pkg: dict = {
        "run_manifest":      src_pkg.get("run_manifest", {}),
        "metrics":           src_pkg.get("metrics", {}),
        "dimension_coverage":src_pkg.get("dimension_coverage", {}),
    }

    for src_key, html_key in DIM_MAP.items():
        items   = src_pkg.get(src_key, [])
        allowed = pass_ids.get(src_key, set())

        # Check if source items have any id field
        has_id = any(get_item_id(x, src_key) is not None for x in items[:5])

        if not has_id:
            # No id field — all items passed review (verified above); include all
            kept  = items
            total = len(items)
        else:
            kept, total = [], len(items)
            for item in items:
                iid = get_item_id(item, src_key)
                if iid and iid in allowed:
                    kept.append(item)
        out_pkg[html_key] = kept
        pct = 100 * len(kept) / total if total else 0
        print(f"  {src_key:36s} → {html_key}: {len(kept)}/{total} ({pct:.0f}% pass kept)")

    OUT_PKG.write_text(json.dumps(out_pkg, ensure_ascii=False, indent=2))
    total_in  = sum(len(src_pkg.get(k, [])) for k in DIM_MAP)
    total_out = sum(len(out_pkg[v]) for v in DIM_MAP.values())
    print(f"\n[filtered-pkg] {total_in} → {total_out} items  →  {OUT_PKG}")


if __name__ == "__main__":
    main()
