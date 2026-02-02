# Event Impact Modeling Methodology

## Overview
We model how events (policy, product_launch, infrastructure, etc.) affect indicators using the `impact_link` records.
Links specify: parent event (`parent_id`), pillar, `related_indicator`, `impact_direction`, `impact_magnitude`, optional `lag_months`, and `evidence_basis`.

## Association Matrix
- Compute per-link numeric effect: `effect = magnitude × direction`.
- Magnitude is numeric if provided; otherwise map {low:0.5, medium:1.0, high:1.5}.
- Direction maps {positive:+1, negative:-1}.
- Pivot to an Event×Indicator matrix with sums across links.
- Zeros indicate no modeled link; we also provide a trimmed non-zero matrix and heatmap.

## Time-Distributed Effects
- For each link, apply a ramp-up over `lag_months`: `effect_t = effect × min(1, t/lag)` for monthly t≥0.
- Sum ramped effects across links to build an indicator-level timeline.
- This captures delayed and cumulative impacts while remaining transparent and simple.

## Event-Augmented Regression
- Fit observed series (e.g., ACC_OWNERSHIP) as: `y = β0 + β1*trend + β2*modeled_effect + ε`.
- Trend uses normalized year; modeled_effect is the indicator timeline at year-end.
- Report coefficients and R²; this is a lightweight check of explanatory power rather than causal identification.

## Validation and Sanity Checks
- Telebirr/M-Pesa: Confirm the model assigns positive effects to mobile money-related indicators and digital transactions.
- Compare modeled timelines against observed points (e.g., ACC_MM_ACCOUNT 2021→2024 increase).

## Assumptions
- Effects are additive across events and approximately linear in magnitude.
- Lag structures approximate build-out realities (agents, coverage, adoption) and are documented in `evidence_basis`.
- Mapping of qualitative magnitudes (low/medium/high) is pragmatic and can be tuned.

## Limitations
- Sparse data (few Findex points) limits precision; identification confounds are possible.
- Supply-side registrations vs survey usage differences can create divergence.
- Overlapping events and context shifts (policy, macro) are not fully disentangled.

## Outputs
- `data/processed/event_indicator_association.csv` and `_trimmed.csv`.
- Heatmaps in `reports/figures/`.
- Notebook sections for diagnostics, timelines, and regressions.
