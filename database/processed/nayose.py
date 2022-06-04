#!/usr/bin/env python3

import sys
import datetime
import re
from typing import List
from typing import Dict
import csv
from dateutil import parser

def nayose_main():
    base_data = prepare_data()
    hwname_data = fix_hwname(base_data)
    nayose_data = nayose_count(hwname_data)
    save_csv("nayose_weekly_hard_1999_2022.csv", nayose_data)

def save_csv(fname: str, data:List):
    data.insert(0, ["begin_date", "end_date", "hw", "units"])
    with open(fname, "w") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerows(data)
        print(f"{fname} is saved")

def prepare_data() -> List:
    data1 = load_csv("gamesdata_weekly_hard_201512.csv")
    data2 = load_csv("geimin_weekly_hard_1999_2015.csv")
    data3 = load_csv("teiten_weekly_hard_2016_2022.csv")
    data = []
    data.extend(data1[1:])
    data.extend(data2[1:])
    data.extend(data3[1:])
    return data

def load_csv(fname):
    with open(fname, "r") as f:
        reader = csv.reader(f)
        rows = []
        for row in reader:
            rows.append(row)
        return rows

def fix_hwname(data: List) -> List:
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
        'NSW':'Switch',
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

    hwlist = {}
    data2 = []
    for d in data:
        begin = parser.parse(d[0]).date()
        end = parser.parse(d[1]).date()
        hw = HWMAP[d[2]]
        units = int(d[3])
        data2.append([begin, end, hw, units])
    return data2

def nayose_count(data:List) -> List:
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
    nayose_main()
    sys.exit(0)
