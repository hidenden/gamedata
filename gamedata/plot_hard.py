# 標準ライブラリ
from datetime import datetime, timedelta
from typing import List, Optional

# サードパーティライブラリ
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.ticker import ScalarFormatter, MultipleLocator

# プロジェクト内モジュール
from gamedata import hard_sales as hs
from gamedata import hard_info as hi
from gamedata import hard_event as he

_FigSize = (10, 5)

def get_figsize() -> tuple[int, int]:
    return _FigSize

def set_figsize(width: int, height: int) -> None:
    global _FigSize
    _FigSize = (width, height)

def plot_cumulative_sales_by_delta(hw: List[str] = [], ymax:Optional[int]=None,
                                   xgrid: Optional[int] = None, ygrid: Optional[int] = None,
                                   mode:str = "week", limit: int = 0) -> tuple[Figure, pd.DataFrame]:
    """
    各ハードウェアの発売日起点・累計販売台数推移をプロットする（週単位）
    
    Args:
        hw: プロットしたいハードウェア名のリスト。[]の場合は全ハードウェアを対象
        mode: "month"の場合は月次の、"week"の場合は週単位、"year"の場合は年単位の累計販売台数をプロットする、 (defaultは"week")
        limit: 表示するデータ数（この数まで表示する）。0の場合は全期間を表示
        
    Returns:
        matplotlib.figure.Figure: グラフのFigureオブジェクト
        pd.DataFrame: プロットに使用したデータのDataFrame
    """
    df = hs.load_hard_sales()
    df = hs.pivot_cumulative_sales_by_delta(df, hw=hw, mode=mode)
    if mode == "month":
        title_key = '月'
    elif mode == "year":
        title_key = '年'
    else:
        title_key = '週'

    if limit > 0:
        df = df.head(limit)

    fig, ax = plt.subplots(figsize=_FigSize)
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

    ax.set_title(f'発売日起点累計販売台数')
    ax.set_xlabel(f'発売からの{title_key}数')
    ax.set_ylabel('累計販売台数')
    ax.legend(title='ハード')

    # Y軸の上限設定
    if ymax is not None:
        ax.set_ylim(top=ymax)
    ax.set_ylim(bottom=0)
    
    # Y軸 ygrid 毎にグリッド線
    if ygrid is not None:
        ax.yaxis.set_major_locator(MultipleLocator(ygrid))
        ax.yaxis.set_minor_locator(MultipleLocator(ygrid / 2))

    # X軸 xgrid毎にグリッド線
    if xgrid is not None:
        ax.xaxis.set_major_locator(MultipleLocator(xgrid))
        ax.xaxis.set_minor_locator(MultipleLocator(xgrid / 2))

    # 縦軸の表示を指数表示から整数表示に変更
    ax.yaxis.set_major_formatter(ScalarFormatter(useOffset=False))
    ax.ticklabel_format(style='plain', axis='y')

    ax.grid(True)
    fig.tight_layout()

    return (fig, df)

