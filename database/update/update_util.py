import os
import sys
import re
import argparse
from datetime import datetime
from typing import Tuple, List

import sqlite3


def validate_row(row) -> bool:
    """
    指定されたrowが登録条件を満たすかどうかを判定する。

    条件:
    - 要素数が6つであること
    - 2つ目の要素が 'YYYY-MM-DD' 形式の日付文字列であること
    - 3つ目の要素が0以上の整数（数値または数値文字列）であること
    - 5つ目の要素が0以上の整数（数値または数値文字列）であること

    Args:
        row (list or tuple): チェック対象のデータ行

    Returns:
        bool: 条件をすべて満たす場合はTrue、そうでない場合はFalse
    """
    # 要素数が5つ
    if len(row) != 6:
        print(f"Skip: Row does not have 5 elements: {row}")
        return False
    # 2つ目の要素: YYYY-MM-DD形式の日付
    try:
        datetime.strptime(row[1], "%Y-%m-%d")
    except Exception:
        print(f"Skip: Second element is not a valid date (YYYY-MM-DD): {row}")
        return False
    # 3つ目の要素: 0以上の整数
    try:
        val3 = int(row[2])
        if val3 < 0:
            raise ValueError
    except Exception:
        print(f"Skip: Third element is not a non-negative integer: {row}")
        return False
    # 5つ目の要素: 0以上の整数
    try:
        val5 = int(row[4])
        if val5 < 0:
            raise ValueError
    except Exception:
        print(f"Skip: Fifth element is not a non-negative integer: {row}")
        return False
    # 6つ目の要素: 整数(負数を許容)
    try:
        val6 = int(row[5])
    except Exception:
        print(f"Skip: Sixth element is not an integer: {row}")
        return False

    return True


def upsert_to_database(db_path: str, newdata: List, precheck: bool = False, dryrun: bool = True) -> None:
    """
    Insert or update hardware sales data into the database.

    Args:
        db_path (str): Path to the SQLite database file.
        newdata (List): List of new hardware sales data to be inserted or updated.
        precheck (bool): If True, perform a pre-check before inserting data.
        dryrun (bool): If True, do not actually perform the database operations.

    Returns:
        None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # upsert前の行数を取得
        cursor.execute('SELECT COUNT(*) FROM gamehard_weekly')
        before_count = cursor.fetchone()[0]

        for row in newdata:
            if not validate_row(row):
                continue

            if (precheck):
                # Pre-check: Check if the row already exists
                cursor.execute('SELECT COUNT(*) FROM gamehard_weekly WHERE id = ?', (row[0],))
                exists = cursor.fetchone()[0]
                if exists:
                    print(f"Row with id {row[0]} already exists. Skipping insert.")
                    continue

            if dryrun:
                print(f"Dry run: Would insert row {row}")
                continue

            cursor.execute('''
                INSERT OR REPLACE INTO gamehard_weekly (id, report_date, period_date, hw, units, adjust_units)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', row)

        conn.commit()

        # upsert後の行数を取得
        cursor.execute('SELECT COUNT(*) FROM gamehard_weekly')
        after_count = cursor.fetchone()[0]

        added_count = after_count - before_count
        print(f"Data has been upserted to the database. {added_count} rows added (or replaced).")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        if not dryrun:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()





