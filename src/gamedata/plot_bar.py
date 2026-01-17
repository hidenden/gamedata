# 標準ライブラリ
from datetime import datetime, timedelta, date
from typing import List, Optional

# サードパーティライブラリ
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.ticker import ScalarFormatter, MultipleLocator
import matplotlib.dates as mdates
import mplcursors

# プロジェクト内モジュール
from . import plot_util as pu
from . import hard_sales as hs
from . import hard_sales_filter as hsf
from . import hard_sales_pivot as pv
from . import hard_info as hi
from . import hard_event as he


def _bar_on_add(sel, df: pd.DataFrame, color2label: dict):
    rect = sel.artist
    ax = rect.axes
    x = rect.get_x()
    w = rect.get_width()
    h = rect.get_height()

    # x座標からカテゴリ名を推定
    idx = int(x + w/2 + 0.5)  # 四捨五入
    if idx < len(df.index):
        x_label = df.index[idx]
        # x_labelの型がintの場合、月または年のラベルに変換
        if isinstance(x_label, int):
            if x_label <= 12:
                x_label = f"{x_label}月"
            else:
                x_label = f"{x_label}年"
    else:
        x_label = ""

    # 棒の色から系列名を特定
    fc = rect.get_facecolor()
    series = color2label.get(fc, "unknown")

    # 注釈テキスト
    sel.annotation.set_text(f"{series}: {x_label}\n{h:,.0f}台")
    sel.annotation.get_bbox_patch().set(fc="lightyellow", alpha=0.85)


def _plot_bar(data_aggregator, color_generator=None, labeler=None,
              tick_params_fn=None,
              begin: Optional[datetime] = None,
              end: Optional[datetime] = None,
              ymax: Optional[int] = None, 
              stacked: bool = False,
              horizontal: bool = False,
              show_values: bool = False,
              value_color: str = 'black',
              bar_width: float = 0.5) -> tuple[Figure, pd.DataFrame]:
    """
    棒グラフをプロットする共通関数  
    Args:
        data_aggregator: データ集計関数。引数は (hard_sales_df: pd.DataFrame) -> pd.DataFrame
        color_generator: 色生成関数。引数は (hard_list: List[str]) -> List[str]
        labeler: ラベル付け関数。戻り値は AxisLabels オブジェクト
        begin: 集計開始日
        end: 集計終了日
        ymax: Y軸の上限値   
        stacked: 棒グラフを積み上げ表示するかどうか
        horizontal: 横棒グラフにするかどうか
        show_values: 各棒の上に値を表示するかどうか
        value_color: 棒の上に表示する値の色
        bar_width: 棒グラフの棒の幅（0.0～1.0）
    Returns:
        matplotlib.figure.Figure: グラフのFigureオブジェクト
        pd.DataFrame: プロットに使用したデータのDataFrame
    """
    hard_sales_df = hs.load_hard_sales()
    if begin is not None:
        hard_sales_df = hard_sales_df.loc[hard_sales_df["report_date"] >= begin]
    if end is not None:
        hard_sales_df = hard_sales_df.loc[hard_sales_df["report_date"] <= end]

    df = data_aggregator(hard_sales_df)
    df.fillna(0, inplace=True)

    fig, ax = plt.subplots(figsize=pu.get_figsize())
    plt.rcParams['font.family'] = 'Hiragino Sans'
    plt.rcParams['axes.unicode_minus'] = False
    # 背景の透明化
    plt.rcParams['figure.facecolor'] = 'none'
    plt.rcParams['axes.facecolor'] = 'none'
    
    if tick_params_fn is not None:
        params = tick_params_fn()
        ax.tick_params(axis=params.axis, which=params.which, labelsize=params.labelsize, rotation=params.rotation)
    
    if color_generator is not None:
        color_table = color_generator(df.columns.tolist())
    else:
        color_table = None

    if horizontal:
        kind = 'barh'
    else:
        kind = 'bar'
    
    df.plot(kind=kind, ax=ax, color=color_table, stacked=stacked, width=bar_width)
    
    if show_values:
        if stacked:
            # 積み上げの場合、各コンテナの個々の値を表示
            for container in ax.containers:
                ax.bar_label(container, fmt='%.1f', color=value_color, label_type='center' if horizontal else 'edge')
        else:
            # 非積み上げの場合、最後のコンテナのみ
            if horizontal:
                ax.bar_label(ax.containers[-1], fmt='%.1f', color=value_color, label_type='edge')
            else:
                ax.bar_label(ax.containers[-1], fmt='%.1f', color=value_color, label_type='edge')
    
    if labeler is not None:
        labels = labeler()
        if labels.title: ax.set_title(labels.title)
        if labels.xlabel: ax.set_xlabel(labels.xlabel)
        if labels.ylabel: ax.set_ylabel(labels.ylabel)
        if labels.legend: ax.legend(title=labels.legend)

    if not horizontal:
        ax.set_xticks(range(len(df.index)))
        ax.set_xticklabels(df.index, rotation=0)
    else:
        ax.set_yticks(range(len(df.index)))
        ax.set_yticklabels(df.index)

    # Y軸の上限設定
    if ymax is not None:
        ax.set_ylim(top=ymax)

    # 縦軸の表示を指数表示から整数表示に変更
    if not horizontal:
        ax.yaxis.set_major_formatter(ScalarFormatter(useOffset=False))
        ax.ticklabel_format(style='plain', axis='y')
        ax.grid(axis='y')
    
    # 凡例のハンドルとラベルを取得し、色とラベルの対応表を作成
    handles, labels = ax.get_legend_handles_labels()
    color2label = {}
    for h, l in zip(handles, labels):
        if hasattr(h, "patches") and len(h.patches) > 0:
            fc = h.patches[0].get_facecolor()  # 1つ目のバーの色
            color2label[fc] = l

    # カーソル表示　（棒グラフではpatchesを設定する）
    cursor = mplcursors.cursor(ax.patches, hover=True)
    @cursor.connect("add")
    def on_add(sel):
        _bar_on_add(sel, df, color2label)

    return fig, df

