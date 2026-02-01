
# Forecasting Financial Inclusion in Ethiopia

Build a forecasting system that tracks Ethiopia's digital financial transformation using time series methods.

## Overview
Ethiopia is undergoing a rapid digital financial transformation. Telebirr has grown to over 54 million users since launching in 2021. M-Pesa entered the market in 2023 and now has over 10 million users. For the first time, interoperable P2P digital transfers have surpassed ATM cash withdrawals. Yet according to the 2024 Global Findex survey, only 49% of Ethiopian adults have a financial account; just 3 percentage points higher than in 2021.

This project builds a forecasting system that predicts Ethiopia's progress on the two core dimensions of financial inclusion as defined by the World Bank's Global Findex: Access (Account Ownership Rate) and Usage (Digital Payment Adoption Rate).

## Business Need
Selam Analytics, a financial technology consulting firm specializing in emerging markets, is engaged by a consortium of stakeholders (development finance institutions, mobile money operators, and the National Bank of Ethiopia) to develop a financial inclusion forecasting system. The consortium wants to understand:
- What drives financial inclusion in Ethiopia?
- How do events like product launches, policy changes, and infrastructure investments affect inclusion outcomes?
- How did inclusion rates change in 2025 and what do forecasts indicate for 2026–2027?

## Global Findex Framework
The Global Findex Database is the world's most comprehensive demand-side survey of financial inclusion, conducted every three years since 2011.

- **Access (Account Ownership)**: “The share of adults (age 15+) who report having an account (by themselves or together with someone else) at a bank or another type of financial institution or report personally using a mobile money service in the past 12 months.”
- **Usage (Digital Payments)**: “The share of adults who report using mobile money, a debit or credit card, or a mobile phone to make a payment from an account, or report using the internet to pay bills or to buy something online, in the past 12 months.”

### Ethiopia's Account Ownership Trajectory
| Year | Account Ownership | Change |
|------|-------------------|--------|
| 2011 | 14%               | —      |
| 2014 | 22%               | +8pp   |
| 2017 | 35%               | +13pp  |
| 2021 | 46%               | +11pp  |
| 2024 | 49%               | +3pp   |

### Usage Indicators (2024)
- **Mobile money account ownership**: 9.45%
- **Made or received a digital payment**: ~35%
- **Used account to receive wages**: ~15%

## Deliverables
- **Enriched dataset**: Understand and extend the provided financial inclusion dataset.
- **EDA notebook**: Analyze patterns and relationships in Ethiopia's inclusion data.
- **Impact modeling**: Quantify how events (policy, product launches, infrastructure) affect indicators.
- **Forecasts (2025–2027)**: Access and Usage with uncertainty bounds.
- **Interactive dashboard**: Communicate insights and forecasts to stakeholders.

## Data
Starter dataset: **ethiopia_fi_unified_data** using a unified schema.

- **record_type** values and design:
  - **observation**: Measured values (Findex surveys, operator reports, infrastructure data)
  - **event**: Policies, product launches, market entries, milestones
  - **impact_link**: Modeled relationships between events and indicators
  - **target**: Official policy goals (e.g., NFIS-II targets)
- **Key principle**: Events are categorized by type (policy, product_launch, infrastructure, etc.) but not pre-assigned to pillars. Their effects are captured via impact_link records to keep data unbiased.

Supporting files in this repo:
- [data/raw/ethiopia_fi_unified_data.csv](data/raw/ethiopia_fi_unified_data.csv)
- [data/raw/reference_codes.csv](data/raw/reference_codes.csv)
- [notebooks/02_eda_analysis.ipynb](notebooks/02_eda_analysis.ipynb)
- README schema notes in this document

Supplementary resource: **Additional Data Points Guide** (external spreadsheet) covering:
- **A. Alternative Baselines**: IMF FAS, G20 indicators, GSMA, ITU, NBE
- **B. Direct Correlation**: active accounts, agent density, POS, QR, transaction volumes, ATM density, branches
- **C. Indirect Correlation**: smartphone penetration, data affordability, gender gap, urbanization, mobile internet, 4G, literacy, electricity, digital ID
- **D. Market Nuances**: Ethiopia-specific context (P2P dominance, mobile money-only users ~0.5%, bank accessibility, low credit penetration)

Use this to identify additional observations, understand indicators, and contextualize market dynamics.

## Project Structure
```
ethiopia-fi-forecast/
├── .github/workflows/
│   └── unittests.yml
├── data/
│   ├── raw/
│   │   ├── ethiopia_fi_unified_data.csv
│   │   └── reference_codes.csv
│   └── processed/
├── notebooks/
│   └── README.md
├── src/
│   ├── __init__.py
├── dashboard/
│   └── app.py
├── tests/
│   └── __init__.py
├── models/
├── reports/
│   └── figures/
├── requirements.txt
├── README.md
└── .gitignore
```

