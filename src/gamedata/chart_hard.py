# 標準ライブラリ
from datetime import datetime
from typing import List, Callable

# サードパーティライブラリ
import pandas as pd
from pandas.io.formats.style import Styler

import polars as pl
from great_tables import GT, style, loc, google_font


# プロジェクト内モジュール
from . import hard_info as hi
from . import hard_sales as hs
from . import hard_sales_filter as hsf

def rename_columns(df: pl.DataFrame) -> pl.DataFrame:
    """
    DataFrameの列名を日本語に変換する
    
    Args:
        df: 変換対象のDataFrame
        
    Returns:
        pl.DataFrame: 列名が日本語に変換されたDataFrame
    """
    base_rename_dict = {
        'full_name': 'ハード',
        'hw': 'ハード',
        'report_date': '集計日',
        'delta_week': '週数',
        'sum_units': '累計台数',
        'units': '販売台数',
        'maker_name': 'メーカー',
        'monthly_units': '月間販売台数',
        'weekly_units': '週間販売台数',
        'yearly_units': '年間販売台数',
        'month': '月',
        'year': '年',
        'week': '週',
    }
    hard_rename_dict = hi.get_hard_dict()
    
    # base_rename_dictとhard_rename_dictを結合
    rename_dict = {**base_rename_dict, **hard_rename_dict}
    
    df = df.rename(rename_dict)
    return df

def rename_hw(df: pl.DataFrame) -> pl.DataFrame:
    """
    DataFrameのhw列の値をフルネームに変換する
    
    Args:
        df: hw列を持つDataFrame
        
    Returns:
        pl.DataFrame: hw列がフルネームに変換されたDataFrame
    """
    hard_dict = hi.get_hard_dict()
    df = df.rename(hard_dict)
    return df

def rename_index(df: pd.DataFrame) -> pd.DataFrame:
    """
    DataFrameのインデックスのハード名をフルネームに変換する
    
    Args:
        df: ハード名をインデックスに持つDataFrame
        
    Returns:
        pd.DataFrame: インデックスがフルネームに変換されたDataFrame
    """
    hard_dict = hi.get_hard_dict()
    df = df.rename(index=hard_dict)
    return df

def rename_index_title(df: pd.DataFrame) -> pd.DataFrame:
    """
    DataFrameのインデックス名を日本語に変換する
    
    Args:
        df: 変換対象のDataFrame
        
    Returns:
        pd.DataFrame: インデックス名が日本語に変換されたDataFrame
    """
    index_dict = {'hw': 'ハード',
                  'report_date': '集計日',
                  'full_name': 'ハード',
                  'month': '月',
                  'year': '年',
                  'week': '週',
                  'delta_week': '週数',}
    ax = df.axes[0]
    if isinstance(ax, pd.MultiIndex):
        current = list(ax.names)
    else:
        current = [df.index.name]
    
    new_titles = [index_dict.get(name, name) for name in current]
    
    if isinstance(ax, pd.MultiIndex):
        return df.rename_axis(new_titles, axis=0)
    else:
        return df.rename_axis(new_titles[0], axis=0)


def chart_units_by_date_hw(df: pd.DataFrame, 
                           begin:datetime | None=None, end:datetime | None=None
                           ) -> tuple[pd.DataFrame, pd.io.formats.style.Styler]:
    """
    日付とハード別の販売台数チャートを出力する
    
    Args:
        df: load_hard_sales()の戻り値のDataFrame
        begin: 集計開始日
        end: 集計終了日
        
    Returns:
        tuple[pd.DataFrame, Styler]: データフレームとスタイル適用済みのStylerオブジェクトのタプル
        
        DataFrameのカラム構成:
        - index: 集計日 (datetime64), ハード (string): 日付とハード名のマルチインデックス
        - columns: 販売台数 (int64), 累計台数 (int64)
    """
    if begin is not None:
        df = df[df['report_date'] >= begin]
    if end is not None:
        df = df[df['report_date'] <= end]
        
    df_out = df.set_index(['report_date', 'hw'])
    df_out.sort_values(by=['report_date', 'units', 'hw'], ascending=[True, False, True], inplace=True)
    df_out = df_out[['units', 'sum_units']]
    df_out = rename_index(df_out)
    df_out = rename_columns(df_out)
    df_out = rename_index_title(df_out)

    styled = (df_out.style
        .format({'販売台数': '{:,}', '累計台数': '{:,}'})
        .set_properties(**{'text-align': 'right'}, subset=['販売台数', '累計台数'])
        .format_index(lambda t: t.strftime('%Y-%m-%d'),  level=0, axis=0)
        .bar(subset=['販売台数'], color="#18ba06")
        )
    return (df_out, styled)