def plot_monthly_bar_by_year(hw:str, begin:Optional[datetime] = None, 
                           end:Optional[datetime] = None,
                           ymax:Optional[int] = None,
                           ticklabelsize:Optional[int] = None) -> tuple[Figure, pd.DataFrame]:
    """
    指定したハードウェアの月間販売台数を年別に棒グラフで表示する
    
    Args:
        hw: プロットしたいハードウェア名
        begin: 集計開始日
        end: 集計終了日
        ymax: Y軸の上限値
        ticklabelsize: 目盛りラベルのフォントサイズ
        
    Returns:
        tuple[Figure, pd.DataFrame]: グラフのFigureオブジェクトとプロットに使用したデータのDataFrameのタプル
        
        DataFrameのカラム構成:
        - index: month (int64): 月（1-12）
        - columns: year (int64): 年
        - values: monthly_units (int64): 月次販売台数
    """

    def data_aggregator(hard_sales_df: pd.DataFrame) -> pd.DataFrame:
        monthly_df = hsf.monthly_sales(hard_sales_df)
        hw_df = monthly_df.loc[monthly_df["hw"] == hw].copy()
        pivot_hw_df = hw_df.pivot(index="month", columns="year", values="monthly_units")
        return pivot_hw_df
    
    def labeler() -> pu.AxisLabels:
        return pu.AxisLabels(
            title=f"{hw} 月間販売台数",
            xlabel="月",
            ylabel="販売台数",
            legend="年"
        )
        
    tick_params_fn = None
    if ticklabelsize is not None:
        tick_params_fn = lambda: pu.TickParams(labelsize=ticklabelsize)
            
    return _plot_bar(
        data_aggregator=data_aggregator,
        labeler=labeler,
        tick_params_fn=tick_params_fn,
        begin=begin,
        end=end,
        ymax=ymax
    )

