
import pandas as pd
from pathlib import Path

DATA_PATH = Path('data/processed/ethiopia_fi_unified_data_combined.csv')
OUT_CSV = Path('data/processed/event_indicator_association.csv')
OUT_TRIM = Path('data/processed/event_indicator_association_trimmed.csv')
OUT_PNG = Path('reports/figures/event_indicator_heatmap_trimmed.png')

# Load
df = pd.read_csv(DATA_PATH)
impact_links = df[df['record_type']=='impact_link'].copy()
events = df[df['record_type']=='event'].copy()

# Merge
links = impact_links.merge(events.rename(columns={'record_id':'event_id'}), left_on='parent_id', right_on='event_id', how='left')

# Map magnitudes/directions

def to_numeric_mag(x):
    try:
        return float(x)
    except Exception:
        s = str(x).strip().lower()
        return {'low':0.5,'medium':1.0,'high':1.5}.get(s, 1.0)

links['mag_num'] = links['impact_magnitude'].apply(to_numeric_mag)
links['dir_num'] = links['impact_direction'].map({'positive':1,'negative':-1}).fillna(1)
links['effect'] = links['mag_num'] * links['dir_num']

col_name = 'related_indicator' if 'related_indicator' in links.columns else 'indicator_code'
mat = links.pivot_table(index='event_id', columns=col_name, values='effect', aggfunc='sum', fill_value=0)

# Save full matrix
OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
mat.to_csv(OUT_CSV)

# Trim to non-zero rows/cols
mat_trim = mat.loc[(mat.sum(axis=1)!=0), (mat.sum(axis=0)!=0)]
mat_trim.to_csv(OUT_TRIM)

# Try plotting heatmap; fallback gracefully if matplotlib/seaborn unavailable
try:
    import seaborn as sns
    import matplotlib.pyplot as plt
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(max(8, 0.6*mat_trim.shape[1]), max(6, 0.4*mat_trim.shape[0])))
    sns.heatmap(mat_trim, cmap='RdBu_r', center=0)
    plt.title('Event–Indicator Association (non-zero only)')
    plt.tight_layout()
    plt.savefig(OUT_PNG)
    print(f"Saved matrix to {OUT_CSV}, trimmed to {OUT_TRIM}, heatmap to {OUT_PNG}")
except Exception as e:
    print(f"Saved matrix to {OUT_CSV} and {OUT_TRIM}. Heatmap skipped: {e}")
