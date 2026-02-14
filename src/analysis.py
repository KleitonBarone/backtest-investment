import pandas as pd
import numpy as np


def total_return(sim: pd.DataFrame) -> float:
    """Absolute return: final value - total invested."""
    return sim["portfolio_value"].iloc[-1] - sim["total_invested"].iloc[-1]


def total_return_pct(sim: pd.DataFrame) -> float:
    """Percentage return over total invested."""
    final = sim["portfolio_value"].iloc[-1]
    invested = sim["total_invested"].iloc[-1]
    return (final - invested) / invested * 100


def cagr(sim: pd.DataFrame) -> float:
    """
    Annualized return approximation for DCA.
    Uses time-weighted approach: CAGR of portfolio value relative to
    what the total invested would be worth at that rate.
    """
    final_value = sim["portfolio_value"].iloc[-1]
    total_invested = sim["total_invested"].iloc[-1]
    n_months = len(sim)
    n_years = n_months / 12

    # For DCA, approximate CAGR using the ratio of final value to total invested
    # adjusted by the fact that money was invested gradually
    # Average dollar was invested for half the period
    avg_years = n_years / 2
    if avg_years <= 0 or total_invested <= 0:
        return 0.0
    return ((final_value / total_invested) ** (1 / avg_years) - 1) * 100


def max_drawdown(sim: pd.DataFrame) -> float:
    """Maximum drawdown of portfolio value as a percentage."""
    values = sim["portfolio_value"].values
    peak = values[0]
    max_dd = 0.0

    for v in values:
        if v > peak:
            peak = v
        dd = (peak - v) / peak * 100
        if dd > max_dd:
            max_dd = dd

    return max_dd


def monthly_returns(sim: pd.DataFrame) -> pd.Series:
    """Calculate month-over-month portfolio returns, accounting for contributions."""
    values = sim["portfolio_value"].values
    contributions = sim["total_invested"].diff().fillna(sim["total_invested"].iloc[0]).values
    returns = []

    for i in range(1, len(values)):
        prev_value = values[i - 1]
        if prev_value > 0:
            r = (values[i] - prev_value - contributions[i]) / prev_value
        else:
            r = 0.0
        returns.append(r)

    return pd.Series(returns)


def sharpe_ratio(sim: pd.DataFrame, risk_free_annual: float = 0.03) -> float:
    """Annualized Sharpe ratio using monthly returns."""
    rets = monthly_returns(sim)
    if rets.std() == 0:
        return 0.0
    rf_monthly = (1 + risk_free_annual) ** (1 / 12) - 1
    excess = rets - rf_monthly
    return (excess.mean() / excess.std()) * np.sqrt(12)


def summarize(sim: pd.DataFrame, label: str) -> dict:
    """Generate a summary dict for a simulation."""
    return {
        "strategy": label,
        "start_date": sim["date"].iloc[0].strftime("%Y-%m"),
        "end_date": sim["date"].iloc[-1].strftime("%Y-%m"),
        "total_invested": sim["total_invested"].iloc[-1],
        "final_value": sim["portfolio_value"].iloc[-1],
        "total_return": total_return(sim),
        "total_return_pct": round(total_return_pct(sim), 2),
        "cagr_pct": round(cagr(sim), 2),
        "max_drawdown_pct": round(max_drawdown(sim), 2),
        "sharpe_ratio": round(sharpe_ratio(sim), 2),
    }


def rolling_summary(windows: list[pd.DataFrame], label: str) -> pd.DataFrame:
    """Summarize all rolling windows into a DataFrame."""
    summaries = [summarize(w, label) for w in windows]
    return pd.DataFrame(summaries)
