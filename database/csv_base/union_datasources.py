#!/usr/bin/env python3

import sys
from typing import List
from dateutil import parser
import util

def union_datasources_main(srcdir:str):
    fixed_data = util.insert_header(union_datasource(srcdir))
    util.save_csv("unioned_hard_weekly.csv", fixed_data)

def union_datasource(srcdir:str) -> List:
    base_data = concat_all_source(srcdir)
    cleaned_data = clean_data(base_data)
    return group_hard_variations(cleaned_data)

def get_this_year() -> int:
    return 2025

def concat_all_source(srcdir:str) -> List:
    this_year = get_this_year()
    data1 = util.load_csv(f"{srcdir}/gamesdata/gamesdata_hard_weekly_2015_12.csv")
    data2 = util.load_csv(f"{srcdir}/geimin_net/geimin_hard_weekly_1999_2015.csv")
    data3 = util.load_csv(f"{srcdir}/teitenkansoku/teiten_hard_weekly_2016_{this_year}.csv")
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
        'NSW':'Switch',
        'NSW2':'Switch2',
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
    data_soruce = "../../data_source"
    union_datasources_main(data_soruce)
    sys.exit(0)
