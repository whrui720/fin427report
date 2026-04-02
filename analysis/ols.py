"""
ols.py — Section 6: Ordinary Least Squares regression.
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

from .config import FEATURES, TARGET, FEATURE_LABELS, MEDIA_DIR
from .utils import compute_metrics, metrics_to_str, get_XY, build_longtable, set_style, save_fig


def run_ols(train, val, test):
    """
    Fit OLS on train + val combined (no hyperparameters to tune).
    Evaluate on test set.

    Returns
    -------
    model        : fitted LinearRegression
    metrics      : dict with r2, rmse, mae, spearman
    coef_df      : DataFrame of feature / coefficient / std_coef
    latex_block  : str  — ready to paste into the LaTeX report
    """
    X_fit = pd.concat([train, val])[FEATURES].values
    y_fit = pd.concat([train, val])[TARGET].values
    X_test, y_test = get_XY(test, FEATURES, TARGET)

    model = LinearRegression()
    model.fit(X_fit, y_fit)
    y_pred = model.predict(X_test)
    metrics = compute_metrics(y_test, y_pred)

    # Standardised coefficients for interpretable comparison
    scaler = StandardScaler()
    scaler.fit(X_fit)
    std_coefs = model.coef_ * scaler.scale_

    coef_df = pd.DataFrame({
        "Feature":    FEATURES,
        "Label":      [FEATURE_LABELS.get(f, f) for f in FEATURES],
        "Coefficient": model.coef_,
        "Std Coef":   std_coefs,
    }).sort_values("Std Coef", key=abs, ascending=False).reset_index(drop=True)

    _plot_coefficients(coef_df)

    latex_block = _build_latex_block(metrics, coef_df)
    return model, metrics, coef_df, latex_block


def predict(model, df, scaler=None):
    """Return predictions for a DataFrame (scaler unused for OLS)."""
    return model.predict(df[FEATURES].values)


# ── Internals ─────────────────────────────────────────────────────────────────

def _plot_coefficients(coef_df):
    """Save fig_ols_coefficients.png — horizontal bar chart of std. coefficients."""
    set_style()
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ["steelblue" if v >= 0 else "crimson" for v in coef_df["Std Coef"]]
    ax.barh(coef_df["Label"], coef_df["Std Coef"], color=colors, edgecolor="white")
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Standardised Coefficient")
    ax.set_title("OLS — Standardised Coefficients (sorted by |coef|)")
    ax.invert_yaxis()
    save_fig(os.path.join(MEDIA_DIR, "fig_ols_coefficients.png"))
    print("  Saved fig_ols_coefficients.png")


def _build_latex_block(metrics, coef_df) -> str:
    rows = [
        {"Feature": row["Label"], "Coefficient": f"{row['Coefficient']:.6f}",
         "Std Coef": f"{row['Std Coef']:.6f}"}
        for _, row in coef_df.iterrows()
    ]
    table = build_longtable(
        rows,
        caption="Table . OLS coefficient estimates (sorted by $|$standardised coef$|$)",
        label="tab:ols_coefs",
    )
    perf = metrics_to_str(metrics, "OLS")
    return rf"""
{perf}

{table}

\begin{{figure}}[htbp]
\centering
\includegraphics[width=0.80\linewidth]{{media/media/fig_ols_coefficients.png}}
\caption{{OLS standardised coefficient estimates. Blue bars indicate a positive
relationship with industry-adjusted returns; red bars indicate a negative
relationship. Sorted by absolute magnitude.}}
\end{{figure}}
"""
