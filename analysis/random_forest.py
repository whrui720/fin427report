"""
random_forest.py — Section 9: Random Forest.
"""
import os
import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score

from .config import FEATURES, TARGET, FEATURE_LABELS, MEDIA_DIR
from .utils import compute_metrics, metrics_to_str, get_XY, set_style, save_fig


# Hyperparameter grid (8 combinations)
_GRID = {
    "n_estimators": [100, 200],
    "max_depth":    [5, 10],
    "max_features": ["sqrt", 0.5],
}


def run_random_forest(train, val, test):
    """
    Grid search over 8 hyperparameter combinations using validation R².
    Refit best configuration on train + val; evaluate on test.

    Returns
    -------
    model       : fitted RandomForestRegressor
    best_params : dict
    metrics     : dict
    latex_block : str
    """
    X_train, y_train = get_XY(train, FEATURES, TARGET)
    X_val,   y_val   = get_XY(val,   FEATURES, TARGET)
    X_test,  y_test  = get_XY(test,  FEATURES, TARGET)

    keys   = list(_GRID.keys())
    combos = list(itertools.product(*[_GRID[k] for k in keys]))

    best_params, best_val_r2 = None, -np.inf
    for combo in combos:
        params = dict(zip(keys, combo))
        m = RandomForestRegressor(**params, random_state=42, n_jobs=-1)
        m.fit(X_train, y_train)
        r2 = r2_score(y_val, m.predict(X_val))
        print(f"    RF {params}  val R²={r2:.4f}")
        if r2 > best_val_r2:
            best_val_r2, best_params = r2, params

    print(f"  RF best params: {best_params}  (val R²={best_val_r2:.4f})")

    X_fit = np.vstack([X_train, X_val])
    y_fit = np.concatenate([y_train, y_val])
    model = RandomForestRegressor(**best_params, random_state=42, n_jobs=-1)
    model.fit(X_fit, y_fit)

    y_pred  = model.predict(X_test)
    metrics = compute_metrics(y_test, y_pred)

    _plot_importance(model)

    latex_block = _build_latex_block(metrics, model, best_params, best_val_r2)
    return model, best_params, metrics, latex_block


def predict(model, df, scaler=None):
    return model.predict(df[FEATURES].values)


# ── Internals ─────────────────────────────────────────────────────────────────

def _plot_importance(model):
    """Save fig_rf_importance.png — top-15 feature importances."""
    set_style()
    imp = pd.Series(
        model.feature_importances_,
        index=[FEATURE_LABELS.get(f, f) for f in FEATURES],
    ).sort_values(ascending=True).tail(15)

    fig, ax = plt.subplots(figsize=(7, 5))
    imp.plot(kind="barh", ax=ax, color="steelblue", edgecolor="white")
    ax.set_xlabel("Feature Importance (Mean Decrease Impurity)")
    ax.set_title("Random Forest — Feature Importances (top 15)")
    save_fig(os.path.join(MEDIA_DIR, "fig_rf_importance.png"))
    print("  Saved fig_rf_importance.png")


def _build_latex_block(metrics, model, best_params, best_val_r2) -> str:
    perf = metrics_to_str(metrics, "random forest")
    p = best_params
    return rf"""
Grid search over \{{\texttt{{n\_estimators}} \in \{{100, 200\}},
\texttt{{max\_depth}} \in \{{5, 10\}},
\texttt{{max\_features}} \in \{{\text{{sqrt}}, 0.5\}}\}} (8 combinations)
selects \textbf{{{p['n_estimators']} trees, max depth {p['max_depth']},
max features {p['max_features']}}} (validation $R^2 = {best_val_r2:.4f}$).
The ensemble averages over many decorrelated trees, reducing variance
relative to the single decision tree.

{perf}

\begin{{figure}}[htbp]
\centering
\includegraphics[width=0.80\linewidth]{{media/media/fig_rf_importance.png}}
\caption{{Random forest feature importances (mean decrease in impurity,
top 15 features). Values are normalised to sum to 1 across all features.}}
\end{{figure}}
"""
