#!/usr/bin/env python3

import sys
import datetime
from dateutil import parser
from typing import List
from typing import Dict
import util

def seven_days_main(csv_file:str):
    src_data = util.load_csv(csv_file)
    seven_days_data = seven_days(src_data[1:])
    seven_days_data = util.insert_header(seven_days_data)
    util.save_csv("hard_weekly.csv", seven_days_data)

def seven_days(data:List) -> List:
    newdata = []
    for row in data:
        line = row
        line[0] = parser.parse(row[0]).date()
        line[1] = parser.parse(row[1]).date()
        newdata.append(line)

    return fix_7days(newdata)

def fix_7days(src_data: List) -> List:
    data2 = []
    for src in src_data:
        begin = src[0]
        end = src[1]
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
    csv_file = "unioned_hard_weekly.csv"
    seven_days_main(csv_file)
    sys.exit(0)
