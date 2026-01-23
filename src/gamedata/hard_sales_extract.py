from datetime import datetime, timedelta
import pandas as pd
from typing import List

from . import hard_sales as hs


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
        - quarter (Period): report_dateの四半期（Period型）
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


def extract_by_date(df: pd.DataFrame, target_date:datetime, hw: List[str] | None = None) -> pd.DataFrame:
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
        - quarter (Period): report_dateの四半期（Period型）
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
        - quarter (Period): report_dateの四半期（Period型）
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
    target_date = hs.current_report_date(df)
    if (1 < weeks):
        target_date -= timedelta(weeks=weeks-1)
    return df.loc[df['report_date'] >= target_date, :]

