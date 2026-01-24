# 標準ライブラリ
from datetime import datetime, timedelta, date
from typing import List

# サードパーティライブラリ
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.ticker import ScalarFormatter, MultipleLocator
import mplcursors

# プロジェクト内モジュール
from . import plot_util as pu
from . import hard_sales as hs
from . import hard_sales_pivot as pv
from . import hard_info as hi
from . import hard_event as he


_BASE_SUNDAY = date(1970, 1, 4)  # 週番号1に対応する日曜日

def _weekfloat_to_datetime(x: float) -> datetime:
    """
    浮動小数点の週番号を datetime に変換する。
    1.0 -> 1970-01-04 00:00:00（日曜）
    2878.0 -> 2025-02-23 00:00:00
    2878.5 -> 2025-02-26 12:00:00（水曜昼）
    """
    if x < 0:
        raise ValueError("値は0以上である必要があります。")
    # 1週 = 7日
    days = (x - 1.0) * 7.0
    return datetime.combine(_BASE_SUNDAY, datetime.min.time()) + timedelta(days=days)

def _weekly_plot_on_add(sel):
    ax = sel.artist.axes
    line = sel.artist
    label = line.get_label()

    x, y = sel.target
    if 1500 < x:
        x_str = _weekfloat_to_datetime(x).strftime("%Y-%m-%d")
    else:
        x_str = f"{x:,.2f}"
    sel.annotation.set_text(f"{label}\n{y:,.0f}台\n{x_str}")
    sel.annotation.get_bbox_patch().set(fc="lightgreen", alpha=0.5)


def _plot_sales(
    data_source,
    labeler=None,
    tick_params_fn=None,
    annotation_positioner=None,
    ymax: int | None = None,
    ybottom: int | None = None,
    xgrid: int | None = None,
    ygrid: int | None = None,
    plot_style: dict = {},
    area: bool = False,
) -> tuple[Figure, pd.DataFrame]:
    """
    各ハードウェアの販売台数をプロット共通関数

    Args:
        data_source: データソース関数。戻り値は (pd.DataFrame, title_key) のタプル
        labeler: ラベル付け関数。引数は (ax, title_key)
        annotation_positioner: イベント注釈の位置決め関数。引数は (event_df, df)
        ymax: Y軸の上限値
        xgrid: X軸のグリッド線の間隔
        ygrid: Y軸のグリッド線の間隔

    Returns:
        matplotlib.figure.Figure: グラフのFigureオブジェクト
        pd.DataFrame: プロットに使用したデータのDataFrame
    """
    (df, title_key) = data_source()

    plt.ioff()
    fig, ax = plt.subplots(figsize=pu.get_figsize())
    plt.rcParams['font.family'] = 'Hiragino Sans'
    plt.rcParams['axes.unicode_minus'] = False
    # 背景の透明化
    if pu.get_transparent_mode():
        plt.rcParams['figure.facecolor'] = 'none'
        plt.rcParams['axes.facecolor'] = 'none'

    color_table = hi.get_hard_colors(df.columns.tolist())
    # color_tableの内容がblackのみの場合、デフォルトのカラーマップを使用する
    if all(c == 'black' for c in color_table):
        color_table = plt.rcParams['axes.prop_cycle'].by_key()['color'][:len(df.columns)]

    default_style = {
        'ax': ax,
        'kind': 'line',
        'marker': 'o',
        'linestyle': '-',
        'linewidth': 2,
        'color': color_table
    }
    if area:
        default_style['kind'] = 'area'
        default_style['stacked'] = True
        del default_style['linewidth']
        del default_style['marker']
        del default_style['linestyle']

    plot_style = default_style | plot_style
    # 折れ線グラフ
    df.plot(**plot_style)

    if annotation_positioner is not None:
        # event_dfの情報をannotationとしてグラフに追加する
        event_df = he.load_hard_event()
        filtered_events = annotation_positioner(event_df, df)
        for report_date, event_row in filtered_events.iterrows():
            color = hi.get_hard_color(event_row['hw'])
            ax.annotate(event_row['event_name'], 
                    xy=(event_row['x_pos'], event_row['y_pos']), 
                    xytext=(8, 8),
                    textcoords='offset points',
                    fontsize=8, color=color, fontweight='bold')

    if labeler is not None:
        labels = labeler(title_key)
        if labels.title: ax.set_title(labels.title)
        if labels.xlabel: ax.set_xlabel(labels.xlabel)
        if labels.ylabel: ax.set_ylabel(labels.ylabel)
        if labels.legend: ax.legend(title=labels.legend)

    if tick_params_fn is not None:
        params = tick_params_fn()
        ax.tick_params(axis=params.axis, which=params.which, labelsize=params.labelsize, rotation=params.rotation)
        
    # Y軸の上限設定
    if ymax is not None:
        ax.set_ylim(top=ymax)
    if ybottom is not None:
        ax.set_ylim(bottom=ybottom)
    
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

    # カーソル表示
    cursor = mplcursors.cursor(ax.lines, hover=True)
    cursor.connect("add", _weekly_plot_on_add)
    
    dispfunc = pu.get_dispfunc()
    if dispfunc is not None:
        dispfunc(fig)

    return (fig, df)


