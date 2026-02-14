"""
DCA BOVA11 vs 100% CDI: 10-Year Brazilian Investment Backtest

Compares Dollar Cost Averaging into BOVA11 (Ibovespa ETF)
vs investing at 100% CDI (renda fixa benchmark).
R$1,000 monthly contributions, 10-year horizon.
"""

from src.data_brazil import get_bova11_prices, get_divo11_prices, get_ivvb11_prices, get_gold11_prices, get_btc_brl_prices, get_cdi_monthly_factors, simulate_cdi
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


def run_cdi_rolling_windows(monthly_factors, monthly_contribution, window_months):
    """Run CDI simulation for every possible rolling window."""
    results = []
    max_start = len(monthly_factors) - window_months

    for start in range(max_start + 1):
        window = monthly_factors.iloc[start : start + window_months].reset_index(drop=True)
        sim = simulate_cdi(window, monthly_contribution, window_months)
        results.append(sim)

    return results


def main():
    print("Downloading Brazilian price data...")
    bova11_prices = get_bova11_prices()
    divo11_prices = get_divo11_prices()
    ivvb11_prices = get_ivvb11_prices()
    gold11_prices = get_gold11_prices()
    btc_brl_prices = get_btc_brl_prices()
    cdi_factors = get_cdi_monthly_factors()

    equity_data = {
        "DCA BOVA11": bova11_prices,
        "DCA DIVO11": divo11_prices,
        "DCA IVVB11": ivvb11_prices,
        "DCA GOLD11": gold11_prices,
        "DCA BTC (BRL)": btc_brl_prices,
    }

    for label, prices in equity_data.items():
        print(f"  {label:<15} {prices.index[0].strftime('%Y-%m')} to {prices.index[-1].strftime('%Y-%m')} ({len(prices)} months)")
    print(f"  {'CDI':<15} {cdi_factors['month'].iloc[0]} to {cdi_factors['month'].iloc[-1]} ({len(cdi_factors)} months)")

    # --- Most recent 10-year window ---
    print("\n=== Most Recent 10-Year Window ===")

    simulations = {}
    summaries = {}
    skipped_10y = []

    for label, prices in equity_data.items():
        if len(prices) < WINDOW_MONTHS:
            print(f"  Skipping {label}: only {len(prices)} months (need {WINDOW_MONTHS})")
            skipped_10y.append(label)
            continue
        sim = simulate_dca(prices.iloc[-WINDOW_MONTHS:], MONTHLY_CONTRIBUTION, WINDOW_MONTHS)
        simulations[label] = sim
        summaries[label] = summarize(sim, label)

    cdi_sim = simulate_cdi(
        cdi_factors.tail(WINDOW_MONTHS).reset_index(drop=True),
        MONTHLY_CONTRIBUTION,
        WINDOW_MONTHS,
    )
    simulations["100% CDI"] = cdi_sim
    summaries["100% CDI"] = summarize(cdi_sim, "100% CDI")

    print_comparison_table(summaries)
    plot_growth_comparison(simulations, filename="brazil_growth_comparison.png")

    # --- Shorter window including all assets ---
    if skipped_10y:
        min_months = min(len(p) for p in equity_data.values())
        short_window = min_months - 1  # leave 1 month margin
        short_years = short_window / 12

        print(f"\n=== All Assets Comparison ({short_years:.1f} Years / {short_window} Months) ===")

        short_sims = {}
        short_summaries = {}

        for label, prices in equity_data.items():
            sim = simulate_dca(prices.iloc[-short_window:], MONTHLY_CONTRIBUTION, short_window)
            short_sims[label] = sim
            short_summaries[label] = summarize(sim, label)

        cdi_short = simulate_cdi(
            cdi_factors.tail(short_window).reset_index(drop=True),
            MONTHLY_CONTRIBUTION,
            short_window,
        )
        short_sims["100% CDI"] = cdi_short
        short_summaries["100% CDI"] = summarize(cdi_short, "100% CDI")

        print_comparison_table(short_summaries)
        plot_growth_comparison(short_sims, filename="brazil_growth_all_assets.png")

    # --- Rolling 10-year windows ---
    print("Running rolling 10-year window analysis...")

    all_rolling = {}
    for label, prices in equity_data.items():
        if len(prices) < WINDOW_MONTHS:
            continue
        windows = run_rolling_windows(prices, MONTHLY_CONTRIBUTION, WINDOW_MONTHS)
        all_rolling[label] = rolling_summary(windows, label)
        print(f"  {label:<15} {len(all_rolling[label])} windows")

    cdi_windows = run_cdi_rolling_windows(cdi_factors, MONTHLY_CONTRIBUTION, WINDOW_MONTHS)
    all_rolling["100% CDI"] = rolling_summary(cdi_windows, "100% CDI")
    print(f"  {'100% CDI':<15} {len(all_rolling['100% CDI'])} windows")

    # Align to common date range
    common_starts = None
    for df in all_rolling.values():
        starts = set(df["start_date"])
        common_starts = starts if common_starts is None else common_starts & starts

    aligned_rolling = {}
    for label, df in all_rolling.items():
        aligned_rolling[label] = df[df["start_date"].isin(common_starts)].reset_index(drop=True)

    print(f"  Common rolling windows: {len(common_starts) if common_starts else 0}")

    if common_starts:
        plot_rolling_returns(aligned_rolling, filename="brazil_rolling_returns.png")
        plot_rolling_final_values(aligned_rolling, filename="brazil_rolling_final_values.png")

        print("\n=== Rolling 10-Year Window Statistics ===")
        for label, df in aligned_rolling.items():
            print(f"\n  {label}:")
            print(f"    Avg return:    {df['total_return_pct'].mean():.1f}%")
            print(f"    Best return:   {df['total_return_pct'].max():.1f}% (started {df.loc[df['total_return_pct'].idxmax(), 'start_date']})")
            print(f"    Worst return:  {df['total_return_pct'].min():.1f}% (started {df.loc[df['total_return_pct'].idxmin(), 'start_date']})")
            print(f"    Avg final val: R${df['final_value'].mean():,.0f}")

    print("\nDone! Check the output/ folder for charts.")


if __name__ == "__main__":
    main()
