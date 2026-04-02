# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Goal

FIN 427 course project: use machine learning to predict industry-adjusted stock returns and select one stock to buy from the **Household and Personal Products** sector (GICS sector `gsector=30`, group `ggroup=3030`) using November 2024 data.

## Repository Layout

- `Aggregate data 20260315_1425.csv` — full panel dataset (Jan 2001–Nov 2024, all sectors)
- `report_latex/reportoutline.latex` — LaTeX report template to fill in
- `report_latex/media/` — figures go here for inclusion in the report
- `spec.txt` — project specification

## Dataset Details

**Key columns:**
- `month` — date (e.g. `31-JAN-2001`)
- `cusip8`, `issuernm`, `ticker`, `permno` — stock identifiers
- `gsector`, `ggroup` — GICS sector/group codes for filtering
- `indadjret` — **target variable**: industry-adjusted monthly return
- `mthret`, `adjret`, `gsret` — raw/adjusted/sector returns
- `lag1mcreal`, `lnlag1mcreal` — lagged real market cap and its log

**Feature naming convention** (each raw variable has three derived forms):
- `fin*` — winsorized/constrained version (use as model input)
- `z*` — z-scored version
- `r*` — rank-normalized version
- `*miss` — missingness indicator (1 = missing, 0 = observed)

**16 predictors** (use `fin*` versions): `lnlag1mcreal`, `bm`, `os`, `mom12`, `npm`, `sdage`, `gender`, `beta`, `nwca`, `illiq`, `cr`, `lnshchg`, `mom11`, `chgroa`, `roic`, and implicitly `lag1mcreal`.

## Analysis Workflow

1. **Filter** to sector 30 / group 3030 only
2. **Split**: training/test/validation = all months except Nov 2024; Nov 2024 = held-out prediction month
3. **Target**: predict `indadjret` for November 2024; rank stocks by predicted return; recommend top-ranked stock
4. **Models to run** (all results go into the LaTeX template):
   - OLS regression
   - LASSO / Ridge (penalized regression)
   - Vanilla decision tree
   - Random forest
   - Gradient boosting (XGBoost)
   - Simple neural network
5. **Final deliverable**: Table 3 in the LaTeX report — stock rankings across all 6 methods, plus Panel B predicted returns

## LaTeX Compilation

```bash
pdflatex report_latex/reportoutline.latex
```

Figures referenced in the template use path `vertopal_5ef99677aafc4edbb4ea6857ad1ad357/media/image2.png` — update paths when inserting new figures.

## Python Environment (recommended packages)

```python
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression, Lasso, Ridge
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
import xgboost as xgb
import torch  # or keras/tensorflow for neural networks
```

The CSV is large (~827 MB); load only needed columns with `usecols=` when possible, or filter by sector immediately after loading.
