#!/usr/bin/env python3

import sys
import datetime
from dateutil import parser
from typing import List
from typing import Dict
import csv

def seven_days_main():
    src_data = load_csv("nayose_weekly_hard_1999_2022.csv")
    seven_days_data = fix_7days(src_data)
    save_csv("weekly_hard_1999_2022.csv", seven_days_data)

def save_csv(fname: str, data:List):
    data.insert(0, ["begin_date", "end_date", "hw", "units"])
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

def fix_7days(src_data: List) -> List:
    data2 = []
    for src in src_data[1:]:
        begin = parser.parse(src[0]).date()
        end = parser.parse(src[1]).date()
        delta = end - begin
        if datetime.timedelta(7) == delta:
            end = end - datetime.timedelta(1)
            delta = end - begin
        elif datetime.timedelta(14) == delta:
            end = end - datetime.timedelta(1)
            delta = end - begin        
        data2.append([begin, end, delta, src[2], int(src[3])])

    data7 = []
    data14 = []
    for d2 in data2:
        if datetime.timedelta(6) < d2[2]:
            data14.append(d2)
        else:
            data7.append(d2)

    newdata7 = []
    for d3 in data14:
        count = int(d3[4]/2)
        begin1 = d3[0]
        end1 = begin1 + datetime.timedelta(6)
        begin2 = end1 + datetime.timedelta(1)   
        end2 = d3[1]
        newdata7.append([begin1, end1, (end1 - begin1), d3[3], count])
        newdata7.append([begin2, end2, (end2 - begin2), d3[3], count])    
    data7.extend(newdata7)
    dataX = sorted(data7, key=lambda x:x[0])

    fixed_data = []
    for dx in dataX:
        fixed_data.append([dx[0],dx[1],dx[3],dx[4]])

    return fixed_data
    # return cut1998(fixed_data)

def cut1998(data:List) -> List:
    after1999 = []
    the_day = datetime.date(1999, 1, 1)
    for d in data:
        if the_day <= d[0]:
            after1999.append(d)
    return after1999

if __name__ == "__main__":
    seven_days_main()
    sys.exit(0)
