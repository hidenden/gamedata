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

URLBASE = "https://web.archive.org/web/20160809181641/http://geimin.net/da/fa"

def build_main():
    scrap_geimin_all()

def scrap_geimin_all():
    page_list = [
        [501, 600], # おかしい
        [601, 700],
        [701, 800],
        [801, 900], # おかしい
        [901, 1000],
        [1001, 1100],
        [1101, 1200], # おかしい
        [1201, 1300],
        [1301, 1400],
        [1401, 1500]
        ]
    for i, p in enumerate(page_list):
        data = scrap_geimin(p[0], p[1])
        data = special_fix(i, data)
        save_geimin(i, data)

def scrap_geimin(start: int, end: int) -> List:
    data_url = f"{URLBASE}/{start}-{end}.php"
    res = download(data_url)
    return parse(BeautifulSoup(res.content, "html.parser"))

def special_fix(i:int, data:List) -> List:
    if i == 9:
        data[1][2] = data[1][2].replace('2015/09/14', '2015/09/21')
        return data
    else:
        return data

def save_geimin(index: int, data: List): 
    file_name = f"geimin_{index}.csv"
    with open(file_name, "w") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerows(data)
        print(file_name + " is saved")

def download(url) -> requests.Response:
    adapter = CacheControlAdapter(heuristic=LastModified(), cache=FileCache('_webcache'))
    session = requests.Session()
    session.mount('https://', adapter)
    return session.get(url)

def parse(soup: BeautifulSoup) -> List:
    tables = soup.findAll("table")
    rows = tables[4].findAll("tr")
    newdata = []
    for row in rows:
        cells = row.findAll("td")
        newline = []
        for cell in cells:
            t = cell.get_text("|")
            newline.append(cell.get_text("|").replace("\n", ""))

        newdata.append(newline)
    return newdata

if __name__ == "__main__":
    build_main()
    sys.exit(0)
