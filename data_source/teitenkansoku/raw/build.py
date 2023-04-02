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

def hwdata_main():
    for y in range(2016, 2024):
        get_hwdata(y)

def get_hwdata(year:int) -> None:
    if year <= 2016:
        lines = clean_hwyear_data_2016(get_hwyear_page(year))
    elif year == get_this_year():
        lines = clean_hwyear_data_thisyear(get_hwyear_page(year))       
    elif year == 2019:
        lines = clean_hwyear_data_2019(get_hwyear_page(year))       
    else:
        lines = clean_hwyear_data_2017(get_hwyear_page(year))

    save_hwdata(year, lines)

def save_hwdata(year:int, data:List) -> None:
    file_name = "hwdata_" + str(year) + ".csv"
    with open(file_name, "w") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerows(data)
        print(file_name + " is saved")

def get_this_year() -> int:
    return 2023

def get_hwyear_page(year: int) -> List:
    URLBASE = "http://www.teitengame.com/"
    year_name = ""
    if year != get_this_year():
        year_name = "_" + str(year)
    data_url = URLBASE + "hard" + year_name + ".html"

    adapter = CacheControlAdapter(heuristic=LastModified(), cache=FileCache('_webcache'))
    session = requests.Session()
    session.mount('http://', adapter)
    response = session.get(data_url)
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", attrs={"class": "table1"})
    rows = table.findAll(["tr"])

    lines = []
    for row in rows:
        csv_row = []
        for cell in row.findAll(['td', 'th']):
            csv_row.append(cell.get_text().replace("\n", "").replace(" ", ""))
        lines.append(csv_row)
    lines[0][0] = ""
    return lines

def clean_hwyear_data_2016(rawdata:List) -> List:
    header = rawdata[0]
    body = rawdata[2:-1]
    newdata = [header]
    for line in body:
        top = line[0]
        if "販売台数" in top:
            offset = 3
        elif "月" in top:
            offset = 2
        elif "週" in top:
            offset = 1
        else:
            offset = 0
        
        newline = []
        for i in range(0, offset):
            newline.append(line[i])
        
        max = len(line)
        for i in range(offset, max, 2):
            newline.append(line[i])
        newdata.append(newline)

    return clean_hwyear_data(newdata)

def clean_hwyear_data_2017(rawdata:List) -> List:
    lines = rawdata[0:-2]
    return clean_hwyear_data(lines)

def clean_hwyear_data_2019(rawdata:List) -> List:
    lines = rawdata[0:-3]
    return clean_hwyear_data(lines)

def clean_hwyear_data_thisyear(rawdata:List) -> List:
    header = rawdata[0]
    body = rawdata[1:-4]
    newdata = [header]
    skip = True
    for line in body:
        if "年販売台数" in line[0]:
            skip = False
        if skip:
            continue
        newdata.append(line)
    return clean_hwyear_data(newdata)
    
def clean_hwyear_data(rawdata:List) -> List:
    header = [''] + rawdata[0]
    header[0] = 'begin_date'
    header[1] = 'end_date'

    year = 2020
    time_stamp = datetime.datetime(year, 1, 1, 0, 0, 0)
    index_offset = 0
    clean_data = []

    for i,data in enumerate(rawdata[1:]):
        numbers = []
        clean_line = []
        if "年販売台数" in data[0]:
            # ここは最初の年のやつ
            m = re.match(r'([0-9]+)年販売台数', data[0])
            year = int(m.groups()[0])
            time_stamp = nth_aggregate_day(year, 0)
            index_offset = i
            numbers = data[3:]
        elif "月" in data[0]:
            numbers = data[2:]
            time_stamp = nth_aggregate_day(year, i - index_offset)
        else:
            numbers = data[1:]
            time_stamp = nth_aggregate_day(year, i - index_offset)

        if len(numbers) == 0:
            clean_data[-1][1] = clean_data[-1][1] + 7
        else:
            clean_line.append(time_stamp)
            clean_line.append(7)
            numlist = []
            for n in numbers:
                n2 = n.replace('\xa0', "").replace(",", "")
                if n2 != "":
                    numlist.append(int(n2))
                else:
                    numlist.append('')              
            clean_line.extend(numlist)
            clean_data.append(clean_line)

    arranged_data = []
    for row in clean_data:
        begin = row[0]
        offset = row[1]
        row[0] = str(begin.date())
        row[1] = str((begin + datetime.timedelta(offset)).date())
        arranged_data.append(row)

    return [header] + arranged_data
    

def nth_aggregate_day(year:int, nth:int) -> datetime.datetime:
    # get first sunday
    new_year_day = datetime.datetime(year, 1, 1, 0, 0, 0)
    first_sunday = new_year_day
    first_weekday = new_year_day.weekday()
    if first_weekday != 6:
        delta_day = 6 - first_weekday
        first_sunday = new_year_day + datetime.timedelta(days = delta_day)
    
    delta_day = nth * 7
    target_day = first_sunday + datetime.timedelta(days = delta_day) + datetime.timedelta(days = -6)
    return target_day




if __name__ == "__main__":
    hwdata_main()
    sys.exit(0)
