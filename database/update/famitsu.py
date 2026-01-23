#! /usr/bin/env python3

import os
import sys
import re
import argparse
from datetime import datetime
from typing import Tuple, List

import requests
from bs4 import BeautifulSoup
from cachecontrol.caches import FileCache
from cachecontrol import CacheControlAdapter
from cachecontrol.heuristics import LastModified
from kanjize import kanji2number
import sqlite3


# ファミ通のハードウェア売上ページから、今週のハード売上リストと集計期間を取得する
def get_famitsu_hwsales_page(url: str) -> Tuple[List[str], List[str]]:
    """
    Fetch the Famitsu hardware sales page and extract the hardware sales list and reporting period.

    Args:
        url (str): The URL of the Famitsu hardware sales page.

    Returns:
        Tuple[List[str], str]: A tuple containing the list of raw hardware sales data and the reporting period string.
    """
    adapter = CacheControlAdapter(heuristic=LastModified(), cache=FileCache('_webcache'))
    session = requests.Session()
    session.mount('https://', adapter)
    response = session.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # ファミ通のハードウェア売上ページは、特定のクラス名を持つ要素からデータを抽出
    # ここでは、"article_detail_itemization_string"クラスのspan要素
    # と、"article_detail_annotation"クラスのspan要素を使用している
    # これらの要素から、ハードウェア売上のリストと集計期間を取得する
    items = soup.find_all("span", attrs={"class": "article_detail_itemization_string"})
    annotations = soup.find_all("span", attrs={"class": "article_detail_annotation"})

    raw_hard_sales = [item.get_text(strip=True) for item in items]
    raw_report_dates = [annotation.get_text(strip=True) for annotation in annotations if "集計期間" in annotation.get_text()]

    return raw_hard_sales, raw_report_dates


def parse_hard_sales_lines(lines: List[str]) -> List[List[str]]:
    """
    Parse the raw hardware sales lines to extract hardware names and weekly sales data.

    Args:
        lines (List[str]): List of raw hardware sales strings.

    Returns:
        List[List[str]]: A list of parsed hardware sales data, where each entry contains the hardware name and weekly sales units.
    """
    hard_sales = []
    for line in lines:
        hard_sales_line = []
        hw, rest = line.split("／", 1)
        weekly_units, cumulative_units = rest.split("台（累計")
        # cumulative_units = cumulative_units.rstrip("台）")
        hard_sales_line.append(hw.strip())
    
        sales_units = kanji2number(weekly_units.strip())
        hard_sales_line.append(sales_units)

        hard_sales.append(hard_sales_line)

    return hard_sales


def normalize_hw_units(hard_sales: List[List[str]]) -> List[List[str]]:
    """
    Normalize the hardware sales data by mapping hardware names to standardized identifiers and aggregating sales.

    Args:
        hard_sales (List[List[str]]): List of hardware sales data with hardware names and sales units.

    Returns:
        List[List[str]]: A list of normalized hardware sales data with standardized hardware identifiers and aggregated sales units.
    """
    HW_MAP = {
        "Switch2": "NS2",
        "Switch": "NSW",
        "Switch Lite": "NSW",
        "Nintendo Switch（有機ELモデル）": "NSW",
        "Switch（有機ELモデル）": "NSW",
        "PS5": "PS5",
        "PS5 デジタル・エディション": "PS5",
        "PS5 Pro": "PS5",
        "PS4": "PS4",
        "Xbox Series X": "XSX",
        "Xbox Series X デジタルエディション": "XSX",
        "Xbox Series S": "XSX"
    }

    normalized_sales = {}
    for hw, units in hard_sales:
        hw_name = HW_MAP.get(hw)
        normalized_sales[hw_name] = normalized_sales.get(hw_name, 0) + units

    normalized_list = []
    for hw, units in normalized_sales.items():
        normalized_list.append([hw, units])

    return normalized_list


