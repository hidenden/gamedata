from datetime import datetime, date
import polars as pl
from typing import List

# プロジェクト内モジュール
from . import hard_sales as hs
from . import hard_sales_filter as hsf
from . import hard_info as hi


def sales_long(src_df: pl.DataFrame, hw: List[str] = [],
               begin: datetime | date | None = None,
               end: datetime | date | None = None) -> pl.DataFrame:
    """
    ハードウェアの週単位の販売台数をlong形式で返す。

    Args:
        src_df: load_hard_sales()で取得したDataFrame
        hw: 対象ハードウェア名のリスト。[]の場合は全ハードウェアを対象
        begin: 集計開始日
        end: 集計終了日

    Returns:
        pl.DataFrame: long形式の販売台数DataFrame

        DataFrameのカラム構成:
        - report_date (Date): 集計期間の末日（日曜日）
        - hw (String): ゲームハードの識別子
        - units (Int64): 週次販売台数
    """
    df = hsf.date_filter(src_df, begin=begin, end=end)
    if len(hw) > 0:
        df = df.filter(pl.col('hw').is_in(hw))
    return df.select(['report_date', 'hw', 'units']).sort('report_date')


def monthly_sales_long(df: pl.DataFrame, hw: List[str] = [],
                       begin: datetime | date| None = None,
                       end: datetime | date | None = None) -> pl.DataFrame:
    """
    ハードウェアの月単位の販売台数をlong形式で返す。

    Args:
        df: load_hard_sales()で取得したDataFrame
        hw: 対象ハードウェア名のリスト。[]の場合は全ハードウェアを対象
        begin: 集計開始日
        end: 集計終了日

    Returns:
        pl.DataFrame: long形式の月次販売台数DataFrame

        DataFrameのカラム構成:
        - year_month (Date): 月の末日
        - year (Int16): 年
        - month (Int8): 月
        - hw (String): ゲームハードの識別子
        - monthly_units (Int64): 月次販売台数
    """
    df = hsf.monthly_sales(df, begin=begin, end=end)
    if len(hw) > 0:
        df = df.filter(pl.col('hw').is_in(hw))
    df = df.with_columns(
        year_month=pl.date(pl.col("year"), pl.col("month"), 1).dt.month_end()
    ).with_columns(
        year_month_str=pl.col("year_month").dt.strftime("%Y-%m")
    )
    return df.select(['year_month', 'year_month_str', 'year', 'month', 'hw', 'monthly_units']).sort('year_month')


def quarterly_sales_long(df: pl.DataFrame, hw: List[str] = [],
                         begin: datetime | date| None = None,
                         end: datetime | date | None = None) -> pl.DataFrame:
    """
    ハードウェアの四半期単位の販売台数をlong形式で返す。

    Args:
        df: load_hard_sales()で取得したDataFrame
        hw: 対象ハードウェア名のリスト。[]の場合は全ハードウェアを対象
        begin: 集計開始日
        end: 集計終了日

    Returns:
        pl.DataFrame: long形式の四半期販売台数DataFrame

        DataFrameのカラム構成:
        - quarter (String): report_dateの四半期（例: "2024Q1"）
        - year (Int16): 年
        - q_num (Int8): 四半期番号（1, 2, 3, 4）
        - hw (String): ゲームハードの識別子
        - quarterly_units (Int64): 四半期販売台数
    """
    df = hsf.quarterly_sales(df, begin=begin, end=end)
    if len(hw) > 0:
        df = df.filter(pl.col('hw').is_in(hw))
    return df.select(['quarter', 'year', 'q_num', 'hw', 'quarterly_units']).sort('quarter')


def yearly_sales_long(df: pl.DataFrame, hw: List[str] = [],
                      begin: datetime | date| None = None,
                      end: datetime | date | None = None) -> pl.DataFrame:
    """
    ハードウェアの年単位の販売台数をlong形式で返す。

    Args:
        df: load_hard_sales()で取得したDataFrame
        hw: 対象ハードウェア名のリスト。[]の場合は全ハードウェアを対象
        begin: 集計開始日
        end: 集計終了日

    Returns:
        pl.DataFrame: long形式の年次販売台数DataFrame

        DataFrameのカラム構成:
        - year (Int16): report_dateの年
        - hw (String): ゲームハードの識別子
        - yearly_units (Int64): 年次販売台数
    """
    df = hsf.yearly_sales(df, begin=begin, end=end)
    if len(hw) > 0:
        df = df.filter(pl.col('hw').is_in(hw))
    return df.select(['year', 'hw', 'yearly_units']).sort('year')


