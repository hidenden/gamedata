#!/usr/bin/env python3

import sys
import csv
from typing import List

def teiten_filter_main():
    hw_data = load_all()

def load_all():   
    normalized_data = [["begin_date", "end_date", "hw", "units"]]
    for year in range(2016, 2023):
        csv_rows = load_csv(year)
        normal_data = teiten2normalize(csv_rows)
        normalized_data.extend(normal_data)
    save_csv("teiten_weekly_hard_2016_2022.csv", normalized_data)
    
def save_csv(fname: str, data:List):
    with open(fname, "w") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerows(data)
        print(f"{fname} is saved")

def load_csv(year:int) -> List:
    file_name = f"../raw/teitenkansoku/hwdata_{year}.csv"
    with open(file_name, "r") as f:
        reader = csv.reader(f)
        rows = []
        for row in reader:
            rows.append(row)
        return rows

def teiten2normalize(teiten_rows:List) -> List:
    HW_MAP = {
        'NINTENDOSWITCH': 'NSW', 
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
    teiten_filter_main()
    sys.exit(0)
