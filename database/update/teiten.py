#!/usr/bin/env python3

import os
import sys
import requests
import datetime
import re
from typing import List
import csv
from cachecontrol.caches import FileCache
from cachecontrol import CacheControlAdapter
from cachecontrol.heuristics import LastModified
from bs4 import BeautifulSoup

# pip install lockfileが必要です

# 定点観測サイトからハード週次データを取得する
def get_hwyear_page() -> List:
    URLBASE = "https://www.teitengame.com/"
    data_url = URLBASE + "hard.html"

    adapter = CacheControlAdapter(heuristic=LastModified(), cache=FileCache('_webcache'))
    session = requests.Session()
    session.mount('https://', adapter)
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
        elif "不明週" in data[0]:
            print(f"Warning: Unclear week data found at line {data}. Skipping this line.")
            continue
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
        row[0] = begin.date()
        row[1] = (begin + datetime.timedelta(offset - 1)).date()
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


def teiten2normalize(teiten_rows:List) -> List:
    HW_MAP = {
        'NINTENDOSWITCH': 'NSW', 
        "NINTENDOSWITCH2": 'NS2',
        'PS4': 'PS4',
        'PS5': 'PS5',
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

def save_csv(fname: str, data:List):
    with open(fname, "w") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerows(data)
        print(f"{fname} is saved")

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

def upsert_to_database(db_path:str, newdata:List) -> None:
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # upsert前の行数を取得
    cursor.execute('SELECT COUNT(*) FROM gamehard_weekly')
    before_count = cursor.fetchone()[0]

    for row in newdata:
        cursor.execute('''
            INSERT OR REPLACE INTO gamehard_weekly (id, report_date, period_date, hw, units)
            VALUES (?, ?, ?, ?, ?)
        ''', row)

    conn.commit()

    # upsert後の行数を取得
    cursor.execute('SELECT COUNT(*) FROM gamehard_weekly')
    after_count = cursor.fetchone()[0]

    added_count = after_count - before_count
    print(f"Data has been upserted to the database. {added_count} rows added (or replaced).")

    

def teiten_main(db_path:str, debug_mode = False):
    # 定点観測サイトからハード週次データをテーブル構造を維持したまま取得
    table_lines = get_hwyear_page()

    #　 テーブル構造から集計データ構造に整形。1行に1週間分の複数HWの売り上げデータが入る
    teiten_data = clean_hwyear_data_thisyear(table_lines)       

    # 1行　1データに正規化する。1行は1HWの1週間分の売り上げデータ
    normalized_data = teiten2normalize(teiten_data)

    # HWのバリアントを共通化し、値を合計する    
    hw_normalized_data = group_hard_variations(normalized_data)

    # データベース用のフォーマットに変換
    latest_data = convert_to_database_format(hw_normalized_data)

    if debug_mode:
        # デバッグモードでは、データをCSVファイルに保存
        save_csv("teiten_hard_weekly.csv", latest_data)
        print("Use -c option to commit changes to the database.")
        exit(0)

    # 本番モードでは、データベースにUPSERT
    upsert_to_database(db_path, latest_data)

    exit(0)


if __name__ == "__main__":
    # 環境変数GAMEHARD_DBが指定されていれば、そこに接続する。
    # 指定されていない場合はエラー終了
    db_path = os.getenv('GAMEHARD_DB')
    if not db_path:
        print("Error: Environment variable GAMEHARD_DB is not set.")
        sys.exit(1)

    # コマンドラインオプション -c の有無で debug_mode を切り替え
    debug_mode = True
    if '-c' in sys.argv:
        debug_mode = False

    teiten_main(db_path, debug_mode=debug_mode)
    sys.exit(0)

