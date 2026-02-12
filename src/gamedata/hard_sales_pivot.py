from datetime import datetime, timedelta
import polars as pl
from typing import List

# プロジェクト内モジュール
from . import hard_sales_filter as hsf

def pivot_sales(src_df: pl.DataFrame, hw:List[str] = [],
                begin: datetime | None = None,
                end: datetime | None = None) -> pl.DataFrame:
    """
    ハードウェアの週単位の販売台数をピボットテーブル形式で返す。

    Args:
        df: load_hard_sales()で取得したDataFrame
        hw: プロットしたいハードウェア名のリスト。[]の場合は全ハードウェアを対象
        begin: 集計開始日
        end: 集計終了日
        full_name: フルネームを使用するかどうか
        
    Returns:
        pl.DataFrame: report_dateをカラム、hwを列、unitsを値とするピボットテーブル
        
        DataFrameのカラム構成:
        - report_date (Date): 集計期間の末日（日曜日）
        - 各hw (Int64): ゲームハード別の週次販売台数
    """
    # begin/endでフィルタリング
    if begin is not None and end is not None:
        df = src_df.filter((pl.col('report_date') >= begin) & (pl.col('report_date') <= end))
    elif begin is not None:
        df = src_df.filter(pl.col('report_date') >= begin)
    elif end is not None:
        df = src_df.filter(pl.col('report_date') <= end)
    else:
        df = src_df.clone()
        
    # HWでフィルタリング
    if len(hw) > 0:
        df = df.filter(pl.col('hw').is_in(hw))

    return df.pivot(index='report_date',
                    on='hw',
                    values='units',
                    aggregate_function='last').sort('report_date')


def pivot_monthly_sales(df: pl.DataFrame, hw:List[str] = [],
                begin: datetime | None = None, 
                end: datetime | None = None) -> pl.DataFrame:
    """
    ハードウェアの月単位の販売台数をピボットテーブル形式で返す。

    Args:
        df: load_hard_sales()で取得したDataFrame
        hw: プロットしたいハードウェア名のリスト。[]の場合は全ハードウェアを対象
        begin: 集計開始日
        end: 集計終了日
        
    Returns:
        pl.DataFrame: year, monthをカラム、hwを列、monthly_unitsを値とするピボットテーブル
        
        DataFrameのカラム構成:
        - month (Date): 月の末日
        - 各hw (Int64): ゲームハード別の月次販売台数
    """
    df = hsf.monthly_sales(df, begin=begin, end=end)
    if len(hw) > 0:
        df = df.filter(pl.col('hw').is_in(hw))

    df = df.pivot(index=['year', 'month'],
                 on='hw',
                 values='monthly_units',
                 aggregate_function='last')
    df = (df
          .with_columns(
              month = pl.date(pl.col("year"), pl.col("month"), 1).dt.month_end())
          .select(['month'] + [col for col in df.columns if col not in ['year', 'month']])
          .sort(by='month')
          )    
    return df

def pivot_quarterly_sales(df: pl.DataFrame, hw:List[str] = [],
                begin: datetime | None = None, 
                end: datetime | None = None) -> pl.DataFrame:
    """
    ハードウェアの四半期単位の販売台数をピボットテーブル形式で返す。

    Args:
        df: load_hard_sales()で取得したDataFrame
        hw: プロットしたいハードウェア名のリスト。[]の場合は全ハードウェアを対象
        begin: 集計開始日
        end: 集計終了日
        
    Returns:
        pl.DataFrame: quarterをカラム、hwを列、quarterly_unitsを値とするピボットテーブル
        
        DataFrameのカラム構成:
        - quarter (String): report_dateの四半期（例: "2024Q1"）
        - 各hw (Int64): ゲームハード別の四半期販売台数
    """
    df = hsf.quarterly_sales(df, begin=begin, end=end)
    # HWでフィルタリング
    if len(hw) > 0:
        df = df.filter(pl.col('hw').is_in(hw))

    return df.pivot(index='quarter',
                    on='hw',
                    values='quarterly_units',
                    aggregate_function='last').sort(by='quarter')


def pivot_yearly_sales(df: pl.DataFrame, hw:List[str] = [],
                begin: datetime | None = None, 
                end: datetime | None = None) -> pl.DataFrame:
    """
    ハードウェアの年単位の販売台数をピボットテーブル形式で返す。

    Args:
        df: load_hard_sales()で取得したDataFrame
        hw: プロットしたいハードウェア名のリスト。[]の場合は全ハードウェアを対象
        begin: 集計開始日
        end: 集計終了日
        
    Returns:
        pl.DataFrame: yearをカラム、hwを列、yearly_unitsを値とするピボットテーブル
        
        DataFrameのカラム構成:
        - year (Int16): report_dateの年
        - 各hw (Int64): ゲームハード別の年次販売台数
    """
    df = hsf.yearly_sales(df, begin=begin, end=end)
    # HWでフィルタリング
    if len(hw) > 0:
        df = df.filter(pl.col('hw').is_in(hw))

    return df.pivot(index='year',
                    on='hw',
                    values='yearly_units',
                    aggregate_function='last').sort(by='year')


