import os
import json
import urllib.request
import pandas as pd
import numpy as np

from src.data import download_monthly_prices

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def get_bova11_prices(start: str = "1990-01-01") -> pd.Series:
    """Get BOVA11 monthly prices from yfinance."""
    return download_monthly_prices("BOVA11.SA", start=start)


def get_divo11_prices(start: str = "1990-01-01") -> pd.Series:
    """Get DIVO11 (dividend aristocrats ETF) monthly prices from yfinance."""
    return download_monthly_prices("DIVO11.SA", start=start)


def get_ivvb11_prices(start: str = "1990-01-01") -> pd.Series:
    """Get IVVB11 (S&P 500 BRL ETF) monthly prices from yfinance."""
    return download_monthly_prices("IVVB11.SA", start=start)


def get_gold11_prices(start: str = "1990-01-01") -> pd.Series:
    """Get GOLD11 (gold ETF) monthly prices from yfinance."""
    return download_monthly_prices("GOLD11.SA", start=start)


def get_btc_brl_prices(start: str = "2010-01-01") -> pd.Series:
    """Get BTC priced in BRL by combining BTC-USD with USD/BRL exchange rate."""
    btc_usd = download_monthly_prices("BTC-USD", start=start)
    usdbrl = download_monthly_prices("BRL=X", start=start)

    # Align on common dates and multiply
    combined = pd.DataFrame({"btc": btc_usd, "fx": usdbrl}).dropna()
    btc_brl = combined["btc"] * combined["fx"]
    btc_brl.name = "Close"
    return btc_brl


def _fetch_cdi_daily() -> pd.DataFrame:
    """Fetch daily CDI rates from Banco Central do Brasil SGS API."""
    os.makedirs(DATA_DIR, exist_ok=True)
    cache_path = os.path.join(DATA_DIR, "CDI_daily.csv")

    if os.path.exists(cache_path):
        df = pd.read_csv(cache_path, parse_dates=["date"])
        return df

    from urllib.parse import quote
    from datetime import datetime

    print("  Fetching CDI data from BCB API...")
    all_records = []
    current_year = datetime.now().year

    import time

    for year in range(2000, current_year + 1):
        start = quote(f"01/01/{year}")
        end = quote(f"31/12/{year}")
        url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.12/dados?formato=json&dataInicial={start}&dataFinal={end}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "*/*"})
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    records = json.loads(resp.read().decode("utf-8"))
                    all_records.extend(records)
                print(f"    {year}: {len(records)} days")
                break
            except urllib.error.HTTPError:
                if attempt < 2:
                    time.sleep(2)
                else:
                    raise
        time.sleep(0.5)

    df = pd.DataFrame(all_records)
    df.columns = ["date", "rate"]
    df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y")
    df["rate"] = pd.to_numeric(df["rate"], errors="coerce")
    df = df.dropna().reset_index(drop=True)
    df.to_csv(cache_path, index=False)
    return df


def get_cdi_monthly_factors() -> pd.DataFrame:
    """
    Convert daily CDI rates to monthly compounded factors.

    Returns DataFrame with columns: month (Period), monthly_factor
    where monthly_factor = product of (1 + daily_rate/100) for all days in that month.
    """
    daily = _fetch_cdi_daily()

    # Daily CDI rate is already the effective daily rate in %
    daily["daily_factor"] = 1 + daily["rate"] / 100
    daily["month"] = daily["date"].dt.to_period("M")

    monthly = daily.groupby("month")["daily_factor"].prod().reset_index()
    monthly.columns = ["month", "monthly_factor"]
    return monthly


def simulate_cdi(
    monthly_factors: pd.DataFrame,
    monthly_contribution: float = 1000.0,
    months: int = 120,
) -> pd.DataFrame:
    """
    Simulate investing monthly_contribution each month at 100% CDI.

    Each deposit compounds at CDI rates from its deposit month onward.
    Returns DataFrame matching simulate_dca() output format.
    """
    factors = monthly_factors.tail(months).reset_index(drop=True)

    if len(factors) < months:
        raise ValueError(
            f"CDI data has {len(factors)} months, need at least {months}"
        )

    records = []
    # Track each deposit and its accumulated value
    deposits = []  # list of current values for each past deposit

    for i, row in factors.iterrows():
        month = row["month"]
        factor = row["monthly_factor"]

        # Compound all existing deposits by this month's factor
        deposits = [d * factor for d in deposits]

        # Add new deposit (it earns this month's rate too)
        deposits.append(monthly_contribution * factor)

        total_invested = monthly_contribution * (i + 1)
        portfolio_value = sum(deposits)

        records.append({
            "date": month.to_timestamp(),
            "price": np.nan,
            "shares_bought": np.nan,
            "total_shares": np.nan,
            "total_invested": total_invested,
            "portfolio_value": portfolio_value,
        })

    return pd.DataFrame(records)