def plot_cumulative_sales_by_delta(hw: List[str] = [], ymax:int | None=None,
                                   xgrid: int | None = None, ygrid: int | None = None,
                                   mode:str = "week",
            
                                   begin:int | None = None,
                                   end:int | None = None,
                                   event_mask : he.EventMasks | None = None,
                                   ) -> tuple[Figure, pd.DataFrame]:
    """
    各ハードウェアの発売日起点・累計販売台数推移をプロットする
    
    Args:
        hw: プロットしたいハードウェア名のリスト。[]の場合は全ハードウェアを対象
        ymax: Y軸の上限値
        xgrid: X軸のグリッド線の間隔
        ygrid: Y軸のグリッド線の間隔
        mode: "month"の場合は月次の、"week"の場合は週単位、"year"の場合は年単位の累計販売台数をプロットする (defaultは"week")
        begin: 集計開始（経過期間の最小値）
        end: 集計終了（経過期間の最大値）
        event_mask: イベント注釈のマスク設定
        
    Returns:
        tuple[matplotlib.figure.Figure, pd.DataFrame]: グラフのFigureオブジェクトとプロットに使用したデータのDataFrameのタプル
        
        DataFrameのカラム構成:
        - index: delta_week (int64) / delta_month (int64) / delta_year (int64): 発売日からの経過期間（modeにより変動）
        - columns: hw (string): ゲームハードの識別子
        - values: sum_units (int64): その経過期間時点での累計販売台数
    """
    
    def data_source() -> tuple[pd.DataFrame, str]:
        df = hs.load_hard_sales()
        df = pv.pivot_cumulative_sales_by_delta(df, hw=hw, mode=mode, begin=begin, end=end)
        if mode == "month":
            title_key = '月'
        elif mode == "year":
            title_key = '年'
        else:
            title_key = '週'
        return (df, title_key)
    
    def labeler(title_key: str) -> pu.AxisLabels:
        return pu.AxisLabels(
            title=f'発売日起点累計販売台数',
            xlabel=f'発売からの{title_key}数',
            ylabel='累計販売台数',
            legend='ハード'
        )

    if event_mask:
        def annotation_positioner(event_df, df):
            event_df = he.delta_event(event_df, hi.load_hard_info())
            return he.add_event_positions_delta(event_df, df, event_mask=event_mask)
    else:
        annotation_positioner = None
        
    return _plot_sales(
        data_source=data_source,
        labeler=labeler,
        annotation_positioner=annotation_positioner,
        ymax=ymax,
        xgrid=xgrid,
        ygrid=ygrid,
        plot_style={'marker': None}
    )


