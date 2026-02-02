
import os
from pathlib import Path
import pandas as pd
import numpy as np
import streamlit as st
import altair as alt

ROOT = Path(__file__).resolve().parent.parent
DATA_COMBINED = ROOT / 'data/processed/ethiopia_fi_unified_data_combined.csv'
FORECAST_CSV = ROOT / 'reports/forecast_access_usage_2025_2027.csv'
MATRIX_TRIM_CSV = ROOT / 'data/processed/event_indicator_association_trimmed.csv'

st.set_page_config(page_title='Ethiopia FI Dashboard', layout='wide')
st.title('Ethiopia Financial Inclusion — Event Impacts & Forecasts')

@st.cache_data(show_spinner=False)
def load_combined():
    if not DATA_COMBINED.exists():
        return None, None, None
    df = pd.read_csv(DATA_COMBINED)
    obs = df[df['record_type']=='observation'].copy()
    ev = df[df['record_type']=='event'].copy()
    links = df[df['record_type']=='impact_link'].copy()
    # datetime parsing
    if 'observation_date' in obs.columns:
        obs['observation_date'] = pd.to_datetime(obs['observation_date'], errors='coerce')
    return obs, ev, links

@st.cache_data(show_spinner=False)
def load_forecast():
    if not FORECAST_CSV.exists():
        return None
    f = pd.read_csv(FORECAST_CSV)
    return f

obs, events, impact_links = load_combined()
forecast_df = load_forecast()

# Sidebar navigation
section = st.sidebar.radio('Section', ['Overview', 'Trends', 'Forecasts', 'Inclusion Projections', 'Downloads'])

# Utility: latest value per indicator
def latest_value(obs, code):
    if obs is None: return None
    s = obs[obs['indicator_code']==code].copy()
    if s.empty: return None
    s = s.dropna(subset=['observation_date']).sort_values('observation_date')
    return float(s['value_numeric'].iloc[-1]) if not s.empty else None

# Utility: YoY change for year-aggregated
def yoy_change(obs, code):
    if obs is None: return None
    s = obs[obs['indicator_code']==code].copy()
    if s.empty: return None
    s['observation_date'] = pd.to_datetime(s['observation_date'], errors='coerce')
    s = s.dropna(subset=['observation_date'])
    s['year'] = s['observation_date'].dt.year
    agg = s.groupby('year')['value_numeric'].mean() if code=='ACC_OWNERSHIP' else s.groupby('year')['value_numeric'].sum()
    if len(agg) < 2: return None
    last, prev = agg.iloc[-1], agg.iloc[-2]
    try:
        return float((last - prev) / (prev if prev != 0 else np.nan) * 100.0)
    except Exception:
        return None

# Overview
if section == 'Overview':
    st.subheader('Key Metrics')
    col1, col2, col3 = st.columns(3)
    acc_latest = latest_value(obs, 'ACC_OWNERSHIP')
    p2p_latest = yoy_change(obs, 'USG_P2P_COUNT')  # use YoY % for highlight
    acc_yoy = yoy_change(obs, 'ACC_OWNERSHIP')
    with col1:
        st.metric('Account Ownership (%)', f"{acc_latest if acc_latest is not None else '—'}", delta=f"{acc_yoy:.2f}% YoY" if acc_yoy is not None else None)
    # P2P vs ATM crossover ratio (last year totals)
    with col2:
        p2p = obs[obs['indicator_code']=='USG_P2P_COUNT'].copy() if obs is not None else pd.DataFrame()
        atm = obs[obs['indicator_code']=='USG_ATM_COUNT'].copy() if obs is not None else pd.DataFrame()
        for df in (p2p, atm):
            if not df.empty:
                df['observation_date'] = pd.to_datetime(df['observation_date'], errors='coerce')
                df['year'] = df['observation_date'].dt.year
        p2p_y = p2p.groupby('year')['value_numeric'].sum() if not p2p.empty else pd.Series(dtype=float)
        atm_y = atm.groupby('year')['value_numeric'].sum() if not atm.empty else pd.Series(dtype=float)
        if not p2p_y.empty and not atm_y.empty and (p2p_y.index[-1] == atm_y.index[-1]):
            ratio = float(p2p_y.iloc[-1] / atm_y.iloc[-1]) if atm_y.iloc[-1] else np.nan
            st.metric('P2P/ATM Crossover Ratio', f"{ratio:.2f}" if not np.isnan(ratio) else '—')
        else:
            st.metric('P2P/ATM Crossover Ratio', '—')
    with col3:
        st.metric('P2P Transactions YoY (%)', f"{p2p_latest:.2f}%" if p2p_latest is not None else '—')

    st.markdown('---')
    st.subheader('Impact Links (non-zero associations)')
    if MATRIX_TRIM_CSV.exists():
        mat = pd.read_csv(MATRIX_TRIM_CSV)
        st.dataframe(mat, use_container_width=True)
        st.download_button('Download association matrix (trimmed CSV)', mat.to_csv(index=False).encode('utf-8'), file_name='event_indicator_association_trimmed.csv', mime='text/csv')
    else:
        st.info('No trimmed association matrix found yet.')

