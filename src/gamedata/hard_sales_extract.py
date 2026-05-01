from datetime import datetime, timedelta, date
import polars as pl
from typing import Any, Dict, List

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
        - begin_date (Date): 集計開始日（週の初日）、月曜日である
        - end_date (Date): 集計終了日（週の末日、=report_date）
        - report_date (Date): 集計期間の末日、日曜日である
        - quarter (String): report_dateの四半期（例: "2024Q1"）
        - period_date (Int16): 集計日数(通常は7, 稀に14)
        - hw (String): ゲームハードの識別子
        - units (Int64): 週次販売台数
        - adjust_units (Int64): 週次販売台数の補正値(unitsは補正済みの値である)
        - year (Int16): report_dateの年
        - month (Int16): report_dateの月
        - mday (Int16): report_dateの日
        - week (Int16): report_dateがその月の何番目の日曜日か
        - delta_day (Int32): 発売日から何日後か
        - delta_week (Int32): 発売日から何週間後か
        - delta_month (Int16): 発売日から何ヶ月後か
        - delta_year (Int16): 発売年から何年後か(同じ年なら0)
        - avg_units (Int64): 1日あたりの販売台数 (units / period_date)
        - sum_units (Int64): report_date時点での累計販売台数
        - launch_date (Date): 発売日
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


def extract_by_date(df: pl.DataFrame, target_date:datetime|date, hw: List[str] | None = None) -> pl.DataFrame:
    """
    指定された日付の週に該当するデータを抽出する関数。
    
    Args:
        df: load_hard_sales()の戻り値のDataFrame（begin_date, end_date, report_dateはDate型に変換済み）
        target_date: 抽出したい日付のdatetime型､またはdate型
        hw: 省略可能なハードウェア名のリスト。指定すると、そのハードウェアに限定して抽出
    
    Returns:
        pl.DataFrame: 指定された日付がbegin_dateからend_dateの範囲にある行を抽出したDataFrame
        
        DataFrameのカラム詳細:
        - weekly_id (String): 週次データのID（gamehard_weekly.id）
        - begin_date (Date): 集計開始日（週の初日）、月曜日である
        - end_date (Date): 集計終了日（週の末日、=report_date）
        - report_date (Date): 集計期間の末日、日曜日である
        - quarter (String): report_dateの四半期（例: "2024Q1"）
        - period_date (Int16): 集計日数(通常は7, 稀に14)
        - hw (String): ゲームハードの識別子
        - units (Int64): 週次販売台数
        - adjust_units (Int64): 週次販売台数の補正値(unitsは補正済みの値である)
        - year (Int16): report_dateの年
        - month (Int16): report_dateの月
        - mday (Int16): report_dateの日
        - week (Int16): report_dateがその月の何番目の日曜日か
        - delta_day (Int32): 発売日から何日後か
        - delta_week (Int32): 発売日から何週間後か
        - delta_month (Int16): 発売日から何ヶ月後か
        - delta_year (Int16): 発売年から何年後か(同じ年なら0)
        - avg_units (Int64): 1日あたりの販売台数 (units / period_date)
        - sum_units (Int64): report_date時点での累計販売台数
        - launch_date (Date): 発売日
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
        - begin_date (Date): 集計開始日（週の初日）、月曜日である
        - end_date (Date): 集計終了日（週の末日、=report_date）
        - report_date (Date): 集計期間の末日、日曜日である
        - quarter (String): report_dateの四半期（例: "2024Q1"）
        - period_date (Int16): 集計日数(通常は7, 稀に14)
        - hw (String): ゲームハードの識別子
        - units (Int64): 週次販売台数
        - adjust_units (Int64): 週次販売台数の補正値(unitsは補正済みの値である)
        - year (Int16): report_dateの年
        - month (Int16): report_dateの月
        - mday (Int16): report_dateの日
        - week (Int16): report_dateがその月の何番目の日曜日か
        - delta_day (Int32): 発売日から何日後か
        - delta_week (Int32): 発売日から何週間後か
        - delta_month (Int16): 発売日から何ヶ月後か
        - delta_year (Int16): 発売年から何年後か(同じ年なら0)
        - avg_units (Int64): 1日あたりの販売台数 (units / period_date)
        - sum_units (Int64): report_date時点での累計販売台数
        - launch_date (Date): 発売日
        - maker_name (String): メーカー名
        - full_name (String): ゲームハードの正式名称
    """
    target_date = hs.current_report_date(df)
    if (1 < weeks):
        target_date -= timedelta(weeks=weeks-1)
    return df.filter(pl.col('report_date') >= target_date).sort(['report_date', 'units'], 
                                                                descending=[False, True])


