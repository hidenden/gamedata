#!/usr/bin/env python3

import sys
import datetime
import re
from typing import List
from typing import Dict
import csv

def geimin_filter_main(srcdir:str, out_path:str):
    all_data_list = []
    for i in range(10):
        csv_rows = load_geimin_csv(srcdir, i)
        csv_data = parse_geimin_csv(csv_rows[1:])
        all_data_list.extend(csv_data)

    fixed_list = fix_2week(all_data_list)
    save_csv(out_path, fixed_list)
    
def save_csv(fname: str, data:List):
    with open(fname, "w") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerows(data)
        print(f"{fname} is saved")

def fix_2week(rows:List) -> List:
    simple_rows = []
    double_rows = []
    for row in rows:
        if '/' in row[3]:
            double_rows.append(row)
        else:
            row[3] = int(row[3])
            simple_rows.append(row)
    
    doubles = []
    for row in double_rows:
        unit0, unit1 = row[3].split('/')
        begin0 = row[0]
        end0 = begin0 + datetime.timedelta(6)
        begin1 = begin0 + datetime.timedelta(7)
        end1 = row[1]
        doubles.append([begin0, end0, row[2], int(unit0)])
        doubles.append([begin1, end1, row[2], int(unit1)])
    
    simple_rows.extend(doubles)
    sorted_rows = sorted(simple_rows, key=lambda x: x[0])
    header = ["begin_date", "end_date", "hw", "units"]
    sorted_rows.insert(0, header)
    return sorted_rows


def parse_geimin_csv(csv_rows: List[str]) -> List:
    all_data = []
    for row in csv_rows:
        data_dict = parse_row(row)
        if len(data_dict["hw"].keys()) == 0:
            continue
        data_list = datalines(data_dict)
        all_data.extend(data_list)
    return all_data

def load_geimin_csv(srcdir:str, index: int) -> List: 
    file_name = f"{srcdir}/geimin_{index}.csv"
    with open(file_name, "r") as f:
        reader = csv.reader(f)
        rows = []
        for row in reader:
            rows.append(row)
        return rows

def parse_hw_cell(a_cell):
    a_cell = a_cell.replace('（2週分）', '')
    hwlines = a_cell.split('|')
    hwdata = {}
    for d in hwlines:
        if '不明' in d:
            continue
        hw_raw_data = d.split(' ')
        if len(hw_raw_data) == 2:
            hwdata[hw_raw_data[0]] = hw_raw_data[1]
    return hwdata

def parse_date(a_cell):
    res = re.search('([0-9]+)/([0-9]+)/([0-9]+)〜([0-9]+)/([0-9]+)/([0-9]+)', a_cell)
    if res:
        (begin_y, begin_m, begin_d, end_y, end_m, end_d) = res.groups()
    else:
        res = re.search('([0-9]+)/([0-9]+)/([0-9]+)〜([0-9]+)/([0-9]+)', a_cell)
        if res:
            (begin_y, begin_m, begin_d, end_m, end_d) = res.groups()
            end_y = begin_y
        else:
            raise RuntimeError(f"Bad date string:{a_cell}")
           
    begin_date = datetime.date(int(begin_y), int(begin_m), int(begin_d))
    end_date = datetime.date(int(end_y), int(end_m), int(end_d))
    return [begin_date, end_date]

def parse_row(cells) -> Dict:
    hwdata = parse_hw_cell(cells[1])
    begin_date, end_date = parse_date(cells[2])
    return {"begin": begin_date,
            "end": end_date,
            "hw" : hwdata}

def datalines(row_dict) -> List:
    lines = []
    for hw_name in row_dict["hw"].keys():
        lines.append([row_dict["begin"],
                      row_dict["end"],
                      hw_name,
                      row_dict["hw"][hw_name]])
    return lines

if __name__ == "__main__":
    srcdir = "../raw"
    out_path = "../geimin_hard_weekly_1999_2015.csv"
    geimin_filter_main(srcdir, out_path)
    sys.exit(0)
    