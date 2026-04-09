"""
config.py — Constants, paths, and feature definitions shared across all modules.
"""
import os

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH  = os.path.join(BASE_DIR, "Aggregate data 20260315_1425.csv")
MEDIA_DIR  = os.path.join(BASE_DIR, "report_latex", "media", "media")
LATEX_IN   = os.path.join(BASE_DIR, "report_latex", "reportoutline.latex")
LATEX_OUT  = os.path.join(BASE_DIR, "report_latex", "reportoutline.latex")

# ── Split dates ───────────────────────────────────────────────────────────────
TRAIN_END  = "2018-12-31"
VAL_END    = "2021-12-31"
TEST_END   = "2024-10-31"
PRED_MONTH = "2024-11-30"

# ── Sector filter ─────────────────────────────────────────────────────────────
SECTOR = 30
GROUP  = 3030

# ── Target & variable of interest ─────────────────────────────────────────────
TARGET = "indadjret"
VOI    = "finnpm"     # Net profit margin (Net profit / Sales)

# ── Feature list (winsorized, zero missing values) ────────────────────────────
# lnlag1mcreal has no fin* prefix — it is already a log transformation
FEATURES = [
    "lnlag1mcreal",
    "finbm",
    "finchgroa",
    "finilliq",
    "finsdage",
    "fingender",
    "finnpm",
    "finmom12",
    "fincr",
    "finos",
    "finbeta",
    "finnwca",
    "finlnshchg",
    "finmom11",
    "finroic",
]

# Human-readable labels for figures and tables
FEATURE_LABELS = {
    "lnlag1mcreal": "Log Market Cap",
    "finbm":        "Book-to-Market",
    "finchgroa":    "Chg in ROA",
    "finilliq":     "Amihud Illiquidity",
    "finsdage":     "Std Dev Board Age",
    "fingender":    "Pct Male Board",
    "finnpm":       "Net Profit Margin",
    "finmom12":     "Momentum 12m",
    "fincr":        "Current Ratio",
    "finos":        "Option/Stock Vol",
    "finbeta":      "Beta",
    "finnwca":      "NWC/Assets",
    "finlnshchg":   "Ln Share Issuance Chg",
    "finmom11":     "Momentum 11m",
    "finroic":      "ROIC",
}

# ── Missingness indicator columns ─────────────────────────────────────────────
# Each is 1 when the raw value was missing (fin* columns are imputed)
MISS_COLS = [
    "bmmiss", "chgroamiss", "illiqmiss", "sdagemiss", "gendermiss",
    "npmmiss", "mom12miss", "crmiss", "osmiss", "betamiss",
    "nwcamiss", "lnshchgmiss", "mom11miss", "roicmiss",
]

# Map fin* feature → its missingness column (lnlag1mcreal has none)
MISS_MAP = {
    "finbm":       "bmmiss",
    "finchgroa":   "chgroamiss",
    "finilliq":    "illiqmiss",
    "finsdage":    "sdagemiss",
    "fingender":   "gendermiss",
    "finnpm":      "npmmiss",
    "finmom12":    "mom12miss",
    "fincr":       "crmiss",
    "finos":       "osmiss",
    "finbeta":     "betamiss",
    "finnwca":     "nwcamiss",
    "finlnshchg":  "lnshchgmiss",
    "finmom11":    "mom11miss",
    "finroic":     "roicmiss",
    "lnlag1mcreal": None,
    "indadjret":   None,
}

# Columns to load from CSV (minimal set for memory efficiency)
USECOLS = (
    ["month", "cusip8", "issuernm", "ticker", "permno",
     "gsector", "ggroup", "indadjret", "mthret"]
    + FEATURES
    + MISS_COLS
)
