#!/usr/bin/env python3

import sys
import pandas as pd

MASTER_PKL = "hard_weekly.pkl"
WEEKLY_HARD_RECORD_PKL = "weekly_hard_record.pkl"

def pivot_hard_main():
    pivot_hard_weekly()

def hard_weekly_df() -> pd.DataFrame:
    return pd.read_pickle(MASTER_PKL)

def pivot_hard_weekly() -> pd.DataFrame:
    hw_weekly_df = hard_weekly_df()
    HW = ['3DS', 'DC','DS', 'GB', 'GBA', 'GC', 'N64', 'NeoGeoP', 'Switch',
        'PS', 'PS2', 'PS3', 'PS4', 'PS5', 'PSP', 'WS', 'SATURN', 'Vita',
        'Wii', 'WiiU', 'XB360', 'XBOne','XSX', 'Xbox', 'PKS']
    hw_dfs = {}
    for h in HW:
        hw_dfs[h] = single_df(hw_weekly_df, h)
    hw_dfs_list = []
    for h in HW[1:]:
        hw_dfs_list.append(hw_dfs[h])
    weekly_hw_df = hw_dfs['3DS'].join(hw_dfs_list, how="outer")
    weekly_hw_df.to_pickle(WEEKLY_HARD_RECORD_PKL)
    return weekly_hw_df

def single_df(df, hwname):
    df2 = df[df['hw'] == hwname].drop("hw", axis=1).rename(columns={"units":hwname})
    return df2    

if __name__ == "__main__":
    pivot_hard_main()
    sys.exit(0)
