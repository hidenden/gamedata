# GameData分析用のユーティリティ関数群

import sqlite3
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Optional


DB_PATH = '/Users/hide/Documents/sqlite3/gamehard.db'

def load_hard_sales() -> pd.DataFrame:
    """
    sqlite3を使用してデータベースからハードウェア販売データを読み込む関数。
    日付関係のカラムをdatetime64[ns]型に変換して返す。
    
    Returns:
        pd.DataFrame: ハードウェア販売データのDataFrame。
                      日付カラム（begin_date, report_date, end_date, launch_date）は
                      datetime64[ns]型に変換済み。
    """
    # SQLite3データベースに接続
    conn = sqlite3.connect(DB_PATH)
    # SQLクエリを実行してデータをDataFrameに読み込む
    query = "SELECT * FROM hard_sales"
    df = pd.read_sql_query(query, conn)
    
    # 接続を閉じる
    conn.close()

    # 日付をdatetime64[ns]型に変換
    df['begin_date'] = pd.to_datetime(df['begin_date'])
    df['report_date'] = pd.to_datetime(df['report_date'])
    df['end_date'] = pd.to_datetime(df['end_date'])
    df['launch_date'] = pd.to_datetime(df['launch_date'])

    return df


def extract_week_reached_units(df: pd.DataFrame, threshold_units: int) -> pd.DataFrame:
    """
    累計販売台数が指定の値を超えた最初の週を見つける関数。
    
    Args:
        df: load_hard_sales()の戻り値のDataFrame
        threshold_units: 閾値となる累計販売台数
    
    Returns:
        pd.DataFrame: 累計販売台数がthreshold_unitsを超えた最初の週ごとに、その行を抽出したDataFrame。
                      ハードごと（hw）に最初に到達した週のみを返す。
                      どのハードも到達していなければ空DataFrameを返す。
    """
    result = []
    for hw, group in df.sort_values(['hw', 'report_date']).groupby('hw'):
        reached = group[group['sum_units'] >= threshold_units]
        if not reached.empty:
            result.append(reached.iloc[0])
    if result:
        return pd.DataFrame(result)
    else:
        # どのハードも到達していなければ空DataFrameを返す
        return df.iloc[0:0]


def extract_by_date(df: pd.DataFrame, date_str: str, hw_names: Optional[List[str]] = None) -> pd.DataFrame:
    """
    指定された日付の週に該当するデータを抽出する関数。
    
    Args:
        df: load_hard_sales()の戻り値のDataFrame（begin_date, end_date, report_dateはdatetime64[ns]型に変換済み）
        date_str: 抽出したい日付の文字列
        hw_names: 省略可能なハードウェア名のリスト。指定すると、そのハードウェアに限定して抽出
    
    Returns:
        pd.DataFrame: 指定された日付がbegin_dateからend_dateの範囲にある行を抽出したDataFrame
    """
    target_date = pd.to_datetime(date_str)

    # target_dateがbegin_dateからend_dateの範囲にある行を抽出
    # begin_dateとend_dateはdatetime64[ns]型なので、比較可能
    filtered_df = df[(df['begin_date'] <= target_date) & (df['end_date'] >= target_date)]

    # hw_namesが指定されている場合は、さらにフィルタリング
    if hw_names:
        filtered_df = filtered_df[filtered_df['hw'].isin(hw_names)]
    return filtered_df


def extract_latest(df: pd.DataFrame) -> pd.DataFrame:
    """
    DataFrameから最新の週を抽出する関数。
    
    Args:
        df: load_hard_sales()の戻り値のDataFrame
    
    Returns:
        pd.DataFrame: 最新のreport_dateを持つ行のDataFrame
    """
    target_date = df['report_date'].max()
    return df[df['report_date'] == target_date]


def extract_by_hw(df: pd.DataFrame, hw_names: List[str]) -> pd.DataFrame:
    """
    指定されたハードウェア名のデータのみを抽出する。
    
    Args:
        df: load_hard_sales()の戻り値のDataFrame
        hw_names: 抽出したいハードウェア名のリスト
    
    Returns:
        pd.DataFrame: 指定されたハードウェア名のデータのみを含むDataFrame
    """
    return df[df['hw'].isin(hw_names)]

def extract_by_maker(df: pd.DataFrame, makers: List[str]) -> pd.DataFrame:
    """
    指定されたメーカー名のデータのみを抽出する。
    
    Args:
        df: load_hard_sales()の戻り値のDataFrame
        makers: 抽出したいメーカー名のリスト
    
    Returns:
        pd.DataFrame: 指定されたメーカー名のデータのみを含むDataFrame
    """
    return df[df['maker_name'].isin(makers)]