def plot_sales(hw: List[str] = [], mode: str = "week",
               begin: datetime | None = None, end: datetime | None = None,
               ymax: int | None = None,
               xgrid: int | None = None, ygrid: int | None = None,
               event_mask: he.EventMasks | None = None,
               area: bool = False,
               ticklabelsize: int | None = None,
               ) -> tuple[Figure, pd.DataFrame]:
    """
    各ハードウェアの販売台数推移をプロットする（default = 週単位）

    Args:
        hw: プロットしたいハードウェア名のリスト。[]の場合は全ハードウェアを対象
        mode: "month"の場合は月次、"quarter"の場合は四半期、"week"の場合は週単位、
            "year"の場合は年単位の販売台数をプロットする (defaultは"week")
        begin: 集計開始日
        end: 集計終了日
        ymax: Y軸の上限値
        xgrid: X軸のグリッド線の間隔
        ygrid: Y軸のグリッド線の間隔
        event_mask: イベント注釈のマスク設定
        area: 面グラフとして表示するかどうか
        ticklabelsize: 目盛りラベルのフォントサイズ

    Returns:
        tuple[matplotlib.figure.Figure, pd.DataFrame]: グラフのFigureオブジェクトとプロットに使用したデータのDataFrameのタプル
        
        DataFrameのカラム構成（modeにより変動）:
        - mode="week"の場合:
            - index: report_date (datetime64): 集計期間の末日（日曜日）
            - columns: hw (string): ゲームハードの識別子
            - values: units (int64): 週次販売台数
        - mode="month"の場合:
            - index: year (int64), month (int64): report_dateの年と月
            - columns: hw (string): ゲームハードの識別子
            - values: monthly_units (int64): 月次販売台数
        - mode="quarter"の場合:
            - index: year (int64), quarter (int64): report_dateの年と四半期
            - columns: hw (string): ゲームハードの識別子
            - values: quarterly_units (int64): 四半期販売台数
        - mode="year"の場合:
            - index: year (int64): report_dateの年
            - columns: hw (string): ゲームハードの識別子
            - values: yearly_units (int64): 年次販売台数
    """
    def data_source():
        df = hs.load_hard_sales()
        if mode == "month":
            df = pv.pivot_monthly_sales(df, hw=hw, begin=begin, end=end)
            title_key = '月'
        if mode == "quarter":
            df = pv.pivot_quarterly_sales(df, hw=hw, begin=begin, end=end)
            title_key = '四半期'
        elif mode == "year":
            df = pv.pivot_yearly_sales(df, hw=hw, begin=begin, end=end)
            title_key = '年'
        else:
            df = pv.pivot_sales(df, hw=hw, begin=begin, end=end)
            title_key = '週'
        return (df, title_key)

    def labeler(title_key: str) -> pu.AxisLabels:
        return pu.AxisLabels(
            title=f'販売台数（{title_key}単位）',
            xlabel='集計日',
            ylabel='販売台数',
            legend='ハード'
        )

    if event_mask:
        annotation_positioner = lambda event_df, df: he.add_event_positions(event_df, df, event_mask=event_mask)
    else:
        annotation_positioner = None

    tick_params_fn = None
    if ticklabelsize is not None:
        tick_params_fn = lambda: pu.TickParams(labelsize=ticklabelsize)
            
    return _plot_sales(
        data_source=data_source,
        labeler=labeler,
        tick_params_fn=tick_params_fn,
        annotation_positioner=annotation_positioner,
        ymax=ymax,
        ybottom=0,
        xgrid=xgrid,
        ygrid=ygrid,
        area=area,
    )


def plot_sales_by_delta(hw: List[str] = [], ymax:int | None=None,
                        xgrid: int | None = None, ygrid: int | None = None,
                        mode:str = "week", 
                        begin:int | None = None,
                        end:int | None = None,
                        event_mask:he.EventMasks | None = None,
                        ) -> tuple[Figure, pd.DataFrame]:
    """
    各ハードウェアの発売日起点・販売台数推移をプロットする（default = 週単位）
    
    Args:
        hw: プロットしたいハードウェア名のリスト。[]の場合は全ハードウェアを対象
        ymax: Y軸の上限値
        xgrid: X軸のグリッド線の間隔
        ygrid: Y軸のグリッド線の間隔
        mode: "month"の場合は月次、"week"の場合は週単位、"year"の場合は年単位の販売台数をプロットする (defaultは"week")
        begin: 集計開始（経過期間の最小値）
        end: 集計終了（経過期間の最大値）
        event_mask: イベント注釈のマスク設定

    Returns:
        tuple[matplotlib.figure.Figure, pd.DataFrame]: グラフのFigureオブジェクトとプロットに使用したデータのDataFrameのタプル
        
        DataFrameのカラム構成:
        - index: delta_week (int64) / delta_month (int64) / delta_year (int64): 発売日からの経過期間（modeにより変動）
        - columns: hw (string): ゲームハードの識別子
        - values: units (int64): 販売台数
    """
    def data_source() -> tuple[pd.DataFrame, str]:
        df = hs.load_hard_sales()
        df = pv.pivot_sales_by_delta(df, hw=hw, mode=mode, begin=begin, end=end)
        if mode == "month":
            title_key = '月'
        elif mode == "year":
            title_key = '年'
        else:
            title_key = '週'
        return (df, title_key)
    
    def labeler(title_key: str) -> pu.AxisLabels:
        return pu.AxisLabels(
            title=f'発売日起点販売台数（{title_key}単位）',
            xlabel=f'発売からの{title_key}数',
            ylabel='販売台数',
            legend='ハード'
        )
        
    if event_mask:
        def annotation_positioner(event_df, df):
            event_df = he.delta_event(event_df, hi.load_hard_info())
            return he.add_event_positions_delta(event_df, df, event_mask=event_mask)
    else:
        annotation_positioner = None
        
    return _plot_sales(
        data_source=data_source,
        labeler=labeler,
        annotation_positioner=annotation_positioner,
        ymax=ymax,
        ybottom=0,
        xgrid=xgrid,
        ygrid=ygrid
    )