## Tasks
- **Task 1: Data Exploration & Enrichment**: Load/explore the unified dataset; add observations, events, and impact_links; document sources and confidence. Status: Completed.
- **Task 2: Exploratory Data Analysis (EDA)**: Summarize dataset, visualize coverage, analyze Access and Usage, infrastructure/enablers, correlations, and key insights. Status: Completed. See [notebooks/02_eda_analysis.ipynb](notebooks/02_eda_analysis.ipynb).
- **Task 3: Event Impact Modeling**: Build event-indicator association matrix; model effect size, direction, and lag; validate against observed changes; document methodology. Status: In progress.
- **Task 4: Forecasting (2025–2027)**: Produce Access and Usage forecasts using trend + event augmentation and scenarios; quantify uncertainty; interpret results. Status: Pending.
- **Task 5: Dashboard Development**: Streamlit app with overview, trends, forecasts, and inclusion projections; at least 4 interactive visuals; clear run instructions. Status: Pending.

## Branching & Workflow
- **Create branches**: `task-1`, `task-2`, `task-3`, `task-4`, `task-5`
- **Minimum essential**: merge via PRs to `main` for each task; use descriptive commit messages.
- **Documentation**: keep a data enrichment log (e.g., `reports/data_enrichment_log.md`) and methodology notes.

## Setup
Prerequisites: Python 3.10+ on Linux.

```bash
# From repo root
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## How to Run
- **Reproduce EDA**:
  - Open [notebooks/02_eda_analysis.ipynb](notebooks/02_eda_analysis.ipynb) and run all cells.
- **Run Dashboard (Streamlit)**:

```bash
# From repo root
source .venv/bin/activate
streamlit run dashboard/app.py
```

- **Data Paths**: Input data in [data/raw](data/raw) and processed outputs in [data/processed](data/processed).

## Analysis Guidance (Summary)
- **Dataset overview**: summarize by `record_type`, `pillar`, `source_type`; visualize temporal coverage and confidence distribution.
- **Access analysis**: account ownership trajectory (2011–2024); growth rates; gender and urban/rural gaps if available; interpret 2021–2024 slowdown.
- **Usage analysis**: mobile money penetration trend; digital payment adoption patterns; registered vs. active gaps; use cases (P2P, merchant, wages).
- **Infrastructure & enablers**: 4G coverage, smartphone penetration, ATM density; assess leading indicators.
- **Event timeline**: timeline of events; overlay on indicators; inspect Telebirr (May 2021), Safaricom entry (Aug 2022), M-Pesa (Aug 2023).
- **Correlation & links**: explore indicator correlations; leverage `impact_link` records for associations.

## Impact Modeling Notes (Planned)
- **Event-indicator matrix**: rows = events; columns = key indicators (e.g., `ACC_OWNERSHIP`, `ACC_MM_ACCOUNT`, `USG_DIGITAL_PAYMENT`); values = effect estimates.
- **Effect dynamics**: immediate vs. lagged effects; additive vs. multiplicative; combination of multiple events.
- **Comparable evidence**: use similar-country studies where local pre/post data is sparse.
- **Validation**: compare modeled impacts to observed trends (e.g., Telebirr 2021 → 2024 mobile money growth from 4.7% to 9.45%).

## Forecasting Notes (Planned)
- **Approach**: trend regression + event augmentation; scenario analysis.
- **Outputs**: baseline and scenario forecasts for 2025–2027; confidence intervals; visualizations.
- **Interpretation**: drivers, largest potential impacts, key uncertainties.

## Dashboard Requirements (Planned)
- **Overview**: key metrics, P2P/ATM crossover ratio, growth highlights.
- **Trends**: interactive time series with filters.
- **Forecasts**: visualization with CI; model selection; milestones.
- **Inclusion Projections**: progress toward 60% target; scenario selector; answer consortium questions.

## Communication & Support
- **Slack**: #all-week-10
- **Office hours**: Mon–Fri, 08:00–15:00 UTC
- **Tutors**: Kerod, Mahbubah, Filimon

## Key Dates
- **Challenge Introduction**: Wed, 28 Jan 2026 (10:30 AM UTC)
- **Interim Submission**: Sun, 01 Feb 2026 (8:00 PM UTC)
- **Final Submission**: Tue, 03 Feb 2026 (8:00 PM UTC)

## Submission Requirements
- **Interim**: repo with Task 1 (enriched dataset + docs) and Task 2 (EDA with visuals); interim report with data enrichment summary, 5+ insights, preliminary event-indicator observations, limitations.
- **Final**: repo with all tasks completed and documented; final report (blog format) with executive summary, methodology, key insights, impact model, forecasts with uncertainty, dashboard screenshots, limitations and future work.

## References
- Global Findex: worldbank.org/globalfindex; methodology; microdata
- IMF Financial Access Survey: data.imf.org/FAS
- GSMA State of the Industry Report: gsma.com/sotir
- World Bank: Financial Inclusion overview
- Demirgüç-Kunt et al. (2018): The Global Findex Database 2017
- IMF: Financial Inclusion and Economic Growth (SDN 15/17)
- CGAP: Beyond the Findex
- FSD Kenya: Administrative data tracking
- Suri & Jack (2016): Long-run impacts of M-Pesa
- Blumenstock et al.: Mobile phone metadata and wealth
- Ethiopia sources: NBE, EthSwitch, Ethio Telecom, Fayda Digital ID, Shega Media

---
**Current Status (Feb 1, 2026)**: Task 1 and Task 2 completed; Task 3–5 to follow.