def _chart_periodic_ranking(rank_n:int = 10, 
                         begin:datetime | None = None, 
                         end:datetime | None = None,
                         hw:List[str] = [], 
                         maker:List[str] = [],
                         data_source_fn:Callable = hsf.monthly_sales,
                         sort_column:str = 'monthly_units',
                         headers:List[str] = ['year', 'month']
                         ) -> pd.DataFrame:
    """
    ある期間のランキングチャートを出力する共通関数

    Args:
        rank_n: 上位n件。マイナスの場合は下位n件
        begin: 集計開始日
        end: 集計終了日
        hw: ハード名リスト（指定時はハードモード）
        maker: メーカー名リスト（指定時はメーカーモード）
        data_source_fn: データソース関数（weekly_sales, monthly_sales, yearly_salesなど）
        sort_column: ソートに使用する列名
        headers: 出力に含めるヘッダー列のリスト
        
    Returns:
        pd.DataFrame: ランキングデータのDataFrame。インデックスは順位（1から開始）
        
        DataFrameのカラム構成（headersとsort_columnにより変動）:
        - 週間: 集計日, ハード/メーカー, 週間販売台数
        - 月間: 年, 月, ハード/メーカー, 月間販売台数
        - 年間: 年, ハード/メーカー, 年間販売台数
    """
    df_all = hs.load_hard_sales()
    if (not hw) and maker:
        # This is maker mode
        maker_mode = True
        key_column = 'maker_name'
    else:
        maker_mode = False
        key_column = 'hw'
        
    df_sum = data_source_fn(df_all, begin=begin, end=end, maker_mode=maker_mode)
        
    if rank_n < 0:
        top_n = abs(rank_n)
        ascending = True
    else:
        top_n = rank_n
        ascending = False
    df_sorted = df_sum.sort_values(by=sort_column, ascending=ascending) 
        
    if hw:
        df_sorted = df_sorted[df_sorted[key_column].isin(hw)]
    if maker:
        df_sorted = df_sorted[df_sorted[key_column].isin(maker)]
        
    df_sorted_top = df_sorted.head(top_n)[[*headers, key_column, sort_column]]
    df_sorted_top = df_sorted_top.reset_index(drop=True)
    df_sorted_top.index += 1
    if (not maker):
        df_sorted_top = rename_hw(df_sorted_top)
    df_sorted_top = rename_columns(df_sorted_top)
    return df_sorted_top


def chart_weekly_ranking(rank_n:int = 10, 
                         begin:datetime | None = None, 
                         end:datetime | None = None,
                         hw:List[str] = [], 
                         maker:List[str] = []) -> pd.DataFrame:
    """
    週間ランキングチャートを出力する
    
    Args:
        rank_n: 上位n件。マイナスの場合は下位n件（デフォルト: 10）
        begin: 集計開始日
        end: 集計終了日
        hw: ハード名リスト（空の場合は全ハード）
        maker: メーカー名リスト（空の場合は全メーカー）
        
    Returns:
        pd.DataFrame: 週間ランキングのDataFrame
        
        DataFrameのカラム構成:
        - index: 順位（1から開始）
        - columns: 集計日 (datetime64), ハード/メーカー (string), 週間販売台数 (int64)
    """
    return _chart_periodic_ranking(rank_n=rank_n, begin=begin, end=end, 
                                  hw=hw, maker=maker, 
                                  data_source_fn=hsf.weekly_sales, 
                                  sort_column='weekly_units', 
                                  headers=['report_date'])
    
def chart_monthly_ranking(rank_n:int = 10, 
                         begin:datetime | None = None, 
                         end:datetime | None = None,
                         hw:List[str] = [], 
                         maker:List[str] = []) -> pd.DataFrame:
    """
    月間ランキングチャートを出力する
    
    Args:
        rank_n: 上位n件。マイナスの場合は下位n件（デフォルト: 10）
        begin: 集計開始日
        end: 集計終了日
        hw: ハード名リスト（空の場合は全ハード）
        maker: メーカー名リスト（空の場合は全メーカー）
        
    Returns:
        pd.DataFrame: 月間ランキングのDataFrame
        
        DataFrameのカラム構成:
        - index: 順位（1から開始）
        - columns: 年 (int64), 月 (int64), ハード/メーカー (string), 月間販売台数 (int64)
    """
    return _chart_periodic_ranking(rank_n=rank_n, begin=begin, end=end, 
                                  hw=hw, maker=maker, 
                                  data_source_fn=hsf.monthly_sales, 
                                  sort_column='monthly_units', 
                                  headers=['year', 'month'])