def cumulative_sales_long(df: pl.DataFrame, hw: List[str] = [],
                          begin: datetime | None = None,
                          end: datetime | None = None,
                          mode: str = "week",
                          full_name: bool = False) -> pl.DataFrame:
    """
    ハードウェアの累計販売台数をlong形式で返す。

    Args:
        df: load_hard_sales()で取得したDataFrame
        hw: 対象ハードウェア名のリスト。[]の場合は全ハードウェアを対象
        begin: 集計開始日
        end: 集計終了日
        mode: "week"、"month"または"year"を指定。週単位の集計なら"week"、月単位の集計なら"month"、年単位の集計なら"year"を指定。
        full_name: カラム名にフルネームを使用する

    Returns:
        pl.DataFrame: long形式の累計販売台数DataFrame

        DataFrameのカラム構成:
        - report_date (Date): 集計期間の末日（日曜日）
        - hw または full_name (String): ゲームハードの識別子またはフルネーム
        - sum_units (Int64): 累計販売台数
    """
    df = hsf.date_filter(df, begin=begin, end=end)
    if len(hw) > 0:
        df = df.filter(pl.col('hw').is_in(hw))

    columns_name = 'full_name' if full_name else 'hw'
    long_df = df.select(['report_date', columns_name, 'sum_units']).sort('report_date')

    if mode == "month":
        return (long_df
                .sort('report_date')
                .group_by_dynamic(
                    'report_date',
                    every='1mo',
                    closed='right',
                    period='1mo',
                    group_by=columns_name
                )
                .agg(pl.col('sum_units').last())
                .sort('report_date'))
    elif mode == "year":
        return (long_df
                .sort('report_date')
                .group_by_dynamic(
                    'report_date',
                    every='1y',
                    closed='right',
                    period='1y',
                    group_by=columns_name
                )
                .agg(pl.col('sum_units').last())
                .sort('report_date'))

    return long_df


def sales_by_delta_long(df: pl.DataFrame, mode: str = "week",
                        begin: int | None = None,
                        end: int | None = None,
                        hw: List[str] = [],
                        full_name: bool = False) -> pl.DataFrame:
    """
    ハードウェアの販売台数を発売日からの経過期間をインデックスとしたlong形式で返す。

    Args:
        df: load_hard_sales()で取得したDataFrame
        mode: "week"、"month"または"year"を指定。週単位の集計なら"week"、月単位の集計なら"month"、年単位の集計なら"year"を指定。
        begin: 集計開始（経過期間の最小値）
        end: 集計終了（経過期間の最大値）
        hw: 対象ハードウェア名のリスト。[]の場合は全ハードウェアを対象
        full_name: フルネームを使用するかどうか

    Returns:
        pl.DataFrame: long形式の販売台数DataFrame

        DataFrameのカラム構成:
        - delta_week (Int32): 発売日からの経過週数（modeが"week"の場合）
        - delta_month (Int16): 発売日からの経過ヶ月数（modeが"month"の場合）
        - delta_year (Int16): 発売年からの経過年数（modeが"year"の場合）
        - hw または full_name (String): ゲームハードの識別子またはフルネーム
        - units (Int64): 販売台数
    """
    if mode == "week":
        index_col = 'delta_week'
    elif mode == "month":
        index_col = 'delta_month'
    elif mode == "year":
        index_col = 'delta_year'
    else:
        raise ValueError("modeは'week', 'month', 'year'のいずれかを指定してください。")

    if begin:
        df = df.filter(pl.col(index_col) >= begin)
    if end:
        df = df.filter(pl.col(index_col) <= end)

    if len(hw) > 0:
        df = df.filter(pl.col('hw').is_in(hw))

    on_columns = 'full_name' if full_name else 'hw'

    return (df
            .group_by([index_col, on_columns])
            .agg(pl.col('units').sum())
            .sort(by=[index_col, on_columns]))


