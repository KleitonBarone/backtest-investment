"""
DCA Investment Backtest Comparison

Compares Dollar Cost Averaging across multiple asset classes:
  - SPY (S&P 500 equities)
  - AGG (Aggregate bonds)
  - SHY (Short-term Treasury 1-3yr)
  - TIP (Treasury Inflation-Protected Securities)
  - BIL (T-Bills, cash equivalent)

$1,000 monthly contributions, 10-year horizon.
"""

from src.data import get_all_prices
from src.simulator import simulate_dca, run_rolling_windows
from src.analysis import summarize, rolling_summary
from src.visualize import (
    plot_growth_comparison,
    plot_rolling_returns,
    plot_rolling_final_values,
    print_comparison_table,
)

MONTHLY_CONTRIBUTION = 1000.0
WINDOW_MONTHS = 120  # 10 years


def main():
    print("Downloading price data...")
    all_prices = get_all_prices()

    for label, prices in all_prices.items():
        print(f"  {label:<25} {prices.index[0].strftime('%Y-%m')} to {prices.index[-1].strftime('%Y-%m')} ({len(prices)} months)")

    # --- Most recent 10-year window ---
    print("\n=== Most Recent 10-Year Window ===")
    simulations = {}
    summaries = {}

    for label, prices in all_prices.items():
        if len(prices) < WINDOW_MONTHS:
            print(f"  Skipping {label}: only {len(prices)} months (need {WINDOW_MONTHS})")
            continue
        sim = simulate_dca(prices.iloc[-WINDOW_MONTHS:], MONTHLY_CONTRIBUTION, WINDOW_MONTHS)
        simulations[label] = sim
        summaries[label] = summarize(sim, label)

    print_comparison_table(summaries)
    plot_growth_comparison(simulations)

    # --- Rolling 10-year windows ---
    print("Running rolling 10-year window analysis...")
    all_rolling = {}

    for label, prices in all_prices.items():
        if len(prices) < WINDOW_MONTHS:
            continue
        windows = run_rolling_windows(prices, MONTHLY_CONTRIBUTION, WINDOW_MONTHS)
        all_rolling[label] = rolling_summary(windows, label)
        print(f"  {label:<25} {len(all_rolling[label])} windows")

    # Align to common date range for fair comparison
    common_starts = None
    for df in all_rolling.values():
        starts = set(df["start_date"])
        common_starts = starts if common_starts is None else common_starts & starts

    aligned_rolling = {}
    for label, df in all_rolling.items():
        aligned_rolling[label] = df[df["start_date"].isin(common_starts)].reset_index(drop=True)

    print(f"\n  Common rolling windows: {len(common_starts) if common_starts else 0}")

    if common_starts:
        plot_rolling_returns(aligned_rolling)
        plot_rolling_final_values(aligned_rolling)

        print("\n=== Rolling 10-Year Window Statistics ===")
        for label, df in aligned_rolling.items():
            print(f"\n  {label}:")
            print(f"    Avg return:    {df['total_return_pct'].mean():.1f}%")
            print(f"    Best return:   {df['total_return_pct'].max():.1f}% (started {df.loc[df['total_return_pct'].idxmax(), 'start_date']})")
            print(f"    Worst return:  {df['total_return_pct'].min():.1f}% (started {df.loc[df['total_return_pct'].idxmin(), 'start_date']})")
            print(f"    Avg final val: ${df['final_value'].mean():,.0f}")

    print("\nDone! Check the output/ folder for charts.")


if __name__ == "__main__":
    main()
