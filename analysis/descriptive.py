"""
descriptive.py — Sections 3, 4, 5:
  - Descriptive statistics on the whole sample
  - Variable of interest (finmom12) analysis
  - Train / test / validation split summary
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from .config import (
    FEATURES, TARGET, VOI, MISS_MAP, FEATURE_LABELS, MEDIA_DIR,
    SECTOR, GROUP, TRAIN_END, VAL_END, TEST_END, PRED_MONTH,
)
from .utils import build_longtable, set_style, save_fig


# ── Section 3: Descriptive Statistics on the Whole Sample ────────────────────

def desc_stats_table(hist_df: pd.DataFrame) -> str:
    """
    Build a LaTeX longtable of descriptive statistics for all 15 features
    plus indadjret.  Runs on hist_df (all data excluding Nov 2024).
    Columns: Variable | N | Mean | Std | p1 | p25 | p50 | p75 | p99 | %Miss
    """
    all_vars = FEATURES + [TARGET]
    rows = []
    for col in all_vars:
        label    = FEATURE_LABELS.get(col, col)
        miss_col = MISS_MAP.get(col)
        pct_miss = hist_df[miss_col].mean() * 100 if miss_col else 0.0
        s = hist_df[col].dropna()
        rows.append({
            "Variable": label,
            "N":        f"{len(s):,}",
            "Mean":     f"{s.mean():.4f}",
            "Std":      f"{s.std():.4f}",
            "p1":       f"{s.quantile(0.01):.4f}",
            "p25":      f"{s.quantile(0.25):.4f}",
            "p50":      f"{s.quantile(0.50):.4f}",
            "p75":      f"{s.quantile(0.75):.4f}",
            "p99":      f"{s.quantile(0.99):.4f}",
            r"\%Miss":  f"{pct_miss:.1f}",
        })
    return build_longtable(
        rows,
        caption=r"Table . Descriptive statistics on the whole sample",
        label="tab:desc_stats",
    )


def plot_correlation_heatmap(train: pd.DataFrame):
    """
    Save fig_desc_stats.png — Spearman correlation heatmap of 15 features
    computed on the training set only (no look-ahead).
    """
    set_style()
    corr = train[FEATURES].corr(method="spearman")
    labels = [FEATURE_LABELS.get(f, f) for f in FEATURES]

    fig, ax = plt.subplots(figsize=(11, 9))
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    sns.heatmap(
        corr,
        mask=mask,
        annot=True,
        fmt=".2f",
        cmap="RdBu_r",
        center=0,
        linewidths=0.4,
        ax=ax,
        xticklabels=labels,
        yticklabels=labels,
        annot_kws={"size": 7},
        vmin=-1, vmax=1,
    )
    ax.set_title("Spearman Correlation Matrix of Predictors (Training Set)", pad=12)
    plt.xticks(rotation=45, ha="right", fontsize=8)
    plt.yticks(rotation=0, fontsize=8)
    save_fig(os.path.join(MEDIA_DIR, "fig_desc_stats.png"))
    print("  Saved fig_desc_stats.png")


# ── Section 4: Variable of Interest (finnpm) ─────────────────────────────────

def voi_desc_table(hist_df: pd.DataFrame) -> str:
    """Single-variable descriptive stats table for finnpm."""
    s = hist_df[VOI].dropna()
    miss_col = MISS_MAP[VOI]
    pct_miss = hist_df[miss_col].mean() * 100
    rows = [{
        "Variable":  FEATURE_LABELS[VOI],
        "N":         f"{len(s):,}",
        "Mean":      f"{s.mean():.4f}",
        "Std":       f"{s.std():.4f}",
        "p1":        f"{s.quantile(0.01):.4f}",
        "p5":        f"{s.quantile(0.05):.4f}",
        "p25":       f"{s.quantile(0.25):.4f}",
        "p50":       f"{s.quantile(0.50):.4f}",
        "p75":       f"{s.quantile(0.75):.4f}",
        "p95":       f"{s.quantile(0.95):.4f}",
        "p99":       f"{s.quantile(0.99):.4f}",
        r"\%Miss":   f"{pct_miss:.1f}",
    }]
    return build_longtable(
        rows,
        caption=r"Table . Descriptive statistics for Net Profit Margin (variable of interest)",
        label="tab:voi_stats",
    )


def plot_voi_distribution(hist_df: pd.DataFrame):
    """
    Save fig_voi_distribution.png — histogram + KDE of finnpm
    for sector 30/3030 stocks only.
    """
    set_style()
    sector_data = hist_df[
        (hist_df["gsector"] == SECTOR) & (hist_df["ggroup"] == GROUP)
    ][VOI].dropna()

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(sector_data, bins=60, density=True, alpha=0.55,
            color="steelblue", edgecolor="white", linewidth=0.3)
    sector_data.plot.kde(ax=ax, color="navy", linewidth=2)
    ax.set_xlabel(FEATURE_LABELS[VOI])
    ax.set_ylabel("Density")
    ax.set_title(
        "Distribution of Net Profit Margin — "
        "Household \\& Personal Products Sector"
    )
    save_fig(os.path.join(MEDIA_DIR, "fig_voi_distribution.png"))
    print("  Saved fig_voi_distribution.png")


def plot_voi_return_scatter(train: pd.DataFrame):
    """
    Save fig_voi_return_scatter.png — mean indadjret by decile of finmom12
    for sector 30/3030 in the training set.  Demonstrates the positive
    monotonic relationship between momentum and future returns.
    """
    set_style()
    sub = train[
        (train["gsector"] == SECTOR) & (train["ggroup"] == GROUP)
    ][[VOI, TARGET]].dropna()

    sub["decile"] = pd.qcut(sub[VOI], q=10, labels=False, duplicates="drop") + 1
    means = sub.groupby("decile")[TARGET].mean() * 100  # as %

    fig, ax = plt.subplots(figsize=(8, 4))
    means.plot(kind="bar", ax=ax, color="steelblue", edgecolor="white")
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_xlabel("Net Profit Margin Decile (1 = lowest, 10 = highest)")
    ax.set_ylabel("Mean Industry-Adjusted Return (\\%)")
    ax.set_title(
        "Mean Industry-Adjusted Return by Net Profit Margin Decile\\n"
        "(Training Set, Household \\& Personal Products)"
    )
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    save_fig(os.path.join(MEDIA_DIR, "fig_voi_return_scatter.png"))
    print("  Saved fig_voi_return_scatter.png")


def voi_latex_block(hist_df: pd.DataFrame, train: pd.DataFrame) -> str:
    """Return a complete LaTeX block for the VOI section."""
    table = voi_desc_table(hist_df)
    plot_voi_distribution(hist_df)
    plot_voi_return_scatter(train)
    text = r"""