def plot_monthly_bar_by_hard(hw:list[str], 
                             begin:Optional[datetime] = None, 
                             end:Optional[datetime] = None,
                             stacked:bool=False,
                             ymax:Optional[int] = None,
                             ticklabelsize:Optional[int] = None) -> tuple[Figure, pd.DataFrame]:
    """
    指定した期間の月間販売台数をハード別に棒グラフで表示する
    
    Args:
        hw: プロットしたいハードウェア名のリスト
        begin: 集計開始日
        end: 集計終了日
        stacked: 棒グラフを積み上げ表示するかどうか
        ymax: Y軸の上限値
        ticklabelsize: 目盛りラベルのフォントサイズ
        
    Returns:
        tuple[Figure, pd.DataFrame]: グラフのFigureオブジェクトとプロットに使用したデータのDataFrameのタプル
        
        DataFrameのカラム構成:
        - index: year_month (string): 年月（"YYYY-MM"形式）
        - columns: hw (string): ゲームハードの識別子
        - values: monthly_units (int64): 月次販売台数
    """

    def data_aggregator(hard_sales_df: pd.DataFrame) -> pd.DataFrame:
        monthly_df = hsf.monthly_sales(hard_sales_df)
        monthly_df["year_month"] = pd.to_datetime(
            dict(year=monthly_df["year"], month=monthly_df["month"], day=1)
        )
        hw_df = monthly_df.loc[monthly_df["hw"].isin(hw)].copy()
        hw_df.sort_values("year_month", inplace=True)
        pivot_hw_df = hw_df.pivot(index="year_month", columns="hw", values="monthly_units")
        pivot_hw_df.sort_index(inplace=True)
        pivot_hw_df.index = pivot_hw_df.index.strftime("%Y-%m")
        return pivot_hw_df

    def color_generator(hard_list: List[str]) -> List[str]:
        return hi.get_hard_colors(hard_list)
    
    def labeler() -> pu.AxisLabels:
        return pu.AxisLabels(
            title=f"月間販売台数",
            xlabel="月",
            ylabel="販売台数",
            legend="ハード"
        )

    tick_params_fn = None
    if ticklabelsize is not None:
        tick_params_fn = lambda: pu.TickParams(labelsize=ticklabelsize)
            
    return _plot_bar(
        data_aggregator=data_aggregator,
        color_generator=color_generator,
        labeler=labeler,
        tick_params_fn=tick_params_fn,
        begin=begin,
        end=end,
        ymax=ymax,
        stacked=stacked
    )

def plot_monthly_bar_by_hard_year(hwy:list[tuple[str, int]], 
                             stacked:bool=False,
                             ymax:Optional[int] = None,
                             ticklabelsize:Optional[int] = None) -> tuple[Figure, pd.DataFrame]:
    """
    指定したハードウェアと年の組み合わせの月間販売台数を棒グラフで表示する
    
    Args:
        hwy: プロットしたいハードウェア名と年のタプルのリスト。例：[("PS5", 2020), ("NSW", 2017)]
        stacked: 棒グラフを積み上げ表示するかどうか
        ymax: Y軸の上限値
        ticklabelsize: 目盛りラベルのフォントサイズ
        
    Returns:
        tuple[Figure, pd.DataFrame]: グラフのFigureオブジェクトとプロットに使用したデータのDataFrameのタプル
        
        DataFrameのカラム構成:
        - index: month (int64): 月（1-12）
        - columns: "{hw}_{year}" (string): ハードウェア名と年を組み合わせた識別子（例："PS5_2020"）
        - values: monthly_units (int64): 月次販売台数
    """
    color_hard_list = []
    def data_aggregator(hard_sales_df: pd.DataFrame) -> pd.DataFrame:
        monthly_df = hsf.monthly_sales(hard_sales_df)
        hw_dfs = []
        for hw, year in hwy:
            temp_df = monthly_df.loc[
                (monthly_df["hw"] == hw) & (monthly_df["year"] == year)
            ].copy()
            temp_pivot_df = temp_df.pivot(index="month", columns="hw", values="monthly_units")
            temp_pivot_df.sort_index(inplace=True)

            col_name = f"{hw}_{year}"
            temp_pivot_df.rename(columns={hw: col_name}, inplace=True)
            hw_dfs.append(temp_pivot_df)
            color_hard_list.append(hw)
            
        # hw_dfsを結合
        result_df = pd.concat(hw_dfs, axis=1)
        result_df.fillna(0, inplace=True)
        return result_df

    def color_generator(hard_list: List[str]) -> List[str]:
        return hi.get_hard_colors(color_hard_list)
    
    def labeler() -> pu.AxisLabels:
        return pu.AxisLabels(
            title=f"月間販売台数",
            xlabel="月",
            ylabel="販売台数",
            legend="ハード_年"
        )

    tick_params_fn = None
    if ticklabelsize is not None:
        tick_params_fn = lambda: pu.TickParams(labelsize=ticklabelsize)
            
    return _plot_bar(
        data_aggregator=data_aggregator,
        color_generator=color_generator,
        labeler=labeler,
        tick_params_fn=tick_params_fn,
        ymax=ymax,
        stacked=stacked
    )

