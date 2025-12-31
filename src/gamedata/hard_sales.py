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
        
        DataFrameのカラム詳細:
        - weekly_id (string): 週次データのID（gamehard_weekly.id）
        - begin_date (datetime64): 集計開始日（週の初日）、月曜日である
        - end_date (datetime64): 集計終了日（週の末日、=report_date）
        - report_date (datetime64): 集計期間の末日、日曜日である
        - period_date (int64): 集計日数(通常は7, 稀に14)
        - hw (string): ゲームハードの識別子
        - units (int64): 週次販売台数
        - adjust_units (int64): 週次販売台数の補正値(unitsは補正済みの値である)
        - year (int64): report_dateの年
        - month (int64): report_dateの月
        - mday (int64): report_dateの日
        - week (int64): report_dateがその月の何番目の日曜日か
        - delta_day (int64): 発売日から何日後か
        - delta_week (int64): 発売日から何週間後か
        - delta_month (int64): 発売日から何ヶ月後か
        - delta_year (int64): 発売年から何年後か(同じ年なら0)
        - avg_units (int64): 1日あたりの販売台数 (units / period_date)
        - sum_units (int64): report_date時点での累計販売台数
        - launch_date (datetime64): 発売日
        - maker_name (string): メーカー名
        - full_name (string): ゲームハードの正式名称
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
        
        DataFrameのカラム詳細:
        - weekly_id (string): 週次データのID（gamehard_weekly.id）
        - begin_date (datetime64): 集計開始日（週の初日）、月曜日である
        - end_date (datetime64): 集計終了日（週の末日、=report_date）
        - report_date (datetime64): 集計期間の末日、日曜日である
        - period_date (int64): 集計日数(通常は7, 稀に14)
        - hw (string): ゲームハードの識別子
        - units (int64): 週次販売台数
        - adjust_units (int64): 週次販売台数の補正値(unitsは補正済みの値である)
        - year (int64): report_dateの年
        - month (int64): report_dateの月
        - mday (int64): report_dateの日
        - week (int64): report_dateがその月の何番目の日曜日か
        - delta_day (int64): 発売日から何日後か
        - delta_week (int64): 発売日から何週間後か
        - delta_month (int64): 発売日から何ヶ月後か
        - delta_year (int64): 発売年から何年後か(同じ年なら0)
        - avg_units (int64): 1日あたりの販売台数 (units / period_date)
        - sum_units (int64): report_date時点での累計販売台数
        - launch_date (datetime64): 発売日
        - maker_name (string): メーカー名
        - full_name (string): ゲームハードの正式名称
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


def extract_by_date(df: pd.DataFrame, target_date:datetime, hw: Optional[List[str]] = None) -> pd.DataFrame:
    """
    指定された日付の週に該当するデータを抽出する関数。
    
    Args:
        df: load_hard_sales()の戻り値のDataFrame（begin_date, end_date, report_dateはdatetime64[ns]型に変換済み）
        target_date: 抽出したい日付のdatetime型
        hw: 省略可能なハードウェア名のリスト。指定すると、そのハードウェアに限定して抽出
    
    Returns:
        pd.DataFrame: 指定された日付がbegin_dateからend_dateの範囲にある行を抽出したDataFrame
        
        DataFrameのカラム詳細:
        - weekly_id (string): 週次データのID（gamehard_weekly.id）
        - begin_date (datetime64): 集計開始日（週の初日）、月曜日である
        - end_date (datetime64): 集計終了日（週の末日、=report_date）
        - report_date (datetime64): 集計期間の末日、日曜日である
        - period_date (int64): 集計日数(通常は7, 稀に14)
        - hw (string): ゲームハードの識別子
        - units (int64): 週次販売台数
        - adjust_units (int64): 週次販売台数の補正値(unitsは補正済みの値である)
        - year (int64): report_dateの年
        - month (int64): report_dateの月
        - mday (int64): report_dateの日
        - week (int64): report_dateがその月の何番目の日曜日か
        - delta_day (int64): 発売日から何日後か
        - delta_week (int64): 発売日から何週間後か
        - delta_month (int64): 発売日から何ヶ月後か
        - delta_year (int64): 発売年から何年後か(同じ年なら0)
        - avg_units (int64): 1日あたりの販売台数 (units / period_date)
        - sum_units (int64): report_date時点での累計販売台数
        - launch_date (datetime64): 発売日
        - maker_name (string): メーカー名
        - full_name (string): ゲームハードの正式名称

    """
    # target_dateがbegin_dateからend_dateの範囲にある行を抽出
    filtered_df = df[(df['begin_date'] <= target_date) & (df['end_date'] >= target_date)]

    # hw_namesが指定されている場合は、さらにフィルタリング
    if hw:
        filtered_df = filtered_df[filtered_df['hw'].isin(hw)]
    return filtered_df


