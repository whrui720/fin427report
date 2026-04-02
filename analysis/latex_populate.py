"""
latex_populate.py — Section 13: Read the LaTeX template and replace all
[Insert ...] placeholders with generated content.
"""
import re
from .config import LATEX_IN, LATEX_OUT


# ── Placeholder strings as they appear verbatim in the template ───────────────
# (These are the exact LaTeX-escaped strings from reportoutline.latex)

_P_DESC_STATS = (
    "{[}Insert a table of descriptive statistics on all variables and comment\n"
    "on the most important aspects of that table, mentioning the time period\n"
    "under study, the number of observations, and the stock\n"
    "characteristics.{]}\n\n"
    "{[}Table to be inserted. Use one column for the percentage missing,\n"
    "which is computed simply using the ``miss'' variables and taking an\n"
    "average. Suppose there were 10 observations and two were missing so have\n"
    "a value of 1 in the miss variable and zero for the eight cases in which\n"
    "the data was not missing. The average is 20 per cent, so 20 the figure\n"
    "that goes in the percentage missing is 20. Report the mean and standard\n"
    "deviation and selected percentiles, which includes the\n"
    "50\\textsuperscript{th} percentile but you can decide what other\n"
    "percentiles to comment on. Run the descriptive statistics on the\n"
    "aggregate dataset you have been provided, not your own data that you\n"
    "submitted. The dataset should exclude the last month but keep all the\n"
    "other months.{]}"
)

_P_VOI = (
    "{[}Explain why you chose your recommended variable of interest and\n"
    "comment on descriptive statistics. Run the descriptive statistics on\n"
    "your variable of interest on the aggregate dataset you have been\n"
    "provided, not your own data that you submitted. The dataset should\n"
    "exclude the last month but keep all the other months.{]}"
)

_P_SPLITS = (
    "{[}Describe your selection of cut-off points for training, test and\n"
    "validation samples, and what you actually do with those samples. The\n"
    "dataset starts with January 2001 and the last month is November 2024.\n"
    "You must exclude November 2024 from the dataset for training, test and\n"
    "validation samples and use November 2024 as the last month. So we will\n"
    "pretend that on October 31, 2024, we form our portfolio for the first\n"
    "time. You will make predictions of industry-adjusted returns for stocks\n"
    "in your industry for November 2024 using all available data prior to\n"
    "that month.{]}"
)

_P_OLS    = "{[}Insert analysis based upon ordinary least squares regression.{]}"
_P_LASSO  = "{[}Insert analysis based upon penalized regression.{]}"
_P_TREE   = "{[}Insert analysis based upon one decision tree.{]}"
_P_RF     = "{[}Insert analysis based upon random forest.{]}"
_P_XGB    = "{[}Insert analysis based upon gradient boosting{]}."
_P_NN     = "Insert analysis based upon neural networks."
_P_RECON  = (
    "{[}Insert text reconciling results summarized in the table below. You\n"
    "must include this table.{]}"
)

# Panel rows inside the reconciliation longtable (10 empty rows each)
_EMPTY_PANEL_A_ROW = "1 & & & & & & \\\\"
_EMPTY_PANEL_B_ROW = "1 & & & & & & \\\\"


def _fill_panel_rows(content: str, panel_a_rows: str, panel_b_rows: str) -> str:
    """
    Replace the 10 empty data rows in Panel A and Panel B of the
    reconciliation longtable.  The template has rows like '1 & & & & & & \\\\'
    through '10 & & & & & & \\\\'.
    """
    for i in range(1, 11):
        empty = rf"{i} & & & & & & \\"
        a_line = panel_a_rows.split("\n")[i - 1] if panel_a_rows else empty
        content = content.replace(empty, a_line, 1)

    # Panel B section follows Panel A; the same numeric rows appear again
    for i in range(1, 11):
        empty = rf"{i} & & & & & & \\"
        b_line = panel_b_rows.split("\n")[i - 1] if panel_b_rows else empty
        content = content.replace(empty, b_line, 1)

    return content


def populate(
    desc_stats_table: str,
    desc_stats_text: str,
    voi_block: str,
    splits_block: str,
    ols_block: str,
    lasso_block: str,
    tree_block: str,
    rf_block: str,
    xgb_block: str,
    nn_block: str,
    recon_text: str,
    panel_a_rows: str,
    panel_b_rows: str,
):
    """
    Read the LaTeX template, substitute all placeholders, write result to disk.
    """
    with open(LATEX_IN, "r", encoding="utf-8") as f:
        content = f.read()

    desc_combined = (
        desc_stats_text
        + "\n\n"
        + desc_stats_table
        + r"""

\begin{figure}[htbp]
\centering
\includegraphics[width=0.90\linewidth]{media/media/fig_desc_stats.png}
\caption{Spearman correlation matrix of the 15 predictor variables computed
on the training set (January 2001 -- December 2018). Values shown are
Spearman rank correlations. The momentum variables (\texttt{finmom11},
\texttt{finmom12}) are highly correlated with each other, as expected.}
\end{figure}
"""
    )

    replacements = [
        (_P_DESC_STATS, desc_combined),
        (_P_VOI,        voi_block),
        (_P_SPLITS,     splits_block),
        (_P_OLS,        ols_block),
        (_P_LASSO,      lasso_block),
        (_P_TREE,       tree_block),
        (_P_RF,         rf_block),
        (_P_XGB,        xgb_block),
        (_P_NN,         nn_block),
        (_P_RECON,      recon_text),
    ]

    for placeholder, replacement in replacements:
        if placeholder in content:
            content = content.replace(placeholder, replacement)
        else:
            print(f"  WARNING: placeholder not found in template:\n  {placeholder[:80]!r}")

    content = _fill_panel_rows(content, panel_a_rows, panel_b_rows)

    with open(LATEX_OUT, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"  LaTeX written to {LATEX_OUT}")
