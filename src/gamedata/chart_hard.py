# 標準ライブラリ
from datetime import datetime
from typing import List, Callable

# サードパーティライブラリ
import pandas as pd
from pandas.io.formats.style import Styler
import polars as pl

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
    df = df.rename(base_rename_dict, strict=False)
    return df

def rename_hw(df: pl.DataFrame) -> pl.DataFrame:
    """
    DataFrameのhw列の値をフルネームに変換する
    
    Args:
        df: hw列を持つDataFrame
        
    Returns:
        pl.DataFrame: hw列がフルネームに変換されたDataFrame
    """
    # dfにカラム:hwがある場合、hw列の値をhard_dictで変換する
    if 'hw' in df.columns:
        hard_dict = hi.get_hard_dict()
        df = (df
              .with_columns(pl.col('hw').replace(hard_dict, default=pl.col('hw')))
            )
    return df


def chart_units_by_date_hw(df: pl.DataFrame, begin:datetime|None = None, end:datetime|None = None) -> pd.io.formats.style.Styler:
    """
    日付とハード別の販売台数チャートを出力する
    
    Args:
        df: load_hard_sales()の戻り値のDataFrame(事前にdate_filter()でフィルタリング済み推奨)
        
    Returns:
        pd.io.formats.style.Styler: スタイル適用済みのStylerオブジェクト

    以下のコメントは後で削除､現在は実装の参考のために残す        
        DataFrameのカラム構成:
        - index: 集計日 (datetime64), ハード (string): 日付とハード名のマルチインデックス
        - columns: 販売台数 (int64), 累計台数 (int64)
    """
    df = hsf.date_filter(df, begin=begin, end=end)
    df = (df
          .sort(by=['report_date', 'units', 'hw'], descending=[False, True, False])
          .select(pl.col('report_date'), 
                  pl.col('full_name'), 
                  pl.col('units'), 
                  pl.col('sum_units'))
    )
    df = rename_columns(df)

    pdf = df.to_pandas()
    pdf = pdf.set_index(['集計日', 'ハード'])
    styled = (pdf.style
        .format({'販売台数': '{:,}', '累計台数': '{:,}'})
        .set_properties(**{'text-align': 'right'}, subset=['販売台数', '累計台数'])
        .format_index(lambda t: t.strftime('%Y-%m-%d'),  level=0, axis=0)
        .bar(subset=['販売台数'], color="#18ba06")
        )
    return styled


def _chart_periodic_ranking(rank_n:int = 10, 
                         begin:datetime | None = None, 
                         end:datetime | None = None,
                         hw:List[str] = [], 
                         maker:List[str] = [],
                         data_source_fn:Callable = hsf.monthly_sales,
                         sort_column:str = 'monthly_units',
                         headers:List[str] = ['year', 'month']
                         ) -> pl.DataFrame:
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
        pl.DataFrame: ランキングデータのDataFrame。インデックスは順位（1から開始）
        
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
        filter_dict = maker
    else:
        maker_mode = False
        key_column = 'hw'
        if hw:
            filter_dict = hw
        else:
            filter_dict = None  # 全ハード対象
                
    if rank_n < 0:  # 負の数の場合は逆順ソート
        top_n = abs(rank_n)
        descending_flag = False
    else: # 正の数の場合は通常ソート
        top_n = rank_n
        descending_flag = True

    df_src : pl.DataFrame = data_source_fn(df_all, begin=begin, end=end, maker_mode=maker_mode)

    df_src = (df_src
              .filter(pl.col(key_column).is_in(filter_dict) if filter_dict is not None else pl.lit(True))
              .sort(by=sort_column, descending=descending_flag)
    )
    if len(df_src) > top_n:
        df_src = df_src.head(top_n)
    actual_rows = len(df_src)
    df_src = (df_src
              .with_columns(pl.arange(1, actual_rows + 1).alias('順位')) # 通番のカラムを追加
              .with_columns(pl.col("順位").cast(pl.Int16))  # ソート列をInt16にキャスト
              .select(['順位', *headers, key_column, sort_column])
    )
    
    if (not maker):
        df_src = rename_hw(df_src)
    df_src = rename_columns(df_src)
    return df_src


