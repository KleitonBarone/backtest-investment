import pandas as pd
import numpy as np


def simulate_dca(
    prices: pd.Series,
    monthly_contribution: float = 1000.0,
    months: int = 120,
) -> pd.DataFrame:
    """
    Simulate dollar cost averaging over a given price series.

    Args:
        prices: Monthly closing prices (DatetimeIndex).
        monthly_contribution: Amount invested each month.
        months: Number of months to invest.

    Returns:
        DataFrame with columns: date, shares_bought, total_shares,
        total_invested, portfolio_value
    """
    if len(prices) < months:
        raise ValueError(
            f"Price series has {len(prices)} months, need at least {months}"
        )

    prices = prices.iloc[:months]
    records = []
    total_shares = 0.0
    total_invested = 0.0

    for date, price in prices.items():
        shares_bought = monthly_contribution / price
        total_shares += shares_bought
        total_invested += monthly_contribution
        portfolio_value = total_shares * price

        records.append({
            "date": date,
            "price": price,
            "shares_bought": shares_bought,
            "total_shares": total_shares,
            "total_invested": total_invested,
            "portfolio_value": portfolio_value,
        })

    return pd.DataFrame(records)


def run_rolling_windows(
    prices: pd.Series,
    monthly_contribution: float = 1000.0,
    window_months: int = 120,
) -> list[pd.DataFrame]:
    """
    Run DCA simulation for every possible rolling window of window_months.

    Returns a list of simulation DataFrames, one per starting month.
    """
    results = []
    max_start = len(prices) - window_months

    for start in range(max_start + 1):
        window_prices = prices.iloc[start : start + window_months]
        sim = simulate_dca(window_prices, monthly_contribution, window_months)
        results.append(sim)

    return results