def extract_latest(df: pd.DataFrame, weeks: int = 1) -> pd.DataFrame:
    """
    DataFrameから最新の週を抽出する関数。
    
    Args:
        df: load_hard_sales()の戻り値のDataFrame
        weeks: 最新から何週間分を抽出するか。デフォルトは1週分。
    
    Returns:
        pd.DataFrame: 最新のreport_dateを持つ行のDataFrame

        DataFrameのカラム詳細:
        - weekly_id (string): 週次データのID（gamehard_weekly.id）
        - begin_date (datetime64): 集計開始日（週の初日）、月曜日である
        - end_date (datetime64): 集計終了日（週の末日、=report_date）
        - report_date (datetime64): 集計期間の末日、日曜日である
        - period_date (int64): 集計日数(通常は7, 稀に14)
        - hw (string): ゲームハードの識別子
        - units (int64): 週次販売台数
        - adjust_units (int64): 週次販売台数の補正値(unitsは補正済みの値である)
        - year (int64): report_dateの年
        - month (int64): report_dateの月
        - mday (int64): report_dateの日
        - week (int64): report_dateがその月の何番目の日曜日か
        - delta_day (int64): 発売日から何日後か
        - delta_week (int64): 発売日から何週間後か
        - delta_month (int64): 発売日から何ヶ月後か
        - delta_year (int64): 発売年から何年後か(同じ年なら0)
        - avg_units (int64): 1日あたりの販売台数 (units / period_date)
        - sum_units (int64): report_date時点での累計販売台数
        - launch_date (datetime64): 発売日
        - maker_name (string): メーカー名
        - full_name (string): ゲームハードの正式名称
    """
    target_date = current_report_date(df)
    if (1 < weeks):
        target_date -= timedelta(weeks=weeks-1)
    return df.loc[df['report_date'] >= target_date, :]


def current_report_date(df: pd.DataFrame) -> datetime:
    """
    DataFrameから最新の報告日を取得する関数。

    Args:
        df: load_hard_sales()の戻り値のDataFrame

    Returns:
        datetime: 最新の報告日
    """
    return df['report_date'].max()