# Trends
elif section == 'Trends':
    st.subheader('Interactive Indicator Trends')
    if obs is None or obs.empty:
        st.warning('No observation data available.')
    else:
        codes = sorted(obs['indicator_code'].dropna().unique().tolist())
        code = st.selectbox('Indicator', options=codes, index=(codes.index('ACC_OWNERSHIP') if 'ACC_OWNERSHIP' in codes else 0))
        df = obs[obs['indicator_code']==code].copy()
        df['observation_date'] = pd.to_datetime(df['observation_date'], errors='coerce')
        df = df.dropna(subset=['observation_date'])
        min_date, max_date = df['observation_date'].min(), df['observation_date'].max()
        rng = st.slider('Date range', min_value=min_date.to_pydatetime(), max_value=max_date.to_pydatetime(), value=(min_date.to_pydatetime(), max_date.to_pydatetime()))
        df = df[(df['observation_date']>=pd.Timestamp(rng[0])) & (df['observation_date']<=pd.Timestamp(rng[1]))]
        chart = alt.Chart(df).mark_line(point=True).encode(
            x='observation_date:T', y='value_numeric:Q', tooltip=['observation_date:T','value_numeric:Q']
        ).properties(height=350)
        st.altair_chart(chart, use_container_width=True)
        st.download_button('Download filtered series (CSV)', df[['observation_date','indicator_code','value_numeric']].to_csv(index=False).encode('utf-8'), file_name=f'{code}_filtered.csv', mime='text/csv')

    st.markdown('---')
    st.subheader('Channel Comparison: P2P vs ATM (monthly)')
    if obs is not None and not obs.empty:
        def build_monthly(code):
            d = obs[obs['indicator_code']==code].copy()
            if d.empty: return pd.DataFrame()
            d['observation_date'] = pd.to_datetime(d['observation_date'], errors='coerce')
            d = d.dropna(subset=['observation_date'])
            d['month'] = d['observation_date'].dt.to_period('M').dt.to_timestamp()
            agg = d.groupby('month')['value_numeric'].sum().reset_index(name='value')
            agg['series'] = code
            return agg
        p2p_m = build_monthly('USG_P2P_COUNT')
        atm_m = build_monthly('USG_ATM_COUNT')
        comp = pd.concat([p2p_m, atm_m], ignore_index=True)
        if not comp.empty:
            chart2 = alt.Chart(comp).mark_line(point=True).encode(
                x='month:T', y='value:Q', color='series:N', tooltip=['month:T','series:N','value:Q']
            ).properties(height=350)
            st.altair_chart(chart2, use_container_width=True)
        else:
            st.info('P2P/ATM monthly series not available.')

# Forecasts
elif section == 'Forecasts':
    st.subheader('Forecasts (2025–2027)')
    if forecast_df is None or forecast_df.empty:
        st.warning('No forecast table found. Run Task 4 to generate forecasts.')
    else:
        targets = forecast_df['target'].unique().tolist()
        target = st.selectbox('Target', options=targets, index=(targets.index('ACC_OWNERSHIP') if 'ACC_OWNERSHIP' in targets else 0))
        scenario = st.radio('Scenario', options=['pessimistic','base','optimistic'], index=1)
        model_sel = st.radio('Model', options=['baseline','with events'], index=1)
        sub = forecast_df[(forecast_df['target']==target) & (forecast_df['scenario']==scenario)].copy()
        y_col = 'baseline_forecast' if model_sel=='baseline' else 'with_events_forecast'
        band_lo, band_hi = 'lower_95', 'upper_95'
        base = alt.Chart(sub).mark_line(point=True).encode(
            x='year:O', y=alt.Y(y_col, title='Forecast'), tooltip=['year:O', y_col]
        )
        band = alt.Chart(sub).mark_area(opacity=0.2).encode(
            x='year:O', y=band_lo, y2=band_hi
        )
        st.altair_chart(band + base, use_container_width=True)
        st.dataframe(sub[['target','scenario','year',y_col,band_lo,band_hi,'event_delta']], use_container_width=True)
        st.download_button('Download forecast (filtered CSV)', sub.to_csv(index=False).encode('utf-8'), file_name=f'forecast_{target}_{scenario}_{model_sel}.csv', mime='text/csv')