def plot_cumulative_sales(hw: List[str] = [], mode:str="week",
                          begin: datetime | None = None,
                          end: datetime | None = None,
                          ymax:int | None=None, xgrid: int | None = None,
                          event_mask:he.EventMasks | None = None,
                          ygrid: int | None = None) -> tuple[Figure, pd.DataFrame]:
    """
    各ハードウェアの累計販売台数をプロットする
    
    Args:
        hw: プロットしたいハードウェア名のリスト。[]の場合は全ハードウェアを対象
        mode: "month"の場合は月次、"week"の場合は週単位、"year"の場合は年単位の累計販売台数をプロットする (defaultは"week")
        begin: 集計開始日
        end: 集計終了日
        ymax: Y軸の上限値
        xgrid: X軸のグリッド線の間隔
        ygrid: Y軸のグリッド線の間隔
        event_mask: イベント注釈のマスク設定
        
    Returns:
        tuple[matplotlib.figure.Figure, pd.DataFrame]: グラフのFigureオブジェクトとプロットに使用したデータのDataFrameのタプル
        
        DataFrameのカラム構成:
        - index: report_date (datetime64): 集計期間の末日（日曜日）。modeが"month"または"year"の場合はリサンプリングされた日付
        - columns: hw (string): ゲームハードの識別子
        - values: sum_units (int64): report_date時点での累計販売台数
    """
    
    def data_source() -> tuple[pd.DataFrame, str]:
        df = hs.load_hard_sales()
        df = pv.pivot_cumulative_sales(df, hw=hw, begin=begin, end=end)
        if mode == "week":
            title_key = '週'
        elif mode == "month":
            df = df.resample('ME').last()
            title_key = '月'
        elif mode == "year":
            df = df.resample('Y').last()
            title_key = '年'
        return (df, title_key)
    
    def labeler(title_key: str) -> pu.AxisLabels:
        return pu.AxisLabels(
            title=f'累計販売台数',
            xlabel=title_key,
            ylabel='累計販売台数',
            legend='ハード'
        )

    if event_mask:
        def annotation_positioner(event_df, df):
            return he.add_event_positions(event_df, df, event_mask=event_mask)
    else:
        annotation_positioner = None
        
    return _plot_sales(
        data_source=data_source,
        labeler=labeler,
        annotation_positioner=annotation_positioner,
        ymax=ymax,
        ybottom=0,
        xgrid=xgrid,
        ygrid=ygrid,
        plot_style={'marker': None}
    )

def plot_cumsum_diffs(cmplist: list[tuple[str, str]],
                      ymax:int | None=None,
                      xgrid: int | None = None,
                      ygrid: int | None = None) -> tuple[Figure, pd.DataFrame]:
    """
    累計販売台数差分の折れ線グラフをプロットする
    
    Args:
        cmplist: 比較対象のHWのタプルのリスト。各タプルは(base_hw, cmp_hw)の形式
        ymax: Y軸の最大値
        xgrid: X軸のメジャーグリッドの間隔
        ygrid: Y軸のメジャーグリッドの間隔
        
    Returns:
        tuple[matplotlib.figure.Figure, pd.DataFrame]: グラフのFigureオブジェクトとDataFrameのタプル
        
        DataFrameのカラム構成:
        - index: 連番（0から始まる整数）
        - columns: "{cmp_hw}_{base_hw}差" (int64): 各ペアの累計販売台数の差分
                   例: "PS5_NSW差"は、PS5の累計販売台数からNSWの累計販売台数を引いた値
    """
    
    def data_source() -> tuple[pd.DataFrame, str]:
        df = hs.load_hard_sales()
        df = pv.cumsum_diffs(df, cmplist)
        title_key = '週'
        return (df, title_key)
    
    def labeler(title_key: str) -> pu.AxisLabels:
        return pu.AxisLabels(
            title=f'累計販売台数差',
            xlabel='販売開始からの週数',
            ylabel='累計販売台数の差',
            legend='販売台数差分'
        )
        
    return _plot_sales(
        data_source=data_source,
        labeler=labeler,

        ymax=ymax,
        ybottom=0,
        xgrid=xgrid,
        ygrid=ygrid,
        plot_style={'marker': None}
    )

