"""
lasso.py — Section 7: LASSO penalized regression.
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import Lasso, LassoCV, lasso_path
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler

from .config import FEATURES, TARGET, FEATURE_LABELS, MEDIA_DIR
from .utils import compute_metrics, metrics_to_str, get_XY, build_longtable, set_style, save_fig


def run_lasso(train, val, test):
    """
    Tune LASSO alpha via LassoCV + TimeSeriesSplit on training set.
    Refit on train + val at optimal alpha; evaluate on test.

    Returns
    -------
    model        : fitted Lasso
    scaler       : fitted StandardScaler (apply before predicting)
    best_alpha   : float
    metrics      : dict
    latex_block  : str
    """
    X_train, y_train = get_XY(train, FEATURES, TARGET)
    X_val,   y_val   = get_XY(val,   FEATURES, TARGET)
    X_test,  y_test  = get_XY(test,  FEATURES, TARGET)

    # Scale (fit on train only)
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_val_s   = scaler.transform(X_val)
    X_test_s  = scaler.transform(X_test)

    # Tune alpha
    tscv   = TimeSeriesSplit(n_splits=5)
    alphas = np.logspace(-5, 0, 50)
    lasso_cv = LassoCV(alphas=alphas, cv=tscv, max_iter=10_000, n_jobs=-1)
    lasso_cv.fit(X_train_s, y_train)
    best_alpha = lasso_cv.alpha_
    print(f"  LASSO best alpha: {best_alpha:.6f}")

    # Refit on train + val
    X_fit_s = np.vstack([X_train_s, X_val_s])
    y_fit   = np.concatenate([y_train, y_val])
    model = Lasso(alpha=best_alpha, max_iter=10_000)
    model.fit(X_fit_s, y_fit)

    y_pred  = model.predict(X_test_s)
    metrics = compute_metrics(y_test, y_pred)

    n_zero = int(np.sum(model.coef_ == 0))
    print(f"  LASSO zeroed {n_zero}/{len(FEATURES)} coefficients")

    _plot_lasso_path(X_train_s, y_train, best_alpha)

    latex_block = _build_latex_block(metrics, model, best_alpha, n_zero)
    return model, scaler, best_alpha, metrics, latex_block


def predict(model, scaler, df):
    """Return predictions after applying the stored scaler."""
    X = scaler.transform(df[FEATURES].values)
    return model.predict(X)


# ── Internals ─────────────────────────────────────────────────────────────────

def _plot_lasso_path(X_train_s, y_train, best_alpha):
    """Save fig_lasso_path.png — regularization path."""
    set_style()
    alphas_path, coefs_path, _ = lasso_path(
        X_train_s, y_train,
        alphas=np.logspace(-5, 0, 80),
        max_iter=5_000,
    )
    labels = [FEATURE_LABELS.get(f, f) for f in FEATURES]

    fig, ax = plt.subplots(figsize=(9, 5))
    for i, label in enumerate(labels):
        ax.plot(-np.log10(alphas_path), coefs_path[i], linewidth=1.2, label=label)
    ax.axvline(-np.log10(best_alpha), color="black", linewidth=1.5,
               linestyle="--", label=f"Selected α={best_alpha:.2e}")
    ax.set_xlabel(r"$-\log_{10}(\alpha)$  (regularization decreases →)")
    ax.set_ylabel("Coefficient")
    ax.set_title("LASSO Regularization Path")
    ax.legend(fontsize=7, ncol=2, loc="upper left")
    save_fig(os.path.join(MEDIA_DIR, "fig_lasso_path.png"))
    print("  Saved fig_lasso_path.png")


def _build_latex_block(metrics, model, best_alpha, n_zero) -> str:
    rows = [
        {"Feature": FEATURE_LABELS.get(f, f),
         "Coefficient": f"{c:.6f}",
         "Zeroed": "Yes" if c == 0 else "No"}
        for f, c in zip(FEATURES, model.coef_)
    ]
    # Sort: non-zero first
    rows.sort(key=lambda r: r["Zeroed"])
    table = build_longtable(
        rows,
        caption=(
            f"Table . LASSO coefficient estimates "
            f"($\\\\alpha={best_alpha:.2e}$, {n_zero} features zeroed)"
        ),
        label="tab:lasso_coefs",
    )
    perf = metrics_to_str(metrics, "LASSO")
    return rf"""
The optimal regularization parameter selected via \texttt{{LassoCV}} with
5-fold time-series cross-validation is $\alpha = {best_alpha:.2e}$.
At this penalty level, {n_zero} of {len(FEATURES)} predictors are shrunk
exactly to zero, demonstrating the variable-selection property of LASSO.

{perf}

{table}

\begin{{figure}}[htbp]
\centering
\includegraphics[width=0.85\linewidth]{{media/media/fig_lasso_path.png}}
\caption{{LASSO regularization path. Each coloured line shows how a
coefficient evolves as the penalty decreases (right). The dashed vertical
line marks the cross-validation-selected $\alpha$.}}
\end{{figure}}
"""
