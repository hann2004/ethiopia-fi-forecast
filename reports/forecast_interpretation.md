# Forecast Interpretation (Task 4)

This summarizes forecasts for 2025–2027 across scenarios.

## ACC_OWNERSHIP
- Baseline: linear trend with 95% CI based on residual RMSE.
- With events: adds ramped event deltas from impact links.

## Digital Payment Usage
- If percent series absent, we use USG_P2P_COUNT as a volume proxy.
- Scenarios scale trend slope and event deltas (0.8/1.0/1.2 and 0.5/1.0/1.5).

## Key Uncertainties
- Data sparsity (few Findex points), timing and magnitude of future events, policy risk.
- Proxy quality for usage when percent series is not present.

## Notes
- Replace the usage proxy with a percent indicator if/when available by setting usage_pct_codes above.