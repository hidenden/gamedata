#!/usr/bin/env python3

import sys
import shutil
import csv
import pandas as pd
import numpy as np
import datetime
import re
import matplotlib.pyplot as plt
import matplotlib as mpl
import japanize_matplotlib
import hw_sum

def build_main():
    copy_data()
    copy2pickle("weekly_hard_1999_2022")
    conv_hardframe()

def copy_data():
    print("Copy from transform")
    fname = "weekly_hard_1999_2022.csv"
    srcdir = "../transform"
    shutil.copy(f"{srcdir}/{fname}", fname)

def load_csv(fname):
    with open(fname, "r") as f:
        reader = csv.reader(f)
        rows = []
        for row in reader:
            rows.append(row)
        return rows

def copy2pickle(fname: str) -> pd.DataFrame:
    print("Convert to pickle")
    csv_name = f"{fname}.csv"
    pkl_name = f"{fname}.pkl"
    hw_weekly_df = pd.read_csv(csv_name, index_col="end_date", parse_dates=[1])
    hw_weekly_df = hw_weekly_df.drop("begin_date", axis=1)
    hw_weekly_df.to_pickle(pkl_name)

def conv_hardframe():
    hw_weekly_df = pd.read_pickle("weekly_hard_1999_2022.pkl")
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
    weekly_hw_df.to_pickle("hard_weekly.pkl")


def single_df(df, hwname):
    df2 = df[df['hw'] == hwname].drop("hw", axis=1).rename(columns={"units":hwname})
    return df2    


if __name__ == "__main__":
    build_main()
    sys.exit(0)
