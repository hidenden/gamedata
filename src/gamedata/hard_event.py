# GameEvent取得用のユーティリティ関数群

import sqlite3
from datetime import datetime
import pandas as pd
from typing import List, Optional


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
    query = "SELECT event_date,hw,event_name,event_type,priority FROM gamehard_event ORDER BY event_date;"
    df = pd.read_sql_query(query, conn)
    
    # 接続を閉じる
    conn.close()

    # 日付をdatetime64[ns]型に変換
    df['event_date'] = pd.to_datetime(df['event_date'])
    
    # report_dateカラムを作成する。event_dateが日曜日ならそのまま、そうでなければ直近の日曜日を設定
    df['report_date'] = df['event_date'].apply(
        lambda d: d if d.weekday() == 6 else d + pd.offsets.Week(weekday=6)
    )
    df.reset_index(inplace=True)
    return df

def delta_event(event_df: pd.DataFrame,
                info_df: pd.DataFrame) -> pd.DataFrame:
    """
    event_dfにinfo_dfのlaunch_dateを結合し、report_dateとlaunch_dateの
    差分からdelta_weekを計算して追加する関数。
    Args:
        event_df (pd.DataFrame): ハードウェアイベントデータ
        info_df (pd.DataFrame): ハードウェア情報データ
    Returns:
        pd.DataFrame: delta_weekが追加されたハードウェアイベントデータ
    """
    event_df = event_df.reset_index()
    df_event_merged = event_df.merge(info_df, left_on='hw', right_on="id", how='left')
    df_event_merged['delta_week'] = (df_event_merged['report_date'] - df_event_merged['launch_date']).dt.days // 7

    df_event_merged = df_event_merged[['report_date', 'event_date', 
                                       'hw', 'event_name', 'event_type',
                                       'priority', 'delta_week']]
    df_event_merged.reset_index(inplace=True)
    return df_event_merged

class EventMasks:
    def __init__(self, soft:float=1.0, hard:float=2.0, price:float=2.0, sale:float=1.0, event:float=3.0):
        self.soft = soft
        self.hard = hard
        self.price = price
        self.sale = sale
        self.event = event

def mask_event(df: pd.DataFrame, 
               event_mask:EventMasks = EventMasks()) -> pd.DataFrame:
    # 以下の全ての条件に合致する行を残す。それ以外は除外したDataFrameを返す。
    # 1. df['event_type']がevent_maskのキーに含まれている。
    # 2. df['priority'] <= event_mask[df['event_type']]
    mask = df['event_type'].isin(event_mask.__dict__.keys()) & (df['priority'] <= df['event_type'].map(lambda x: event_mask.__dict__.get(x, 0)))
    return df[mask]

def filter_event(df: pd.DataFrame, 
                 start_date: Optional[datetime] = None, 
                 end_date: Optional[datetime] = None, 
                 hw: List[str] = [], event_mask:EventMasks = EventMasks()) -> pd.DataFrame:
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
        filtered = filtered.loc[filtered["report_date"] >= start_date]
    if end_date is not None:
        filtered = filtered.loc[filtered["report_date"] <= end_date]

    if len(hw) > 0:
        hw_mask = filtered['hw'].isin(hw)
        filtered = filtered.loc[hw_mask]

    filtered = mask_event(filtered, event_mask=event_mask)

    return filtered


def add_event_positions(event_df: pd.DataFrame, pivot_df: pd.DataFrame, 
                        event_mask:EventMasks = EventMasks()) -> pd.DataFrame:
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
    filtered_events = event_df.copy()
    filtered_events = mask_event(filtered_events, event_mask=event_mask)
    x_pos_list = []
    y_pos_list = []
    drop_indices = []

    for idx, event_row in filtered_events.iterrows():
        report_date = event_row['report_date']
        hw = event_row['hw']
        y_pos = None

        # report_dateがpivot_dfのindexに存在しない場合は除外
        if report_date not in pivot_df.index:
            drop_indices.append(idx)
            continue

        pivot_row = pivot_df.loc[report_date]

        # hwの値がNAでなく、pivot_rowに存在する場合
        if pd.notna(hw) and hw in pivot_row and not pd.isna(pivot_row[hw]):
            y_pos = pivot_row[hw]
        else:
            drop_indices.append(idx)
            continue

        x_pos_list.append(event_row['event_date'])
        y_pos_list.append(y_pos)

    # drop_indicesで行を除外
    filtered_events = filtered_events.drop(index=drop_indices)
    filtered_events = filtered_events.assign(x_pos=x_pos_list, y_pos=y_pos_list)
    return filtered_events


def add_event_positions_delta(event_df: pd.DataFrame, 
                              pivot_delta_df: pd.DataFrame, 
                              event_mask:EventMasks = EventMasks()) -> pd.DataFrame:
    """
    event_dfにx_pos（event_date）とy_pos（該当ハードの販売数）を追加し、条件に合わない行は除外した新しいDataFrameを返す。

    Args:
        event_df (pd.DataFrame): ゲームイベントデータ
        pivot_delta_df (pd.DataFrame): 累積週次販売データのピボット
        event_mask (dict, optional): イベントマスク。デフォルトはDEFAULT_EVENT_MASK。

    Returns:
        pd.DataFrame: x_pos, y_posを追加したイベントデータ（条件に合わない行は除外）
    """
    filtered_events = event_df.copy()
    filtered_events = mask_event(filtered_events, event_mask=event_mask)
    x_pos_list = []
    y_pos_list = []
    drop_indices = []
    
    for idx, event_row in filtered_events.iterrows():
        delta_week = event_row['delta_week']
        hw = event_row['hw']
        y_pos = None

        # delta_weekがpivot_delta_dfのindexに存在しない場合は除外
        if delta_week not in pivot_delta_df.index:
            drop_indices.append(idx)
            continue

        pivot_row = pivot_delta_df.loc[delta_week]

        # hwの値がNAでなく、pivot_rowに存在する場合
        if pd.notna(hw) and hw in pivot_row and not pd.isna(pivot_row[hw]):
            y_pos = pivot_row[hw]
        else:
            drop_indices.append(idx)
            continue

        x_pos_list.append(delta_week)
        y_pos_list.append(y_pos)

    # drop_indicesで行を除外
    filtered_events = filtered_events.drop(index=drop_indices)
    filtered_events = filtered_events.assign(x_pos=x_pos_list, y_pos=y_pos_list)
    return filtered_events

EVENT_MASK_MIDDLE = EventMasks(hard=1.5, price=3, sale=2, soft=1.5, event=1)
EVENT_MASK_LONG = EventMasks(hard=0.5, soft=0, event=0, price=0, sale=0)
EVENT_MASK_SHORT = EventMasks(hard=2, soft=4, event=2, price=4, sale=5)
