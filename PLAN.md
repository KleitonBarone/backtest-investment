# DCA vs Bonds: 10-Year Investment Comparison

## Goal

Compare the performance of **Dollar Cost Averaging into equities** vs **investing in bonds**, over a 10-year period with **$1,000 monthly contributions** and **no initial capital**.

---

## Parameters

| Parameter          | Value              |
|--------------------|--------------------|
| Initial investment | $0                 |
| Monthly investment | $1,000             |
| Time horizon       | 10 years (120 months) |
| Total invested     | $120,000           |

---

## Strategy A: DCA into Equities

- Invest $1,000/month into a broad market index (e.g., S&P 500 via SPY/VOO)
- Buy at whatever the current price is each month (true DCA)
- Backtest using historical monthly closing prices

### Metrics to calculate
- Total portfolio value at end of 10 years
- Total return (absolute and %)
- Annualized return (CAGR)
- Max drawdown during the period
- Worst and best 10-year windows (rolling analysis)

---

## Strategy B: Bonds

- Invest $1,000/month into bonds (e.g., US 10-Year Treasury or aggregate bond index like AGG/BND)
- Same monthly contribution schedule
- Use historical bond yields/prices for backtesting

### Metrics to calculate
- Total portfolio value at end of 10 years
- Total return (absolute and %)
- Annualized return (CAGR)
- Max drawdown during the period
- Worst and best 10-year windows (rolling analysis)

---

## Comparison Outputs

1. **Summary table** - side by side final values, returns, risk metrics
2. **Growth chart** - portfolio value over time for both strategies
3. **Rolling 10-year returns** - how each strategy performed across different start dates
4. **Risk-adjusted return** - Sharpe ratio or similar metric for both

---

## Implementation Plan

### Step 1: Project setup
- Initialize Python project with dependencies (pandas, numpy, matplotlib, yfinance)
- Set up project structure

### Step 2: Data collection
- Download historical monthly prices for S&P 500 (or SPY) going back as far as possible
- Download historical monthly prices/yields for bonds (AGG, BND, or 10-Year Treasury data)
- Store raw data locally as CSV for reproducibility

### Step 3: DCA simulation engine
- Build a function that takes: monthly prices, monthly contribution amount, number of months
- Simulates buying shares each month at that month's price
- Tracks: shares owned, total invested, portfolio value over time

### Step 4: Run backtests
- Run DCA simulation on equity data for every possible 10-year window
- Run same simulation on bond data
- Collect results for all windows

### Step 5: Analysis and visualization
- Generate comparison table
- Plot portfolio growth curves
- Plot rolling 10-year return comparison
- Calculate risk metrics (max drawdown, volatility, Sharpe ratio)

### Step 6: Results summary
- Write findings to a results file or notebook
- Highlight key takeaways

---

## Tech Stack

- **Python 3**
- **pandas** - data manipulation
- **numpy** - calculations
- **matplotlib/seaborn** - charts
- **yfinance** - historical price data

---

## Directory Structure (planned)

```
backtest-investment/
  PLAN.md
  requirements.txt
  src/
    data.py          # data download and caching
    simulator.py     # DCA simulation engine
    analysis.py      # metrics and comparison logic
    visualize.py     # chart generation
  main.py            # run everything
  data/              # cached CSV files
  output/            # charts and results
```
