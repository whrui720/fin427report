"""
neural_net.py — Section 11: Simple neural network (sklearn MLPRegressor).
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler

from .config import FEATURES, TARGET, MEDIA_DIR
from .utils import compute_metrics, metrics_to_str, get_XY, set_style, save_fig


def run_neural_net(train, val, test):
    """
    3-layer MLP (128→64→32), ReLU, Adam, L2 regularization, early stopping.
    Features are StandardScaler-normalized (fit on train only).

    Returns
    -------
    model       : fitted MLPRegressor
    scaler      : fitted StandardScaler
    metrics     : dict
    latex_block : str
    """
    X_train, y_train = get_XY(train, FEATURES, TARGET)
    X_val,   y_val   = get_XY(val,   FEATURES, TARGET)
    X_test,  y_test  = get_XY(test,  FEATURES, TARGET)

    scaler    = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_val_s   = scaler.transform(X_val)
    X_test_s  = scaler.transform(X_test)

    # Combine train + val; MLPRegressor's internal early stopping
    # uses a random 10% holdout drawn from the combined set
    X_fit_s = np.vstack([X_train_s, X_val_s])
    y_fit   = np.concatenate([y_train, y_val])

    model = MLPRegressor(
        hidden_layer_sizes=(128, 64, 32),
        activation="relu",
        solver="adam",
        alpha=1e-3,              # L2 weight decay
        learning_rate_init=1e-3,
        max_iter=500,
        early_stopping=True,
        validation_fraction=0.1,
        n_iter_no_change=20,
        random_state=42,
        verbose=False,
    )
    model.fit(X_fit_s, y_fit)
    print(
        f"  Neural network: {model.n_iter_} iterations, "
        f"best val score={model.best_validation_score_:.4f}"
    )

    y_pred  = model.predict(X_test_s)
    metrics = compute_metrics(y_test, y_pred)

    _plot_loss_curve(model)

    latex_block = _build_latex_block(metrics, model)
    return model, scaler, metrics, latex_block


def predict(model, scaler, df):
    X = scaler.transform(df[FEATURES].values)
    return model.predict(X)


# ── Internals ─────────────────────────────────────────────────────────────────

def _plot_loss_curve(model):
    """Save fig_nn_loss.png — training loss curve vs epochs."""
    set_style()
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(model.loss_curve_, label="Training loss", linewidth=1.5, color="steelblue")
    if hasattr(model, "validation_scores_") and model.validation_scores_:
        # validation_scores_ is negative MSE; negate for display
        val_mse = [-s for s in model.validation_scores_]
        ax.plot(val_mse, label="Validation loss (MSE)", linewidth=1.5,
                color="darkorange", linestyle="--")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Loss (MSE)")
    ax.set_title("Neural Network — Training Loss Curve")
    ax.legend()
    save_fig(os.path.join(MEDIA_DIR, "fig_nn_loss.png"))
    print("  Saved fig_nn_loss.png")


def _build_latex_block(metrics, model) -> str:
    perf = metrics_to_str(metrics, "neural network")
    n_params = sum(
        w.size for w in model.coefs_
    ) + sum(b.size for b in model.intercepts_)
    return rf"""
The neural network architecture is a 3-layer multi-layer perceptron
(MLP) with hidden layers of sizes $(128, 64, 32)$, ReLU activations,
Adam optimiser ($\eta = 0.001$), and L2 weight decay $\alpha = 0.001$
({n_params:,} trainable parameters total). Input features are
standardised using a \texttt{{StandardScaler}} fitted on the training set.
Early stopping monitors validation loss with patience 20; training
stopped at epoch \textbf{{{model.n_iter_}}}.

{perf}

\begin{{figure}}[htbp]
\centering
\includegraphics[width=0.82\linewidth]{{media/media/fig_nn_loss.png}}
\caption{{Neural network training and validation loss curves. The dashed
vertical line (where present) marks the early-stopping epoch.}}
\end{{figure}}
"""