def get_hw(df: pd.DataFrame) -> List[str]:
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
    直近1年間のデータを元にアクティブなハードウェア名のリストを取得する。
    
    Returns:
        List[str]: アクティブなハードウェア名のリスト
    """
    base_df = load_hard_sales()
    now = datetime.now()
    one_year_ago = now - timedelta(days=365)
    recent_df = base_df.loc[base_df['report_date'] >= one_year_ago, :]
    active_hw = get_hw(recent_df)
    return active_hw    


def weekly_sales(src_df: pd.DataFrame, 
                  begin: Optional[datetime] = None, end: Optional[datetime] = None,
                  maker_mode:bool = False) -> pd.DataFrame:
    """
    週毎の販売台数と、その週までの累計販売台数（sum_units）を集計して返す。
    
    Args:
        src_df: load_hard_sales()の戻り値のDataFrame
        begin: 集計開始日
        end: 集計終了日
        maker_mode: Trueの場合、メーカー毎に集計。Falseの場合、ハード毎に集計。

    Returns:
        pd.DataFrame: 週毎の販売台数（weekly_units）と累計販売台数（sum_units）を含むDataFrame
        
        DataFrameのカラム詳細:
        - report_date (datetime64): 集計期間の末日、日曜日である
        - hw (string): ゲームハードの識別子 (maker_mode=Falseの場合)
        - maker_name (string): メーカー名 (maker_mode=Trueの場合)
        - weekly_units (int64): 週次販売台数
        - sum_units (int64): report_date時点での累計販売台数
    """
    
    if begin is not None and end is not None:
        df = src_df.loc[(src_df['report_date'] >= begin) & (src_df['report_date'] <= end), :]
    elif begin is not None:
        df = src_df.loc[src_df['report_date'] >= begin, :]
    elif end is not None:
        df = src_df.loc[src_df['report_date'] <= end, :]
    else:
        df = src_df.copy()

    # 週ごとの販売台数を集計
    if maker_mode:
        key_column = 'maker_name'
    else:
        key_column = 'hw'
    
    weekly_sales = df.groupby(['report_date', key_column]).agg({'units': 'sum'}).reset_index()
    weekly_sales.rename(columns={'units': 'weekly_units'}, inplace=True)

    # 週ごとの累計販売台数を計算
    weekly_sales['sum_units'] = (
        weekly_sales
        .sort_values([key_column, 'report_date'])
        .groupby(key_column)['weekly_units']
        .cumsum()
    )
    return weekly_sales


def monthly_sales(src_df: pd.DataFrame, 
                  begin: Optional[datetime] = None, end: Optional[datetime] = None,
                  maker_mode:bool = False) -> pd.DataFrame:
    """
    月毎の販売台数と、その月までの累計販売台数（sum_units）を集計して返す。
    
    Args:
        src_df: load_hard_sales()の戻り値のDataFrame
        begin: 集計開始日
        end: 集計終了日
        maker_mode: Trueの場合、メーカー毎に集計。Falseの場合、ハード毎に集計。

    Returns:
        pd.DataFrame: 月毎の販売台数（monthly_units）と累計販売台数（sum_units）を含むDataFrame
        
        DataFrameのカラム詳細:
        - year (int64): report_dateの年
        - month (int64): report_dateの月
        - hw (string): ゲームハードの識別子 (maker_mode=Falseの場合) 
        - maker_name (string): メーカー名 (maker_mode=Trueの場合)
        - monthly_units (int64): 月次販売台数
        - sum_units (int64): その月時点での累計販売台数
    """
    if begin is not None and end is not None:
        df = src_df.loc[(src_df['report_date'] >= begin) & (src_df['report_date'] <= end), :]
    elif begin is not None:
        df = src_df.loc[src_df['report_date'] >= begin, :]
    elif end is not None:
        df = src_df.loc[src_df['report_date'] <= end, :]
    else:
        df = src_df.copy()

    # 月ごとの販売台数を集計
    if maker_mode:
        key_column = 'maker_name'
    else:
        key_column = 'hw'
    
    monthly_sales = df.groupby(['year', 'month', key_column]).agg({'units': 'sum'}).reset_index()
    monthly_sales.rename(columns={'units': 'monthly_units'}, inplace=True)

    # 月ごとの累計販売台数を計算
    monthly_sales['sum_units'] = (
        monthly_sales
        .sort_values([key_column, 'year', 'month'])
        .groupby(key_column)['monthly_units']
        .cumsum()
    )
    return monthly_sales


def yearly_sales(src_df: pd.DataFrame, 
                 begin: Optional[datetime] = None, end: Optional[datetime] = None,
                 maker_mode:bool = False) -> pd.DataFrame:
    """
    年毎の販売台数と、その年までの累計販売台数（sum_units）を集計して返す。

    Args:
        src_df: load_hard_sales()の戻り値のDataFrame
        begin: 集計開始日
        end: 集計終了日
        maker_mode: Trueの場合、メーカー毎に集計。Falseの場合、ハード毎に集計。

    Returns:
        pd.DataFrame: 年毎の販売台数（yearly_units）と累計販売台数（sum_units）を含むDataFrame
        
        DataFrameのカラム詳細:
        - year (int64): report_dateの年
        - hw (string): ゲームハードの識別子 (maker_mode=Falseの場合) 
        - maker_name (string): メーカー名 (maker_mode=Trueの場合)
        - yearly_units (int64): 年次販売台数
        - sum_units (int64): その年時点での累計販売台数
    """
    if begin is not None and end is not None:
        df = src_df.loc[(src_df['report_date'] >= begin) & (src_df['report_date'] <= end), :]
    elif begin is not None:
        df = src_df.loc[src_df['report_date'] >= begin, :]
    elif end is not None:
        df = src_df.loc[src_df['report_date'] <= end, :]
    else:
        df = src_df.copy()

    # 年ごとの販売台数を集計
    if maker_mode:
        key_column = 'maker_name'
    else:
        key_column = 'hw'

    yearly_sales = df.groupby(['year', key_column]).agg({'units': 'sum'}).reset_index()
    yearly_sales.rename(columns={'units': 'yearly_units'}, inplace=True)

    # 年ごとの累計販売台数を計算
    yearly_sales['sum_units'] = (
        yearly_sales
        .sort_values([key_column, 'year'])
        .groupby(key_column)['yearly_units']
        .cumsum()
    )

    return yearly_sales


def yearly_maker_sales(src_df: pd.DataFrame, 
                begin: Optional[datetime] = None, end: Optional[datetime] = None) -> pd.DataFrame:
    """
    年毎、メーカー毎の販売台数を集計して返す。

    Args:
        src_df: load_hard_sales()の戻り値のDataFrame
        begin: 集計開始日
        end: 集計終了日

    Returns:
        pd.DataFrame: 年毎、メーカー毎の販売台数を含むDataFrame

        DataFrameのカラム詳細:
        - year (int64): report_dateの年
        - maker_name (string): メーカー名
        - yearly_units (int64): 年次販売台数
    """
    df = yearly_sales(src_df, begin=begin, end=end, maker_mode=True)
    ## dfからsum_unitsを削除する
    return df.drop(columns=['sum_units'])


def delta_yearly_sales(df: pd.DataFrame) -> pd.DataFrame:
    """
    販売開始からの経過年毎の販売台数と、その経過年までの累計販売台数（sum_units）を集計して返す。

    Args:
        df: load_hard_sales()の戻り値のDataFrame
    
    Returns:
        pd.DataFrame: 経過年毎の販売台数（yearly_units）と累計販売台数（sum_units）を含むDataFrame
        
        DataFrameのカラム詳細:
        - delta_year (int64): 発売年から何年後か(同じ年なら0)
        - hw (string): ゲームハードの識別子
        - yearly_units (int64): 経過年次販売台数
        - sum_units (int64): その経過年時点での累計販売台数
    """
    # 年ごとの販売台数を集計
    delta_yearly_sales = df.groupby(['delta_year', 'hw']).agg({'units': 'sum'}).reset_index()
    delta_yearly_sales.rename(columns={'units': 'yearly_units'}, inplace=True)

    # 年ごとの累計販売台数を計算
    delta_yearly_sales['sum_units'] = (
        delta_yearly_sales
        .sort_values(['hw', 'delta_year'])
        .groupby('hw')['yearly_units']
        .cumsum()
    )
    return delta_yearly_sales


def pivot_sales(src_df: pd.DataFrame, hw:List[str] = [],
                begin: Optional[datetime] = None,
                end: Optional[datetime] = None) -> pd.DataFrame:
    """
    ハードウェアの週単位の販売台数をピボットテーブル形式で返す。

    Args:
        df: load_hard_sales()で取得したDataFrame
        hw: プロットしたいハードウェア名のリスト。[]の場合は全ハードウェアを対象
        begin: 集計開始日
        end: 集計終了日
        full_name: フルネームを使用するかどうか
        
    Returns:
        pd.DataFrame: report_dateをインデックス、hwを列、unitsを値とするピボットテーブル
        
        DataFrameのカラム構成:
        - index: report_date (datetime64): 集計期間の末日（日曜日）
        - columns: hw (string): ゲームハードの識別子
        - values: units (int64): 週次販売台数
    """
    # begin/endでフィルタリング
    if begin is not None and end is not None:
        df = src_df.loc[(src_df['report_date'] >= begin) & (src_df['report_date'] <= end)]
    elif begin is not None:
        df = src_df.loc[src_df['report_date'] >= begin]
    elif end is not None:
        df = src_df.loc[src_df['report_date'] <= end]
    else:
        df = src_df.copy()
        
    # HWでフィルタリング
    if len(hw) > 0:
        df =  df.loc[df['hw'].isin(hw)]

    return df.pivot(index='report_date', columns='hw', values='units')


def pivot_monthly_sales(df: pd.DataFrame, hw:List[str] = [],
                begin: Optional[datetime] = None, 
                end: Optional[datetime] = None) -> pd.DataFrame:
    """
    ハードウェアの月単位の販売台数をピボットテーブル形式で返す。

    Args:
        df: load_hard_sales()で取得したDataFrame
        hw: プロットしたいハードウェア名のリスト。[]の場合は全ハードウェアを対象
        begin: 集計開始日
        end: 集計終了日
        
    Returns:
        pd.DataFrame: year, monthをインデックス、hwを列、monthly_unitsを値とするピボットテーブル
        
        DataFrameのカラム構成:
        - index: year (int64), month (int64): report_dateの年と月
        - columns: hw (string): ゲームハードの識別子
        - values: monthly_units (int64): 月次販売台数
    """
    df = monthly_sales(df, begin=begin, end=end)
    if len(hw) > 0:
        df =  df.loc[df['hw'].isin(hw)]

    return df.pivot(index=['year', 'month'], columns='hw', values='monthly_units')

def pivot_yearly_sales(df: pd.DataFrame, hw:List[str] = [],
                begin: Optional[datetime] = None, 
                end: Optional[datetime] = None) -> pd.DataFrame:
    """
    ハードウェアの年単位の販売台数をピボットテーブル形式で返す。

    Args:
        df: load_hard_sales()で取得したDataFrame
        hw: プロットしたいハードウェア名のリスト。[]の場合は全ハードウェアを対象
        begin: 集計開始日
        end: 集計終了日
        
    Returns:
        pd.DataFrame: yearをインデックス、hwを列、yearly_unitsを値とするピボットテーブル
        
        DataFrameのカラム構成:
        - index: year (int64): report_dateの年
        - columns: hw (string): ゲームハードの識別子
        - values: yearly_units (int64): 年次販売台数
    """
    df = yearly_sales(df, begin=begin, end=end)
    # HWでフィルタリング
    if len(hw) > 0:
        df =  df.loc[df['hw'].isin(hw), :]

    return df.pivot(index='year', columns='hw', values='yearly_units')


def pivot_cumulative_sales(df: pd.DataFrame, hw:List[str] = [], 
                           begin: Optional[datetime] = None,
                           end: Optional[datetime] = None,
                           full_name:bool = False) -> pd.DataFrame:
    """
    ハードウェアの累計販売台数をピボットテーブル形式で返す。
    
    Args:
        df: load_hard_sales()で取得したDataFrame
        hw: プロットしたいハードウェア名のリスト。[]の場合は全ハードウェアを対象
        begin: 集計開始日
        end: 集計終了日
        full_name: カラム名にフルネームを使用する
    
    Returns:
        pd.DataFrame: report_dateをインデックス、hwを列、sum_unitsを値とするピボットテーブル
        
        DataFrameのカラム構成:
        - index: report_date (datetime64): 集計期間の末日（日曜日）
        - columns: hw (string): ゲームハードの識別子 またはfull_name (string): ゲームハードの正式名称 (full_name=Trueの場合)
        - values: sum_units (int64): report_date時点での累計販売台数
    """
    # begin/endでフィルタリング
    if begin is not None:
        df = df[df['report_date'] >= begin]
    if end is not None:
        df = df[df['report_date'] <= end]
    # HWでフィルタリング
    if len(hw) > 0:
        filtered_df = df[df['hw'].isin(hw)]
    else:
        filtered_df = df

    # 横軸のカラム
    columns_name = 'full_name' if full_name else 'hw'

    # ピボットテーブルを作成
    return filtered_df.pivot(index='report_date', columns=columns_name, values='sum_units')

def pivot_sales_by_delta(df: pd.DataFrame, mode:str = "week", 
                         begin:Optional[int] = None,
                         end:Optional[int] = None,
                         hw:List[str] = [], full_name:bool = False) -> pd.DataFrame:
    """
    ハードウェアの販売台数を発売日からの経過状況をインデックス、hwを列、unitsを値とするピボットテーブル形式で返す。
    
    Args:
        df: load_hard_sales()で取得したDataFrame
        mode: "week"、"month"または"year"を指定。週単位の集計なら"week"、月単位の集計なら"month"、年単位の集計なら"year"を指定。
        begin: 集計開始（経過期間の最小値）
        end: 集計終了（経過期間の最大値）
        hw: プロットしたいハードウェア名のリスト。[]の場合は全ハードウェアを対象
        full_name: フルネームを使用するかどうか

    Returns:
        pd.DataFrame: delta_week, delta_month, delta_yearのいずれかインデックス、hwを列、unitsを値とするピボットテーブル
        
        DataFrameのカラム構成:
        - index: delta_week (int64) / delta_month (int64) / delta_year (int64): 発売日からの経過期間（modeにより変動）
        - columns: hw (string): ゲームハードの識別子（full_name=Trueの場合はfull_name）
        - values: units (int64): 販売台数
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
    
    if begin:
        df = df.loc[df[index_col] >= begin, :]
    if end:
        df = df.loc[df[index_col] <= end, :]
    
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