def pivot_cumulative_sales(df: pl.DataFrame, hw:List[str] = [], 
                           begin: datetime | None = None,
                           end: datetime | None = None,
                           mode:str = "week",
                           full_name:bool = False) -> pl.DataFrame:
    """
    ハードウェアの累計販売台数をピボットテーブル形式で返す。
    
    Args:
        df: load_hard_sales()で取得したDataFrame
        hw: プロットしたいハードウェア名のリスト。[]の場合は全ハードウェアを対象
        begin: 集計開始日
        end: 集計終了日
        mode: "week"、"month"または"year"を指定。週単位の集計なら"week"、月単位の集計なら"month"、年単位の集計なら"year"を指定。
        full_name: カラム名にフルネームを使用する
    
    Returns:
        pl.DataFrame: report_dateをカラム、hwを列、sum_unitsを値とするピボットテーブル
        
        DataFrameのカラム構成:
        - report_date (Date): 集計期間の末日（日曜日）
        - 各hw/full_name (Int64): ゲームハード別の累計販売台数
    """
    # begin/endでフィルタリング
    df = hsf.date_filter(df, begin=begin, end=end)
    # HWでフィルタリング
    if len(hw) > 0:
        df = df.filter(pl.col('hw').is_in(hw))

    # 横軸のカラム
    columns_name = 'full_name' if full_name else 'hw'
    # ピボットテーブルを作成
    df = (df
          .pivot(index='report_date', on=columns_name, values='sum_units',
                 aggregate_function='last')
          .sort('report_date')
    )
    if mode == "month":
        df = (df
              .group_by_dynamic(
                  "report_date",
                    every="1mo",
                    closed="right",
                    period="1mo"
              ).agg(pl.exclude("report_date").last())
              .sort('report_date')
        )
    elif mode == "year":
        df = (df
              .group_by_dynamic(
                  "report_date",
                    every="1y",
                    closed="right",
                    period="1y"
              ).agg(pl.exclude("report_date").last())
              .sort('report_date')
        )
    
    return df

