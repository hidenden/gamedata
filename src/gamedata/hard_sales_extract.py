from datetime import datetime, timedelta
import polars as pl
from typing import List

from . import hard_sales as hs


def extract_week_reached_units(df: pl.DataFrame, threshold_units: int) -> pl.DataFrame:
    """
    累計販売台数が指定の値を超えた最初の週を見つける関数。
    
    Args:
        df: load_hard_sales()の戻り値のDataFrame
        threshold_units: 閾値となる累計販売台数
    
    Returns:
        pl.DataFrame: 累計販売台数がthreshold_unitsを超えた最初の週ごとに、その行を抽出したDataFrame。
                      ハードごと（hw）に最初に到達した週のみを返す。
                      どのハードも到達していなければ空DataFrameを返す。
        
        DataFrameのカラム詳細:
        - weekly_id (String): 週次データのID（gamehard_weekly.id）
        - begin_date (Datetime): 集計開始日（週の初日）、月曜日である
        - end_date (Datetime): 集計終了日（週の末日、=report_date）
        - report_date (Datetime): 集計期間の末日、日曜日である
        - quarter (String): report_dateの四半期（例: "2024Q1"）
        - period_date (Int64): 集計日数(通常は7, 稀に14)
        - hw (String): ゲームハードの識別子
        - units (Int64): 週次販売台数
        - adjust_units (Int64): 週次販売台数の補正値(unitsは補正済みの値である)
        - year (Int64): report_dateの年
        - month (Int64): report_dateの月
        - mday (Int64): report_dateの日
        - week (Int64): report_dateがその月の何番目の日曜日か
        - delta_day (Int64): 発売日から何日後か
        - delta_week (Int64): 発売日から何週間後か
        - delta_month (Int64): 発売日から何ヶ月後か
        - delta_year (Int64): 発売年から何年後か(同じ年なら0)
        - avg_units (Int64): 1日あたりの販売台数 (units / period_date)
        - sum_units (Int64): report_date時点での累計販売台数
        - launch_date (Datetime): 発売日
        - maker_name (String): メーカー名
        - full_name (String): ゲームハードの正式名称
    """
    # ハードごとに累計販売台数が閾値を超えた最初の週を取得
    result = (
        df.sort(['hw', 'report_date'])
        .filter(pl.col('sum_units') >= threshold_units)
        .group_by('hw', maintain_order=True)
        .first()
        .sort('report_date')
    )
    
    return result


def extract_by_date(df: pl.DataFrame, target_date:datetime, hw: List[str] | None = None) -> pl.DataFrame:
    """
    指定された日付の週に該当するデータを抽出する関数。
    
    Args:
        df: load_hard_sales()の戻り値のDataFrame（begin_date, end_date, report_dateはDatetime型に変換済み）
        target_date: 抽出したい日付のdatetime型
        hw: 省略可能なハードウェア名のリスト。指定すると、そのハードウェアに限定して抽出
    
    Returns:
        pl.DataFrame: 指定された日付がbegin_dateからend_dateの範囲にある行を抽出したDataFrame
        
        DataFrameのカラム詳細:
        - weekly_id (String): 週次データのID（gamehard_weekly.id）
        - begin_date (Datetime): 集計開始日（週の初日）、月曜日である
        - end_date (Datetime): 集計終了日（週の末日、=report_date）
        - report_date (Datetime): 集計期間の末日、日曜日である
        - quarter (String): report_dateの四半期（例: "2024Q1"）
        - period_date (Int64): 集計日数(通常は7, 稀に14)
        - hw (String): ゲームハードの識別子
        - units (Int64): 週次販売台数
        - adjust_units (Int64): 週次販売台数の補正値(unitsは補正済みの値である)
        - year (Int64): report_dateの年
        - month (Int64): report_dateの月
        - mday (Int64): report_dateの日
        - week (Int64): report_dateがその月の何番目の日曜日か
        - delta_day (Int64): 発売日から何日後か
        - delta_week (Int64): 発売日から何週間後か
        - delta_month (Int64): 発売日から何ヶ月後か
        - delta_year (Int64): 発売年から何年後か(同じ年なら0)
        - avg_units (Int64): 1日あたりの販売台数 (units / period_date)
        - sum_units (Int64): report_date時点での累計販売台数
        - launch_date (Datetime): 発売日
        - maker_name (String): メーカー名
        - full_name (String): ゲームハードの正式名称

    """
    # target_dateがbegin_dateからend_dateの範囲にある行を抽出
    filtered_df = df.filter((pl.col('begin_date') <= target_date) & (pl.col('end_date') >= target_date))

    # hw_namesが指定されている場合は、さらにフィルタリング
    if hw:
        filtered_df = filtered_df.filter(pl.col('hw').is_in(hw))
    return filtered_df


def extract_latest(df: pl.DataFrame, weeks: int = 1) -> pl.DataFrame:
    """
    DataFrameから最新の週を抽出する関数。
    
    Args:
        df: load_hard_sales()の戻り値のDataFrame
        weeks: 最新から何週間分を抽出するか。デフォルトは1週分。
    
    Returns:
        pl.DataFrame: 最新のreport_dateを持つ行のDataFrame

        DataFrameのカラム詳細:
        - weekly_id (String): 週次データのID（gamehard_weekly.id）
        - begin_date (Datetime): 集計開始日（週の初日）、月曜日である
        - end_date (Datetime): 集計終了日（週の末日、=report_date）
        - report_date (Datetime): 集計期間の末日、日曜日である
        - quarter (String): report_dateの四半期（例: "2024Q1"）
        - period_date (Int64): 集計日数(通常は7, 稀に14)
        - hw (String): ゲームハードの識別子
        - units (Int64): 週次販売台数
        - adjust_units (Int64): 週次販売台数の補正値(unitsは補正済みの値である)
        - year (Int64): report_dateの年
        - month (Int64): report_dateの月
        - mday (Int64): report_dateの日
        - week (Int64): report_dateがその月の何番目の日曜日か
        - delta_day (Int64): 発売日から何日後か
        - delta_week (Int64): 発売日から何週間後か
        - delta_month (Int64): 発売日から何ヶ月後か
        - delta_year (Int64): 発売年から何年後か(同じ年なら0)
        - avg_units (Int64): 1日あたりの販売台数 (units / period_date)
        - sum_units (Int64): report_date時点での累計販売台数
        - launch_date (Datetime): 発売日
        - maker_name (String): メーカー名
        - full_name (String): ゲームハードの正式名称
    """
    target_date = hs.current_report_date(df)
    if (1 < weeks):
        target_date -= timedelta(weeks=weeks-1)
    return df.filter(pl.col('report_date') >= target_date).sort(['report_date', 'units'], 
                                                                descending=[False, True])

