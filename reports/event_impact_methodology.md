# Event Impact Modeling — Methodology

## Functional Form
- We model event impacts as additive step changes to indicator series starting at `event_date + lag_months`.
- Where `impact_magnitude` is provided, it is used directly. If unavailable, we use `impact_estimate` or unit effect based on `impact_direction` (+1/-1).
- Percentage indicators are adjusted in percentage points; count indicators in units.

## Association Matrix
- Built from `impact_link` records joined to events via `parent_id`→`record_id`.
- Matrix rows are events; columns are indicators; values are mean effect magnitudes.
- Visualized as a heatmap to highlight strongest relationships.

## Lag Structure and Decay
- Effects apply after `lag_months` from the event date.
- Optionally, effects can be extended with simple linear decay (not enabled by default).

## Validation
- Compare predicted event-adjusted trajectories to observed points.
- Example: Telebirr (2021) and M-Pesa (2023) impacts on `ACC_MM_ACCOUNT` (mobile money accounts) from 2021→2024.

## Assumptions
- Effects are additive and independent (no interaction terms).
- Impact magnitudes are comparable across events within the same indicator.
- Observation series are forward-filled monthly to enable comparison.

## Limitations
- Sparse observations (Findex triennial) constrain estimation accuracy.
- Impact heterogeneity by region/gender not captured in the simple framework.
- Supply-side milestones may not map 1:1 to demand-side survey outcomes.

## Sources
- Global Findex 2011–2024 (World Bank)
- Ethio Telecom (Telebirr) announcements
- Safaricom Ethiopia (M-Pesa) announcements
- EthSwitch interoperability reports