def pivot_sales_by_delta(df: pl.DataFrame, mode:str = "week", 
                         begin:int | None = None,
                         end:int | None = None,
                         hw:List[str] = [], full_name:bool = False) -> pl.DataFrame:
    """
    ハードウェアの販売台数を発売日からの経過状況をカラム、hwを列、unitsを値とするピボットテーブル形式で返す。
    
    Args:
        df: load_hard_sales()で取得したDataFrame
        mode: "week"、"month"または"year"を指定。週単位の集計なら"week"、月単位の集計なら"month"、年単位の集計なら"year"を指定。
        begin: 集計開始（経過期間の最小値）
        end: 集計終了（経過期間の最大値）
        hw: プロットしたいハードウェア名のリスト。[]の場合は全ハードウェアを対象
        full_name: フルネームを使用するかどうか

    Returns:
        pl.DataFrame: delta_week, delta_month, delta_yearのいずれかをカラム、hwを列、unitsを値とするピボットテーブル
        
        DataFrameのカラム構成:
        - delta_week (Int32): 発売日からの経過週数（modeが"week"の場合）
        - delta_month (Int16): 発売日からの経過ヶ月数（modeが"month"の場合）
        - delta_year (Int16): 発売年からの経過年数（modeが"year"の場合）
        - 各hw/full_name (Int64): ゲームハード別の販売台数
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
        df = df.filter(pl.col(index_col) >= begin)
    if end:
        df = df.filter(pl.col(index_col) <= end)
    
    if len(hw) > 0:
        filtered_df = df.filter(pl.col('hw').is_in(hw))
    else:
        filtered_df = df

    # 横軸のカラム
    on_columns = 'full_name' if full_name else 'hw'

    # グループ化して集計してからピボット
    return (
        filtered_df
        .group_by([index_col, on_columns])
        .agg(pl.col('units').sum())
        .pivot(index=index_col, 
               on=on_columns, 
               values='units', 
               aggregate_function='last')
        .sort(by=[index_col])
    )


def pivot_sales_with_offset(src_df: pl.DataFrame, 
                            hw_periods: List[dict], end:int = 52) -> pl.DataFrame:
    """
    複数のハードウェアの異なる期間のデータを、各期間の開始点を揃えてピボットテーブル形式で返す。
    
    Args:
        src_df: load_hard_sales()で取得したDataFrame
        hw_periods: 各ハードウェアの期間設定のリスト
            各要素は以下のキーを持つ辞書:
            - 'hw' (str, required): ハードウェアの識別子
            - 'begin' (datetime, required): 集計開始日
            - 'label' (str, optional): 列名（省略時はhw名を使用）
        end: 各期間の最大週数（デフォルトは52週）
    
    Returns:
        pl.DataFrame: offset_weekをカラム、labelを列、unitsを値とするピボットテーブル
        
        DataFrameのカラム構成:
        - offset_week (Int32): 各期間の開始日からの経過週数
        - 各label (Int64): ハードウェア別の週次販売台数
        
    Example:
        >>> df = load_hard_sales()
        >>> hw_periods = [
        ...     {'hw': 'NSW', 'begin': datetime(2018, 1, 1), 'label': 'NSW 2018~'},
        ...     {'hw': 'NS2', 'begin': datetime(2026, 3, 1), 'label': 'NS2 2026~'}
        ... ]
        >>> result = pivot_sales_with_offset(df, hw_periods)
    """
    all_data = []
    
    for period in hw_periods:
        hw = period['hw']
        begin = period['begin']
        # defaultのlabelを生成､hw:YYYY.MM.DD〜形式
        default_label = f"{hw}:{begin.strftime('%Y.%m.%d')}〜"
        label = period.get('label', default_label)
        
        # 該当ハードウェアのデータを抽出
        hw_df = src_df.filter(pl.col('hw') == hw)
        
        # 期間でフィルタリング
        hw_df = hw_df.filter(pl.col('report_date') >= begin)
        # endのデータ数で制限
        hw_df = hw_df.sort('report_date').head(end)
        
        # 開始日からの経過週数を計算
        hw_df = hw_df.with_columns(
            offset_week = ((pl.col('report_date') - begin).dt.total_days() / 7).cast(pl.Int32)
        )
        
        # 必要な列のみ抽出し、labelを付与
        hw_df = (hw_df
                 .select(['offset_week', 'units'])
                 .with_columns(label = pl.lit(label))
        )
        
        all_data.append(hw_df)
    
    # すべてのデータを結合
    combined_df = pl.concat(all_data)
    
    # ピボットテーブル化
    return (combined_df
            .pivot(index='offset_week', 
                   on='label', 
                   values='units',
                   aggregate_function='last')
            .sort('offset_week'))


def pivot_cumulative_sales_by_delta(df: pl.DataFrame, mode:str = "week", 
                                    hw:List[str] = [],
                                    begin:int | None = None,
                                    end:int | None = None
                                    ) -> pl.DataFrame:
    """
    ハードウェアの累計販売台数を発売日からの経過状況をカラム、hwを列、sum_unitsを値とするピボットテーブル形式で返す。
    Args:
        df: load_hard_sales()で取得したDataFrame
        mode: "week"、"month"または"year"を指定。週単位の集計なら"week"、月単位の集計なら"month"、年単位の集計なら"year"を指定。
        hw: プロットしたいハードウェア名のリスト。[]の場合は全ハードウェアを対象
        begin: 集計開始（経過期間の最小値）
        end: 集計終了（経過期間の最大値）

    Returns:
        pl.DataFrame: delta_week, delta_month, delta_yearのいずれかをカラム、hwを列、sum_unitsを値とするピボットテーブル
        
        DataFrameのカラム構成:
        - delta_week (Int32): 発売日からの経過週数（modeが"week"の場合）
        - delta_month (Int16): 発売日からの経過ヶ月数（modeが"month"の場合）
        - delta_year (Int16): 発売年からの経過年数（modeが"year"の場合）
        - 各hw (Int64): ゲームハード別の累計販売台数
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
        df = df.filter(pl.col(index_col) >= begin)
    if end:
        df = df.filter(pl.col(index_col) <= end)

    if len(hw) > 0:
        filtered_df = df.filter(pl.col('hw').is_in(hw))
    else:
        filtered_df = df

    # グループ化して最後の値を取得してからピボット
    return (
        filtered_df
        .group_by([index_col, 'hw'])
        .agg(pl.col('sum_units').last())
        .pivot(index=index_col,
               on='hw',
               values='sum_units',
               aggregate_function='last')
        .sort(by=[index_col])
    )


