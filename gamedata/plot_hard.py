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
from gamedata import hard_info as hi


def plot_cumulative_sales_by_delta(df: pd.DataFrame, hw: List[str] = [], 
                                   mode:str = "week", limit: int = 0) -> Figure:
    """
    各ハードウェアの発売日起点・累計販売台数推移をプロットする（週単位）
    
    Args:
        df: load_hard_sales()の戻り値のDataFrame
        hw: プロットしたいハードウェア名のリスト。[]の場合は全ハードウェアを対象
        mode: "month"の場合は月次の、"week"の場合は週単位、"year"の場合は年単位の累計販売台数をプロットする、 (defaultは"week")
        limit: 表示するデータ数（この数まで表示する）。0の場合は全期間を表示
        
    Returns:
        matplotlib.figure.Figure: グラフのFigureオブジェクト
    """
    df = hs.pivot_cumulative_sales_by_delta(df, hw=hw, mode=mode)
    if mode == "month":
        title_key = '月'
    elif mode == "year":
        title_key = '年'
    else:
        title_key = '週'

    if limit > 0:
        df = df.head(limit)

    fig, ax = plt.subplots(figsize=(18, 9))
    plt.rcParams['font.family'] = 'Hiragino Sans'
    plt.rcParams['axes.unicode_minus'] = False
    color_table = hi.get_hard_colors(df.columns.tolist())
               
    # 折れ線グラフ（細い線のみ）
    df.plot(
        ax=ax,
        kind='line',
        linestyle='-',
        linewidth=2,
        color=color_table
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


def plot_cumulative_sales(df: pd.DataFrame, hw: List[str] = [], mode:str="week") -> Figure:
    """
    各ハードウェアの累計販売台数をプロットする
    Args:
        df: load_hard_sales()の戻り値のDataFrame
        hw: プロットしたいハードウェア名のリスト。[]の場合は全ハードウェアを対象
        mode: "month"の場合は月次の、"week"の場合は週単位、"year"の場合は年単位の累計販売台数をプロットする、 (defaultは"week")
    Returns:
        matplotlib.figure.Figure: グラフのFigureオブジェクト
    """
    df = hs.pivot_cumulative_sales(df, hw=hw)
    if mode == "week":
        title_key = '週'
    elif mode == "month":
        df = df.resample('M').last()
        title_key = '月'
    elif mode == "year":
        df = df.resample('Y').last()
        title_key = '年'

    fig, ax = plt.subplots(figsize=(18, 9))
    plt.rcParams['font.family'] = 'Hiragino Sans'
    plt.rcParams['axes.unicode_minus'] = False

    color_table = hi.get_hard_colors(df.columns.tolist())              

    # 折れ線グラフ
    df.plot(
        ax=ax,
        kind='line',
        linestyle='-',
        linewidth=2,
        color=color_table
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


