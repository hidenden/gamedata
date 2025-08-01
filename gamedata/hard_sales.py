# GameData分析用のユーティリティ関数群

import sqlite3
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Optional
import warnings


DB_PATH = '/Users/hide/Documents/sqlite3/gamehard.db'

def load_hard_sales(normalize7: bool = False) -> pd.DataFrame:
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

    # normalize7がTrueの場合、7日間集計に正規化
    if normalize7:
        df = normalize_7days(df)

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


def pivot_sales(df: pd.DataFrame, hw:List[str] = []) -> pd.DataFrame:
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

    return filtered_df.pivot(index='report_date', columns='hw', values='units')


def pivot_cumulative_sales(df: pd.DataFrame, hw:List[str] = []) -> pd.DataFrame:
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

    # ピボットテーブルを作成
    return filtered_df.pivot(index='report_date', columns='hw', values='sum_units')

def pivot_sales_by_delta(df: pd.DataFrame, mode:str = "week", hw:List[str] = []) -> pd.DataFrame:
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

    return filtered_df.groupby(["hw", index_col])['units'].sum().unstack('hw')


def pivot_cumulative_sales_by_delta(df: pd.DataFrame, mode:str = "week", hw:List[str] = []) -> pd.DataFrame:
    """
    ハードウェアの累計販売台数を発売日からの経過状況をインデックス、hwを列、unitsを値とするピボットテーブル形式で返す。
    Args:
        df: load_hard_sales()で取得したDataFrame
        mode: "day"、"month"または"year"を指定。日単位の集計なら"day"、月単位の集計なら"month"、年単位の集計なら"year"を指定。
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

    return filtered_df.groupby(["hw", index_col])['sum_units'].last().unstack('hw')

#    if len(hw) > 0:
#        return df[df['hw'].isin(hw)].pivot(index=index_col, columns='hw', values='sum_units')
#    else:
#        return df.pivot(index=index_col, columns='hw', values='sum_units')


def normalize_7days(df: pd.DataFrame) -> pd.DataFrame:
    """
    14日間の集計行を2つの7日間の集計行に分割し、7日間の集計行はそのまま保持して正規化する関数。
    
    Args:
        df: load_hard_sales()の戻り値のDataFrame
    
    Returns:
        pd.DataFrame: 全ての行が7日間集計に正規化されたDataFrame。
                      14日間の集計行は2つの7日間行に分割される。
    """
    # 7日間と14日間の行を分離
    df_7days = df[df['period_date'] == 7].copy()
    df_14days = df[df['period_date'] == 14].copy()

    # 7日でも14日でもない行があれば警告を出し、それらの行を除外
    invalid_rows = df[~df['period_date'].isin([7, 14])]
    if not invalid_rows.empty:
        unique_periods = invalid_rows['period_date'].unique()
        warnings.warn(f"集計日数が7日または14日でない行が{len(invalid_rows)}件見つかりました。"
                     f"period_date: {unique_periods}。これらの行は出力から除外されます。")
   
    # 14日間の行を7日間の2行に分割
    normalized_rows = []
    
    for _, row in df_14days.iterrows():
        # 第1週の行（前半7日間）
        row1 = row.copy()
        row1['period_date'] = 7
        row1['units'] = row['units'] // 2
        row1['avg_units'] = row1['units'] // 7
        row1['end_date'] = row['begin_date'] + timedelta(days=6)
        row1['report_date'] = row1['end_date']
        row1['year'] = row1['report_date'].year
        row1['month'] = row1['report_date'].month
        row1['mday'] = row1['report_date'].day
        row1['week'] = row1['report_date'].isocalendar().week
        
        # weekly_idを再生成
        row1['weekly_id'] = f"{row1['report_date'].strftime('%Y-%m-%d')}_{row1['hw']}"
        
        # delta_day, delta_week, delta_yearを再計算
        days_from_launch = (row1['report_date'] - row['launch_date']).days
        row1['delta_day'] = days_from_launch
        row1['delta_week'] = days_from_launch // 7
        row1['delta_year'] = row1['report_date'].year - row['launch_date'].year

        # sum_unitsを再計算（元の累計販売台数から前半週の販売台数を引いた値）
        row1['sum_units'] = row['sum_units'] - row1['units']
        
        normalized_rows.append(row1)
        
        # 第2週の行（後半7日間）
        row2 = row.copy()
        row2['period_date'] = 7
        row2['units'] = row['units'] - row1['units']  # 残りの販売台数
        row2['avg_units'] = row2['units'] // 7
        row2['begin_date'] = row1['end_date'] + timedelta(days=1)
        row2['end_date'] = row['end_date']
        row2['report_date'] = row2['end_date']
        row2['year'] = row2['report_date'].year
        row2['month'] = row2['report_date'].month
        row2['mday'] = row2['report_date'].day
        row2['week'] = row2['report_date'].isocalendar().week
        
        # weekly_idを再生成
        row2['weekly_id'] = f"{row2['report_date'].strftime('%Y-%m-%d')}_{row2['hw']}"
        
        # delta_day, delta_week, delta_yearを再計算
        days_from_launch = (row2['report_date'] - row['launch_date']).days
        row2['delta_day'] = days_from_launch
        row2['delta_week'] = days_from_launch // 7
        row2['delta_year'] = row2['report_date'].year - row['launch_date'].year
        
        # sum_unitsはそのまま（元の累計販売台数を保持）
        row2['sum_units'] = row['sum_units']
        
        normalized_rows.append(row2)
    
    # 結果をまとめる
    if normalized_rows:
        df_normalized_14days = pd.DataFrame(normalized_rows)
        result_df = pd.concat([df_7days, df_normalized_14days], ignore_index=True)
    else:
        result_df = df_7days
    
    # report_dateでソートし、インデックスを再設定
    result_df = result_df.sort_values(['report_date']).reset_index(drop=True)

    return result_df