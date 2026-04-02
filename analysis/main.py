"""
main.py — Orchestrator for the FIN 427 ML report analysis.

Run from the repo root:
    python -m analysis.main
or:
    python analysis/main.py

Sections
--------
1  Data loading & splitting
2  Descriptive statistics (whole sample + VOI + split description)
3  OLS regression
4  LASSO penalized regression
5  Vanilla decision tree
6  Random forest
7  Gradient boosting (XGBoost)
8  Neural network
9  November 2024 predictions + reconciliation table
10 LaTeX template population

After completion, compile the report with:
    pdflatex report_latex/reportoutline.latex
"""
import os
import sys
import warnings
warnings.filterwarnings("ignore")

# Allow running as a script directly (python analysis/main.py)
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import matplotlib
matplotlib.use("Agg")  # non-interactive backend — must be set before pyplot import

from analysis.config import MEDIA_DIR
from analysis import data as _data
from analysis import descriptive as _desc
from analysis import ols as _ols
from analysis import lasso as _lasso
from analysis import tree as _tree
from analysis import random_forest as _rf
from analysis import gradient_boosting as _gb
from analysis import neural_net as _nn
from analysis import predictions as _pred
from analysis import latex_populate as _latex


def main():
    os.makedirs(MEDIA_DIR, exist_ok=True)

    # ── 1. Load & split ───────────────────────────────────────────────────────
    print("\n[1/10] Loading data...")
    df = _data.load_data()
    hist_df, train, val, test, pred_sector = _data.make_splits(df)
    _data.free_raw(df)

    # ── 2. Descriptive statistics ─────────────────────────────────────────────
    print("\n[2/10] Descriptive statistics...")
    desc_stats_table = _desc.desc_stats_table(hist_df)
    desc_stats_text  = (
        "The dataset covers the period January 2001 to October 2024, "
        "comprising {:,} stock-month observations across all GICS sectors. "
        "Table~\\ref{{tab:desc_stats}} reports summary statistics for all "
        "15 predictor variables and the target variable "
        "(industry-adjusted return, \\texttt{{indadjret}}), "
        "computed on the full sample excluding November 2024. "
        "The \\texttt{{fin*}} columns are winsorized at the percentile "
        "constraints listed in Table~1; the percentage missing reflects "
        "the fraction of raw observations that required imputation. "
        "\\texttt{{lnshchg}} (log change in shares issued) has the highest "
        "missingness at approximately 75\\%, while illiquidity and momentum "
        "are nearly complete.".format(len(hist_df))
    )
    _desc.plot_correlation_heatmap(train)
    voi_block    = _desc.voi_latex_block(hist_df, train)
    splits_block = _desc.splits_latex_block(train, val, test, pred_sector)

    # ── 3. OLS ────────────────────────────────────────────────────────────────
    print("\n[3/10] OLS regression...")
    ols_model, ols_metrics, ols_coef_df, ols_block = _ols.run_ols(train, val, test)
    print(f"  OLS test R²={ols_metrics['r2']:.4f}  RMSE={ols_metrics['rmse']:.4f}")

    # ── 4. LASSO ──────────────────────────────────────────────────────────────
    print("\n[4/10] LASSO...")
    lasso_model, lasso_scaler, lasso_alpha, lasso_metrics, lasso_block = \
        _lasso.run_lasso(train, val, test)
    print(f"  LASSO test R²={lasso_metrics['r2']:.4f}  RMSE={lasso_metrics['rmse']:.4f}")

    # ── 5. Vanilla decision tree ──────────────────────────────────────────────
    print("\n[5/10] Vanilla decision tree...")
    tree_model, tree_depth, tree_metrics, tree_block = _tree.run_tree(train, val, test)
    print(f"  Tree test R²={tree_metrics['r2']:.4f}  RMSE={tree_metrics['rmse']:.4f}")

    # ── 6. Random forest ──────────────────────────────────────────────────────
    print("\n[6/10] Random forest (grid search — may take several minutes)...")
    rf_model, rf_params, rf_metrics, rf_block = _rf.run_random_forest(train, val, test)
    print(f"  RF test R²={rf_metrics['r2']:.4f}  RMSE={rf_metrics['rmse']:.4f}")

    # ── 7. Gradient boosting ──────────────────────────────────────────────────
    print("\n[7/10] XGBoost gradient boosting...")
    xgb_model, xgb_metrics, xgb_block = _gb.run_gradient_boosting(train, val, test)
    print(f"  XGB test R²={xgb_metrics['r2']:.4f}  RMSE={xgb_metrics['rmse']:.4f}")

    # ── 8. Neural network ─────────────────────────────────────────────────────
    print("\n[8/10] Neural network...")
    nn_model, nn_scaler, nn_metrics, nn_block = _nn.run_neural_net(train, val, test)
    print(f"  NN test R²={nn_metrics['r2']:.4f}  RMSE={nn_metrics['rmse']:.4f}")

    # ── 9. November 2024 predictions ─────────────────────────────────────────
    print("\n[9/10] November 2024 predictions...")
    fitted_models = {
        "ols":   {"model": ols_model},
        "lasso": {"model": lasso_model, "scaler": lasso_scaler},
        "tree":  {"model": tree_model},
        "rf":    {"model": rf_model},
        "xgb":  {"model": xgb_model},
        "nn":   {"model": nn_model, "scaler": nn_scaler},
    }
    results_df = _pred.build_predictions(pred_sector, fitted_models)

    all_metrics = {
        "OLS":               ols_metrics,
        "LASSO":             lasso_metrics,
        "Vanilla Tree":      tree_metrics,
        "Random Forest":     rf_metrics,
        "Gradient Boosting": xgb_metrics,
        "Neural Network":    nn_metrics,
    }
    _pred.plot_sector_predictions(results_df)
    _pred.plot_metrics_comparison(all_metrics)
    recon_text   = _pred.reconciliation_text(results_df, all_metrics)
    panel_a, panel_b = _pred.build_reconciliation_latex(results_df)

    top_pick = results_df.iloc[0]
    print(
        f"\n  *** TOP RECOMMENDATION: {top_pick['ticker']} ({top_pick['issuernm']}) ***\n"
        f"  Average rank across 6 models: {top_pick['avg_rank']:.2f}"
    )

    # ── 10. Populate LaTeX ────────────────────────────────────────────────────
    print("\n[10/10] Populating LaTeX template...")
    _latex.populate(
        desc_stats_table=desc_stats_table,
        desc_stats_text=desc_stats_text,
        voi_block=voi_block,
        splits_block=splits_block,
        ols_block=ols_block,
        lasso_block=lasso_block,
        tree_block=tree_block,
        rf_block=rf_block,
        xgb_block=xgb_block,
        nn_block=nn_block,
        recon_text=recon_text,
        panel_a_rows=panel_a,
        panel_b_rows=panel_b,
    )

    print("\nDone. To compile the report:")
    print("  cd report_latex && pdflatex reportoutline.latex")


if __name__ == "__main__":
    main()