def pivot_cumulative_sales_by_delta(df: pd.DataFrame, mode:str = "week", 
                                    hw:List[str] = [],
                                    begin:Optional[int] = None,
                                    end:Optional[int] = None
                                    ) -> pd.DataFrame:
    """
    ハードウェアの累計販売台数を発売日からの経過状況をインデックス、hwを列、unitsを値とするピボットテーブル形式で返す。
    Args:
        df: load_hard_sales()で取得したDataFrame
        mode: "week"、"month"または"year"を指定。週単位の集計なら"week"、月単位の集計なら"month"、年単位の集計なら"year"を指定。
        hw: プロットしたいハードウェア名のリスト。[]の場合は全ハードウェアを対象
        begin: 集計開始（経過期間の最小値）
        end: 集計終了（経過期間の最大値）

    Returns:
        pd.DataFrame: delta_week, delta_month, delta_yearのいずれかインデックス、hwを列、sum_unitsを値とするピボットテーブル
        
        DataFrameのカラム構成:
        - index: delta_week (int64) / delta_month (int64) / delta_year (int64): 発売日からの経過期間（modeにより変動）
        - columns: hw (string): ゲームハードの識別子
        - values: sum_units (int64): その経過期間時点での累計販売台数
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

    if begin:
        df = df.loc[df[index_col] >= begin]
    if end:
        df = df.loc[df[index_col] <= end]

    if len(hw) > 0:
        filtered_df = df[df['hw'].isin(hw)]
    else:
        filtered_df = df

    return filtered_df.pivot_table(
        index=index_col,
        columns='hw',
        values='sum_units',
        aggfunc='last'
    )


def pivot_maker(df: pd.DataFrame, begin_year: Optional[int] = None, end_year: Optional[int] = None) -> pd.DataFrame:
    """
    ハードウェアのメーカー別販売データをピボットテーブル形式に変換する

    Parameters
    ----------
    df : pd.DataFrame
        load_hard_sales()で取得した週次販売データ
    begin_year : int, optional
        開始年（デフォルト: None）
    end_year : int, optional
        終了年（デフォルト: None）

    Returns
    -------
    pd.DataFrame
        メーカー別の販売データをピボットテーブル形式に変換したDataFrame
        
        DataFrameのカラム構成:
        - index: year (int64): report_dateの年
        - columns: maker_name (string): メーカー名（Nintendo, SONY, Microsoft, SEGA等）
        - values: yearly_units (int64): 年次販売台数
    """
    begin = None if begin_year is None else datetime(begin_year, 1, 1)
    end = None if end_year is None else datetime(end_year, 12, 31)

    df = yearly_maker_sales(df, begin=begin, end=end)
    pivot_df = df.pivot(index='year', columns='maker_name', values='yearly_units')
    
        # カラムの順序を調整
    desired_order = ['Nintendo', 'SONY', 'Microsoft', 'SEGA']
    existing_columns = pivot_df.columns.tolist()
    
    # 指定した順序でカラムを並べ替え
    ordered_columns = []
    for maker in desired_order:
        if maker in existing_columns:
            ordered_columns.append(maker)
    
    # その他のカラムを追加
    other_columns = [col for col in existing_columns if col not in desired_order]
    ordered_columns.extend(other_columns)
    
    return pivot_df[ordered_columns]



def cumsum_diffs(df:pd.DataFrame,
                       cmplist: list[tuple[str, str]]) -> pd.DataFrame:
    """
    複数のハードウェア間の累計販売台数の差分を計算してDataFrameで返す。
    
    Args:
        df: load_hard_sales()で取得したDataFrame
        cmplist: 比較するハードウェアのペアのリスト。各タプルは(base_hw, cmp_hw)の形式で、
                 cmp_hwの累計販売台数からbase_hwの累計販売台数を引いた差分を計算する。
    
    Returns:
        pd.DataFrame: 各ペアの差分を列として持つDataFrame
        
        DataFrameのカラム構成:
        - index: 連番（0から始まる整数）
        - columns: "{cmp_hw}_{base_hw}差" (int64): 各ペアの累計販売台数の差分
                   例: "PS5_NSW差"は、PS5の累計販売台数からNSWの累計販売台数を引いた値
    """

    def cumsum_diff_frame(df:pd.DataFrame, base_hw: str, cmp_hw: str) -> pd.DataFrame:
        """base_hwとcmp_hwの週販差分を計算したDataFrameを返す"""
        pivot_df = pivot_cumulative_sales(df, hw=[base_hw, cmp_hw])
    
        # pivot_dfのbase_hw列の値がNaNでない行で最も小さいindexの行の直前の行のbase_hw列の値を0に設定
        # なおindexはtimestamp型である
        first_valid_index = pivot_df[pivot_df[base_hw].notna()].index.min()
        if first_valid_index is not None:
            prior_index = pivot_df.index[pivot_df.index.get_loc(first_valid_index) - 1]
            pivot_df.at[prior_index, base_hw] = 0
  
        # カラム　base_hwがNaNでない行を抽出
        pivot_df = pivot_df[pivot_df[base_hw].notna()]
        diff_col_name = f"{cmp_hw}_{base_hw}差"
        pivot_df[diff_col_name] = pivot_df[cmp_hw] - pivot_df[base_hw]
    
        # pivot_df[diff_col_name]の値が　-10000より小さな行を削除
        pivot_df = pivot_df[pivot_df[diff_col_name] >= -10000]
        # pivot_dfのindexを0からのシリアル番号にする
        pivot_df.reset_index(drop=True, inplace=True)
    
        # diff_col_name列のみを返す
        return pivot_df[[diff_col_name]]

    diff_dfs = []
    for base_hw, cmp_hw in cmplist:
        diff_df = cumsum_diff_frame(df, base_hw, cmp_hw)
        diff_dfs.append(diff_df)
    # diff_dfsを結合する
    result_df = pd.concat(diff_dfs, axis=1)
    return result_df
