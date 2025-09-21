# 標準ライブラリ
import os
from datetime import datetime, timedelta
from typing import Optional

# サードパーティライブラリ
import pandas as pd
from pandas import Timedelta
from pandas import MultiIndex
from pandas.io.formats.style import Styler

# プロジェクト内モジュール
from gamedata import hard_info as hi

def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={
        'full_name': 'ハード',
        'hw': 'ハード',
        'report_date': '集計日',
        'delta_week': '週数',
        'sum_units': '累計台数',
        'units': '販売台数',
    })
    hard_dict = hi.get_hard_dict()
    df = df.rename(columns=hard_dict)
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
