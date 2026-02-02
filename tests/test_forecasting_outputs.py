
import csv
from pathlib import Path
import pytest

CSV_PATH = Path('reports/forecast_access_usage_2025_2027.csv')
PNG_PATH = Path('reports/figures/forecast_access_usage.png')
MD_PATH  = Path('reports/forecast_interpretation.md')

REQUIRED_COLS = {
    'target','scenario','year','baseline_forecast','with_events_forecast','lower_95','upper_95','event_delta'
}


def test_artifacts_exist():
    assert CSV_PATH.exists(), f"Missing forecast CSV: {CSV_PATH}"
    assert MD_PATH.exists(),  f"Missing interpretation MD: {MD_PATH}"
    if not PNG_PATH.exists():
        pytest.skip('Scenario PNG is ignored by .gitignore and not committed')
    assert PNG_PATH.stat().st_size > 0


def test_csv_schema_and_years():
    with CSV_PATH.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        header = set(reader.fieldnames or [])
        assert REQUIRED_COLS.issubset(header), f"Missing columns: {REQUIRED_COLS - header}"
        years = set()
        targets = set()
        scenarios = set()
        for row in reader:
            try:
                years.add(int(row['year']))
            except Exception:
                pass
            targets.add(row.get('target',''))
            scenarios.add(row.get('scenario',''))
        for y in (2025, 2026, 2027):
            assert y in years, f"Year {y} not present in forecast CSV"
        assert 'ACC_OWNERSHIP' in targets, "ACC_OWNERSHIP target missing"
        assert {'base','pessimistic','optimistic'}.issubset(scenarios), "Scenarios missing"


def test_acc_base_within_bounds():
    # Check base scenario for ACC_OWNERSHIP stays within [0, 100]
    with CSV_PATH.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = [r for r in reader if r.get('target')=='ACC_OWNERSHIP' and r.get('scenario')=='base']
    assert rows, "No base scenario rows for ACC_OWNERSHIP"
    for r in rows:
        b = float(r['baseline_forecast'])
        w = float(r['with_events_forecast'])
        assert 0.0 <= b <= 100.0, f"Baseline out of bounds: {b}"
        assert 0.0 <= w <= 100.0, f"With-events out of bounds: {w}"