def extract_date_range(date_strings: List[str]) -> Tuple[datetime, datetime]:
    """
    Extract the start and end dates from a date range string.

    Args:
        date_string (str): A string containing a date range in the format "YYYY年MM月DD日～MM月DD日" or "YYYY年MM月DD日～YYYY年MM月DD日".

    Returns:
        Tuple[datetime, datetime]: A tuple containing the start date and end date as datetime objects.

    Raises:
        ValueError: If the date range string is invalid or cannot be parsed.
    """
    # 正規表現で日付を抽出
    # date_stringsの末尾の要素から順に正規表現に一致しているか確認し、一致していたらその値を使用。
    # 一致していなかったらdata_stringsの前の要素を確認。
    # 最終的に一致する要素がなければ　ValueErrorを発生させる。
    match = False
    for ds in reversed(date_strings):
        if match := re.search(r"(\d{4}年\d{1,2}月\d{1,2}日)～(\d{1,2}月\d{1,2}日|\d{4}年\d{1,2}月\d{1,2}日)", ds):
            break
        if match := re.search(r"(\d{4}年\d{1,2}月\d{1,2}日)～年(\d{1,2}月\d{1,2}日)", ds):
            # 2026/01/22のミス表記対応
            break

    if not match:
        raise ValueError("有効な日付範囲が見つかりませんでした。")

    start_date_str, end_date_str = match.groups()

    # 開始日をdatetimeに変換
    start_date = datetime.strptime(start_date_str, "%Y年%m月%d日")

    # 終了日の年が含まれているか確認
    if "年" in end_date_str:
        end_date = datetime.strptime(end_date_str, "%Y年%m月%d日")
    else:
        # 開始日の年を使用して終了日を補完
        end_date = datetime.strptime(f"{start_date.year}年{end_date_str}", "%Y年%m月%d日")

    return start_date, end_date

def calculate_date_range_days(start_date: datetime, end_date: datetime) -> Tuple[datetime, int]:
    """
    Calculate the number of days in the date range from start_date to end_date (inclusive).

    Args:
        start_date (datetime): The start date of the range.
        end_date (datetime): The end date of the range.

    Returns:
        Tuple[datetime, int]: A tuple containing the end date and the number of days in the range.
    """
    delta_days = (end_date - start_date).days + 1  # +1 to include both start and end dates
    return end_date, delta_days

def upsert_to_database(db_path: str, newdata: List) -> None:
    """
    Insert or update hardware sales data into the database.

    Args:
        db_path (str): Path to the SQLite database file.
        newdata (List): List of new hardware sales data to be inserted or updated.

    Returns:
        None
    """
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

def famitsu_main(db_path: str, target_url: str, dry_run: bool = False) -> None:
    """
    Main function to process Famitsu hardware sales data and optionally insert it into the database.

    Args:
        db_path (str): Path to the SQLite database file.
        target_url (str): URL of the Famitsu hardware sales page.
        dry_run (bool, optional): If True, only print the data to be inserted without modifying the database. Defaults to False.

    Returns:
        None
    """
    raw_sales, raw_report_dates = get_famitsu_hwsales_page(target_url)

    parsed_list = parse_hard_sales_lines(raw_sales)
    normalized_list = normalize_hw_units(parsed_list)

    start_date, end_date = extract_date_range(raw_report_dates)
    end_date, period_date = calculate_date_range_days(start_date, end_date)
    end_date_str = end_date.strftime("%Y-%m-%d")

    new_record = [[f"{end_date_str}_{sales_line[0]}", end_date_str, period_date, sales_line[0], sales_line[1]] for sales_line in normalized_list]

    if dry_run:
        print("Dry run mode: Data to be inserted:")
        for record in new_record:
            print(record)
        return
    
    upsert_to_database(db_path, new_record)



if __name__ == "__main__":
    # 環境変数GAMEHARD_DBが指定されていれば、そこに接続する。
    # 指定されていない場合はエラー終了
    db_path = os.getenv('GAMEHARD_DB')
    if not db_path:
        print("Error: Environment variable GAMEHARD_DB is not set.")
        sys.exit(1)

    # 引数処理
    parser = argparse.ArgumentParser(description="Process Famitsu hardware sales data.")
    parser.add_argument("-c", "--commit", action="store_true", help="Commit changes to the database.")
    parser.add_argument("url", type=str, help="Target URL for Famitsu hardware sales data.")
    args = parser.parse_args()

    # URL検証
    target_url = args.url
    if not target_url.startswith("https://www.famitsu.com/"):
        print("Error: The URL must start with 'https://www.famitsu.com/'.")
        sys.exit(1)

    # dry_run設定
    dry_run = not args.commit

    # メイン処理呼び出し
    famitsu_main(db_path, target_url=target_url, dry_run=dry_run)
    sys.exit(0)

