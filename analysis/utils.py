"""
utils.py — Shared helpers: metrics, LaTeX table builders, figure styling.
"""
import numpy as np
import pandas as pd
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from scipy.stats import spearmanr
import matplotlib.pyplot as plt


# ── Metrics ───────────────────────────────────────────────────────────────────

def compute_metrics(y_true, y_pred):
    """Return dict of R², RMSE, MAE, Spearman ρ."""
    r2   = r2_score(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae  = mean_absolute_error(y_true, y_pred)
    rho, pval = spearmanr(y_true, y_pred)
    return {"r2": r2, "rmse": rmse, "mae": mae, "spearman": rho, "spearman_p": pval}


def metrics_to_str(metrics, model_name):
    """Return a one-paragraph LaTeX string summarising test-set performance."""
    return (
        f"The {model_name} model achieves an out-of-sample $R^2$ of "
        f"{metrics['r2']:.4f} on the test set (January 2022 -- October 2024), "
        f"with RMSE of {metrics['rmse']:.4f}, MAE of {metrics['mae']:.4f}, "
        f"and Spearman rank correlation of {metrics['spearman']:.4f} "
        f"($p$-value {metrics['spearman_p']:.4f})."
    )


# ── Array helpers ─────────────────────────────────────────────────────────────

def get_XY(df, features, target):
    """Return (X ndarray, y ndarray) from a DataFrame."""
    return df[features].values, df[target].values


# ── LaTeX table builder ───────────────────────────────────────────────────────

def build_longtable(rows, caption, col_specs=None, label=None):
    """
    Build a LaTeX longtable from a list of dicts.

    Parameters
    ----------
    rows : list[dict]
        Each dict is one table row; keys become column headers on first call.
    caption : str
    col_specs : str, optional
        LaTeX column specification string, e.g. 'lrrrrrrrrr'.
        Defaults to one 'l' + (n-1) 'r' columns.
    label : str, optional
        \\label{} value for cross-referencing.
    """
    if not rows:
        return ""
    headers = list(rows[0].keys())
    n = len(headers)
    if col_specs is None:
        col_specs = "l" + "r" * (n - 1)

    label_str = f"\\label{{{label}}}" if label else ""
    lines = [
        f"\\begin{{longtable}}[]{{{{{col_specs}}}}}",
        f"\\caption{{{caption}}}{label_str}\\tabularnewline",
        "\\toprule()",
        " & ".join(f"\\textbf{{{h}}}" for h in headers) + " \\\\",
        "\\midrule()",
        "\\endfirsthead",
        "\\toprule()",
        " & ".join(f"\\textbf{{{h}}}" for h in headers) + " \\\\",
        "\\midrule()",
        "\\endhead",
    ]
    for row in rows:
        lines.append(" & ".join(str(row[h]) for h in headers) + " \\\\")
    lines += ["\\bottomrule()", "\\end{longtable}"]
    return "\n".join(lines)


# ── Figure styling ────────────────────────────────────────────────────────────

def set_style():
    """Apply a clean, publication-ready matplotlib style."""
    plt.rcParams.update({
        "figure.dpi": 150,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.grid": True,
        "grid.alpha": 0.3,
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
    })


def save_fig(path, tight=True):
    """Save current figure and close it."""
    import os
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if tight:
        plt.tight_layout()
    plt.savefig(path, bbox_inches="tight")
    plt.close()