We select \textbf{net profit margin} (\texttt{finnpm}) as our variable of
interest. Net profit margin (net income divided by sales) is a fundamental
profitability measure that captures how efficiently a firm converts revenue
into earnings. In the Household and Personal Products sector, where firms
compete on brand equity and operational efficiency, sustained profit margins
signal durable competitive advantages that may be rewarded by the market.

The variable is winsorized at the 1\textsuperscript{st} and
99\textsuperscript{th} percentiles (constraint 1.00), which preserves large
profitability signals while eliminating extreme data errors.
Descriptive statistics for the full sample (excluding November 2024) are
presented in the table below. Figure~2 shows the distribution of
\texttt{finnpm} within our sector, and Figure~3 shows the relationship
between net profit margin decile and mean industry-adjusted return in the
training set.

"""
    return text + "\n\n" + table + r"""

\begin{figure}[htbp]
\centering
\includegraphics[width=0.80\linewidth]{media/media/fig_voi_distribution.png}
\caption{Distribution of net profit margin (\texttt{finnpm}) for
Household \& Personal Products stocks (sector 30, group 3030).}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.80\linewidth]{media/media/fig_voi_return_scatter.png}
\caption{Mean industry-adjusted return by decile of net profit margin,
training set (January 2001 -- December 2018), Household \& Personal Products sector.}
\end{figure}
"""


# ── Section 5: Split Description ─────────────────────────────────────────────

def splits_latex_block(train, val, test, pred_sector) -> str:
    """Return LaTeX table + figure for the train/test/validation section."""
    _plot_split_timeline()

    rows = [
        {
            "Split":   "Training",
            "Start":   "January 2001",
            "End":     "December 2018",
            "N Rows":  f"{len(train):,}",
            "N Stocks": str(train["permno"].nunique()),
            "N Months": str(train["month"].nunique()),
        },
        {
            "Split":   "Validation",
            "Start":   "January 2019",
            "End":     "December 2021",
            "N Rows":  f"{len(val):,}",
            "N Stocks": str(val["permno"].nunique()),
            "N Months": str(val["month"].nunique()),
        },
        {
            "Split":   "Test",
            "Start":   "January 2022",
            "End":     "October 2024",
            "N Rows":  f"{len(test):,}",
            "N Stocks": str(test["permno"].nunique()),
            "N Months": str(test["month"].nunique()),
        },
        {
            "Split":   "Prediction",
            "Start":   "November 2024",
            "End":     "November 2024",
            "N Rows":  str(len(pred_sector)),
            "N Stocks": str(pred_sector["permno"].nunique()),
            "N Months": "1",
        },
    ]
    table = build_longtable(rows, caption="Table . Data splits", label="tab:splits")

    text = r"""
