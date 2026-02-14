import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")


def _ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def plot_growth_comparison(
    simulations: dict[str, pd.DataFrame],
    filename: str = "growth_comparison.png",
):
    """Plot portfolio value over time for all strategies."""
    _ensure_output_dir()
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(14, 7))

    first_sim = next(iter(simulations.values()))
    ax.plot(first_sim["date"], first_sim["total_invested"],
            label="Total Invested", linewidth=1.5, linestyle="--", color="gray")

    for label, sim in simulations.items():
        ax.plot(sim["date"], sim["portfolio_value"], label=label, linewidth=2)

    ax.set_title("Portfolio Growth: DCA Comparison (10 Years)", fontsize=14)
    ax.set_xlabel("Date")
    ax.set_ylabel("Portfolio Value ($)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.legend(loc="upper left")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=150)
    plt.close()
    print(f"Saved: {filename}")


def plot_rolling_returns(
    rolling_data: dict[str, pd.DataFrame],
    filename: str = "rolling_returns.png",
):
    """Plot rolling 10-year total return % for all strategies."""
    _ensure_output_dir()
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(14, 7))

    for label, df in rolling_data.items():
        ax.plot(
            pd.to_datetime(df["start_date"]),
            df["total_return_pct"],
            label=label,
            linewidth=2,
        )

    ax.set_title("Rolling 10-Year DCA Returns by Start Date", fontsize=14)
    ax.set_xlabel("Start Date")
    ax.set_ylabel("Total Return (%)")
    ax.axhline(y=0, color="red", linestyle="--", alpha=0.5)
    ax.legend(loc="upper left")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=150)
    plt.close()
    print(f"Saved: {filename}")


def print_comparison_table(summaries: dict[str, dict]):
    """Print a side-by-side comparison table for all strategies."""
    labels = list(summaries.keys())
    col_width = 20
    label_width = 25

    header = f"{'Metric':<{label_width}}" + "".join(f"{l:>{col_width}}" for l in labels)
    separator = "-" * len(header)

    metrics = [
        ("Period", lambda s: s["start_date"] + " to " + s["end_date"]),
        ("Total Invested", lambda s: f"${s['total_invested']:,.0f}"),
        ("Final Value", lambda s: f"${s['final_value']:,.0f}"),
        ("Total Return", lambda s: f"${s['total_return']:,.0f}"),
        ("Total Return %", lambda s: f"{s['total_return_pct']:.2f}%"),
        ("CAGR (approx)", lambda s: f"{s['cagr_pct']:.2f}%"),
        ("Max Drawdown", lambda s: f"{s['max_drawdown_pct']:.2f}%"),
        ("Sharpe Ratio", lambda s: f"{s['sharpe_ratio']:.2f}"),
    ]

    print("\n" + separator)
    print(header)
    print(separator)
    for metric_name, fmt in metrics:
        row = f"{metric_name:<{label_width}}"
        for label in labels:
            row += f"{fmt(summaries[label]):>{col_width}}"
        print(row)
    print(separator + "\n")


def plot_rolling_final_values(
    rolling_data: dict[str, pd.DataFrame],
    filename: str = "rolling_final_values.png",
):
    """Box plot of final portfolio values across all rolling windows."""
    _ensure_output_dir()
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(10, 6))

    data = pd.DataFrame({
        label: df["final_value"].values
        for label, df in rolling_data.items()
    })

    sns.boxplot(data=data, ax=ax, palette="Set2")
    ax.set_title("Distribution of Final Portfolio Values (Rolling 10-Year Windows)", fontsize=13)
    ax.set_ylabel("Final Portfolio Value ($)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=150)
    plt.close()
    print(f"Saved: {filename}")
