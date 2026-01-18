from datetime import datetime
import pandas as pd
from typing import List

# プロジェクト内モジュール
from . import hard_sales_filter as hsf

def pivot_sales(src_df: pd.DataFrame, hw:List[str] = [],
                begin: datetime | None = None,
                end: datetime | None = None) -> pd.DataFrame:
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
                begin: datetime | None = None, 
                end: datetime | None = None) -> pd.DataFrame:
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
    df = hsf.monthly_sales(df, begin=begin, end=end)
    if len(hw) > 0:
        df =  df.loc[df['hw'].isin(hw)]

    return df.pivot(index=['year', 'month'], columns='hw', values='monthly_units')

def pivot_quarterly_sales(df: pd.DataFrame, hw:List[str] = [],
                begin: datetime | None = None, 
                end: datetime | None = None) -> pd.DataFrame:
    """
    ハードウェアの四半期単位の販売台数をピボットテーブル形式で返す。

    Args:
        df: load_hard_sales()で取得したDataFrame
        hw: プロットしたいハードウェア名のリスト。[]の場合は全ハードウェアを対象
        begin: 集計開始日
        end: 集計終了日
        
    Returns:
        pd.DataFrame: quarterをインデックス、hwを列、quarterly_unitsを値とするピボットテーブル
        
        DataFrameのカラム構成:
        - index: quarter (Period): report_dateの四半期
        - columns: hw (string): ゲームハードの識別子
        - values: quarterly_units (int64): 四半期販売台数
    """
    df = hsf.quarterly_sales(df, begin=begin, end=end)
    # HWでフィルタリング
    if len(hw) > 0:
        df =  df.loc[df['hw'].isin(hw)]

    return df.pivot(index='quarter', columns='hw', values='quarterly_units')


def pivot_yearly_sales(df: pd.DataFrame, hw:List[str] = [],
                begin: datetime | None = None, 
                end: datetime | None = None) -> pd.DataFrame:
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
    df = hsf.yearly_sales(df, begin=begin, end=end)
    # HWでフィルタリング
    if len(hw) > 0:
        df =  df.loc[df['hw'].isin(hw), :]

    return df.pivot(index='year', columns='hw', values='yearly_units')


def pivot_cumulative_sales(df: pd.DataFrame, hw:List[str] = [], 
                           begin: datetime | None = None,
                           end: datetime | None = None,
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
                         begin:int | None = None,
                         end:int | None = None,
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
                                    begin:int | None = None,
                                    end:int | None = None
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


def pivot_maker(df: pd.DataFrame, begin_year: int | None = None, end_year: int | None = None) -> pd.DataFrame:
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

    df = hsf.yearly_maker_sales(df, begin=begin, end=end)
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
