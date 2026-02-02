
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

DATA_PATH = Path('data/processed/ethiopia_fi_unified_data_combined.csv')
OUT_CSV = Path('data/processed/event_indicator_association.csv')
OUT_PNG = Path('reports/figures/event_indicator_heatmap.png')

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

# Save csv
OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
mat.to_csv(OUT_CSV)

# Plot heatmap
OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
plt.figure(figsize=(10,8))
sns.heatmap(mat, cmap='RdBu_r', center=0)
plt.title('Event–Indicator Association (Effect)')
plt.tight_layout()
plt.savefig(OUT_PNG)
print(f"Saved matrix to {OUT_CSV} and heatmap to {OUT_PNG}")