def plot_sales(hw: List[str] = [], begin: Optional[datetime] = None, 
               end: Optional[datetime] = None, ymax:Optional[int]=None, 
               xgrid: Optional[int] = None, ygrid: Optional[int] = None,
               mode: Optional[str] = "week",
               event_priority: int = 2
               ) -> tuple[Figure, pd.DataFrame]:
    """
    各ハードウェアの販売台数推移をプロットする（default = 週単位）

    Args:
        hw: プロットしたいハードウェア名のリスト。[]の場合は全ハードウェアを対象
    Args:
        hw: プロットしたいハードウェア名のリスト。[]の場合は全ハードウェアを対象
        mode: "month"の場合は月次の、"week"の場合は週単位、"year"の場合は年単位の累計販売台数をプロットする、 (defaultは"week")
        limit: 表示するデータ数（この数まで表示する）。0の場合は全期間を表示
        ymax: Y軸の上限値
        ygrid: Y軸のグリッド線の間隔
        xgrid: X軸のグリッド線の間隔

    Returns:
        matplotlib.figure.Figure: グラフのFigureオブジェクト
        pd.DataFrame: プロットに使用したデータのDataFrame
    """
    df = hs.load_hard_sales()

    if mode == "month":
        df = hs.pivot_monthly_sales(df, hw=hw, begin=begin, end=end)
        title_key = '月'
    elif mode == "year":
        df = hs.pivot_yearly_sales(df, hw=hw, begin=begin, end=end)
        title_key = '年'
    else:
        df = hs.pivot_sales(df, hw=hw, begin=begin, end=end)
        title_key = '週'

    fig, ax = plt.subplots(figsize=_FigSize)
    plt.rcParams['font.family'] = 'Hiragino Sans'
    plt.rcParams['axes.unicode_minus'] = False
    color_table = hi.get_hard_colors(df.columns.tolist())
               
    # 折れ線グラフ
    df.plot(
        ax=ax,
        kind='line',
        marker='o',
        linewidth=2,
        color=color_table
    )

    # event_dfの情報をannotationとしてグラフに追加する
    event_df = he.load_hard_event()
    filtered_events = he.add_event_positions(event_df, df, priority=event_priority)
    for report_date, event_row in filtered_events.iterrows():
        ax.annotate(event_row['event_name'], 
                    xy=(event_row['x_pos'], event_row['y_pos']), 
                    xytext=(8, 8),
                    textcoords='offset points',
                    fontsize=9, color='black')

    ax.set_title(f'販売台数（{title_key}単位）')
    ax.set_ylabel('販売台数')
    ax.set_xlabel('集計日')
    ax.legend(title='ハード')

    # Y軸の上限設定
    if ymax is not None:
        ax.set_ylim(top=ymax)
    ax.set_ylim(bottom=0)
    
    # Y軸 ygrid 毎にグリッド線
    if ygrid is not None:
        ax.yaxis.set_major_locator(MultipleLocator(ygrid))
        ax.yaxis.set_minor_locator(MultipleLocator(ygrid / 2))

    # X軸 xgrid毎にグリッド線
    if xgrid is not None:
        ax.xaxis.set_major_locator(MultipleLocator(xgrid))
        ax.xaxis.set_minor_locator(MultipleLocator(xgrid / 2))

    # 縦軸の表示を指数表示から整数表示に変更
    ax.yaxis.set_major_formatter(ScalarFormatter(useOffset=False))
    ax.ticklabel_format(style='plain', axis='y')

    ax.grid(True)
    fig.tight_layout()

    return (fig, df)

def plot_sales_by_delta(hw: List[str] = [], ymax:Optional[int]=None,
                        xgrid: Optional[int] = None, ygrid: Optional[int] = None,
                        mode:str = "week", limit: int = 0) -> tuple[Figure, pd.DataFrame]:
    """
    各ハードウェアの発売日起点・販売台数推移をプロットする（default = 週単位）
    
    Args:
        hw: プロットしたいハードウェア名のリスト。[]の場合は全ハードウェアを対象
        mode: "month"の場合は月次の、"week"の場合は週単位、"year"の場合は年単位の累計販売台数をプロットする、 (defaultは"week")
        limit: 表示するデータ数（この数まで表示する）。0の場合は全期間を表示
        ymax: Y軸の上限値
        ygrid: Y軸のグリッド線の間隔
        xgrid: X軸のグリッド線の間隔

    Returns:
        matplotlib.figure.Figure: グラフのFigureオブジェクト
        pd.DataFrame: プロットに使用したデータのDataFrame
    """
    df = hs.load_hard_sales()
    df = hs.pivot_sales_by_delta(df, hw=hw, mode=mode)
    if mode == "month":
        title_key = '月'
    elif mode == "year":
        title_key = '年'
    else:
        title_key = '週'

    if limit > 0:
        df = df.head(limit)

    fig, ax = plt.subplots(figsize=_FigSize)
    plt.rcParams['font.family'] = 'Hiragino Sans'
    plt.rcParams['axes.unicode_minus'] = False
    color_table = hi.get_hard_colors(df.columns.tolist())
               
    # 折れ線グラフ
    df.plot(
        ax=ax,
        kind='line',
        marker='o',
        linewidth=2,
        color=color_table
    )

    ax.set_title(f'発売日起点販売台数（{title_key}単位）')
    ax.set_xlabel(f'発売からの{title_key}数')
    ax.set_ylabel('販売台数')
    ax.legend(title='ハード')

    # Y軸の上限設定
    if ymax is not None:
        ax.set_ylim(top=ymax)
    ax.set_ylim(bottom=0)
    
    # Y軸 ygrid 毎にグリッド線
    if ygrid is not None:
        ax.yaxis.set_major_locator(MultipleLocator(ygrid))
        ax.yaxis.set_minor_locator(MultipleLocator(ygrid / 2))

    # X軸 xgrid毎にグリッド線
    if xgrid is not None:
        ax.xaxis.set_major_locator(MultipleLocator(xgrid))
        ax.xaxis.set_minor_locator(MultipleLocator(xgrid / 2))

    # 縦軸の表示を指数表示から整数表示に変更
    ax.yaxis.set_major_formatter(ScalarFormatter(useOffset=False))
    ax.ticklabel_format(style='plain', axis='y')

    ax.grid(True)
    fig.tight_layout()

    return (fig, df)

