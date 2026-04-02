"""
tree.py — Section 8: Vanilla decision tree.
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeRegressor, plot_tree
from sklearn.metrics import r2_score

from .config import FEATURES, TARGET, FEATURE_LABELS, MEDIA_DIR
from .utils import compute_metrics, metrics_to_str, get_XY, set_style, save_fig


def run_tree(train, val, test):
    """
    Tune max_depth via validation R² over {2,3,4,5,6,8,10}.
    Refit on train + val at best depth; evaluate on test.

    Returns
    -------
    model       : fitted DecisionTreeRegressor
    best_depth  : int
    metrics     : dict
    latex_block : str
    """
    X_train, y_train = get_XY(train, FEATURES, TARGET)
    X_val,   y_val   = get_XY(val,   FEATURES, TARGET)
    X_test,  y_test  = get_XY(test,  FEATURES, TARGET)

    best_depth, best_val_r2 = None, -np.inf
    for depth in [2, 3, 4, 5, 6, 8, 10]:
        m = DecisionTreeRegressor(max_depth=depth, random_state=42)
        m.fit(X_train, y_train)
        r2 = r2_score(y_val, m.predict(X_val))
        if r2 > best_val_r2:
            best_val_r2, best_depth = r2, depth

    print(f"  Decision Tree best depth: {best_depth}  (val R²={best_val_r2:.4f})")

    X_fit = np.vstack([X_train, X_val])
    y_fit = np.concatenate([y_train, y_val])
    model = DecisionTreeRegressor(max_depth=best_depth, random_state=42)
    model.fit(X_fit, y_fit)

    y_pred  = model.predict(X_test)
    metrics = compute_metrics(y_test, y_pred)

    _plot_tree_diagram(model, best_depth)
    _plot_importance(model)

    latex_block = _build_latex_block(metrics, model, best_depth, best_val_r2)
    return model, best_depth, metrics, latex_block


def predict(model, df, scaler=None):
    return model.predict(df[FEATURES].values)


# ── Internals ─────────────────────────────────────────────────────────────────

def _plot_tree_diagram(model, best_depth):
    """Save fig_tree_structure.png — tree diagram (visualised at depth ≤ 3)."""
    set_style()
    vis_depth = min(best_depth, 3)
    fig, ax = plt.subplots(figsize=(16, 6))
    plot_tree(
        model,
        max_depth=vis_depth,
        feature_names=[FEATURE_LABELS.get(f, f) for f in FEATURES],
        filled=True,
        rounded=True,
        fontsize=7,
        ax=ax,
        impurity=False,
    )
    ax.set_title(
        f"Decision Tree Structure (best depth={best_depth}, "
        f"visualised at depth≤{vis_depth})"
    )
    save_fig(os.path.join(MEDIA_DIR, "fig_tree_structure.png"))
    print("  Saved fig_tree_structure.png")


def _plot_importance(model):
    """Save fig_tree_importance.png — feature importance bar chart."""
    set_style()
    importances = pd.Series(
        model.feature_importances_,
        index=[FEATURE_LABELS.get(f, f) for f in FEATURES],
    ).sort_values(ascending=True)

    fig, ax = plt.subplots(figsize=(7, 5))
    importances.plot(kind="barh", ax=ax, color="steelblue", edgecolor="white")
    ax.set_xlabel("Feature Importance (Mean Decrease Impurity)")
    ax.set_title("Vanilla Decision Tree — Feature Importances")
    save_fig(os.path.join(MEDIA_DIR, "fig_tree_importance.png"))
    print("  Saved fig_tree_importance.png")


def _build_latex_block(metrics, model, best_depth, best_val_r2) -> str:
    perf = metrics_to_str(metrics, "vanilla decision tree")
    top_feature = FEATURE_LABELS.get(
        FEATURES[int(np.argmax(model.feature_importances_))], ""
    )
    return rf"""
The optimal tree depth selected via validation-set $R^2$ grid search is
\textbf{{{best_depth}}} (validation $R^2 = {best_val_r2:.4f}$).
The most important splitting feature is \textbf{{{top_feature}}}.

{perf}

\begin{{figure}}[htbp]
\centering
\includegraphics[width=\linewidth]{{media/media/fig_tree_structure.png}}
\caption{{Vanilla decision tree structure (best depth = {best_depth},
rendered at depth $\leq 3$ for readability). Shading intensity
indicates the predicted value in each leaf.}}
\end{{figure}}

\begin{{figure}}[htbp]
\centering
\includegraphics[width=0.75\linewidth]{{media/media/fig_tree_importance.png}}
\caption{{Vanilla decision tree feature importances (mean decrease in
impurity). Only features assigned non-zero importance are split upon.}}
\end{{figure}}
"""
