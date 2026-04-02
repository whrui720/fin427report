"""
predictions.py — Section 12: November 2024 predictions and reconciliation table.

Generates:
  - results_df : DataFrame with predicted indadjret and rank per model for 38 stocks
  - LaTeX reconciliation table (matching the template's Panel A / Panel B format)
  - fig_sector_predictions.png
  - fig_metrics_comparison.png
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from .config import FEATURES, TARGET, MEDIA_DIR
from .utils import set_style, save_fig
from . import ols as _ols
from . import lasso as _lasso
from . import tree as _tree
from . import random_forest as _rf
from . import gradient_boosting as _gb
from . import neural_net as _nn


MODEL_COLS = ["OLS", "LASSO", "Vanilla", "Random Forest", "Gradient Boosting", "Neural Network"]


def build_predictions(pred_sector, fitted_models: dict) -> pd.DataFrame:
    """
    Apply each model to pred_sector and rank all 38 stocks.

    fitted_models keys: 'ols', 'lasso', 'tree', 'rf', 'xgb', 'nn'
    Each value is a dict with 'model' and optionally 'scaler'.

    Returns a DataFrame with columns:
      issuernm, ticker, {m}_pred, {m}_rank  for m in model keys
    """
    results = pred_sector[["issuernm", "ticker", "permno"]].copy()

    preds = {
        "ols":   _ols.predict(fitted_models["ols"]["model"], pred_sector),
        "lasso": _lasso.predict(fitted_models["lasso"]["model"],
                                fitted_models["lasso"]["scaler"], pred_sector),
        "tree":  _tree.predict(fitted_models["tree"]["model"], pred_sector),
        "rf":    _rf.predict(fitted_models["rf"]["model"], pred_sector),
        "xgb":  _gb.predict(fitted_models["xgb"]["model"], pred_sector),
        "nn":   _nn.predict(fitted_models["nn"]["model"],
                             fitted_models["nn"]["scaler"], pred_sector),
    }

    for key, pred_arr in preds.items():
        results[f"{key}_pred"] = pred_arr
        # Rank 1 = highest predicted return = top BUY recommendation
        results[f"{key}_rank"] = results[f"{key}_pred"].rank(
            ascending=False, method="min"
        ).astype(int)

    # Average rank across all models (lower = more consistently recommended)
    rank_cols = [f"{k}_rank" for k in preds]
    results["avg_rank"] = results[rank_cols].mean(axis=1)
    results = results.sort_values("avg_rank").reset_index(drop=True)

    return results


def plot_sector_predictions(results: pd.DataFrame):
    """Save fig_sector_predictions.png — bar chart of stocks by avg rank score."""
    set_style()
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = [
        "crimson" if r <= 3 else ("darkorange" if r <= 10 else "steelblue")
        for r in results["avg_rank"]
    ]
    ax.barh(results["ticker"], results["avg_rank"],
            color=colors, edgecolor="white")
    ax.axvline(10.5, color="black", linewidth=0.8, linestyle="--",
               label="Top 10 cutoff")
    ax.set_xlabel("Average Rank Across 6 Models (lower = better)")
    ax.set_title(
        "November 2024 Stock Rankings — Household \\& Personal Products\\n"
        "(crimson = top 3, orange = top 10)"
    )
    ax.invert_yaxis()
    ax.legend(fontsize=9)
    save_fig(os.path.join(MEDIA_DIR, "fig_sector_predictions.png"))
    print("  Saved fig_sector_predictions.png")


def plot_metrics_comparison(all_metrics: dict):
    """
    Save fig_metrics_comparison.png — test-set R² and RMSE for all 6 models.

    all_metrics: {'ols': {...}, 'lasso': {...}, ...}
    """
    set_style()
    labels = list(all_metrics.keys())
    r2s    = [all_metrics[m]["r2"]   for m in labels]
    rmses  = [all_metrics[m]["rmse"] for m in labels]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))

    ax1.bar(labels, r2s, color="steelblue", edgecolor="white")
    ax1.set_ylabel("Out-of-Sample $R^2$")
    ax1.set_title("Test-Set $R^2$ by Model")
    ax1.tick_params(axis="x", rotation=30)

    ax2.bar(labels, rmses, color="darkorange", edgecolor="white")
    ax2.set_ylabel("RMSE")
    ax2.set_title("Test-Set RMSE by Model")
    ax2.tick_params(axis="x", rotation=30)

    save_fig(os.path.join(MEDIA_DIR, "fig_metrics_comparison.png"))
    print("  Saved fig_metrics_comparison.png")


def build_reconciliation_latex(results: pd.DataFrame, top_n: int = 10) -> str:
    """
    Build the LaTeX content to fill the reconciliation longtable in the template.
    Returns a string with Panel A rows (stock tickers) and Panel B rows
    (predicted returns as %).

    The template table has 6 model columns:
    OLS | LASSO | Vanilla | Random Forest | Gradient Boosting | Neural Network
    """
    model_keys  = ["ols", "lasso", "tree", "rf", "xgb", "nn"]

    # For each model, get stocks ranked 1..top_n
    ranked = {}
    for key in model_keys:
        ranked[key] = (
            results.sort_values(f"{key}_rank")
            .head(top_n)[["ticker", f"{key}_pred"]]
            .reset_index(drop=True)
        )

    panel_a_rows = []
    panel_b_rows = []
    for i in range(top_n):
        rank = i + 1
        tickers  = [ranked[k].loc[i, "ticker"]      for k in model_keys]
        ret_pcts = [ranked[k].loc[i, f"{k}_pred"] * 100 for k in model_keys]

        panel_a_rows.append(
            f"{rank} & " + " & ".join(tickers) + r" \\"
        )
        panel_b_rows.append(
            f"{rank} & " + " & ".join(f"{r:.2f}" for r in ret_pcts) + r" \\"
        )

    panel_a = "\n".join(panel_a_rows)
    panel_b = "\n".join(panel_b_rows)
    return panel_a, panel_b


def reconciliation_text(results: pd.DataFrame, all_metrics: dict) -> str:
    """Return a LaTeX paragraph summarising the reconciliation."""
    top_ticker = results.iloc[0]["ticker"]
    top_name   = results.iloc[0]["issuernm"]

    # Count how many models rank this stock in top 3
    model_keys = ["ols", "lasso", "tree", "rf", "xgb", "nn"]
    top3_count = sum(
        1 for k in model_keys
        if results.iloc[0][f"{k}_rank"] <= 3
    )

    metrics_summary = " | ".join(
        f"{m.upper()}: $R^2={v['r2']:.3f}$"
        for m, v in all_metrics.items()
    )

    return rf"""
Table~\ref{{tab:reconciliation}} presents the top-10 predicted
industry-adjusted return rankings for November 2024 across all six
estimation methods. Panel A reports the stock ticker at each rank;
Panel B reports the corresponding predicted industry-adjusted return
expressed as a percentage.

Test-set performance varies across methods: {metrics_summary}.
Despite this variation, the rankings show meaningful consistency for
the top-ranked stocks. \textbf{{{top_ticker} ({top_name})}}
appears in the top 3 under {top3_count} of 6 models and is our
recommended buy for November 2024.

\begin{{figure}}[htbp]
\centering
\includegraphics[width=0.90\linewidth]{{media/media/fig_sector_predictions.png}}
\caption{{Average rank across six models for all 38 Household \& Personal
Products stocks in November 2024. Lower average rank indicates a more
consistent buy recommendation. Crimson bars denote the top-3 consensus picks.}}
\end{{figure}}

\begin{{figure}}[htbp]
\centering
\includegraphics[width=0.90\linewidth]{{media/media/fig_metrics_comparison.png}}
\caption{{Out-of-sample $R^2$ and RMSE for each model evaluated on the
test set (January 2022 -- October 2024).}}
\end{{figure}}
"""
