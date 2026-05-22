#  Cross-Asset Market Intelligence Workspace

An interactive quantitative research workspace built with **Plotly Dash** and **Pandas** to evaluate cross-asset risk-reward profiles across 451 macro financial assets.

### 🔗 Project Deliverables
* **Repository:** [GitHub](https://github.com/xiasong/Yahoo_Finance_Global_Markets_Intelligence_2026/tree/main)
* **Data Source:** [Kaggle Dataset](https://www.kaggle.com/datasets/kanchana1990/yahoo-finance-global-markets-intelligence-2026?resource=download)
* **App URL:** `http://localhost:8050/`

---

## 🛠️ 1. Environment Setup & Core Dependencies

### 📦 Core Dependencies
*   **pandas** >= 3.0.2 (Data manipulation)
*   **dash** >= 4.1.0 (UI framework)
*   **plotly** >= 6.7.0 (Graphics rendering)

### 💻 Installation Commands
```bash
# 1. Project Directory Layout
mkdir -p Documents/xiasong/interviews/DAS_project
cd Documents/xiasong/interviews/DAS_project

# 2. Virtual Environment Isolation
conda create --name dash-env python=3.13 -y
conda activate dash-env

# 3. Dependencies Ingestion
pip install -r requirements.txt
```
*Note: Target data file is mounted directly at `DAS_project/yahoo_finance_dashboard/data/`.*

---

## 📊 2. Data Audit & Core Metrics

The schema spans **135 columns** for 451 assets. To optimize a rapid 2-hour development cycle, the workspace targets four core variables:
* `ticker`: Unique asset identifier.
* `asset_class`: Macroeconomic cluster mapping.
* `return_1w_pct`: Short-term reward proxy.
* `volatility_30d_ann`: Annualized 30-day risk proxy.

> 💡 **Financial Rationale:** Using annualized volatility scales risk to a standard 1-year horizon. This permits mathematically sound "apples-to-apples" efficiency comparisons between diverse asset clusters (e.g., Crypto vs. Forex) on a single spatial plane.

---

## 💻 3. Modular Code Architecture

### 🔄 Data Pipeline (`utils/data_loader.py`)
* **Dynamic File Discovery:** Bypasses hardcoded paths via `os.listdir()` to automatically ingest the first available `.csv` in the `/data` folder.
* **Bug Fix (Vectorized Strings):** 
  * *Issue:* `AttributeError: 'Series' object has no attribute 'strip'` raised during column sanitization.
  * *Fix:* Vectorized the string transformation using explicit Pandas accessor syntax: `df[col] = df[col].astype(str).str.strip()`.

### 🎛️ Presentation Layer (`app.py`)
* **Cascading UI Callbacks:** State triggers dynamically update the child `ticker` selector array based on the active parent `asset_class` choice.
* **Data Guardrails:** Enforces `pd.to_numeric(errors='coerce')` and immediate `.dropna()` execution to protect rendering loops from text-string corruptions.
* **Memory Optimization:** Downcasts `asset_class` strings to the memory-efficient `category` data type to maximize background search speeds.

---

## 📈 4. Analytical UI Layout

* **Leaderboard Momentum Panel (Chart 1):** Bar chart ranking the top 20 assets in the class by weekly gains. The highlighted ticker turns bright crimson (`#e74c3c`) against slate grey peers to isolate momentum shifts.
* **Risk-Efficiency Frontier Matrix (Chart 2):** Scatter plot mapping annualized risk against weekly returns. Analysts can instantly identify high-efficiency assets in the upper-left quadrant and high-risk laggards in the lower-right quadrant.