# GameEvent取得用のユーティリティ関数群

import sqlite3
from datetime import datetime
import polars as pl
from typing import List, TypedDict, Dict, Any


DB_PATH = '/Users/hide/Documents/sqlite3/gamehard.db'

def load_hard_event() -> pl.DataFrame:
    """
    sqlite3を使用してデータベースからハードウェアイベントデータを読み込む関数。
    日付関係のカラムをdatetime型に変換して返す。
    
    Returns:
        pl.DataFrame: ハードウェアイベントデータのDataFrame。
                      日付カラム（event_date）はdatetime型に変換済み。
    """
    # SQLite3データベースに接続
    conn = sqlite3.connect(DB_PATH)
    # SQLクエリを実行してデータをDataFrameに読み込む
    query = "SELECT event_date,hw,event_name,event_type,priority FROM gamehard_event ORDER BY event_date;"
    df = pl.read_database(query, conn)
    
    # 接続を閉じる
    conn.close()

    # 日付をdatetime64[ns]型に変換
    df = df.with_columns(pl.col('event_date').str.to_datetime())
    
    # report_dateカラムを作成する。event_dateが日曜日ならそのまま、そうでなければ直近の日曜日を設定
    df = df.with_columns(
        pl.when(pl.col('event_date').dt.weekday() == 6)
          .then(pl.col('event_date'))
          .otherwise(pl.col('event_date') + pl.duration(days=(6 - pl.col('event_date').dt.weekday())))
          .alias('report_date')
    )
    return df

