#!/usr/bin/env python3

import os
import sys
from datetime import datetime, date

def insert_weekly_analysis(db_path: str, debug_mode: bool = False) -> None:
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # gamehard_infoの発売日を辞書化
    cursor.execute("SELECT id, launch_date FROM gamehard_info")
    launch_map = {row[0]: row[1] for row in cursor.fetchall()}

    # gamehard_weeklyをreport_date昇順（古い順）で取得
    cursor.execute("SELECT id, report_date, hw, units, period_date FROM gamehard_weekly ORDER BY report_date ASC, hw")
    rows = cursor.fetchall()

    # テーブル全体を削除
    cursor.execute("DELETE FROM gamehard_weekly_analysis")

    # 累計台数計算用
    sum_units_map = {}

    analysis_data = []
    for row in rows:
        id, report_date, hw, units, period_date = row

        units = int(units)
        period_date = int(period_date)
        launch_date_str = launch_map[hw]
        launch_dt = datetime.strptime(launch_date_str, "%Y-%m-%d").date()
        report_dt = datetime.strptime(report_date, "%Y-%m-%d").date()

        # 年月日
        year = report_dt.year
        month = report_dt.month
        mday = report_dt.day
        week = int(report_dt.isocalendar()[1])

        # 発売からの差分
        delta_day = (report_dt - launch_dt).days
        delta_week = delta_day // 7
        delta_year = report_dt.year - launch_dt.year

        # 累計台数
        key = hw
        prev_sum = sum_units_map.get(key, 0)
        sum_units = prev_sum + units
        sum_units_map[key] = sum_units

        # 1日あたり販売台数
        avg_units = units // period_date if period_date > 0 else 0
        
        analysis_data.append([
            id, year, month, mday, week, delta_day, delta_week, delta_year, avg_units, sum_units
        ])

    # 全件INSERT
    if analysis_data:
        cursor.executemany('''
            INSERT INTO gamehard_weekly_analysis
            (id, year, month, mday, week, delta_day, delta_week, delta_year, avg_units, sum_units)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', analysis_data)
        if debug_mode:
            print(f"{len(analysis_data)} 行を再構築しました。")
    else:
        if debug_mode:
            print("追加する行はありません。")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    db_path = os.getenv('GAMEHARD_DB')
    if not db_path:
        print("Error: Environment variable GAMEHARD_DB is not set.")
        sys.exit(1)

    insert_weekly_analysis(db_path, debug_mode=True)