# Inclusion Projections
elif section == 'Inclusion Projections':
    st.subheader('Financial Inclusion Rate Projections toward 60%')
    if forecast_df is None or forecast_df.empty:
        st.warning('No forecast table found. Run Task 4 to generate forecasts.')
    else:
        scenario = st.selectbox('Scenario', options=['pessimistic','base','optimistic'], index=1)
        y_col = st.radio('Model', options=['baseline_forecast','with_events_forecast'], index=1)
        acc = forecast_df[(forecast_df['target']=='ACC_OWNERSHIP') & (forecast_df['scenario']==scenario)].copy()
        if acc.empty:
            st.info('ACC_OWNERSHIP forecast not available.')
        else:
            acc['target_line'] = 60.0
            chart = alt.Chart(acc).mark_line(point=True).encode(
                x='year:O', y=alt.Y(y_col, title='ACC_OWNERSHIP (%)'), tooltip=['year:O', y_col]
            )
            goal = alt.Chart(acc).mark_rule(color='red').encode(y='target_line:Q')
            st.altair_chart(chart + goal, use_container_width=True)
            # Milestone detection
            reached = acc[acc[y_col] >= 60.0]
            if not reached.empty:
                yr = int(reached['year'].iloc[0])
                st.success(f"Projected to reach ≥60% in {yr} ({scenario}, {y_col.replace('_',' ')})")
            else:
                st.info('Projected level remains below 60% across 2025–2027 for the selected scenario/model.')

            # Progress bars
            for _, r in acc.iterrows():
                st.progress(min(1.0, float(r[y_col])/60.0), text=f"{int(r['year'])}: {r[y_col]:.1f}% of 60% target")
# Downloads
elif section == 'Downloads':
    st.subheader('Data & Exports')
    # Combined dataset download (optionally filtered)
    if obs is None:
        st.info('Combined dataset not found. Ensure processed CSV exists.')
    else:
        st.markdown('### Combined Dataset')
        codes = sorted(obs['indicator_code'].dropna().unique().tolist())
        filt_code = st.selectbox('Filter by indicator (optional)', options=['(all)'] + codes, index=0)
        df_dl = obs.copy() if filt_code=='(all)' else obs[obs['indicator_code']==filt_code].copy()
        st.dataframe(df_dl[['observation_date','indicator_code','value_numeric']].head(50), use_container_width=True)
        st.download_button('Download combined (CSV)', df_dl.to_csv(index=False).encode('utf-8'), file_name=('combined_filtered.csv' if filt_code!='(all)' else 'combined.csv'), mime='text/csv')

    st.markdown('---')
    # Forecast table download
    st.markdown('### Forecast Table (Task 4)')
    if forecast_df is None or forecast_df.empty:
        st.info('No forecast table found. Generate via Task 4.')
    else:
        tgt = st.selectbox('Target', options=sorted(forecast_df['target'].unique().tolist()))
        scen = st.selectbox('Scenario', options=['pessimistic','base','optimistic'], index=1)
        mdl = st.selectbox('Model', options=['baseline_forecast','with_events_forecast'], index=1)
        sub = forecast_df[(forecast_df['target']==tgt) & (forecast_df['scenario']==scen)].copy()
        st.dataframe(sub[['target','scenario','year',mdl,'lower_95','upper_95','event_delta']], use_container_width=True)
        st.download_button('Download forecast (filtered CSV)', sub.to_csv(index=False).encode('utf-8'), file_name=f'forecast_{tgt}_{scen}_{mdl}.csv', mime='text/csv')

    st.markdown('---')
    # Impact association matrix: show heatmap + download
    st.markdown('### Event–Indicator Association (Trimmed)')
    if MATRIX_TRIM_CSV.exists():
        mat = pd.read_csv(MATRIX_TRIM_CSV)
        # Identify id column for rows
        id_col = 'event_id' if 'event_id' in mat.columns else mat.columns[0]
        mat_long = mat.melt(id_vars=[id_col], var_name='indicator', value_name='effect')
        hm = alt.Chart(mat_long).mark_rect().encode(
            x=alt.X('indicator:N', title='Indicator'),
            y=alt.Y(f'{id_col}:N', title='Event'),
            color=alt.Color('effect:Q', scale=alt.Scale(scheme='redblue'), title='Effect'),
            tooltip=['indicator','effect', id_col]
        ).properties(height=400)
        st.altair_chart(hm, use_container_width=True)
        st.download_button('Download association matrix (trimmed CSV)', mat.to_csv(index=False).encode('utf-8'), file_name='event_indicator_association_trimmed.csv', mime='text/csv')
    else:
        st.info('No trimmed association matrix CSV found.')
