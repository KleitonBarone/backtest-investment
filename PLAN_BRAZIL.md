# DCA BOVA11 vs 100% CDI: 10-Year Brazilian Investment Comparison

## Goal

Compare the performance of **DCA into BOVA11** (Ibovespa ETF on B3) vs **investing at 100% CDI** (renda fixa benchmark), over a 10-year period with **R$1,000 monthly contributions** and **no initial capital**.

---

## Parameters

| Parameter          | Value                  |
|--------------------|------------------------|
| Initial investment | R$0                    |
| Monthly investment | R$1,000                |
| Time horizon       | 10 years (120 months)  |
| Total invested     | R$120,000              |
| Currency           | BRL                    |

---

## Strategy A: DCA into BOVA11

- Invest R$1,000/month into BOVA11 (B3 ETF that tracks Ibovespa)
- Buy at monthly closing price (true DCA)
- Data source: yfinance ticker `BOVA11.SA`

---

## Strategy B: 100% CDI

- Invest R$1,000/month into a product that yields 100% of CDI
- Each monthly deposit compounds at the daily CDI rate from deposit date onward
- Simulates CDB 100% CDI, Tesouro Selic, or similar renda fixa product
- Data source: Banco Central do Brasil API (SGS series 12 - CDI daily rate)

---

## Metrics

- Total portfolio value at end of 10 years
- Total return (absolute in R$ and %)
- Annualized return (CAGR approximation)
- Max drawdown
- Rolling 10-year windows (if data allows)
- Sharpe ratio

---

## Implementation Plan

### Step 1: Create separate entry point

- Create `main_brazil.py` as a standalone command (independent from `main.py`)
- Reuse `src/simulator.py` and `src/analysis.py` (they are asset-agnostic)
- Create `src/data_brazil.py` for Brazilian data sources

### Step 2: BOVA11 data

- Download monthly closing prices via yfinance (`BOVA11.SA`)
- Cache as CSV in `data/`
- Reuse existing `download_monthly_prices()` from `src/data.py`

### Step 3: CDI data

- Fetch daily CDI rate from BCB SGS API: `https://api.bcb.gov.br/dados/serie/bcdata.sgs.12/dados?formato=json`
- Convert daily CDI rates to monthly compounded returns
- Simulate: each R$1,000 deposit compounds at the CDI rate from its deposit month onward
- Build a CDI simulator that produces the same DataFrame format as `simulate_dca()` so analysis/viz modules work with it
- Cache raw CDI data as CSV in `data/`

### Step 4: CDI simulation logic

- Unlike stock DCA (buy shares), CDI works differently:
  - Each deposit earns compound interest from its deposit date
  - Final value = sum of each deposit × compounded CDI factor from deposit month to end
- Build `simulate_cdi()` in `src/data_brazil.py` that returns a DataFrame with the same columns as `simulate_dca()` (date, total_invested, portfolio_value)

### Step 5: Visualization

- Reuse `src/visualize.py` (already supports multiple strategies)
- Output charts to `output/` with `brazil_` prefix to keep them separate

### Step 6: Run and compare

- `python main_brazil.py` runs the full comparison independently
- Prints comparison table and generates charts

---

## Data Sources

| Data        | Source                          | Notes                                    |
|-------------|---------------------------------|------------------------------------------|
| BOVA11      | yfinance (`BOVA11.SA`)          | Monthly close prices                     |
| CDI (daily) | BCB SGS API (series 12)         | Daily annualized rate, needs compounding |

---

## Directory Changes

```
backtest-investment/
  main.py              # US comparison (unchanged)
  main_brazil.py       # NEW - Brazilian comparison
  src/
    data.py            # US data (unchanged)
    data_brazil.py     # NEW - BOVA11 + CDI data fetching & simulation
    simulator.py       # Reused as-is for BOVA11
    analysis.py        # Reused as-is
    visualize.py       # Reused as-is
```

---

## CDI Simulation Detail

The CDI rate from BCB comes as a daily annualized rate. To simulate:

1. Fetch daily CDI rates
2. Calculate daily factor: `(1 + rate/100) ^ (1/252)`
3. Group by month, compound daily factors to get monthly CDI factor
4. For each R$1,000 deposit at month `t`, compound it through all subsequent monthly factors
5. Portfolio value at month `n` = sum of all deposits × their respective compounded factors