def sales_with_offset_long(src_df: pl.DataFrame,
                           hw_periods: List[dict],
                           end: int = 52) -> pl.DataFrame:
    """
    複数のハードウェアの異なる期間のデータを、各期間の開始点を揃えたlong形式で返す。

    Args:
        src_df: load_hard_sales()で取得したDataFrame
        hw_periods: 各ハードウェアの期間設定のリスト
            各要素は以下のキーを持つ辞書:
            - 'hw' (str, required): ハードウェアの識別子
            - 'begin' (datetime, required): 集計開始日
            - 'label' (str, optional): 列名（省略時はhw名を使用）
        end: 各期間の最大週数（デフォルトは52週）

    Returns:
        pl.DataFrame: long形式のDataFrame

        DataFrameのカラム構成:
        - offset_week (Int32): 各期間の開始日からの経過週数
        - label (String): ハードウェアのラベル
        - units (Int64): 週次販売台数
    """
    all_data = []

    for period in hw_periods:
        hw = period['hw']
        begin = period['begin']
        default_label = f"{hw}:{begin.strftime('%Y.%m.%d')}〜"
        label = period.get('label', default_label)

        hw_df = src_df.filter(pl.col('hw') == hw)
        hw_df = hw_df.filter(pl.col('report_date') >= begin)
        hw_df = hw_df.sort('report_date').head(end)

        hw_df = hw_df.with_columns(
            offset_week=((pl.col('report_date') - begin).dt.total_days() / 7).cast(pl.Int32)
        )

        hw_df = (hw_df
                 .select(['offset_week', 'units'])
                 .with_columns(label=pl.lit(label))
                 )

        all_data.append(hw_df)

    return pl.concat(all_data).sort('offset_week')


def cumulative_sales_by_delta_long(df: pl.DataFrame, mode: str = "week",
                                   hw: List[str] = [],
                                   begin: int | None = None,
                                   end: int | None = None) -> pl.DataFrame:
    """
    ハードウェアの累計販売台数を発売日からの経過期間をインデックスとしたlong形式で返す。

    Args:
        df: load_hard_sales()で取得したDataFrame
        mode: "week"、"month"または"year"を指定。週単位の集計なら"week"、月単位の集計なら"month"、年単位の集計なら"year"を指定。
        hw: 対象ハードウェア名のリスト。[]の場合は全ハードウェアを対象
        begin: 集計開始（経過期間の最小値）
        end: 集計終了（経過期間の最大値）

    Returns:
        pl.DataFrame: long形式の累計販売台数DataFrame

        DataFrameのカラム構成:
        - delta_week (Int32): 発売日からの経過週数（modeが"week"の場合）
        - delta_month (Int16): 発売日からの経過ヶ月数（modeが"month"の場合）
        - delta_year (Int16): 発売年からの経過年数（modeが"year"の場合）
        - hw (String): ゲームハードの識別子
        - sum_units (Int64): 累計販売台数
    """
    if mode == "week":
        index_col = 'delta_week'
    elif mode == "month":
        index_col = 'delta_month'
    elif mode == "year":
        index_col = 'delta_year'
    else:
        raise ValueError("modeは'week', 'month', 'year'のいずれかを指定してください。")

    if begin:
        df = df.filter(pl.col(index_col) >= begin)
    if end:
        df = df.filter(pl.col(index_col) <= end)

    if len(hw) > 0:
        df = df.filter(pl.col('hw').is_in(hw))

    return (df
            .group_by([index_col, 'hw'])
            .agg(pl.col('sum_units').last())
            .sort(by=[index_col, 'hw']))


def maker_long(df: pl.DataFrame,
               begin_year: int | None = None,
               end_year: int | None = None) -> pl.DataFrame:
    """
    ハードウェアのメーカー別年次販売台数をlong形式で返す。

    Args:
        df: load_hard_sales()で取得したDataFrame
        begin_year: 開始年（デフォルト: None）
        end_year: 終了年（デフォルト: None）

    Returns:
        pl.DataFrame: long形式のメーカー別年次販売台数DataFrame

        DataFrameのカラム構成:
        - year (Int16): report_dateの年
        - maker_name (String): メーカー名
        - yearly_units (Int64): 年次販売台数
        - yearly_percentage (Float64): 年次販売台数のシェア()
        （同年の全ハードウェアの年次販売台数に対する割合のパーセント）
    """
    begin = None if begin_year is None else datetime(begin_year, 1, 1)
    end = None if end_year is None else datetime(end_year, 12, 31)
    df = hsf.yearly_maker_sales(df, begin=begin, end=end)

    df = df.with_columns(
        yearly_ratio = (pl.col('yearly_units') / pl.col('yearly_units').sum().over('year')), 
    )
    df = df.with_columns(
        yearly_pct = pl.col('yearly_ratio')  * 100
    )
    maker_list = hs.get_maker(df)
    df = df.sort(by=['year', pl.col(name='maker_name').cast(dtype=pl.Enum(categories=maker_list))])
    return df.select(['year', 'maker_name', 'yearly_units', 'yearly_ratio', 'yearly_pct'])
