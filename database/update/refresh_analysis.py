#!/usr/bin/env python3

"""gamehard_weeklyの14日集計を7日×2に正規化し、分析テーブルを再構築するユーティリティ。
- normalize7_db(): period_date=14 の行を 7 日×2 に分割してINSERT/UPDATEする
- insert_weekly_analysis(): gamehard_weekly_analysis を全件削除してから再生成する
"""

import os
import sys
from datetime import datetime, date, timedelta
import sqlite3

def insert_weekly_analysis(db_path: str, debug_mode: bool = True) -> None:
    """gamehard_weekly の内容から gamehard_weekly_analysis を再構築する。
    
    Args:
        db_path: SQLiteデータベースのパス。
        debug_mode: True の場合、処理件数などを標準出力に表示。
    
    処理概要:
        - gamehard_info から発売日を取得し辞書化。
        - gamehard_weekly を report_date, hw で昇順取得。
        - gamehard_weekly_analysis をDELETEで全消去。
        - 各行について以下を算出し一括INSERT:
          - begin_date = report_date - (period_date - 1)
          - year, month, mday, week(report_dateがその月で何回目の日曜日か)
          - delta_day/week/month/year（発売日との差分）
          - avg_units = units // period_date（整数除算）
          - sum_units = ハード別の累計台数（昇順で加算）
    
    Side Effects:
        - gamehard_weekly_analysis テーブルを削除・再挿入する。
    """

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # gamehard_infoの発売日を辞書化
    cursor.execute("SELECT id, launch_date FROM gamehard_info")
    launch_map = {row[0]: row[1] for row in cursor.fetchall()}

    # gamehard_weeklyをreport_date昇順（古い順）で取得
    cursor.execute("SELECT id, report_date, hw, units, adjust_units, period_date FROM gamehard_weekly ORDER BY report_date ASC, hw")
    rows = cursor.fetchall()

    # テーブル全体を削除
    if debug_mode:
        print("[DELETE予定] gamehard_weekly_analysis テーブル全件削除")
    else:
        cursor.execute("DELETE FROM gamehard_weekly_analysis")

    # 累計台数計算用
    sum_units_map = {}

    analysis_data = []
    for row in rows:
        id, report_date, hw, units, adjust_units, period_date = row

        units = int(units)
        adjust_units = int(adjust_units)
        units += adjust_units  # 調整値を加算
        period_date = int(period_date)
        launch_date_str = launch_map[hw]
        launch_dt = datetime.strptime(launch_date_str, "%Y-%m-%d").date()
        report_dt = datetime.strptime(report_date, "%Y-%m-%d").date()

        # begindateを計算
        begin_date = report_dt - timedelta(days=period_date - 1)

        # 年月日
        year = report_dt.year
        month = report_dt.month
        mday = report_dt.day
        
        # 週番号、report_dateがその月で何回目の日曜日か
        week = ((report_dt - report_dt.replace(day=1)).days // 7) + 1

        # 発売からの差分
        delta_day = (report_dt - launch_dt).days
        delta_week = delta_day // 7
        delta_year = report_dt.year - launch_dt.year
        
        # 発売からの月数差分（カレンダー月）
        delta_month = (report_dt.year - launch_dt.year) * 12 + (report_dt.month - launch_dt.month)

        # 累計台数
        key = hw
        prev_sum = sum_units_map.get(key, 0)
        sum_units = prev_sum + units
        sum_units_map[key] = sum_units

        # 1日あたり販売台数
        avg_units = units // period_date if period_date > 0 else 0
        
        analysis_data.append([
            id, begin_date, year, month, mday, week, delta_day, delta_week, delta_month, delta_year, avg_units, sum_units
        ])

    # 全件INSERT
    if analysis_data:
        if debug_mode:
            for rec in analysis_data:
                print(f"[INSERT] id={rec[0]}, begin_date={rec[1]}, year={rec[2]}, month={rec[3]}, mday={rec[4]}, week={rec[5]}, delta_day={rec[6]}, delta_week={rec[7]}, delta_month={rec[8]}, delta_year={rec[9]}, avg_units={rec[10]}, sum_units={rec[11]}")
            print(f"予定INSERT: {len(analysis_data)} 行")
        else:
            cursor.executemany('''
                INSERT INTO gamehard_weekly_analysis
                (id, begin_date, year, month, mday, week, delta_day, delta_week, delta_month, delta_year, avg_units, sum_units)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', analysis_data)
            print(f"{len(analysis_data)} 行を再構築しました。")
    else:
        if debug_mode:
            print("追加する行はありません。")
        else:
            print("追加する行はありません。")

    if not debug_mode:
        conn.commit()
    conn.close()

def normalize7_db(db_path:str, debug_mode:bool=True) -> None:
    """period_date=14 の週次データを 7 日×2 のレコードへ正規化する。
    
    Args:
        db_path: SQLiteデータベースのパス。
        debug_mode: True の場合、対象件数・INSERT/UPDATE件数を表示のみ（DB更新なし）。
    
    処理概要:
        - gamehard_weekly から period_date=14 の行を取得。
        - 各行について以下を実施:
          - 新規行: report_date を 7 日前にした日付、id は '{YYYY-MM-DD}_{hw}'。
          - units を半分に分割（new_units = units // 2、元行には残りを設定）。
          - 新規行を period_date=7, flag=1 で INSERT。
          - 元行を period_date=7, flag=1, units=残り で UPDATE。
        - debug_mode=True時はSQL実行せず内容のみ表示。
        - 全件処理後に commit（debug_mode=False時のみ）。
    
    注意:
        - 新規 id が既存と衝突する場合は INSERT で失敗する可能性がある。
        - 分割後の新旧2行の units 合計は元値と一致する。
    """

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        # period_date=14 のレコードを取得
        cursor.execute("""
            SELECT id, report_date, hw, units
            FROM gamehard_weekly
            WHERE period_date = 14
            ORDER BY report_date ASC, hw
        """)
        rows = cursor.fetchall()

        if debug_mode:
            print(f"period_date=14 のレコード: {len(rows)} 件（DB更新は行いません）")

        inserted = 0
        updated = 0

        for row in rows:
            orig_id, report_date_str, hw, units = row
            units = int(units)

            # 新しいreport_date（7日前）を計算
            report_dt = datetime.strptime(report_date_str, "%Y-%m-%d").date()
            new_report_dt = report_dt - timedelta(days=7)
            new_report_date_str = new_report_dt.strftime("%Y-%m-%d")

            # unitsを分割（整数切り捨て）
            new_units = units // 2
            remain_units = units - new_units  # 残り

            # 新しい行のidを生成
            new_id = f"{new_report_date_str}_{hw}"

            if debug_mode:
                print(f"[INSERT] id={new_id}, report_date={new_report_date_str}, hw={hw}, units={new_units}, period_date=7, flag=1")
                print(f"[UPDATE] id={orig_id}, units={remain_units}, period_date=7, flag=1")
                inserted += 1
                updated += 1
            else:
                # 新しい行をINSERT（period_date=7, flag=1）
                cursor.execute(
                    "INSERT INTO gamehard_weekly (id, report_date, hw, units, period_date, flag) VALUES (?, ?, ?, ?, ?, ?)",
                    (new_id, new_report_date_str, hw, new_units, 7, 1)
                )
                inserted += 1

                # 既存行をUPDATE（period_date=7, flag=1, unitsを残りへ）
                cursor.execute(
                    "UPDATE gamehard_weekly SET units = ?, period_date = ?, flag = ? WHERE id = ?",
                    (remain_units, 7, 1, orig_id)
                )
                updated += 1

        if not debug_mode:
            conn.commit()
            print(f"INSERT: {inserted} 行, UPDATE: {updated} 行")
        else:
            print(f"予定INSERT: {inserted} 行, 予定UPDATE: {updated} 行")
    finally:
        conn.close()

def main() -> None:
    """環境変数 GAMEHARD_DB のDBを対象に正規化と分析テーブル再構築を実行する。
    
    実行順:
        1) normalize7_db() で 14日集計の行を 7日×2 に分割
        2) insert_weekly_analysis() で分析用テーブルを再生成
    """
    db_path = os.getenv('GAMEHARD_DB')
    if not db_path:
        print("Error: Environment variable GAMEHARD_DB is not set.")
        sys.exit(1)

    # コマンドラインオプション -c の判定
    debug_mode = True
    if '-c' in sys.argv:
        debug_mode = False

    normalize7_db(db_path, debug_mode=debug_mode)
    insert_weekly_analysis(db_path, debug_mode=debug_mode)

if __name__ == "__main__":
    main()
