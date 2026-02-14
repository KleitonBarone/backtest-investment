import os
import pandas as pd
import yfinance as yf

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def download_monthly_prices(ticker: str, start: str = "1990-01-01") -> pd.Series:
    """Download monthly adjusted close prices for a ticker, caching to CSV."""
    os.makedirs(DATA_DIR, exist_ok=True)
    cache_path = os.path.join(DATA_DIR, f"{ticker}_monthly.csv")

    if os.path.exists(cache_path):
        df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
        return df["Close"]

    data = yf.download(ticker, start=start, interval="1mo", auto_adjust=True, progress=False)

    # yfinance may return multi-level columns
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # Fallback: if monthly interval returns too little data, download daily and resample
    if data.empty or len(data) < 3:
        data = yf.download(ticker, start=start, interval="1d", auto_adjust=True, progress=False)
        if data.empty:
            raise ValueError(f"No data returned for {ticker}")
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        data = data[["Close"]].dropna().resample("ME").last().dropna()

    monthly = data[["Close"]].dropna()
    monthly.index.name = "Date"
    monthly.to_csv(cache_path)
    return monthly["Close"]


# All strategies to compare
STRATEGIES = {
    "Equities (SPY)": "SPY",
    "Agg Bonds (AGG)": "AGG",
    "Short Treasury (SHY)": "SHY",
    "TIPS (TIP)": "TIP",
    "T-Bills (BIL)": "BIL",
    "Bitcoin (BTC)": "BTC-USD",
}


def get_all_prices(start: str = "1990-01-01") -> dict[str, pd.Series]:
    """Download monthly prices for all strategies. Returns {label: prices}."""
    result = {}
    for label, ticker in STRATEGIES.items():
        try:
            result[label] = download_monthly_prices(ticker, start=start)
        except ValueError as e:
            print(f"Warning: skipping {label} - {e}")
    return result