def pivot_maker(df: pl.DataFrame, begin_year: int | None = None, end_year: int | None = None) -> pl.DataFrame:
    """
    ハードウェアのメーカー別販売データをピボットテーブル形式に変換する

    Parameters
    ----------
    df : pl.DataFrame
        load_hard_sales()で取得した週次販売データ
    begin_year : int, optional
        開始年（デフォルト: None）
    end_year : int, optional
        終了年（デフォルト: None）

    Returns
    -------
    pl.DataFrame
        メーカー別の販売データをピボットテーブル形式に変換したDataFrame
        
        DataFrameのカラム構成:
        - year (Int16): report_dateの年
        - 各maker_name (Int64): メーカー別の年次販売台数（Nintendo, SONY, Microsoft, SEGA等）
    """
    begin = None if begin_year is None else datetime(begin_year, 1, 1)
    end = None if end_year is None else datetime(end_year, 12, 31)

    df = hsf.yearly_maker_sales(df, begin=begin, end=end)
    pivot_df = df.pivot(index='year',
                        on='maker_name', 
                        values='yearly_units',
                        aggregate_function='last')
    
    # カラムの順序を調整
    desired_order = ['Nintendo', 'SONY', 'Microsoft', 'SEGA']
    existing_columns = pivot_df.columns
    
    # 指定した順序でカラムを並べ替え
    ordered_columns = ['year']  # indexカラムを先頭に
    for maker in desired_order:
        if maker in existing_columns:
            ordered_columns.append(maker)
    
    # その他のカラムを追加
    other_columns = [col for col in existing_columns if col not in desired_order and col != 'year']
    ordered_columns.extend(other_columns)
    
    return pivot_df.select(ordered_columns).sort('year')



def cumsum_diffs(df:pl.DataFrame,
                       cmplist: list[tuple[str, str]]) -> pl.DataFrame:
    """
    複数のハードウェア間の累計販売台数の差分を計算してDataFrameで返す。
    
    Args:
        df: load_hard_sales()で取得したDataFrame
        cmplist: 比較するハードウェアのペアのリスト。各タプルは(base_hw, cmp_hw)の形式で、
                 cmp_hwの累計販売台数からbase_hwの累計販売台数を引いた差分を計算する。
    
    Returns:
        pl.DataFrame: 各ペアの差分を列として持つDataFrame
        
        DataFrameのカラム構成:
        - weeks (UInt32): 経過週番号（0から始まる整数）
        - 各"{cmp_hw}_{base_hw}差" (Int64): 各ペアの累計販売台数の差分
                   例: "PS5_NSW差"は、PS5の累計販売台数からNSWの累計販売台数を引いた値
    """

    def cumsum_diff_frame(df:pl.DataFrame, base_hw: str, cmp_hw: str) -> pl.DataFrame:
        """base_hwとcmp_hwの週販差分を計算したDataFrameを返す"""
        pivot_df = pivot_cumulative_sales(df, hw=[base_hw, cmp_hw])
    
        # base_hw列の値がnullでない最初の行の1つ前の行のbase_hw列を0に設定
        # polarsではwith_row_indexで行番号を追加してから処理
        pivot_df = pivot_df.with_row_index('row_nr')
        
        # base_hwがnullでない最初の行番号を取得
        first_valid_row = pivot_df.filter(pl.col(base_hw).is_not_null()).select('row_nr').head(1)
        
        if first_valid_row.height > 0:
            first_row_nr = first_valid_row.item(0, 0)
            if first_row_nr > 0:
                prior_row_nr = first_row_nr - 1
                # その1つ前の行のbase_hwを0に設定
                pivot_df = pivot_df.with_columns(
                    pl.when(pl.col('row_nr') == prior_row_nr)
                    .then(0)
                    .otherwise(pl.col(base_hw))
                    .alias(base_hw)
                )
  
        # base_hwがnullでない行を抽出し、差分を計算
        diff_col_name = f"{cmp_hw}_{base_hw}差"
        pivot_df = (
            pivot_df
            .filter(pl.col(base_hw).is_not_null())
            .with_columns(
                diff_col_name = pl.col(cmp_hw) - pl.col(base_hw)
            )
            .filter(pl.col(diff_col_name) >= -10000)
            .select(['row_nr', diff_col_name])
        )
        
        # 行番号を0から振り直す
        pivot_df = pivot_df.with_row_index('new_row_nr').drop('row_nr').rename({'new_row_nr': 'row_nr'})
    
        return pivot_df

    diff_dfs = []
    for base_hw, cmp_hw in cmplist:
        diff_df = cumsum_diff_frame(df, base_hw, cmp_hw)
        diff_dfs.append(diff_df)
    
    # 最初のDataFrameをベースに、他のDataFrameをrow_nrで結合
    result_df = diff_dfs[0]
    for diff_df in diff_dfs[1:]:
        result_df = result_df.join(diff_df, on='row_nr', how='outer')
    
    # 行番号を0から振り直す
    result_df = (
        result_df.with_row_index('weeks')
        .drop('row_nr')
        .drop('row_nr_right')
    )
    return result_df