def chart_yearly_ranking(rank_n:int = 10, 
                         begin:datetime | None = None, 
                         end:datetime | None = None,
                         hw:List[str] = [], 
                         maker:List[str] = []) -> pd.DataFrame:
    """
    年間ランキングチャートを出力する
    
    Args:
        rank_n: 上位n件。マイナスの場合は下位n件（デフォルト: 10）
        begin: 集計開始日
        end: 集計終了日
        hw: ハード名リスト（空の場合は全ハード）
        maker: メーカー名リスト（空の場合は全メーカー）
        
    Returns:
        pd.DataFrame: 年間ランキングのDataFrame
        
        DataFrameのカラム構成:
        - index: 順位（1から開始）
        - columns: 年 (int64), ハード/メーカー (string), 年間販売台数 (int64)
    """
    return _chart_periodic_ranking(rank_n=rank_n, begin=begin, end=end, 
                                  hw=hw, maker=maker, 
                                  data_source_fn=hsf.yearly_sales, 
                                  sort_column='yearly_units', 
                                  headers=['year'])

    
def chart_delta_week_ranking(delta_week:int) -> pd.DataFrame:
    """
    指定された発売後の経過週数での累計販売台数ランキングを出力する
    
    Args:
        delta_week: 発売日から何週間後か
        
    Returns:
        pd.DataFrame: 経過週数時点での累計販売台数ランキングのDataFrame
        
        DataFrameのカラム構成:
        - index: 順位（1から開始）
        - columns: 集計日 (datetime64), 週数 (int64), hw (string), ハード (string), 累計台数 (int64)
    """

    df = hs.load_hard_sales()
    df = df.loc[df["delta_week"] == delta_week, :]
    df = df.loc[:, ['report_date', 'delta_week', 'hw', 'full_name', 'sum_units']]
    # dfを絡む sum_unitsの多い順にソートする
    df = df.sort_values(by='sum_units', ascending=False)
    df.reset_index(drop=True, inplace=True)
    df.index += 1
    return df

def style_sales(df: pd.DataFrame, columns:List[str] | None = None,
                date_columns:List[str] | None = None,
                percent_columns:List[str] | None = None,
                datetime_index:bool = False,
                highlights:List[str] | None = None,
                gradients:List[str] | None = None,
                gradient_horizontal:bool = False,
                bars:List[str] | None = None,
                bar_color:str = "#18ba06dd") -> Styler:
    """
    販売台数データフレームにスタイルを適用する
    
    Args:
        df: 販売台数データフレーム
        columns: スタイルを適用する列名のリスト（Noneの場合は全列）
        date_columns: 日付フォーマットを適用する列名のリスト
        percent_columns: パーセントフォーマットを適用する列名のリスト
        datetime_index: インデックスがdatetime型の場合に日付フォーマットを適用するかどうか(level=0のみ対応)
        highlights: 強調表示する列名のリスト
        gradients: グラデーションを適用する列名のリスト
        gradient_horizontal: 行方向にグラデーションを適用するかどうか
        bars: 棒グラフを適用する列名のリスト
        bar_color: 棒グラフの色（デフォルト: "#5fba7d"）
        
    Returns:
        Styler: スタイルが適用されたStylerオブジェクト
    """
    styled = df.style
    if columns is None:
        columns = df.columns.tolist()
    styled = styled.format('{:,.0f}', subset=columns)
    styled = styled.set_properties(**{'text-align': 'right'}, subset=columns)
    
    if date_columns is not None:
        styled = styled.format(subset=date_columns, formatter=lambda t: t.strftime('%Y-%m-%d')) 
        styled = styled.set_properties(**{'text-align': 'left'}, subset=date_columns)        
    
    if percent_columns is not None:
        styled = styled.format(subset=percent_columns, formatter='{:.1%}')
        styled = styled.set_properties(**{'text-align': 'right'}, subset=percent_columns)
        
    if highlights is not None:
        for highlight in highlights:
            if highlight in columns:
                styled = styled.highlight_max(subset=[highlight], color="#b31d15")
        
    if gradients is not None:
        for gradient in gradients:
            if gradient in columns:
                styled = styled.background_gradient(subset=[gradient], cmap='Blues')
        
    if gradient_horizontal:
        styled = styled.background_gradient(axis=1, cmap='Blues')
        
    if bars is not None:
        for bar in bars:
            if bar in columns:
                styled = styled.bar(subset=[bar], color=bar_color)
        
    if datetime_index:
        styled = styled.format_index(lambda t: t.strftime('%Y-%m-%d'), axis=0, level=0)
    
    return styled