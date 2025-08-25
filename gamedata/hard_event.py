# GameEvent取得用のユーティリティ関数群

import sqlite3
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Optional
import warnings


DB_PATH = '/Users/hide/Documents/sqlite3/gamehard.db'

def load_hard_event() -> pd.DataFrame:
    """
    sqlite3を使用してデータベースからハードウェアイベントデータを読み込む関数。
    日付関係のカラムをdatetime64[ns]型に変換して返す。
    
    Returns:
        pd.DataFrame: ハードウェアイベントデータのDataFrame。
                      日付カラム（event_date）はdatetime64[ns]型に変換済み。
    """
    # SQLite3データベースに接続
    conn = sqlite3.connect(DB_PATH)
    # SQLクエリを実行してデータをDataFrameに読み込む
    query = "SELECT event_date,hw,hw2,event_name,priority FROM gamehard_event ORDER BY event_date;"
    df = pd.read_sql_query(query, conn)
    
    # 接続を閉じる
    conn.close()

    # 日付をdatetime64[ns]型に変換
    df['event_date'] = pd.to_datetime(df['event_date'])
    
    # report_dateカラムを作成する。event_dateが日曜日ならそのまま、そうでなければ直近の日曜日を設定
    df['report_date'] = df['event_date'].apply(
        lambda d: d if d.weekday() == 6 else d + pd.offsets.Week(weekday=6)
    )
    df.set_index('report_date', inplace=True)
    return df

def filter_event(df: pd.DataFrame, 
                 start_date: Optional[datetime] = None, 
                 end_date: Optional[datetime] = None, 
                 hw: List[str] = [], priority:int = 3) -> pd.DataFrame:
    """
    ハードウェアイベントデータをフィルタリングする関数。

    Args:
        df (pd.DataFrame): フィルタリング対象のDataFrame。
        start_date (datetime): フィルタリング開始日。(始端にこの日付を含む) 指定されない場合は始端なし。
        end_date (datetime): フィルタリング終了日。(終端にこの日付を含む) 指定されない場合は終端なし。
        hw (Optional[str], optional): フィルタリングするハードウェア名。デフォルトはフィルタなし。
        priority (int, optional): フィルタリングする優先度。デフォルトは3。1,2,3のいずれかの値を指定すること(優先度1>2>3)

    Returns:
        pd.DataFrame: フィルタリング後のDataFrame。
    """
    filtered = df.copy()

    if start_date is not None:
        filtered = filtered.loc[filtered.index >= start_date]
    if end_date is not None:
        filtered = filtered.loc[filtered.index <= end_date]

    if len(hw) > 0:
        hw_mask = filtered['hw'].isin(hw)
        hw2_mask = filtered['hw2'].isin(hw)
        filtered = filtered.loc[hw_mask | hw2_mask]

    filtered = filtered[filtered['priority'] <= priority]

    return filtered