def plot_yearly_bar_by_hard(hw:list[str], begin:Optional[datetime] = None, 
                           end:Optional[datetime] = None, stacked:bool=False,
                           ymax:Optional[int] = None,
                           ticklabelsize:Optional[int] = None
                           ) -> tuple[Figure, pd.DataFrame]:
    """
    指定した期間の年間販売台数をハード別に棒グラフで表示する
    
    Args:
        hw: プロットしたいハードウェア名のリスト
        begin: 集計開始日(通常は年初めに設定する)
        end: 集計終了日(通常は年末に設定する)
        stacked: 棒グラフを積み上げ表示するかどうか
        ymax: Y軸の上限値
        ticklabelsize: 目盛りラベルのフォントサイズ
        
    Returns:
        tuple[Figure, pd.DataFrame]: グラフのFigureオブジェクトとプロットに使用したデータのDataFrameのタプル
        
        DataFrameのカラム構成:
        - index: year (int64): report_dateの年
        - columns: hw (string): ゲームハードの識別子
        - values: yearly_units (int64): 年次販売台数
    """
    def data_aggregator(hard_sales_df: pd.DataFrame) -> pd.DataFrame:
        yearly_df = hsf.yearly_sales(hard_sales_df)
        hw_df = yearly_df.loc[yearly_df["hw"].isin(hw)].copy()
        pivot_hw_df = hw_df.pivot(index="year", columns="hw", values="yearly_units")
        return pivot_hw_df
    
    def color_generator(hard_list: List[str]) -> List[str]:
        return hi.get_hard_colors(hard_list)
    
    def labeler() -> pu.AxisLabels:
        return pu.AxisLabels(
            title=f"年間販売台数",
            xlabel="年",
            ylabel="販売台数",
            legend="ハード"
        )

    tick_params_fn = None
    if ticklabelsize is not None:
        tick_params_fn = lambda: pu.TickParams(labelsize=ticklabelsize)

    return _plot_bar(
        data_aggregator=data_aggregator,
        color_generator=color_generator,
        labeler=labeler,
        tick_params_fn=tick_params_fn,
        begin=begin,
        end=end,
        ymax=ymax,
        stacked=stacked,
    )

def plot_yearly_bar_by_month(month:int,
                           begin:Optional[datetime] = None, 
                           end:Optional[datetime] = None,
                           ymax:Optional[int] = None,
                           stacked:bool=True,
                           ticklabelsize:Optional[int] = None
                           ) -> tuple[Figure, pd.DataFrame]:
    """
    指定した月の年ごとの移り変わりをメーカーごとの棒グラフで表示する
    
    Args:
        month: 対象月（1-12）
        begin: 集計開始日(通常は年初めに設定する)
        end: 集計終了日(通常は年末に設定する)
        ymax: Y軸の上限値
        stacked: 棒グラフを積み上げ表示するかどうか
        ticklabelsize: 目盛りラベルのフォントサイズ
        
    Returns:
        tuple[Figure, pd.DataFrame]: グラフのFigureオブジェクトとプロットに使用したデータのDataFrameのタプル
        
        DataFrameのカラム構成:
        - index: year (int64): report_dateの年
        - columns: maker_name (string): メーカー名
        - values: monthly_units (int64): 月次販売台数
    """
    def data_aggregator(hard_sales_df: pd.DataFrame) -> pd.DataFrame:
        hard_sales_df = hs.load_hard_sales()
        monthly_df = hsf.monthly_sales(hard_sales_df, begin=begin, end=end, maker_mode=True)
        target_month_df = monthly_df.loc[monthly_df["month"] == month].copy()
        target_month_df = target_month_df.set_index("year")
        target_month_df = target_month_df.loc[:, ["monthly_units", 'maker_name']]
        target_month_wide_df = target_month_df.pivot_table(index="year", columns="maker_name", 
                                                           values="monthly_units", fill_value=0)
        return target_month_wide_df
    
    def color_generator(maker_list: List[str]) -> List[str]:
        return hi.get_maker_colors(maker_list)                                  
    
    def labeler() -> pu.AxisLabels:
        return pu.AxisLabels(
            title=f"{month}月ハード販売台数",
            xlabel="年",
            ylabel="販売台数",
            legend="メーカー"
        )

    tick_params_fn = None
    if ticklabelsize is not None:
        tick_params_fn = lambda: pu.TickParams(labelsize=ticklabelsize)

    return _plot_bar(
        data_aggregator=data_aggregator,
        color_generator=color_generator,
        labeler=labeler,
        tick_params_fn=tick_params_fn,
        begin=begin,
        end=end,
        ymax=ymax,
        stacked=stacked,
    )