def plot_cumulative_sales(hw: List[str] = [], mode:str="week",
                          begin: Optional[datetime] = None,
                          end: Optional[datetime] = None,
                          ymax:Optional[int]=None, xgrid: Optional[int] = None,
                          ygrid: Optional[int] = None) -> tuple[Figure, pd.DataFrame]:
    """
    各ハードウェアの累計販売台数をプロットする
    Args:
        df: load_hard_sales()の戻り値のDataFrame
        hw: プロットしたいハードウェア名のリスト。[]の場合は全ハードウェアを対象
        mode: "month"の場合は月次の、"week"の場合は週単位、"year"の場合は年単位の累計販売台数をプロットする、 (defaultは"week")
    Returns:
        matplotlib.figure.Figure: グラフのFigureオブジェクト
    """
    df = hs.load_hard_sales()
    df = hs.pivot_cumulative_sales(df, hw=hw, begin=begin, end=end)
    if mode == "week":
        title_key = '週'
    elif mode == "month":
        df = df.resample('M').last()
        title_key = '月'
    elif mode == "year":
        df = df.resample('Y').last()
        title_key = '年'

    fig, ax = plt.subplots(figsize=_FigSize)
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

    ax.set_title(f'累計販売台数')
    ax.set_xlabel(title_key)
    ax.set_ylabel('累計販売台数')
    ax.legend(title='ハード')

    # Y軸の上限設定
    if ymax is not None:
        ax.set_ylim(top=ymax)
    ax.set_ylim(bottom=0)
    
    # Y軸 ygrid 毎にグリッド線
    if ygrid is not None:
        ax.yaxis.set_major_locator(MultipleLocator(ygrid))
        ax.yaxis.set_minor_locator(MultipleLocator(ygrid / 2))

    # X軸 xgrid毎にグリッド線
    if xgrid is not None:
        ax.xaxis.set_major_locator(MultipleLocator(xgrid))
        ax.xaxis.set_minor_locator(MultipleLocator(xgrid / 2))

    # 縦軸の表示を指数表示から整数表示に変更
    ax.yaxis.set_major_formatter(ScalarFormatter(useOffset=False))
    ax.ticklabel_format(style='plain', axis='y')

    ax.grid(True)
    fig.tight_layout()
    
    return (fig, df)


def plot_monthly_histogram(hw:str, begin:Optional[datetime] = None, 
                           end:Optional[datetime] = None,
                           ymax:Optional[int] = None) -> tuple[Figure, pd.DataFrame]:
    hard_sales_df = hs.load_hard_sales()
    if begin is not None:
        hard_sales_df = hard_sales_df.loc[hard_sales_df["report_date"] >= begin]
    if end is not None:
        hard_sales_df = hard_sales_df.loc[hard_sales_df["report_date"] <= end]
    
    monthly_df = hs.monthly_sales(hard_sales_df)
    # 特定の機種に絞る
    hw_df = monthly_df.loc[monthly_df["hw"] == hw].copy()
    pivot_hw_df = hw_df.pivot(index="month", columns="year", values="monthly_units")
    pivot_hw_df.fillna(0, inplace=True)

    fig, ax = plt.subplots(figsize=get_figsize())
    plt.rcParams['font.family'] = 'Hiragino Sans'
    plt.rcParams['axes.unicode_minus'] = False
    pivot_hw_df.plot(kind='bar', ax=ax)
    ax.set_title(f"{hw} 月間販売台数")
    ax.set_xlabel("月")
    ax.set_ylabel("販売台数")
    ax.set_xticks(range(len(pivot_hw_df.index)))
    ax.set_xticklabels(pivot_hw_df.index, rotation=0)
    ax.legend(title="年")

    # Y軸の上限設定
    if ymax is not None:
        ax.set_ylim(top=ymax)

    # 縦軸の表示を指数表示から整数表示に変更
    ax.yaxis.set_major_formatter(ScalarFormatter(useOffset=False))
    ax.ticklabel_format(style='plain', axis='y')

    ax.grid(axis='y')
    return fig, pivot_hw_df


