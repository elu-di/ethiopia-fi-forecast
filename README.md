# Ethiopia Financial Inclusion Forecasting System

[![Tests](https://github.com/selam-analytics/ethiopia-fi-forecast/actions/workflows/unittests.yml/badge.svg)](https://github.com/selam-analytics/ethiopia-fi-forecast/actions)

**Selam Analytics** | Financial Inclusion Forecasting for Ethiopia 2025–2027

---

## 🇪🇹 Overview

A data science system that forecasts Ethiopia's progress on the two core dimensions of financial inclusion (as defined by the World Bank Global Findex):

| Dimension | Indicator | 2024 Baseline |
|-----------|-----------|---------------|
| **Access** | Account Ownership Rate | 49% |
| **Usage** | Digital Payment Adoption | ~35% |

The system integrates historical Findex survey data, operator-reported metrics, infrastructure data, and an event impact model to produce 2025–2027 scenario forecasts.

---

## 🏗️ Project Structure

```
ethiopia-fi-forecast/
├── data/
│   ├── raw/                        # Original Findex + reference CSVs
│   └── processed/                  # Enriched dataset, forecast outputs
├── notebooks/
│   ├── 01_data_exploration_enrichment.ipynb   # Task 1: EDA + enrichment
│   ├── 02_exploratory_data_analysis.ipynb     # Task 2: Visualizations + insights
│   ├── 03_event_impact_modeling.ipynb         # Task 3: Association matrix + validation
│   └── 04_forecasting_access_usage.ipynb      # Task 4: 2025-2027 forecasts
├── src/
│   ├── __init__.py
│   ├── data_loader.py              # Data loading and preprocessing
│   ├── impact_model.py             # Event impact modeling engine
│   └── forecaster.py              # Time-series forecasting framework
├── dashboard/
│   └── app.py                     # Streamlit interactive dashboard
├── tests/
│   ├── test_data_loader.py
│   ├── test_impact_model.py
│   └── test_forecaster.py
├── reports/
│   └── figures/                   # Generated visualizations
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone and install dependencies

```bash
git clone https://github.com/selam-analytics/ethiopia-fi-forecast.git
cd ethiopia-fi-forecast
pip install -r requirements.txt
```

### 2. Run the Interactive Dashboard

```bash
streamlit run dashboard/app.py
```

The dashboard opens at **http://localhost:8501** with 4 sections:
- **📊 Overview** — Key metrics, P2P/ATM crossover, consortium Q&A
- **📈 Historical Trends** — Access, usage, gender gap, infrastructure enablers
- **🔗 Event Impact Matrix** — Association heatmap, temporal curves, event timeline
- **🔮 2025–2027 Projections** — Scenario forecasts, confidence intervals, CSV download

### 3. Run Unit Tests

```bash
python -m pytest tests/ -v
```

### 4. Explore Notebooks

```bash
jupyter notebook notebooks/
```

---

## 📊 Forecast Results (Base Scenario)

| Year | Access (Account Ownership %) | Usage (Digital Payments %) |
|------|------------------------------|---------------------------|
| 2024 | 49.0% (actual) | 35.0% (actual) |
| 2025 | ~57.2% | ~41.1% |
| 2026 | ~61.4% | ~44.7% |
| 2027 | ~64.6% | ~47.9% |

> **NFIS-II Target**: 60% account ownership by 2027 — **achievable in the Base scenario** by 2026.

---

## 🔬 Methodology

### Data
- **5 Global Findex survey points** (2011–2024) for Access
- **4 Findex digital payment data points** (2014–2024) for Usage
- **Enriched with**: Telebirr (54.8M users), M-Pesa (10.8M), infrastructure metrics, Fayda Digital ID data

### Forecasting Approach
1. **OLS Trend Regression** fitted on historical Findex data
2. **Event-Augmented Intervention**: Each cataloged event (product launch, policy, infrastructure) adds modeled impact via **Logistic S-Curves** with evidence-based lag periods (3–24 months)
3. **Scenario Analysis**: Optimistic (×1.25 event effects), Base (×1.0), Pessimistic (×0.75)

### Event Impact Modeling
Events are mapped to indicators through `impact_link` records specifying:
- `impact_direction`: increase / decrease
- `impact_magnitude`: estimated percentage point effect
- `lag_months`: realization delay
- `evidence_basis`: comparable country evidence (Kenya M-Pesa, Tanzania, Ghana)

---

## 📁 Data Sources

| Source | Description |
|--------|-------------|
| World Bank Global Findex 2011–2024 | Primary Access & Usage survey data |
| Ethio Telecom / Telebirr | User counts, transaction volumes |
| Safaricom Ethiopia | M-Pesa user and active rates |
| EthSwitch S.C. | P2P / ATM transaction counts |
| National Bank of Ethiopia | Agent density, ATM data |
| GSMA State of the Industry | Mobile/smartphone penetration |
| IMF Financial Access Survey | Infrastructure benchmarks |
| Fayda Digital ID Program | Enrollment data |

---

## 🔑 Key Findings

1. **P2P/ATM Crossover (Oct 2024)**: Digital P2P transfers (128.3M) have surpassed ATM withdrawals (119.3M) — a historic milestone signaling Ethiopia's digital payment maturation.

2. **The 2021–2024 Paradox**: Despite 65M+ mobile money accounts registered, account ownership only grew +3pp. Explanation: Findex measures *active* usage in past 12 months; many users are registered-only, and P2P is used commercially without being categorized as "digital payment."

3. **Fayda Digital ID is the single biggest policy lever**: Projected +10pp cumulative impact on Access over 24 months (based on Kenya's Huduma Namba comparable evidence).

4. **Usage may outpace Access by 2026**: The P2P-dominant payment culture means Ethiopians use mobile money for commerce even without formal account classification.

5. **NFIS-II 60% target by 2027**: Only achievable in the Optimistic scenario with full Fayda deployment, rural agent expansion, and EthioPay interoperability adoption.

---

## 📅 Project Timeline

| Task | Description | Status |
|------|-------------|--------|
| Task 1 | Data exploration & enrichment | ✅ Complete |
| Task 2 | Exploratory data analysis | ✅ Complete |
| Task 3 | Event impact modeling | ✅ Complete |
| Task 4 | Forecasting Access & Usage | ✅ Complete |
| Task 5 | Interactive dashboard | ✅ Complete |

---

## 👥 Team

**Selam Analytics** — Financial Technology Consulting for Emerging Markets  
Tutors: Kerod, Mahbubah, Feven