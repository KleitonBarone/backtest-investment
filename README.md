# DCA Investment Backtest

Compare Dollar Cost Averaging strategies across US and Brazilian markets using historical data.

## About

This tool simulates monthly fixed-amount investments (DCA) into different asset classes and compares their performance over 10-year horizons. It answers questions like: *"If I had invested $1,000/month in SPY vs bonds vs Bitcoin over the last 10 years, how would each have performed?"* — and does so across every possible 10-year window in the data, not just the most recent one.

## Features

- DCA simulation with configurable monthly contributions and time horizon
- Rolling window analysis across all available history for robust comparisons
- Side-by-side performance tables and charts
- Cached data downloads to avoid redundant API calls
- Separate entry points for US and Brazilian markets

## Assets Covered

### US Market (`main.py`)

| Label | Ticker | Asset Class |
|-------|--------|-------------|
| Equities | SPY | S&P 500 ETF |
| Agg Bonds | AGG | Aggregate bond index |
| Short Treasury | SHY | 1-3 year Treasuries |
| TIPS | TIP | Inflation-protected bonds |
| T-Bills | BIL | Cash equivalent |
| Bitcoin | BTC-USD | Cryptocurrency |

### Brazilian Market (`main_brazil.py`)

| Label | Ticker | Asset Class |
|-------|--------|-------------|
| BOVA11 | BOVA11.SA | Ibovespa ETF |
| DIVO11 | DIVO11.SA | Dividend aristocrats ETF |
| IVVB11 | IVVB11.SA | S&P 500 in BRL |
| GOLD11 | GOLD11.SA | Gold ETF |
| BTC (BRL) | BTC-USD × BRL=X | Bitcoin in BRL |
| 100% CDI | BCB API | Fixed income benchmark |

## Metrics

Each simulation calculates:

- **Total return** — absolute and percentage gain over invested capital
- **CAGR** — annualized return approximation adjusted for gradual DCA investing
- **Max drawdown** — largest peak-to-trough portfolio decline
- **Sharpe ratio** — risk-adjusted return using monthly returns

Rolling window analysis adds:

- Average, best, and worst return across all 10-year windows
- Average final portfolio value

## Getting Started

### Prerequisites

- Python 3.10+

### Installation

```bash
pip install -r requirements.txt
```

### Usage

Run the US market backtest:

```bash
python main.py
```

Run the Brazilian market backtest:

```bash
python main_brazil.py
```

On first run, price data is downloaded and cached in `data/`. Charts are saved to `output/`.

## Project Structure

```
├── main.py              # US market backtest entry point
├── main_brazil.py       # Brazilian market backtest entry point
├── requirements.txt     # Python dependencies
├── src/
│   ├── data.py          # US market data fetching (yfinance)
│   ├── data_brazil.py   # Brazilian data fetching (yfinance + BCB API)
│   ├── simulator.py     # DCA simulation engine
│   ├── analysis.py      # Financial metrics (CAGR, Sharpe, drawdown)
│   └── visualize.py     # Charts and comparison tables
├── data/                # Cached price data (CSV)
└── output/              # Generated charts (PNG)
```

## How It Works

1. **Data** — Monthly closing prices are downloaded via yfinance (and the Banco Central do Brasil API for CDI rates), then cached as CSV files.
2. **Simulation** — For each asset, the tool simulates buying a fixed dollar amount of shares every month and tracks portfolio value over time.
3. **Rolling windows** — Instead of only looking at the most recent 10-year period, the simulation slides a 10-year window across all available history (one month at a time), producing a distribution of outcomes for each asset class.
4. **Output** — Results are printed as comparison tables and saved as PNG charts in the `output/` directory.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