def chart_weekly_ranking(rank_n:int = 10, 
                         begin:datetime | None = None, 
                         end:datetime | None = None,
                         hw:List[str] = [], 
                         maker:List[str] = []) -> pl.DataFrame:
    """
    週間ランキングチャートを出力する
    
    Args:
        rank_n: 上位n件。マイナスの場合は下位n件（デフォルト: 10）
        begin: 集計開始日
        end: 集計終了日
        hw: ハード名リスト（空の場合は全ハード）
        maker: メーカー名リスト（空の場合は全メーカー）
        
    Returns:
        pl.DataFrame: 週間ランキングのDataFrame
        
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
                         maker:List[str] = []) -> pl.DataFrame:
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
                         maker:List[str] = []) -> pl.DataFrame:
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

    
def chart_delta_week_ranking(delta_week:int) -> pl.DataFrame:
    """
    指定された発売後の経過週数での累計販売台数ランキングを出力する
    
    Args:
        delta_week: 発売日から何週間後か
        
    Returns:
        pl.DataFrame: 経過週数時点での累計販売台数ランキングのDataFrame
        
        DataFrameのカラム構成:
        - 順位（1から開始）
        - 集計日 (datetime64)
        - 週数 (int64)
        - ハード (string) 
        - 累計台数 (int64)
    """

    df = hs.load_hard_sales()
    
    df = (df
          .filter(pl.col("delta_week") == delta_week)
          .sort(by="sum_units", descending=True)
          )
    row_num = len(df)
    df = (df
          .with_columns(pl.arange(1, row_num + 1).alias('順位')) # 通番のカラムを追加
          .with_columns(pl.col("順位").cast(pl.Int16))  # ソート列をInt16にキャスト
          .select(['順位', 'report_date', 'delta_week', 'full_name', 'sum_units'])
    )
    return rename_columns(df)

def style_sales(df: pl.DataFrame, columns:List[str] | None = None,
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

    first_column = df.columns[0]
    pd_df = df.to_pandas()
    pd_df = pd_df.set_index(first_column)
    
    styled = pd_df.style
    if columns is None:
        columns = pd_df.columns.tolist()
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


def style(df: pl.DataFrame,
           highlight:bool = False,
           gradient:bool = False,
           bar:bool = False,
           gradient_horizontal:bool = False,
           bar_color:str = "#18ba06dd") -> Styler:
    """
    DataFrameをPandasのStylerオブジェクトに変換する
    
    Args:
        df: 変換対象のDataFrame
        highlight: 数値列を自動的に強調表示するかどうか
        gradient: 数値列に自動的にグラデーションを適用するかどうか
        bar: 数値列に自動的に棒グラフを適用するかどうか
        gradient_horizontal: 行方向にグラデーションを適用するかどうか
        bar_color: 棒グラフの色
    Returns:
        Styler: 変換されたStylerオブジェクト
    """
    # df.columns[0]の値がユニークかどうかを確認する｡ユニークはないなら､行番号のカラムを一番左側に追加する
    first_column = df.columns[0]
    all_columns = df.columns
    if df[first_column].n_unique() != df.height:
        df = (df
              .with_columns(pl.arange(0, df.height).alias('id'))
              .with_columns(pl.col("id").cast(pl.Int32))
              .select(['id'] + all_columns)
              )
    
    num_columns = df.select(pl.col(pl.Int64)).columns
    highlights = num_columns if highlight else None
    gradients = num_columns if gradient or gradient_horizontal else None
    bars = num_columns if bar else None
        
    date_columns = df.select(pl.col(pl.Date)).columns
    percent_columns = df.select(pl.col(pl.Float64)).columns
    
    # date_columns[0]とdf.columns[0]が同じ場合、date_columnsから削除する
    if date_columns and (date_columns[0] == df.columns[0]):
        date_columns = date_columns[1:]
        datetime_index = True
    else:
        datetime_index = False
    
    return style_sales(df,
                columns = num_columns,
                date_columns = date_columns,
                percent_columns = percent_columns,
                datetime_index = datetime_index,
                highlights = highlights,
                gradients = gradients,
                gradient_horizontal = gradient_horizontal,
                bars = bars,
                bar_color = bar_color
                )