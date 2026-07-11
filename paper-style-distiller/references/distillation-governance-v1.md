# Distillation Governance v1

## Scope

This governance applies to the 11-dimension paper style distillation workflow.

## Accepted Improvements and Concrete Controls

### 1. Unified Data Contract

- Use one stable schema file: style-distill-schema-v1.json.
- Reject outputs that do not match required fields.
- All records must carry stable id, source_id, and confidence.

### 2. Cross-Dimension Dedup and Conflict Resolution

- Dedup key: section + intent + tense + normalized_pattern.
- Semantic duplicate threshold: cosine >= 0.90.
- Keep the entry with higher evidence_count, then higher confidence.
- If still tied, keep the newer entry and archive the older one.

### 3. Quality Gates and Rejection Rules

Required metrics:

- coverage >= 0.70
- consistency >= 0.60
- actionability >= 0.70
- leakage_risk <= 0.20

Hard rejection triggers:

- missing evidence binding for any strong claim
- unresolved schema errors
- unresolved duplicate conflict count > 20

### 5. Leakage and Copyright Defense

- No sentence-level reuse above 13 consecutive tokens.
- ngram_overlap_4 <= 0.25 against source set.
- semantic_similarity_max <= 0.92 at sentence level.
- Any candidate above threshold must be rewritten and rechecked.

### 6. Traceable Evidence Chain

Each rule or template must map to:

- source_paper_id
- source_paragraph_id
- evidence_type
- evidence_strength
- extraction_timestamp

No evidence chain means no publication to memory.

### 8. Fallback Paths

When one dimension fails quality gates:

- fallback A: lower rhetorical_strength and rerun extraction.
- fallback B: restrict to section + intent extraction only.
- fallback C: route to human review with fail reasons.

### 9. Human Review Protocol

Human review is mandatory for:

- innovation dimension outputs
- any strong claim with confidence < 0.75
- any leakage risk warning

Review checklist:

- factual safety
- evidence alignment
- novelty phrasing quality
- reproducibility notes

### 10. Reproducibility and Versioning

Every run must output run-manifest with:

- schema_version
- prompt_pack_version
- skill_versions
- source_corpus_hash
- run_timestamp
- operator

### 12. Cost and Latency Budget

Default budget per run:

- max_tokens_total: 500000
- max_minutes_total: 90
- max_dimensions_parallel: 3

Escalation rule:

- If budget usage > 80 percent before dimension 8, switch to Core-5 mode.

### 13. Safety Boundary Definition

Policy goal:

- Learn methods, not replicate source text.

Boundary rules:

- never preserve source named entities that are not needed
- never copy citation sentence structures verbatim
- preserve scientific meaning while restructuring syntax and discourse flow

## Core-5 First Strategy

Run dimensions in this order for minimal closed loop:

1. macro blueprint
2. paragraph templates
3. claim-evidence binding
4. related-work positioning
5. innovation argument and phrase patterns

Then run blind evaluation before enabling all 11 dimensions.
