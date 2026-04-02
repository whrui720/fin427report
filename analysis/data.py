"""
data.py — CSV loading, date parsing, and train/val/test/predict splits.
"""
import gc
import pandas as pd
from .config import (
    DATA_PATH, USECOLS, FEATURES, TARGET, MISS_COLS,
    TRAIN_END, VAL_END, TEST_END, PRED_MONTH,
    SECTOR, GROUP,
)


def load_data() -> pd.DataFrame:
    """
    Load the aggregate CSV with only the required columns.
    Parses the 'month' column from 31-JAN-2001 format to datetime.
    """
    print("  Loading CSV (this may take a minute for 827 MB)...")
    df = pd.read_csv(DATA_PATH, usecols=USECOLS)
    df["month"] = pd.to_datetime(df["month"], format="%d-%b-%Y")
    df = df.sort_values("month").reset_index(drop=True)
    print(f"  Loaded {len(df):,} rows across {df['month'].nunique()} months.")
    return df


def make_splits(df: pd.DataFrame):
    """
    Return (hist_df, train, val, test, pred_sector).

    hist_df      — all rows before November 2024 (used for descriptive stats)
    train        — Jan 2001–Dec 2018, full universe
    val          — Jan 2019–Dec 2021, full universe
    test         — Jan 2022–Oct 2024, full universe
    pred_sector  — Nov 2024, sector 30 / group 3030 only (38 stocks)
    """
    train_end  = pd.Timestamp(TRAIN_END)
    val_end    = pd.Timestamp(VAL_END)
    test_end   = pd.Timestamp(TEST_END)
    pred_month = pd.Timestamp(PRED_MONTH)

    hist_df = df[df["month"] <= test_end].copy()

    train = hist_df[hist_df["month"] <= train_end].reset_index(drop=True)
    val   = hist_df[(hist_df["month"] > train_end) & (hist_df["month"] <= val_end)].reset_index(drop=True)
    test  = hist_df[hist_df["month"] > val_end].reset_index(drop=True)

    pred_all = df[df["month"] == pred_month]
    pred_sector = pred_all[
        (pred_all["gsector"] == SECTOR) & (pred_all["ggroup"] == GROUP)
    ].reset_index(drop=True)

    print(
        f"  Splits — Train: {len(train):,} | Val: {len(val):,} | "
        f"Test: {len(test):,} | Predict (sector): {len(pred_sector)}"
    )
    return hist_df, train, val, test, pred_sector


def free_raw(df: pd.DataFrame):
    """Delete the full DataFrame and trigger garbage collection."""
    del df
    gc.collect()