def extract_total(df: pl.DataFrame, compact: bool = False) -> pl.DataFrame:
    """
    DataFrameから各ハードの最新の累計値行を抽出する関数。
    
    Args:
        df: load_hard_sales()の戻り値のDataFrame
        compact: Trueの場合､最小限のカラムのみを返す。デフォルトはFalseで、全てのカラムを返す。
    
    Returns:
        pl.DataFrame: 各ハードの最新の累計値行のDataFrame

        DataFrameのカラム詳細:
        - weekly_id (String): 週次データのID（gamehard_weekly.id）
        - begin_date (Date): 集計開始日（週の初日）、月曜日である
        - end_date (Date): 集計終了日（週の末日、=report_date）
        - report_date (Date): 集計期間の末日、日曜日である
        - quarter (String): report_dateの四半期（例: "2024Q1"）
        - period_date (Int16): 集計日数(通常は7, 稀に14)
        - hw (String): ゲームハードの識別子
        - units (Int64): 週次販売台数
        - adjust_units (Int64): 週次販売台数の補正値(unitsは補正済みの値である)
        - year (Int16): report_dateの年
        - month (Int16): report_dateの月
        - mday (Int16): report_dateの日
        - week (Int16): report_dateがその月の何番目の日曜日か
        - delta_day (Int32): 発売日から何日後か
        - delta_week (Int32): 発売日から何週間後か
        - delta_month (Int16): 発売日から何ヶ月後か
        - delta_year (Int16): 発売年から何年後か(同じ年なら0)
        - avg_units (Int64): 1日あたりの販売台数 (units / period_date)
        - sum_units (Int64): report_date時点での累計販売台数
        - launch_date (Date): 発売日
        - maker_name (String): メーカー名
        - full_name (String): ゲームハードの正式名称
    """
    df = (df
          .sort(['hw', 'sum_units'])          # sum_units昇順でソート
          .group_by('hw', maintain_order=False)
          .last()                              # 最大sum_unitsの行（＝最新行）を取得
          .sort('sum_units', descending=True)
        )
    if compact:
        df = df.select(['hw', 'sum_units','report_date' ])
    return df


# 累計台数到達週を計算する際の閾値リスト (台数, dict キー名)
_REACH_THRESHOLDS: List[tuple[int, str]] = [
    (500_000,    'weeks_to_500k'),
    (1_000_000,  'weeks_to_1m'),
    (5_000_000,  'weeks_to_5m'),
    (10_000_000, 'weeks_to_10m'),
    (15_000_000, 'weeks_to_15m'),
    (20_000_000, 'weeks_to_20m'),
    (25_000_000, 'weeks_to_25m'),
    (30_000_000, 'weeks_to_30m'),
    (35_000_000, 'weeks_to_35m'),
]