def plot_sales_pase_diff(base_hw: str,
                         compare_hw: str,
                         ymax:int | None=None,
                         ybottom:int | None=None,
                         xgrid: int | None = None,
                         ygrid: int | None = None) -> tuple[Figure, pd.DataFrame]:
    """
    販売ペース差分の折れ線グラフをプロットする
    
    Args:
        base_hw: 基準ハードウェア名
        compare_hw: 比較ハードウェア名
        ymax: Y軸の最大値
        ybottom: Y軸の最小値
        xgrid: X軸のメジャーグリッドの間隔
        ygrid: Y軸のメジャーグリッドの間隔
        
    Returns:
        tuple[matplotlib.figure.Figure, pd.DataFrame]: グラフのFigureオブジェクトとDataFrameのタプル
        
        DataFrameのカラム構成:
        - index: delta_week (int64): 発売日からの経過週数
        - columns: 
            - "{compare_hw}累計_{base_hw}累計差" (int64): compare_hwの累計販売台数からbase_hwの累計販売台数を引いた差分
            - "{base_hw.lower()}_report_date" (datetime64): base_hwの集計日
            - "{compare_hw.lower()}_report_date" (datetime64): compare_hwの集計日
    """
    
    def data_source() -> tuple[pd.DataFrame, str]:
        df = hs.load_hard_sales()
        pv1 = pv.pivot_cumulative_sales_by_delta(df, hw=[base_hw, compare_hw])
        pv1[f'{compare_hw}累計_{base_hw}累計差'] = pv1[compare_hw] - pv1[base_hw]
        pv2 = pv1.loc[:, [f'{compare_hw}累計_{base_hw}累計差']]
        # カラムの値がNaNの行を取り除く
        pv2.dropna(inplace=True)
        title_key = '週'
        return (pv2, title_key)
    
    def labeler(title_key: str) -> pu.AxisLabels:
        return pu.AxisLabels(
            title=f'販売ペース差分',
            xlabel='販売開始からの週数',
            ylabel='販売ペースの差（台/週）',
            legend='販売ペース差分'
        )

    def combine_report_dates(diff_df:pd.DataFrame, base_hw:str, compare_hw:str) -> pd.DataFrame:
        base_df = hs.load_hard_sales()
        delta_weeks = diff_df.index
        week_list = delta_weeks.to_list()

        for hw in [base_hw, compare_hw]:
            if hw not in base_df['hw'].unique():
                raise ValueError(f"Invalid hardware: {hw}")
            
            hw_df = base_df.loc[base_df['hw'] == hw, :]
            if not all(week in hw_df['delta_week'].values for week in week_list):
                raise ValueError(f"Hardware {hw} does not have all required delta_week values.")
            
            filtered_hw_df = hw_df[hw_df["delta_week"].isin(week_list)].sort_values(by="delta_week")
            hw_report_date = filtered_hw_df.loc[:, "report_date"]
            diff_df = pd.concat([diff_df.reset_index(drop=True), hw_report_date.reset_index(drop=True)], axis=1)
            diff_df = diff_df.rename(columns={"report_date": f"{hw.lower()}_report_date"})
        return diff_df
        
    (diff_fig, diff_df) = _plot_sales(
        data_source=data_source,
        labeler=labeler,
        ymax=ymax,
        ybottom=ybottom,
        xgrid=xgrid,
        ygrid=ygrid,
        plot_style={'marker': None}
    )
    diff_df = combine_report_dates(diff_df, base_hw, compare_hw)
    return (diff_fig, diff_df)
