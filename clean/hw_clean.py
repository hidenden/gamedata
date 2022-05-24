#!/usr/bin/env python3

import pandas as pd
import numpy as np
import datetime
import re
import matplotlib.pyplot as plt
import matplotlib as mpl
import sys

def hw_clean_main():
    # index_colでインデックスにするカラムを指定｡
    # parse_datesで日付としてパースするカラムを指定
    hw2021 = pd.read_csv("../raw/hwdata_2021.csv", index_col="end_date", parse_dates=[1])
    hw2020 = pd.read_csv("../raw/hwdata_2020.csv", index_col="end_date", parse_dates=[1])
    hw2019 = pd.read_csv("../raw/hwdata_2019.csv", index_col="end_date", parse_dates=[1])
    hw2018 = pd.read_csv("../raw/hwdata_2018.csv", index_col="end_date", parse_dates=[1])
    hw2017 = pd.read_csv("../raw/hwdata_2017.csv", index_col="end_date", parse_dates=[1])
    hw2016 = pd.read_csv("../raw/hwdata_2016.csv", index_col="end_date", parse_dates=[1])
    hw2022 = pd.read_csv("../raw/hwdata_2022.csv", index_col="end_date", parse_dates=[1])
    hwold = pd.read_csv("../raw/hwdata_old.csv", index_col="end_date", parse_dates=[1])

    hw2 = pd.concat([hwold, hw2016, hw2017, hw2018, hw2019, hw2020, hw2021, hw2022], axis=0)
    hw_all = hw2.drop("begin_date", axis=1)
    
    # カラム名の変更(扱いやすいようにHWの省略形に)
    column_map = {'NINTENDOSWITCH': 'NSW', 'XboxSeriesX/S':'XSX', 'ゲームボーイアドバンス':'GBA', 'ニンテンドー3DS':'3DS', 'ニンテンドーDS':'NDS',
       'ニンテンドーゲームキューブ':'GC', 'プレイステーション2':'PS2', 'プレイステーション3':'PS3', 'プレイステーション4':'PS4', 'プレイステーション5':'PS5',
       'プレイステーションVita':'Vita', 'プレイステーション・ポータブル':'PSP'}
    hw_all.rename(columns=column_map, inplace=True)
    # カラムの順序をメーカー順､登場順に並べる
    column_order = ['GBA', 'GC', 'NDS', 'Wii', '3DS', 'WiiU', 'NSW', 'Xbox', 'Xbox360', 'XboxOne', 'XSX', 'PS2', 'PSP', 'PS3', 'Vita', 'PS4', 'PS5']
    hw_all = hw_all.reindex(columns=column_order)

    # すべてのHW売上データの合体したもの
    hw_all.to_pickle("hw_all.pkl")

    # HW売上データの累計
    hw_sum = hw_all.cumsum()
    hw_sum.to_pickle("hw_cumsum.pkl")

    # 年ごとのHW売上データ
    hw_year = hw_all.resample('Y').sum()
    hw_year.to_pickle("hw_year.pkl")


if __name__ == "__main__":
    hw_clean_main()
    sys.exit(0)