def get_hw_names(df: pd.DataFrame) -> List[str]:
    """
    DataFrameからハードウェア名のユニークなリストを取得する。
    
    Args:
        df: load_hard_sales()の戻り値のDataFrame
    
    Returns:
        List[str]: ハードウェア名のユニークなリスト
    """
    return df['hw'].unique().tolist()

def extract_by_year(df: pd.DataFrame, year: int) -> pd.DataFrame:
    """
    指定された年のデータのみを抽出する。
    
    Args:
        df: load_hard_sales()の戻り値のDataFrame
        year: 抽出したい年
    
    Returns:
        pd.DataFrame: 指定された年のデータのみを含むDataFrame
    """
    return df[df['year'] == year]

def aggregate_monthly_sales(df: pd.DataFrame) -> pd.DataFrame:
    """
    月毎の販売台数と、その月までの累計販売台数（sum_units）を集計して返す。
    
    Args:
        df: load_hard_sales()の戻り値のDataFrame
    
    Returns:
        pd.DataFrame: 月毎の販売台数（monthly_units）と累計販売台数（sum_units）を含むDataFrame
    """
    # 月ごとの販売台数を集計
    monthly_sales = df.groupby(['year', 'month', 'hw']).agg({'units': 'sum'}).reset_index()
    monthly_sales.rename(columns={'units': 'monthly_units'}, inplace=True)

    # 月ごとの累計販売台数を計算
    monthly_sales['sum_units'] = (
        monthly_sales
        .sort_values(['hw', 'year', 'month'])
        .groupby('hw')['monthly_units']
        .cumsum()
    )

    return monthly_sales

def pivot_cumulative_sales_by_hw(df: pd.DataFrame, hw_names: List[str]) -> pd.DataFrame:
    """
    指定されたハードウェアの累計販売台数をピボットテーブル形式で返す。
    
    Args:
        df: load_hard_sales()で取得したDataFrame
        hw_names: 出力に含むハードウェア名のリスト
    
    Returns:
        pd.DataFrame: report_dateをインデックス、hwを列、sum_unitsを値とするピボットテーブル
    """
    # 指定されたハードウェアのデータのみを抽出
    filtered_df = extract_by_hw(df, hw_names)
    
    # ピボットテーブルを作成
    pivot_df = filtered_df.pivot(index='report_date', columns='hw', values='sum_units')

    return pivot_df

def pivot_monthly_cumulative_sales_by_hw(df: pd.DataFrame, hw_names: List[str]) -> pd.DataFrame:
    """
    指定されたハードウェアの月毎累計販売台数をピボットテーブル形式で返す。
    
    Args:
        df: load_hard_sales()で取得したDataFrame
        hw_names: 出力に含むハードウェア名のリスト
    
    Returns:
        pd.DataFrame: 月初日(毎月1日)をインデックス、hwを列、その月最初のsum_unitsを値とするピボットテーブル
    """
    # 指定されたハードウェアのデータのみを抽出
    filtered_df = extract_by_hw(df, hw_names)
    
    # 月初日(1日)のカラムを追加
    filtered_df = filtered_df.copy()
    filtered_df['month_start'] = filtered_df['report_date'].dt.to_period('M').dt.start_time
    
    # 各ハードウェア・月毎に最初のsum_unitsを取得
    monthly_first = (
        filtered_df
        .sort_values(['hw', 'report_date'])
        .groupby(['hw', 'month_start'])
        .first()
        .reset_index()
    )
    
    # ピボットテーブルを作成
    pivot_df = monthly_first.pivot(index='month_start', columns='hw', values='sum_units')
    
    return pivot_df

def pivot_cumulative_sales_by_delta_week(df: pd.DataFrame, hw_names: List[str]) -> pd.DataFrame:
    """
    指定されたハードウェアの累計販売台数をピボットテーブル形式で返す（発売からの週数ベース）。
    
    Args:
        df: load_hard_sales()で取得したDataFrame
        hw_names: 出力に含むハードウェア名のリスト
    
    Returns:
        pd.DataFrame: delta_weekをインデックス、hwを列、sum_unitsを値とするピボットテーブル。
                      欠損値は後方補間（各ハードの後続の値で補填）される。
    """
    # 指定されたハードウェアのデータのみを抽出
    filtered_df = extract_by_hw(df, hw_names)
    
    # ピボットテーブルを作成
    pivot_df = filtered_df.pivot(index='delta_week', columns='hw', values='sum_units')
    
    # 各列（ハードウェア）ごとに後方補間を行う
    pivot_df = pivot_df.bfill()

    return pivot_df
