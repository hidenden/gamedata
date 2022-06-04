#!/usr/bin/env python3

import sys
import pandas as pd

MASTER_DB = "../hard_weekly.csv"
MASTER_PKL = "hard_weekly.pkl"

def pklmaster_main():
    master2pkl()

def master2pkl() -> pd.DataFrame:
    hw_weekly_df = pd.read_csv(MASTER_DB, index_col="end_date", parse_dates=[1]).drop("begin_date", axis=1)
    hw_weekly_df.to_pickle(MASTER_PKL)
    return hw_weekly_df

def hard_weekly_df() -> pd.DataFrame:
    return pd.read_pickle(MASTER_PKL)

if __name__ == "__main__":
    pklmaster_main()
    sys.exit(0)