def hard_sales_summary(df: pl.DataFrame, hw: List[str] | None = None) -> List[Dict[str, Any]]:
    """
    各ゲームハードのサマリ情報を辞書の配列で返す関数。

    Args:
        df: load_hard_sales()の戻り値のDataFrame
        hw: HW識別子の配列。Noneや空リストの場合は全ハードの情報を返す。

    Returns:
        List[dict]: 各ハードのサマリ情報を含む辞書の配列。
                    辞書のキーと型は以下の通り。

        - hw (str): HW識別子
        - full_name (str): ハードのフルネーム
        - maker_name (str): メーカー名
        - launch_date (date): 発売年月日
        - last_report_date (date): 集計情報の最終年月日
        - total_units (int): 累計台数
        - sales_period (timedelta): 集計期間
        - sales_weeks (int): 集計週数
        - avg_weekly_units (int): 1週間あたりの平均販売台数
        - max_weekly_units (int): 週間の最大販売台数記録
        - max_weekly_date (date): 週間の最大販売台数を記録した集計日
        - max_monthly_units (int): 月間の最大販売台数記録
        - max_monthly_period (str): 月間最大販売台数を記録した年月 (例: "2020-11")
        - max_quarterly_units (int): 四半期の最大販売台数記録
        - max_quarterly_period (str): 四半期最大販売台数を記録した四半期 (例: "2020Q4")
        - max_yearly_units (int): 年間の最大販売台数記録
        - max_yearly_year (int): 年間の最大販売台数を記録した年
        - launch_week_units (int): 発売週の販売台数
        - weeks_to_500k (int | None): 累計50万台到達週 (発売週を1と数える)
        - weeks_to_1m (int | None): 累計100万台到達週
        - weeks_to_5m (int | None): 累計500万台到達週
        - weeks_to_10m (int | None): 累計1000万台到達週
        - weeks_to_15m (int | None): 累計1500万台到達週
        - weeks_to_20m (int | None): 累計2000万台到達週
        - weeks_to_25m (int | None): 累計2500万台到達週
        - weeks_to_30m (int | None): 累計3000万台到達週
        - weeks_to_35m (int | None): 累計3500万台到達週
    """
    hw_list: List[str] = hw if hw else df['hw'].unique().to_list()

    result: List[Dict[str, Any]] = []

    for h in hw_list:
        hw_df = df.filter(pl.col('hw') == h).sort('report_date')

        if hw_df.is_empty():
            continue

        first_row = hw_df.row(0, named=True)
        launch_date: date = first_row['launch_date']
        full_name: str = first_row['full_name']
        maker_name: str = first_row['maker_name']

        last_report_date: date = hw_df['report_date'].max()
        total_units: int = int(hw_df['sum_units'].max())
        sales_weeks: int = hw_df.height
        sales_period: timedelta = last_report_date - launch_date
        avg_weekly_units: int = round(total_units / sales_weeks) if sales_weeks > 0 else 0

        # 週間最大
        max_weekly_idx: int = int(hw_df['units'].arg_max())
        max_weekly_units: int = int(hw_df['units'][max_weekly_idx])
        max_weekly_date: date = hw_df['report_date'][max_weekly_idx]

        # 月間最大
        monthly = (
            hw_df.group_by(['year', 'month'])
            .agg(pl.col('units').sum().alias('monthly_units'))
        )
        max_monthly_idx: int = int(monthly['monthly_units'].arg_max())
        max_monthly_units: int = int(monthly['monthly_units'][max_monthly_idx])
        max_monthly_year: int = int(monthly['year'][max_monthly_idx])
        max_monthly_month: int = int(monthly['month'][max_monthly_idx])
        max_monthly_period: str = f"{max_monthly_year}-{max_monthly_month:02d}"

        # 四半期最大
        quarterly = (
            hw_df.group_by('quarter')
            .agg(pl.col('units').sum().alias('quarterly_units'))
        )
        max_quarterly_idx: int = int(quarterly['quarterly_units'].arg_max())
        max_quarterly_units: int = int(quarterly['quarterly_units'][max_quarterly_idx])
        max_quarterly_period: str = quarterly['quarter'][max_quarterly_idx]

        # 年間最大
        yearly = (
            hw_df.group_by('year')
            .agg(pl.col('units').sum().alias('yearly_units'))
        )
        max_yearly_idx: int = int(yearly['yearly_units'].arg_max())
        max_yearly_units: int = int(yearly['yearly_units'][max_yearly_idx])
        max_yearly_year: int = int(yearly['year'][max_yearly_idx])

        # 発売週の販売台数 (delta_week == 0)
        launch_week_df = hw_df.filter(pl.col('delta_week') == 0)
        launch_week_units: int = int(launch_week_df['units'].sum()) if not launch_week_df.is_empty() else 0

        summary: Dict[str, Any] = {
            'hw': h,
            'full_name': full_name,
            'maker_name': maker_name,
            'launch_date': launch_date,
            'last_report_date': last_report_date,
            'total_units': total_units,
            'sales_period': sales_period,
            'sales_weeks': sales_weeks,
            'avg_weekly_units': avg_weekly_units,
            'max_weekly_units': max_weekly_units,
            'max_weekly_date': max_weekly_date,
            'max_monthly_units': max_monthly_units,
            'max_monthly_period': max_monthly_period,
            'max_quarterly_units': max_quarterly_units,
            'max_quarterly_period': max_quarterly_period,
            'max_yearly_units': max_yearly_units,
            'max_yearly_year': max_yearly_year,
            'launch_week_units': launch_week_units,
        }

        # 累計台数到達週
        for threshold, key in _REACH_THRESHOLDS:
            reached = hw_df.filter(pl.col('sum_units') >= threshold)
            if reached.is_empty():
                summary[key] = None
            else:
                summary[key] = int(reached['delta_week'][0]) + 1

        result.append(summary)

    return result