We partition the data chronologically to prevent look-ahead bias. All models
are trained on the full cross-sectional universe (all GICS sectors) to maximise
the number of observations available for learning the relationship between stock
characteristics and industry-adjusted returns; predictions are then restricted
to the 38 Household and Personal Products stocks present in November 2024.

\begin{itemize}
  \item \textbf{Training set (January 2001 -- December 2018):} Used to fit
    all model parameters. The 18-year window captures multiple full business
    cycles including the dot-com bust, the 2008 financial crisis, and the
    subsequent recovery.
  \item \textbf{Validation set (January 2019 -- December 2021):} Used for
    hyperparameter selection (LASSO penalty, tree depth, forest grid, XGBoost
    early stopping). This window includes the COVID-19 shock of 2020, testing
    model robustness to structural breaks.
  \item \textbf{Test set (January 2022 -- October 2024):} Used for final
    out-of-sample performance reporting ($R^2$, RMSE, Spearman $\rho$).
    Models are refit on training + validation combined before test evaluation.
  \item \textbf{Prediction month (November 2024):} Features are observed as
    of October 31, 2024 (the portfolio formation date). The \texttt{indadjret}
    for November 2024 is \emph{never} used during modelling; it serves only
    for ex-post verification of the recommendation.
\end{itemize}

"""
    figure = r"""
\begin{figure}[htbp]
\centering
\includegraphics[width=0.85\linewidth]{media/media/fig_train_test_timeline.png}
\caption{Chronological data splits. Models are trained on the full
cross-sectional universe; the prediction is restricted to 38 Household
\& Personal Products stocks in November 2024.}
\end{figure}
"""
    return text + "\n\n" + table + "\n\n" + figure


def _plot_split_timeline():
    """Save fig_train_test_timeline.png — horizontal bar chart of splits."""
    set_style()
    import matplotlib.dates as mdates
    from datetime import date

    segments = [
        ("Training",   date(2001, 1, 1),  date(2018, 12, 31), "steelblue"),
        ("Validation", date(2019, 1, 1),  date(2021, 12, 31), "darkorange"),
        ("Test",       date(2022, 1, 1),  date(2024, 10, 31), "seagreen"),
        ("Prediction", date(2024, 11, 1), date(2024, 11, 30), "crimson"),
    ]

    fig, ax = plt.subplots(figsize=(10, 3))
    for i, (label, start, end, color) in enumerate(segments):
        ax.barh(
            y=0,
            width=(end - start).days,
            left=(start - date(2001, 1, 1)).days,
            height=0.5,
            color=color,
            alpha=0.85,
            label=label,
        )
        mid = (start - date(2001, 1, 1)).days + (end - start).days / 2
        ax.text(mid, 0, label, ha="center", va="center", color="white",
                fontsize=9, fontweight="bold")

    # Convert x-axis from days-since-2001 to year labels
    year_ticks = [date(y, 1, 1) for y in range(2001, 2026, 2)]
    ax.set_xticks([(d - date(2001, 1, 1)).days for d in year_ticks])
    ax.set_xticklabels([str(d.year) for d in year_ticks], rotation=45)
    ax.set_yticks([])
    ax.set_xlabel("Year")
    ax.set_title("Chronological Data Splits")
    save_fig(os.path.join(MEDIA_DIR, "fig_train_test_timeline.png"))
    print("  Saved fig_train_test_timeline.png")
