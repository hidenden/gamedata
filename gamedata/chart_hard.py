# 標準ライブラリ
import os
from datetime import datetime, timedelta
from typing import Optional, List, Callable

# サードパーティライブラリ
import pandas as pd
from pandas import Timedelta
from pandas import MultiIndex
from pandas.io.formats.style import Styler

# プロジェクト内モジュール
from gamedata import hard_info as hi
from gamedata import hard_sales as hs

def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={
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
    })
    hard_dict = hi.get_hard_dict()
    df = df.rename(columns=hard_dict)
    return df

def rename_hw(df: pd.DataFrame) -> pd.DataFrame:
    hard_dict = hi.get_hard_dict()
    df['hw'] = df['hw'].map(hard_dict).fillna(df['hw'])
    return df

def rename_index(df: pd.DataFrame) -> pd.DataFrame:
    hard_dict = hi.get_hard_dict()
    df = df.rename(index=hard_dict)
    return df

def rename_index_title(df: pd.DataFrame) -> pd.DataFrame:
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
                           begin:Optional[datetime]=None, end:Optional[datetime]=None
                           ) -> tuple[pd.DataFrame, pd.io.formats.style.Styler]:
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
        .format_index(lambda t: t.strftime('%Y-%m-%d'),  level=0, axis=0))
    return (df_out, styled)


def _chart_periodic_ranking(rank_n:int = 10, 
                         begin:Optional[datetime] = None, 
                         end:Optional[datetime] = None,
                         hw:List[str] = [], 
                         maker:List[str] = [],
                         data_source_fn:Callable = hs.monthly_sales,
                         sort_column:str = 'monthly_units',
                         headers:List[str] = ['year', 'month']
                         ) -> pd.DataFrame:
    """ある期間のランキングチャートを出力

    Args:
        rank_n (int, optional): 上位n件. Defaults to 10.
            マイナスだった場合は下位n件.
        begin (Optional[datetime], optional): 開始日. Defaults to None.
        end (Optional[datetime], optional): 終了日. Defaults to None.
        hw (List[str], optional): ハード名リスト. Defaults to [].
        maker (List[str], optional): メーカー名リスト. Defaults to [].
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
                         begin:Optional[datetime] = None, 
                         end:Optional[datetime] = None,
                         hw:List[str] = [], 
                         maker:List[str] = []) -> pd.DataFrame:
    """週間ランキングチャートを出力
    Args:
        rank_n (int, optional): 上位n件. Defaults to 10.
            マイナスだった場合は下位n件.
        begin (Optional[datetime], optional): 開始日. Defaults to None.
        end (Optional[datetime], optional): 終了日. Defaults to None.
        hw (List[str], optional): ハード名リスト. Defaults to [].
        maker (List[str], optional): メーカー名リスト. Defaults to [].
    """
    return _chart_periodic_ranking(rank_n=rank_n, begin=begin, end=end, 
                                  hw=hw, maker=maker, 
                                  data_source_fn=hs.weekly_sales, 
                                  sort_column='weekly_units', 
                                  headers=['report_date'])
    
def chart_monthly_ranking(rank_n:int = 10, 
                         begin:Optional[datetime] = None, 
                         end:Optional[datetime] = None,
                         hw:List[str] = [], 
                         maker:List[str] = []) -> pd.DataFrame:
    """月間ランキングチャートを出力
    Args:
        rank_n (int, optional): 上位n件. Defaults to 10.
            マイナスだった場合は下位n件.
        begin (Optional[datetime], optional): 開始日. Defaults to None.
        end (Optional[datetime], optional): 終了日. Defaults to None.
        hw (List[str], optional): ハード名リスト. Defaults to [].
        maker (List[str], optional): メーカー名リスト. Defaults to [].
    """
    return _chart_periodic_ranking(rank_n=rank_n, begin=begin, end=end, 
                                  hw=hw, maker=maker, 
                                  data_source_fn=hs.monthly_sales, 
                                  sort_column='monthly_units', 
                                  headers=['year', 'month'])

def chart_yearly_ranking(rank_n:int = 10, 
                         begin:Optional[datetime] = None, 
                         end:Optional[datetime] = None,
                         hw:List[str] = [], 
                         maker:List[str] = []) -> pd.DataFrame:
    """年間ランキングチャートを出力
    Args:
        rank_n (int, optional): 上位n件. Defaults to 10.
            マイナスだった場合は下位n件.
        begin (Optional[datetime], optional): 開始日. Defaults to None.
        end (Optional[datetime], optional): 終了日. Defaults to None.
        hw (List[str], optional): ハード名リスト. Defaults to [].
        maker (List[str], optional): メーカー名リスト. Defaults to [].
    """
    return _chart_periodic_ranking(rank_n=rank_n, begin=begin, end=end, 
                                  hw=hw, maker=maker, 
                                  data_source_fn=hs.yearly_sales, 
                                  sort_column='yearly_units', 
                                  headers=['year'])