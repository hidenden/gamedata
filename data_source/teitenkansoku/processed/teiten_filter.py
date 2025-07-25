#!/usr/bin/env python3

import sys
import csv
from typing import List

def get_this_year() -> int:
    return 2025

def teiten_filter_main(srcdir:str, out_path:str):
    hw_data = load_all(srcdir)
    save_csv(out_path, hw_data)

def load_all(dir:str) -> List:   
    normalized_data = [["begin_date", "end_date", "hw", "units"]]
    for year in range(2016, get_this_year() + 1):
        csv_rows = load_csv(dir, year)
        normal_data = teiten2normalize(csv_rows)
        normalized_data.extend(normal_data)
    return normalized_data
    
def save_csv(fname: str, data:List):
    with open(fname, "w") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerows(data)
        print(f"{fname} is saved")

def load_csv(dir:str, year:int) -> List:
    file_name = f"{dir}/hwdata_{year}.csv"
    with open(file_name, "r") as f:
        reader = csv.reader(f)
        rows = []
        for row in reader:
            rows.append(row)
        return rows

def teiten2normalize(teiten_rows:List) -> List:
    HW_MAP = {
        'NINTENDOSWITCH': 'NSW', 
        "NINTENDOSWITCH2": 'NSW2',
        'PS4': 'PS4',
        'PS5': 'PS5',
        'XboxSeriesX/S':'XSX',
        'ゲームボーイアドバンス':'GBA',
        'ニンテンドー3DS':'3DS',
        'ニンテンドーDS':'NDS',
        'ニンテンドーゲームキューブ':'GC',
        'プレイステーション2':'PS2',
        'プレイステーション3':'PS3',
        'プレイステーション4':'PS4',
        'プレイステーション5':'PS5',
        'プレイステーションVita':'Vita',
        'プレイステーション・ポータブル':'PSP',
        'WiiU': 'WiiU',
        'XboxOne': 'XBOne'
        }

    normalized_data = []
    header = teiten_rows[0]
    for row in teiten_rows[1:]:
        begin_date = row[0]
        end_date = row[1]
        for i, hw in enumerate(header[2:]):
            units = row[i + 2]
            if units == "":
                continue
            hw_name = HW_MAP[hw]
            normalized_data.append([begin_date, end_date, hw_name, units])

    return normalized_data

if __name__ == "__main__":
    srcdir = "../raw"
    this_year = get_this_year()
    out_path = f"../teiten_hard_weekly_2016_{this_year}.csv"
    teiten_filter_main(srcdir, out_path)
    sys.exit(0)
