# GameData分析用のユーティリティ関数群

import sqlite3
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Optional
import warnings


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
    query = "SELECT * FROM hard_sales ORDER BY weekly_id;"
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


def get_hw_names(df: pd.DataFrame) -> List[str]:
    """
    DataFrameからハードウェア名のユニークなリストを取得する。
    
    Args:
        df: load_hard_sales()の戻り値のDataFrame
    
    Returns:
        List[str]: ハードウェア名のユニークなリスト
    """
    return df['hw'].unique().tolist()

def get_active_hw() -> List[str]:
    """
    現在アクティブなハードウェア名のリストを取得する。
    
    Returns:
        List[str]: アクティブなハードウェア名のリスト
    """
    # ここでは、NSW, NS2, PS5, XSXをアクティブと仮定
    return ['NSW', 'NS2', 'PS5', 'XSX']


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


def pivot_sales(df: pd.DataFrame, hw:List[str] = [], full_name:bool = False) -> pd.DataFrame:
    """
    ハードウェアの販売台数をピボットテーブル形式で返す。

    Args:
        df: load_hard_sales()で取得したDataFrame
        hw: プロットしたいハードウェア名のリスト。[]の場合は全ハードウェアを対象

    Returns:
        pd.DataFrame: report_dateをインデックス、hwを列、unitsを値とするピボットテーブル
    """
    # ピボットテーブルを作成
    if len(hw) > 0:
        filtered_df =  df[df['hw'].isin(hw)]
    else:
        filtered_df = df

    # 横軸のカラム
    columns_name = 'full_name' if full_name else 'hw'

    return filtered_df.pivot(index='report_date', columns=columns_name, values='units')


def pivot_cumulative_sales(df: pd.DataFrame, hw:List[str] = [], full_name:bool = False) -> pd.DataFrame:
    """
    ハードウェアの累計販売台数をピボットテーブル形式で返す。
    
    Args:
        df: load_hard_sales()で取得したDataFrame
        hw: プロットしたいハードウェア名のリスト。[]の場合は全ハードウェアを対象
    
    Returns:
        pd.DataFrame: report_dateをインデックス、hwを列、sum_unitsを値とするピボットテーブル
    """

    if len(hw) > 0:
        filtered_df = df[df['hw'].isin(hw)]
    else:
        filtered_df = df

    # 横軸のカラム
    columns_name = 'full_name' if full_name else 'hw'

    # ピボットテーブルを作成
    return filtered_df.pivot(index='report_date', columns=columns_name, values='sum_units')

def pivot_sales_by_delta(df: pd.DataFrame, mode:str = "week", hw:List[str] = [], full_name:bool = False) -> pd.DataFrame:
    """
    ハードウェアの販売台数を発売日からの経過状況をインデックス、hwを列、unitsを値とするピボットテーブル形式で返す。
    
    Args:
        df: load_hard_sales()で取得したDataFrame
        mode: "week"、"month"または"year"を指定。週単位の集計なら"week"、月単位の集計なら"month"、年単位の集計なら"year"を指定。
        hw: プロットしたいハードウェア名のリスト。[]の場合は全ハードウェアを対象

    Returns:
        pd.DataFrame: delta_week, delta_month, delta_yearのいずれかインデックス、hwを列、unitsを値とするピボットテーブル
    """
    # ピボットテーブルを作成
    if mode == "week":
        index_col = 'delta_week'
    elif mode == "month":
        index_col = 'delta_month'
    elif mode == "year":
        index_col = 'delta_year'
    else:
        raise ValueError("modeは'week', 'month', 'year'のいずれかを指定してください。")
    
    if len(hw) > 0:
        filtered_df = df[df['hw'].isin(hw)]
    else:
        filtered_df = df

    # 横軸のカラム
    columns_name = 'full_name' if full_name else 'hw'

    return filtered_df.pivot_table(
        index=index_col,
        columns=columns_name,
        values='units',
        aggfunc='sum'
    )


def pivot_cumulative_sales_by_delta(df: pd.DataFrame, mode:str = "week", hw:List[str] = [], full_name:bool = False) -> pd.DataFrame:
    """
    ハードウェアの累計販売台数を発売日からの経過状況をインデックス、hwを列、unitsを値とするピボットテーブル形式で返す。
    Args:
        df: load_hard_sales()で取得したDataFrame
        mode: "week"、"month"または"year"を指定。週単位の集計なら"week"、月単位の集計なら"month"、年単位の集計なら"year"を指定。
        hw: プロットしたいハードウェア名のリスト。[]の場合は全ハードウェアを対象

    Returns:
        pd.DataFrame: delta_week, delta_month, delta_yearのいずれかインデックス、hwを列、sum_unitsを値とするピボットテーブル
    """
    # ピボットテーブルを作成
    if mode == "week":
        index_col = 'delta_week'
    elif mode == "month":
        index_col = 'delta_month'
    elif mode == "year":
        index_col = 'delta_year'
    else:
        raise ValueError("modeは'week', 'month', 'year'のいずれかを指定してください。")

    if len(hw) > 0:
        filtered_df = df[df['hw'].isin(hw)]
    else:
        filtered_df = df

    # 横軸のカラム
    columns_name = 'full_name' if full_name else 'hw'

    return filtered_df.pivot_table(
        index=index_col,
        columns=columns_name,
        values='sum_units',
        aggfunc='last'
    )


def pivot_maker(df: pd.DataFrame, maker:List[str] = [], hw:List[str] = []) -> pd.DataFrame:
    """
    メーカー毎のハードウェアの販売台数をピボットテーブル形式で返す。

    Args:
        df: load_hard_sales()で取得したDataFrame
        maker: プロットしたいメーカー名のリスト。[]の場合は全メーカーを対象
        hw: プロットしたいハードウェア名のリスト。[]の場合は全ハードウェアを対象

    Returns:
        pd.DataFrame: report_dateをインデックス、maker_nameを列、unitsを値とするピボットテーブル
    """
    # hwでフィルタリング
    if len(hw) > 0:
        df = df[df['hw'].isin(hw)]

    # makerでフィルタリング
    if len(maker) > 0:
        df =  df[df['maker_name'].isin(maker)]

    # ピボットテーブルを作成
    return df.pivot_table(index='report_date',
                          columns='maker_name',
                          values='units',
                          aggfunc='sum')


