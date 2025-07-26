#!/usr/bin/env python3

import sys
from typing import List
import csv
from dateutil import parser

def insert_header(data:List) -> List:
    data.insert(0, ["id", "report_date", "period_date", "hw", "units"])
    return data
    
def save_csv(fname: str, data:List):
    with open(fname, "w") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerows(data)
        print(f"{fname} is saved")

def load_csv(fname) -> List:
    with open(fname, "r") as f:
        reader = csv.reader(f)
        rows = []
        for row in reader:
            rows.append(row)
        return rows

def union_datasources_main(srcdir:str, output_file:str):
    fixed_data = insert_header(convert_to_database_format(union_datasource(srcdir)))
    save_csv(output_file, fixed_data)

def convert_to_database_format(data:List) -> List:
    # dataは配列の配列である。dataの各エントリを処理して、新たな配列の配列を構成し返す。
    new_data = []
    for row in data:
        begin_date = row[0]
        report_date = row[1]
        report_date_str = report_date.strftime('%Y-%m-%d')
        # begin_dateとreport_dateの差を計算
        period_date = (report_date - begin_date).days + 1
        
        hw = row[2]
        units = row[3]
        id = report_date_str + "_" + hw

        new_data.append([id, report_date_str, period_date, hw, units])

    return new_data


def union_datasource(srcdir:str) -> List:
    base_data = concat_all_source(srcdir)
    cleaned_data = clean_data(base_data)
    return group_hard_variations(cleaned_data)

def get_this_year() -> int:
    return 2025

def concat_all_source(srcdir:str) -> List:
    this_year = get_this_year()
    data1 = load_csv(f"{srcdir}/gamesdata/gamesdata_hard_weekly_2015_12.csv")
    data2 = load_csv(f"{srcdir}/geimin_net/geimin_hard_weekly_1999_2015.csv")
    data3 = load_csv(f"{srcdir}/teitenkansoku/teiten_hard_weekly_2016_{this_year}.csv")
    data = []
    data.extend(data1[1:])
    data.extend(data2[1:])
    data.extend(data3[1:])
    return data

def clean_data(data: List) -> List:
    HWMAP = {
        '3DS':'3DS',
        'DC':'DC',
        'DS':'DS',
        'DSL':'DS',
        'DSi':'DS',
        'GB':'GB',
        'GBA':'GBA',
        'GBASP':'GBA',
        'GBC':'GB',
        'GBM':'GB',
        'GC':'GC',
        'N64':'N64',
        'NGP':'NeoGeoP',
        'NSW':'NSW',
        'Switch':'NSW',
        'NS2':'NS2',
        'NSW2':'NS2',
        'Switch2':'NS2',
        'New3DS':'3DS',
        'PS':'PS',
        'PS2':'PS2',
        'PS3':'PS3',
        'PS4':'PS4',
        'PS5':'PS5',
        'PSP':'PSP',
        'PSPgo':'PSP',
        'SC':'WS',
        'SS':'SATURN',
        'Vita':'Vita',
        'WS':'WS',
        'WSC':'WS',
        'Wii':'Wii',
        'WiiU':'WiiU',
        'XB360':'XB360',
        'XBOne':'XBOne',
        'XSX': 'XSX',
        'Xbox':'Xbox',
        'XboxOne':'XBOne',
        'ps':'PKS'}

    data2 = []
    for d in data:
        begin = parser.parse(d[0]).date()
        end = parser.parse(d[1]).date()
        hw = HWMAP[d[2]]
        units = int(d[3])
        data2.append([begin, end, hw, units])
    return data2

def group_hard_variations(data:List) -> List:
    daylist = [row[0] for row in data]
    dayset = sorted(set(daylist))

    day_data = {}
    for day in dayset:
        day_data[day] = {}
        for d2 in data:
            if d2[0] == day:
                current_data = day_data[day].get(d2[2], None)
                if current_data:
                    # print(f"nayose {current_data}\n.   {d2}")
                    current_data[3] += d2[3]
                    # print(f"   -> {current_data[3]}")
                else:
                    day_data[day][d2[2]] = d2
    new_data = []
    for day in day_data.keys():
        new_data.extend(day_data[day].values())

    return new_data


if __name__ == "__main__":
    # 第一引数にデータソースディレクトリ、第二引数に出力ファイル名が指定される。
    if len(sys.argv) < 3:
        print("Usage: python union_datasources.py <data_source_directory> <output_file>")
        sys.exit(1)
    srcdir = sys.argv[1]
    if not srcdir.endswith("/"):
        srcdir += "/"
    output_file = sys.argv[2]
    if not output_file.endswith(".csv"):
        print("Output file must be a CSV file.")
        sys.exit(1)

    union_datasources_main(srcdir, output_file)
    sys.exit(0)
