# Blind Evaluation A/B Template

## Setup

- A: baseline style-guided writing without Core-5 distill package
- B: style-guided writing with Core-5 distill package
- reviewers: at least 2
- samples per arm: at least 3 sections

## Scoring Sheet

Score each axis from 1 to 5.

| Axis | A Score | B Score | Winner | Notes |
|---|---:|---:|---|---|
| Argument coherence |  |  |  |  |
| Evidence alignment |  |  |  |  |
| Novelty clarity |  |  |  |  |
| Style consistency |  |  |  |  |
| Reviewer acceptability |  |  |  |  |

## Pass Rule

- B must beat A on at least 4 axes.
- If not passed, patch failed dimensions only and rerun.

## Reviewer Metadata

- reviewer_id
- domain
- years_experience
- review_timestamp