def delta_event(event_df: pl.DataFrame,
                info_df: pl.DataFrame) -> pl.DataFrame:
    """
    event_dfにinfo_dfのlaunch_dateを結合し、report_dateとlaunch_dateの
    差分からdelta_weekを計算して追加する関数。
    Args:
        event_df (pl.DataFrame): ハードウェアイベントデータ
        info_df (pl.DataFrame): ハードウェア情報データ
    Returns:
        pl.DataFrame: delta_weekが追加されたハードウェアイベントデータ
    """

    df_event_merged = event_df.join(info_df, left_on='hw', right_on="id", how='left')
    df_event_merged = df_event_merged.with_columns(
        ((pl.col('report_date') - pl.col('launch_date')).dt.total_days() // 7)
        .alias('delta_week')
    )

    df_event_merged = df_event_merged.select(['report_date', 'event_date', 
                                       'hw', 'event_name', 'event_type',
                                       'priority', 'delta_week'])
    return df_event_merged

class EventMasks(TypedDict, total=True):
    soft: float
    hard: float
    price: float
    sale: float
    event: float

EVENT_MASK_MIDDLE:EventMasks = {"hard":1.5, "price":3, "sale":2, "soft":1.5, "event":1}
EVENT_MASK_LONG:EventMasks = {"hard":0.5, "soft":0, "event":0, "price":0, "sale":0}
EVENT_MASK_SHORT:EventMasks = {"hard":2, "soft":4, "event":2, "price":4, "sale":5}

def mask_event(df: pl.DataFrame, 
               event_mask: EventMasks) -> pl.DataFrame:
    """
    イベントタイプと優先度に基づいてイベントデータをフィルタリングする関数。
    
    以下の全ての条件に合致する行を残し、それ以外は除外したDataFrameを返す：
    1. df['event_type']がevent_maskの属性名に含まれている
    2. df['priority'] <= event_mask[df['event_type']]の値
    
    Args:
        df (pl.DataFrame): フィルタリング対象のPolars DataFrame
        event_mask (EventMasks): イベントタイプごとの優先度閾値を持つEventMasksオブジェクト
        
    Returns:
        pl.DataFrame: フィルタリング後のPolars DataFrame
    """
    event_types = list(event_mask.keys())
    df = df.filter(pl.col('event_type').is_in(event_types))
    # dfのevent_typeに対応するevent_mask[event_type]の値をmask_priorityカラムとして追加
    df = df.with_columns(
        pl.col('event_type')
        .replace(event_mask, default=0.0)
        .alias('mask_priority')
    )
    # 追加したmask_priorityカラムを使用してフィルタリング
    df = df.filter(pl.col('priority') <= pl.col('mask_priority'))
    # 追加したmask_priorityカラムを削除
    df = df.drop('mask_priority')
    return df

def filter_event(df: pl.DataFrame, 
                 start_date: datetime | None = None, 
                 end_date: datetime | None = None, 
                 hw: List[str] = [], event_mask:EventMasks = {} ) -> pl.DataFrame:
    """
    ハードウェアイベントデータをフィルタリングする関数。

    Args:
        df (pl.DataFrame): フィルタリング対象のDataFrame。
        start_date (datetime): フィルタリング開始日。(始端にこの日付を含む) 指定されない場合は始端なし。
        end_date (datetime): フィルタリング終了日。(終端にこの日付を含む) 指定されない場合は終端なし。
        hw (Optional[str], optional): フィルタリングするハードウェア名。デフォルトはフィルタなし。
        priority (int, optional): フィルタリングする優先度。デフォルトは3。1,2,3のいずれかの値を指定すること(優先度1>2>3)

    Returns:
        pl.DataFrame: フィルタリング後のDataFrame。
    """
    # filtered = df.copy()

    if start_date is not None:
        df = df.filter(pl.col("report_date") >= start_date)
    if end_date is not None:
        df = df.filter(pl.col("report_date") <= end_date)

    if len(hw) > 0:
        df = df.filter(pl.col("hw").is_in(hw))
    df = mask_event(df, event_mask=event_mask)

    return df

def add_event_positions(event_df: pl.DataFrame, pivot_df: pl.DataFrame, 
                        event_mask:EventMasks = EventMasks()) -> pl.DataFrame:
    """
    event_dfにx_pos（event_date）とy_pos（該当ハードの販売数）を追加し、条件に合わない行は除外した新しいDataFrameを返す。

    Args:
        event_df (pl.DataFrame): ゲームイベントデータ
        pivot_df (pl.DataFrame): 週次販売データのピボット（Polars DataFrame）
        event_mask (EventMasks): イベントマスク

    Returns:
        pl.DataFrame: x_pos, y_posを追加したイベントデータ（条件に合わない行は除外）
    """
    # priorityでフィルタ（指定値以下のみ残す）
    filtered_events = mask_event(event_df, event_mask=event_mask)
    print(filtered_events.tail(10))

    pivot_columns = pivot_df.columns
    
    result_rows = []
    
    for row in filtered_events.iter_rows(named=True):
        report_date = row['report_date']
        hw = row['hw']
        
        # report_dateがpivot_dfに存在するか確認
        pivot_row = pivot_df.filter(pl.col('report_date') == report_date)
        print(f"Checking event: {row['event_name']} on {report_date}")
        
        if pivot_row.height == 0:
            continue
        else:
            print(f"Found matching report_date for event: {row['event_name']} on {report_date}")
        
        # hwカラムが存在し、値がNoneでない場合
        print(f"Processing event: {row['event_name']} on {report_date} for hw: {hw}")
        if hw is not None and hw in pivot_columns:
            y_pos_value = pivot_row[hw][0]
            
            # nullチェック
            if y_pos_value is not None:
                result_rows.append({
                    **row,
                    'x_pos': row['event_date'],
                    'y_pos': y_pos_value
                })
    
    if len(result_rows) == 0:
        # 空のDataFrameを返す（元のカラム + x_pos, y_posを持つ）
        return filtered_events.with_columns([
            pl.lit(None).cast(pl.Datetime).alias('x_pos'),
            pl.lit(None).cast(pl.Float64).alias('y_pos')
        ]).head(0)
    
    return pl.DataFrame(result_rows)


def add_event_positions_delta(event_df: pl.DataFrame, 
                              pivot_delta_df: pl.DataFrame, 
                              event_mask:EventMasks = EventMasks()) -> pl.DataFrame:
    """
    event_dfにx_pos（delta_week）とy_pos（該当ハードの累積販売数）を追加し、条件に合わない行は除外した新しいDataFrameを返す。

    Args:
        event_df (pl.DataFrame): ゲームイベントデータ
        pivot_delta_df (pl.DataFrame): 累積週次販売データのピボット（Polars DataFrame）
        event_mask (EventMasks): イベントマスク

    Returns:
        pl.DataFrame: x_pos, y_posを追加したイベントデータ（条件に合わない行は除外）
    """
    filtered_events = mask_event(event_df, event_mask=event_mask)
    print(filtered_events.tail(10))
    
    # pivot_delta_dfのカラムを取得
    pivot_columns = pivot_delta_df.columns
    result_rows = []
    for row in filtered_events.iter_rows(named=True):
        delta_week = row['delta_week']
        hw = row['hw']
        
        # delta_weekがpivot_delta_dfに存在するか確認
        pivot_row = pivot_delta_df.filter(pl.col('delta_week') == delta_week)
        
        if pivot_row.height == 0:
            continue
        
        # hwカラムが存在し、値がNoneでない場合
        if hw is not None and hw in pivot_columns:
            y_pos_value = pivot_row[hw][0]
            
            # nullチェック
            if y_pos_value is not None:
                result_rows.append({
                    **row,
                    'x_pos': delta_week,
                    'y_pos': y_pos_value
                })
    
    if len(result_rows) == 0:
        # 空のDataFrameを返す（元のカラム + x_pos, y_posを持つ）
        return filtered_events.with_columns([
            pl.lit(None).cast(pl.Int64).alias('x_pos'),
            pl.lit(None).cast(pl.Float64).alias('y_pos')
        ]).head(0)
    
    return pl.DataFrame(result_rows)

