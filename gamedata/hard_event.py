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


def add_event_positions(event_df: pd.DataFrame, pivot_df: pd.DataFrame, priority: int = 3) -> pd.DataFrame:
    """
    event_dfにx_pos（event_date）とy_pos（該当ハードの販売数）を追加し、条件に合わない行は除外した新しいDataFrameを返す。

    Args:
        event_df (pd.DataFrame): ゲームイベントデータ
        pivot_df (pd.DataFrame): 週次販売データのピボット
        priority (int): この値以下のpriorityのイベントのみ残す

    Returns:
        pd.DataFrame: x_pos, y_posを追加したイベントデータ（条件に合わない行は除外）
    """
    # priorityでフィルタ（指定値以下のみ残す）
    filtered_events = event_df[event_df['priority'] <= priority].copy()
    x_pos_list = []
    y_pos_list = []
    drop_indices = []

    for idx, event_row in filtered_events.iterrows():
        report_date = idx
        hw = event_row['hw']
        hw2 = event_row['hw2']
        y_pos = None

        # report_dateがpivot_dfのindexに存在しない場合は除外
        if report_date not in pivot_df.index:
            drop_indices.append(idx)
            continue

        pivot_row = pivot_df.loc[report_date]

        # hwの値がNAでなく、pivot_rowに存在する場合
        if pd.notna(hw) and hw in pivot_row and not pd.isna(pivot_row[hw]):
            y_pos = pivot_row[hw]
        # hw2の値がNAでなく、pivot_rowに存在する場合
        elif pd.notna(hw2) and hw2 in pivot_row and not pd.isna(pivot_row[hw2]):
            y_pos = pivot_row[hw2]
        else:
            drop_indices.append(idx)
            continue

        x_pos_list.append(event_row['event_date'])
        y_pos_list.append(y_pos)

    # drop_indicesで行を除外
    filtered_events = filtered_events.drop(index=drop_indices)
    filtered_events = filtered_events.assign(x_pos=x_pos_list, y_pos=y_pos_list)
    return filtered_events
