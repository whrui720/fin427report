"""
gradient_boosting.py — Section 10: Gradient Boosting (XGBoost).
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from xgboost import XGBRegressor

from .config import FEATURES, TARGET, FEATURE_LABELS, MEDIA_DIR
from .utils import compute_metrics, metrics_to_str, get_XY, set_style, save_fig


def run_gradient_boosting(train, val, test):
    """
    XGBoost with early stopping evaluated on the validation set.
    n_estimators=1000 with early_stopping_rounds=50 to prevent overfitting.

    Returns
    -------
    model       : fitted XGBRegressor
    metrics     : dict
    latex_block : str
    """
    X_train, y_train = get_XY(train, FEATURES, TARGET)
    X_val,   y_val   = get_XY(val,   FEATURES, TARGET)
    X_test,  y_test  = get_XY(test,  FEATURES, TARGET)

    model = XGBRegressor(
        n_estimators=1000,
        learning_rate=0.05,
        max_depth=5,
        subsample=0.8,
        colsample_bytree=0.8,
        early_stopping_rounds=50,
        random_state=42,
        n_jobs=-1,
        verbosity=0,
    )
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=False,
    )
    best_iter = model.best_iteration
    print(f"  XGBoost early stopped at iteration {best_iter}")

    y_pred  = model.predict(X_test)
    metrics = compute_metrics(y_test, y_pred)

    _plot_importance(model)

    latex_block = _build_latex_block(metrics, model, best_iter)
    return model, metrics, latex_block


def predict(model, df, scaler=None):
    return model.predict(df[FEATURES].values)


# ── Internals ─────────────────────────────────────────────────────────────────

def _plot_importance(model):
    """Save fig_xgb_importance.png — gain-based feature importance."""
    set_style()
    imp = model.get_booster().get_score(importance_type="gain")
    # Map internal feature names (f0, f1, ...) back to labels
    feat_name_map = {f"f{i}": FEATURE_LABELS.get(f, f) for i, f in enumerate(FEATURES)}
    imp_mapped = {feat_name_map.get(k, k): v for k, v in imp.items()}

    s = pd.Series(imp_mapped).sort_values(ascending=True)

    fig, ax = plt.subplots(figsize=(7, 5))
    s.plot(kind="barh", ax=ax, color="darkorange", edgecolor="white")
    ax.set_xlabel("Feature Importance (Gain)")
    ax.set_title("XGBoost — Feature Importances (Gain-based)")
    save_fig(os.path.join(MEDIA_DIR, "fig_xgb_importance.png"))
    print("  Saved fig_xgb_importance.png")


def _build_latex_block(metrics, model, best_iter) -> str:
    perf = metrics_to_str(metrics, "XGBoost gradient boosting")
    return rf"""
XGBoost is configured with \texttt{{n\_estimators=1000}},
\texttt{{learning\_rate=0.05}}, \texttt{{max\_depth=5}},
\texttt{{subsample=0.8}}, \texttt{{colsample\_bytree=0.8}}, and
early stopping with patience 50 evaluated on the validation set.
Training halted at iteration \textbf{{{best_iter}}}.

{perf}

\begin{{figure}}[htbp]
\centering
\includegraphics[width=0.80\linewidth]{{media/media/fig_xgb_importance.png}}
\caption{{XGBoost feature importances measured by gain (total improvement
in the loss function attributed to each feature across all splits).
Features absent from the figure received zero gain during training.}}
\end{{figure}}
"""
