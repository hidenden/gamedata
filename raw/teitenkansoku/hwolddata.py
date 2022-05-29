#!/usr/bin/env python3

import sys
import requests
from cachecontrol.caches import FileCache
from cachecontrol import CacheControlAdapter
from cachecontrol.heuristics import LastModified
from bs4 import BeautifulSoup
import datetime
import re
from typing import List
import csv

# pip install lockfileが必要です

def hwhist_main():
    get_hwhist()

def get_hwhist() -> None:
    lines = arrange_hwhist_data(get_hwhist_page())
    save_hwhist(lines)

def save_hwhist(data:List) -> None:
    file_name = "hwdata_old.csv"
    with open(file_name, "w") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerows(data)
        print(file_name + " is saved")

def get_hwhist_page() -> List:
    URLBASE = "http://www.teitengame.com/"
    data_url = URLBASE + "hard_rekidai.html"

    adapter = CacheControlAdapter(heuristic=LastModified(), cache=FileCache('_webcache'))
    session = requests.Session()
    session.mount('http://', adapter)
    response = session.get(data_url)
    soup = BeautifulSoup(response.content, "html.parser")
    tables = soup.findAll("table", attrs={"class": "table1"})
    rows = tables[1].findAll(["tr"])

    lines = []
    for row in rows:
        csv_row = []
        for cell in row.findAll(['td', 'th']):
            csv_row.append(cell.get_text().replace("\n", "").replace(" ", "").replace('\xa0', ""))
        lines.append(csv_row)

    return lines

def arrange_hwhist_data(rawdata:List) -> List:
    history_data = {}
    for row in rawdata:
        nums = row[1:]
        key = row[0]
        if key in history_data.keys():
            history_data[key] += nums
        else:
            history_data[key] = nums

    years = history_data.pop("機種")
    hards = list(history_data.keys())
    hards.sort()  
    header = ["begin_date", "end_date"] + hards

    datalist = []
    datalist.append(header)
    for index, v in enumerate(years):
        line = []
        m = re.match(r'([0-9]+)年', v)
        year = int(m.groups()[0])
        if 2016 <= year:
            break
        begin_date = datetime.date(year, 1, 1)
        end_date =  begin_date + datetime.timedelta(364)
        line.append(str(begin_date))
        line.append(str(end_date))
        for m in hards:
            v = history_data[m][index]
            if v != "":
                v = float(v) * 10000
            line.append(v)
            
        datalist.append(line)    

    return datalist

if __name__ == "__main__":
    hwhist_main()
    sys.exit(0)