def plot_delta_yearly_bar(hw:list[str],
                                delta_begin:Optional[int] = None, 
                                delta_end:Optional[int] = None,
                                ymax:Optional[int] = None,
                                ticklabelsize:Optional[int] = None) -> tuple[Figure, pd.DataFrame]:
    """
    指定した機種の経過年毎販売台数をハード別に棒グラフで表示する
    
    Args:
        hw: プロットしたいハードウェア名のリスト
        delta_begin: 経過年の開始（指定しない場合は0年）
        delta_end: 経過年の終了（指定しない場合は全期間）
        ymax: Y軸の上限値
        ticklabelsize: 目盛りラベルのフォントサイズ
        
    Returns:
        tuple[Figure, pd.DataFrame]: グラフのFigureオブジェクトとプロットに使用したデータのDataFrameのタプル
        
        DataFrameのカラム構成:
        - index: delta_year (int64): 発売年から何年後か（同じ年なら0）
        - columns: hw (string): ゲームハードの識別子
        - values: yearly_units (int64): 経過年次販売台数
    """
    
    def data_aggregator(hard_sales_df: pd.DataFrame) -> pd.DataFrame:
        delta_yearly_df = hsf.delta_yearly_sales(hard_sales_df)
        # 特定の機種に絞る
        hw_df = delta_yearly_df.loc[delta_yearly_df["hw"].isin(hw)].copy()
        pivot_hw_df = hw_df.pivot(index="delta_year", columns="hw", values="yearly_units")
        
        if delta_begin is not None:
            pivot_hw_df = pivot_hw_df.loc[pivot_hw_df.index >= delta_begin]
        if delta_end is not None:
            pivot_hw_df = pivot_hw_df.loc[pivot_hw_df.index <= delta_end]
        return pivot_hw_df
    
    def color_generator(hard_list: List[str]) -> List[str]:
        return hi.get_hard_colors(hard_list)
    
    def labeler() -> pu.AxisLabels:
        return pu.AxisLabels(
            title=f"経過年毎販売台数",
            xlabel="経過年",
            ylabel="販売台数",
            legend="ハード"
        )

    tick_params_fn = None
    if ticklabelsize is not None:
        tick_params_fn = lambda: TickParams(labelsize=ticklabelsize)

    return _plot_bar(
        data_aggregator=data_aggregator,
        color_generator=color_generator,
        labeler=labeler,
        tick_params_fn=tick_params_fn,
        ymax=ymax
    )  

def plot_maker_share_bar(begin:Optional[datetime] = None, 
                         end:Optional[datetime] = None,
                         ticklabelsize:Optional[int] = None
                        ) -> tuple[Figure, pd.DataFrame]:
    """指定した期間のメーカー別シェアを棒グラフで表示する
    
    Args:
        begin: 集計開始日(通常は年初めに設定する)
        end: 集計終了日(通常は年末に設定する)
        
    Returns:
        tuple[Figure, pd.DataFrame]: グラフのFigureオブジェクトとプロットに使用したデータのDataFrameのタプル
        
        DataFrameのカラム構成:
        - index: year (int64): report_dateの年
        - columns: hw (string): ゲームハードの識別子
        - values: yearly_units (int64): 年次販売台数
    """
    def data_aggregator(hard_sales_df: pd.DataFrame) -> pd.DataFrame:
        pvmaker_df = pv.pivot_maker(hard_sales_df, 
                                    begin_year=begin.year if begin else None,
                                    end_year=end.year if end else None)
        # pvmaker_dfはカラム名がメーカーのDFである｡これをシェア率に変換する
        pvshare_df = pvmaker_df.div(pvmaker_df.sum(axis=1), axis=0) * 100.0
        return pvshare_df
    
    def color_generator(maker_list: List[str]) -> List[str]:
        return hi.get_maker_colors(maker_list)
    
    def labeler() -> pu.AxisLabels:
        return pu.AxisLabels(
            title=f"メーカーシェア",
            xlabel="シェア (%)",
            ylabel="年",
            legend="メーカー"
        )

    tick_params_fn = None
    if ticklabelsize is not None:
        tick_params_fn = lambda: TickParams(labelsize=ticklabelsize)

    return _plot_bar(
        data_aggregator=data_aggregator,
        color_generator=color_generator,
        labeler=labeler,
        tick_params_fn=tick_params_fn,
        begin=begin,
        end=end,
        stacked=True,
        horizontal=True,
        show_values=True,
        value_color="#D0E5D8",
        bar_width=0.8
    )

