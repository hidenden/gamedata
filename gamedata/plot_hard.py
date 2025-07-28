# 標準ライブラリ
from datetime import datetime, timedelta
from typing import List, Optional

# サードパーティライブラリ
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.ticker import ScalarFormatter

# プロジェクト内モジュール
from gamedata import hard_sales as hs


def plot_cumulative_sales_by_delta(df: pd.DataFrame, hw: Optional[List[str]], 
                                monthly:bool = False, limit: int = 0) -> Figure:
    """
    各ハードウェアの発売日起点・累計販売台数推移をプロットする（週単位）
    
    Args:
        df: load_hard_sales()の戻り値のDataFrame
        hw: プロットしたいハードウェア名のリスト。Noneの場合は全ハードウェアを対象
        monthly: 月次の累計販売台数をプロットする場合はTrue、週単位の場合はFalse (defaultはFalse) 
        limit: 表示する週数(月数)（この数まで表示する）。0の場合は全期間を表示
        
    Returns:
        matplotlib.figure.Figure: グラフのFigureオブジェクト
    """
    if monthly:
        df = hs.pivot_cumulative_sales_by_delta_month(df, hw)
        title_key = '月'
    else:
        df = hs.pivot_cumulative_sales_by_delta(df, hw)
        title_key = '週'

    if limit > 0:
        df = df.head(limit)

    fig, ax = plt.subplots(figsize=(18, 9))
    plt.rcParams['font.family'] = 'Hiragino Sans'
    plt.rcParams['axes.unicode_minus'] = False

    # 折れ線グラフ（細い線のみ）
    df.plot(
        ax=ax,
        kind='line',
        linestyle='-',
        linewidth=2
    )

    ax.set_title(f'各ハードウェアの発売日起点・累計販売台数推移（{title_key}単位）')
    ax.set_xlabel(f'発売からの{title_key}数')
    ax.set_ylabel('累計販売台数')
    ax.legend(title='ハードウェア')

    # 縦軸の表示を指数表示から整数表示に変更
    ax.yaxis.set_major_formatter(ScalarFormatter(useOffset=False))
    ax.ticklabel_format(style='plain', axis='y')

    ax.grid(True)
    fig.tight_layout()

    return fig


def plot_cumulative_sales(df: pd.DataFrame, hw: Optional[List[str]], monthly:bool = False) -> Figure:
    """
    各ハードウェアの累計販売台数をプロットする
    Args:
        df: load_hard_sales()の戻り値のDataFrame
        hw: プロットしたいハードウェア名のリスト。Noneの場合は全ハードウェアを対象
        monthly: 月次の累計販売台数をプロットする場合はTrue、週単位の場合はFalse (defaultはFalse)
    Returns:
        matplotlib.figure.Figure: グラフのFigureオブジェクト
    """
    if monthly:
        df = hs.pivot_cumulative_sales_monthly(df, hw)
        title_key = '月'
    else:
        df = hs.pivot_cumulative_sales(df, hw)
        title_key = '週'

    fig, ax = plt.subplots(figsize=(18, 9))
    plt.rcParams['font.family'] = 'Hiragino Sans'
    plt.rcParams['axes.unicode_minus'] = False

    # 折れ線グラフ
    df.plot(
        ax=ax,
        kind='line',
        linestyle='-',
        linewidth=2
    )

    ax.set_title(f'各ハードウェアの{title_key}次累計販売台数推移')
    ax.set_xlabel(title_key)
    ax.set_ylabel('累計販売台数')
    ax.legend(title='ハードウェア')

    # 縦軸の表示を指数表示から整数表示に変更
    ax.yaxis.set_major_formatter(ScalarFormatter(useOffset=False))
    ax.ticklabel_format(style='plain', axis='y')

    ax.grid(True)
    fig.tight_layout()
    
    return fig


