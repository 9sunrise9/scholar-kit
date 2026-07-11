"""
update_claim_keywords.py
─────────────────────────────────────────────────────────────
从语料库学习 claim 关键词，写入 runs/claim_keywords.json。

使用方式：
    python3 scripts/update_claim_keywords.py \
        --sample-dir samples/zotero-control-guidance-decision-top-journals \
        --preprocessed-dir samples/preprocessed_md \
        --out-dir runs

建议在以下场景重新运行：
  - 新增或删除了语料论文
  - 调整了 min_papers / top_n 参数
  - 觉得 claim 命中率偏低/偏高时
"""

from __future__ import annotations

import argparse
import json
from collections import OrderedDict
from datetime import date
from pathlib import Path

# ── 复用主脚本的辅助函数 ──────────────────────────────────────────────────
import sys

sys.path.insert(0, str(Path(__file__).parent))
from run_core5_bootstrap import (
    find_preprocessed_md,
    learn_claim_keywords,
    read_pdf_head,
    read_preprocessed_md,
    split_sentences,
)

SEED_KWS = [
    "we propose", "we present", "we introduce", "we develop",
    "our method", "our approach", "our framework",
    "this paper proposes", "in this paper", "in this work",
    "a novel", "the proposed", "is proposed", "are proposed",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Learn claim keywords from corpus and save to JSON.")
    parser.add_argument("--sample-dir", required=True, type=Path)
    parser.add_argument("--preprocessed-dir", type=Path, default=None)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--min-papers", type=int, default=2,
                        help="n-gram 必须出现在至少几篇论文中（默认 2）")
    parser.add_argument("--top-n", type=int, default=200,
                        help="最多保留几个学习到的关键词（默认 200）")
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)

    # ── 构建语料句子库 ────────────────────────────────────────────────────
    pdfs = sorted(args.sample_dir.glob("*.pdf"))
    print(f"[corpus] {len(pdfs)} PDFs found in {args.sample_dir}")

    sentences_by_paper: dict[str, list[tuple[str, str]]] = OrderedDict()
    md_used = pdf_fallback = 0

    for pdf in pdfs:
        md_path = find_preprocessed_md(pdf, args.preprocessed_dir)
        if md_path is not None and md_path.stat().st_size >= 1000:
            text, section_map = read_preprocessed_md(md_path)
            md_used += 1
        else:
            text = read_pdf_head(pdf)
            section_map = {}
            pdf_fallback += 1

        sentences = split_sentences(text)
        for i, s in enumerate(sentences):
            key = s[:40]
            section = section_map.get(key, "Unknown")
            para_id = f"body:{section}:p{i:04d}"
            sentences_by_paper.setdefault(pdf.name, []).append((para_id, s))

    print(f"[corpus] {md_used} from preprocessed MD, {pdf_fallback} fallback to pdftotext")

    # ── 学习关键词 ────────────────────────────────────────────────────────
    learned = learn_claim_keywords(
        sentences_by_paper,
        min_papers=args.min_papers,
        top_n=args.top_n,
    )
    merged = list(dict.fromkeys(learned + SEED_KWS))

    # ── 写入 JSON ─────────────────────────────────────────────────────────
    out_path = args.out_dir / "claim_keywords.json"
    payload = {
        "generated_at": str(date.today()),
        "corpus_papers": len(sentences_by_paper),
        "params": {"min_papers": args.min_papers, "top_n": args.top_n},
        "learned": learned,
        "seed": SEED_KWS,
        "merged": merged,
    }
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    print(f"[done] learned={len(learned)}, seed={len(SEED_KWS)}, merged={len(merged)}")
    print(f"[done] → {out_path}")

    # ── 预览 top-20 ───────────────────────────────────────────────────────
    print("\nTop-20 learned keywords:")
    for i, kw in enumerate(learned[:20], 1):
        print(f"  {i:2d}. {kw}")


if __name__ == "__main__":
    main()