def plot_yearly_histogram(hw:list[str], begin:Optional[datetime] = None, 
                           end:Optional[datetime] = None,
                           ymax:Optional[int] = None) -> tuple[Figure, pd.DataFrame]:
    hard_sales_df = hs.load_hard_sales()
    if begin is not None:
        hard_sales_df = hard_sales_df.loc[hard_sales_df["report_date"] >= begin]
    if end is not None:
        hard_sales_df = hard_sales_df.loc[hard_sales_df["report_date"] <= end]

    yearly_df = hs.yearly_sales(hard_sales_df)
    # 特定の機種に絞る
    hw_df = yearly_df.loc[yearly_df["hw"].isin(hw)].copy()
    pivot_hw_df = hw_df.pivot(index="year", columns="hw", values="yearly_units")
    pivot_hw_df.fillna(0, inplace=True)

    fig, ax = plt.subplots(figsize=get_figsize())
    plt.rcParams['font.family'] = 'Hiragino Sans'
    plt.rcParams['axes.unicode_minus'] = False

    color_table = hi.get_hard_colors(pivot_hw_df.columns.tolist())
    pivot_hw_df.plot(kind='bar', ax=ax, color=color_table)
    ax.set_title(f"年間販売台数")
    ax.set_xlabel("年")
    ax.set_ylabel("販売台数")
    ax.set_xticks(range(len(pivot_hw_df.index)))
    ax.set_xticklabels(pivot_hw_df.index, rotation=0)
    ax.legend(title="ハード")

    # Y軸の上限設定
    if ymax is not None:
        ax.set_ylim(top=ymax)

    # 縦軸の表示を指数表示から整数表示に変更
    ax.yaxis.set_major_formatter(ScalarFormatter(useOffset=False))
    ax.ticklabel_format(style='plain', axis='y')

    ax.grid(axis='y')
    return fig, pivot_hw_df


def plot_delta_yearly_histogram(hw:list[str],
                                delta_begin:Optional[int] = None, 
                                delta_end:Optional[int] = None,
                                ymax:Optional[int] = None) -> tuple[Figure, pd.DataFrame]:
    hard_sales_df = hs.load_hard_sales()
    if delta_begin is not None:
        hard_sales_df = hard_sales_df.loc[hard_sales_df["delta_year"] >= delta_begin]
    if delta_end is not None:
        hard_sales_df = hard_sales_df.loc[hard_sales_df["delta_year"] <= delta_end]

    delta_yearly_df = hs.delta_yearly_sales(hard_sales_df)
    # 特定の機種に絞る
    hw_df = delta_yearly_df.loc[delta_yearly_df["hw"].isin(hw)].copy()
    pivot_hw_df = hw_df.pivot(index="delta_year", columns="hw", values="yearly_units")
    pivot_hw_df.fillna(0, inplace=True)

    fig, ax = plt.subplots(figsize=get_figsize())
    plt.rcParams['font.family'] = 'Hiragino Sans'
    plt.rcParams['axes.unicode_minus'] = False

    color_table = hi.get_hard_colors(pivot_hw_df.columns.tolist())
    pivot_hw_df.plot(kind='bar', ax=ax, color=color_table)
    ax.set_title(f"経過年毎販売台数")
    ax.set_xlabel("経過年")
    ax.set_ylabel("販売台数")
    ax.set_xticks(range(len(pivot_hw_df.index)))
    ax.set_xticklabels(pivot_hw_df.index, rotation=0)
    ax.legend(title="ハード")

    # Y軸の上限設定
    if ymax is not None:
        ax.set_ylim(top=ymax)

    # 縦軸の表示を指数表示から整数表示に変更
    ax.yaxis.set_major_formatter(ScalarFormatter(useOffset=False))
    ax.ticklabel_format(style='plain', axis='y')

    ax.grid(axis='y')
    return fig, pivot_hw_df


def plot_maker_share_pie(begin_year:Optional[int] = None, 
                         end_year:Optional[int] = None) -> tuple[Figure, pd.DataFrame]:
    """
    年ごとのメーカーシェアを円グラフで可視化する

    Parameters
    ----------
    hard_sales_df : pd.DataFrame
        load_hard_sales()で取得した週次販売データ
    start_year : int
        表示する最初の年（デフォルト: 2023）
    """
    df = hs.load_hard_sales()
    maker_sales = hs.pivot_maker(df, begin_year=begin_year, end_year=end_year)

    n = len(maker_sales)
    fig, axes = plt.subplots(1, n, figsize=(4*n, 4))
    plt.rcParams['font.family'] = 'Hiragino Sans'
    plt.rcParams['axes.unicode_minus'] = False

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

    return (fig, maker_sales)