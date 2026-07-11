# Core-5 Execution Playbook

## Goal

Run a minimal but high-value distillation loop before full 11-dimension rollout.

## Core-5 Dimensions

1. Macro blueprint
2. Paragraph templates
3. Claim-evidence binding
4. Related-work positioning
5. Innovation argument and phrase patterns

## Skill Mapping

- Macro blueprint: rules-distill + distill
- Paragraph templates: extract-pattern + prose-distill
- Claim-evidence binding: argumentation + argument-validator
- Related-work positioning: academic-writing + distill
- Innovation patterns: prose-distill + argumentation + rules-distill

## Execution Steps

1. Prepare corpus and freeze source list.
2. Run distillation for the 5 dimensions.
3. Merge outputs into schema-compliant package.
4. Apply dedup and conflict resolution.
5. Run quality gates and leakage checks.
6. Trigger human review for innovation outputs.
7. Publish distill-memory package.
8. Run blind evaluation A/B.

## Bootstrap Command

```bash
RUN_ID="core5-$(date +%Y%m%d-%H%M%S)"
OUT_DIR="paper-style-distiller/runs/$RUN_ID"
python3 paper-style-distiller/scripts/run_core5_bootstrap.py \
	--sample-dir paper-style-distiller/samples/zotero-control-guidance-decision-top-journals \
	--out-dir "$OUT_DIR" \
	--manifest-template paper-style-distiller/references/run-manifest-template.json
```

Expected outputs:

- paper-style-distiller/runs/<run_id>/core5-distill-package.json
- paper-style-distiller/runs/<run_id>/core5-summary.md

## Blind Evaluation A/B

Use template: blind-eval-ab-template.md

A arm:

- Write with baseline style-guided workflow only.

B arm:

- Write with Core-5 distilled package.

Scoring axes:

- argument coherence
- evidence alignment
- novelty clarity
- style consistency
- reviewer acceptability

Pass criterion:

- B beats A on at least 4 out of 5 axes.

## Rollout Rule

- If Core-5 passes, enable full 11-dimension run.
- If Core-5 fails, repair failed dimensions only and rerun A/B.