def maker_sales_summary(df: pl.DataFrame, makers: List[str] | None = None) -> List[Dict[str, Any]]:
    """
    各ゲームハードメーカーのサマリ情報を辞書の配列で返す関数。

    Args:
        df: load_hard_sales()の戻り値のDataFrame
        makers: メーカー名の配列。Noneや空リストの場合は全メーカーの情報を返す。

    Returns:
        List[dict]: 各メーカーのサマリ情報を含む辞書の配列。
                    辞書のキーと型は以下の通り。

        - maker_name (str): メーカー名
        - hw_list (List[str]): 発売したHW識別子の配列
        - total_units (int): 累計販売台数
        - max_weekly_units (int): 週間の最大販売台数記録
        - max_weekly_date (date): 週間の最大販売台数を記録した集計日
        - max_weekly_hw (List[str]): 週間最大時のハード構成
        - max_monthly_units (int): 月間の最大販売台数記録
        - max_monthly_period (str): 月間最大販売台数を記録した年月 (例: "2020-11")
        - max_monthly_hw (List[str]): 月間最大時のハード構成
        - max_quarterly_units (int): 四半期の最大販売台数記録
        - max_quarterly_period (str): 四半期最大販売台数を記録した四半期 (例: "2020Q4")
        - max_quarterly_hw (List[str]): 四半期最大時のハード構成
        - max_yearly_units (int): 年間の最大販売台数記録
        - max_yearly_year (int): 年間の最大販売台数を記録した年
        - max_yearly_hw (List[str]): 年間最大時のハード構成
    """
    maker_list: List[str] = makers if makers else df['maker_name'].unique().to_list()

    result: List[Dict[str, Any]] = []

    for maker in maker_list:
        maker_df = df.filter(pl.col('maker_name') == maker)

        if maker_df.is_empty():
            continue

        # このメーカーの全HW識別子
        hw_list: List[str] = maker_df['hw'].unique().sort().to_list()

        # 累計販売台数 (各HWの最大sum_unitsの合計)
        total_units: int = int(
            maker_df.sort(['hw', 'sum_units'])
            .group_by('hw', maintain_order=False)
            .last()
            .select('sum_units')
            .sum()
            .item()
        )

        # 週間最大: report_dateごとに集計
        weekly = (
            maker_df.group_by('report_date')
            .agg(
                pl.col('units').sum().alias('weekly_total'),
                pl.col('hw').unique().sort().alias('hw_composition'),
            )
        )
        max_weekly_idx: int = int(weekly['weekly_total'].arg_max())
        max_weekly_units: int = int(weekly['weekly_total'][max_weekly_idx])
        max_weekly_date: date = weekly['report_date'][max_weekly_idx]
        max_weekly_hw: List[str] = weekly['hw_composition'][max_weekly_idx].to_list()

        # 月間最大: year+monthごとに集計
        monthly = (
            maker_df.group_by(['year', 'month'])
            .agg(
                pl.col('units').sum().alias('monthly_total'),
                pl.col('hw').unique().sort().alias('hw_composition'),
            )
        )
        max_monthly_idx: int = int(monthly['monthly_total'].arg_max())
        max_monthly_units: int = int(monthly['monthly_total'][max_monthly_idx])
        max_monthly_year: int = int(monthly['year'][max_monthly_idx])
        max_monthly_month: int = int(monthly['month'][max_monthly_idx])
        max_monthly_period: str = f"{max_monthly_year}-{max_monthly_month:02d}"
        max_monthly_hw: List[str] = monthly['hw_composition'][max_monthly_idx].to_list()

        # 四半期最大
        quarterly = (
            maker_df.group_by('quarter')
            .agg(
                pl.col('units').sum().alias('quarterly_total'),
                pl.col('hw').unique().sort().alias('hw_composition'),
            )
        )
        max_quarterly_idx: int = int(quarterly['quarterly_total'].arg_max())
        max_quarterly_units: int = int(quarterly['quarterly_total'][max_quarterly_idx])
        max_quarterly_period: str = quarterly['quarter'][max_quarterly_idx]
        max_quarterly_hw: List[str] = quarterly['hw_composition'][max_quarterly_idx].to_list()

        # 年間最大
        yearly = (
            maker_df.group_by('year')
            .agg(
                pl.col('units').sum().alias('yearly_total'),
                pl.col('hw').unique().sort().alias('hw_composition'),
            )
        )
        max_yearly_idx: int = int(yearly['yearly_total'].arg_max())
        max_yearly_units: int = int(yearly['yearly_total'][max_yearly_idx])
        max_yearly_year: int = int(yearly['year'][max_yearly_idx])
        max_yearly_hw: List[str] = yearly['hw_composition'][max_yearly_idx].to_list()

        result.append({
            'maker_name': maker,
            'hw_list': hw_list,
            'total_units': total_units,
            'max_weekly_units': max_weekly_units,
            'max_weekly_date': max_weekly_date,
            'max_weekly_hw': max_weekly_hw,
            'max_monthly_units': max_monthly_units,
            'max_monthly_period': max_monthly_period,
            'max_monthly_hw': max_monthly_hw,
            'max_quarterly_units': max_quarterly_units,
            'max_quarterly_period': max_quarterly_period,
            'max_quarterly_hw': max_quarterly_hw,
            'max_yearly_units': max_yearly_units,
            'max_yearly_year': max_yearly_year,
            'max_yearly_hw': max_yearly_hw,
        })

    return result

