# 標準ライブラリ

# サードパーティライブラリ
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

# プロジェクト内モジュール
from . import hard_sales as hs
from . import hard_sales_pivot as pv
from . import hard_info as hi
from . import plot_util as pu

def plot_maker_share_pie(begin_year:int | None = None, 
                         end_year:int | None = None) -> tuple[Figure, pd.DataFrame]:
    """
    年ごとのメーカーシェアを円グラフで可視化する

    Args:
        begin_year: 表示する最初の年
        end_year: 表示する最後の年
        
    Returns:
        tuple[Figure, pd.DataFrame]: グラフのFigureオブジェクトとプロットに使用したデータのDataFrameのタプル
        
        DataFrameのカラム構成:
        - index: year (int64): report_dateの年
        - columns: maker_name (string): メーカー名（Nintendo, SONY, Microsoft, SEGA等）
        - values: yearly_units (int64): 年次販売台数
    """
    df = hs.load_hard_sales()
    maker_sales = pv.pivot_maker(df, begin_year=begin_year, end_year=end_year)

    n = len(maker_sales)
    plt.ioff()
    fig, axes = plt.subplots(1, n, figsize=(4*n, 4))
    plt.rcParams['font.family'] = 'Hiragino Sans'
    plt.rcParams['axes.unicode_minus'] = False
    # 背景の透明化
    if pu.get_transparent_mode():
        plt.rcParams['figure.facecolor'] = 'none'
        plt.rcParams['axes.facecolor'] = 'none'

    if n == 1:
        axes = [axes]
    legend_labels = None
    legend_handles = None
    for i, (ax, (idx, s)) in enumerate(zip(axes, maker_sales.iterrows())):
        s_data = s[s > 0]
        colors = hi.get_maker_colors(s_data.index.to_list())
        wedges, texts, autotexts = ax.pie(s_data, labels=None, autopct='%1.1f%%', colors=colors, startangle=90, counterclock=False)
        for autotext in autotexts:
            autotext.set_color('white')
        ax.set_title(f'メーカーシェア {s.name}')
        if i == 0:
            legend_labels = s_data.index.to_list()
            legend_handles = wedges
    if legend_handles and legend_labels:
        fig.legend(legend_handles, legend_labels, loc='upper right', bbox_to_anchor=(1.05, 1))
    fig.tight_layout()
    
    dispfunc = pu.get_dispfunc()
    if dispfunc is not None:
        dispfunc(fig)

    return (fig, maker_sales)

