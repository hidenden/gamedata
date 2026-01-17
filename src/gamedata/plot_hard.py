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
from . import hard_sales as hs
from . import hard_info as hi
from . import hard_event as he

_FigSize = (10, 5)


BASE_SUNDAY = date(1970, 1, 4)  # 週番号1に対応する日曜日

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
    return datetime.combine(BASE_SUNDAY, datetime.min.time()) + timedelta(days=days)

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

class AxisLabels:
    def __init__(self, title=None, xlabel=None, ylabel=None, legend=None):
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.legend = legend

class TickParams:
    def __init__(self, axis='x', which='major', labelsize=10, rotation=None):
        self.axis = axis
        self.which = which
        self.labelsize = labelsize
        self.rotation = rotation

def get_figsize() -> tuple[int, int]:
    return _FigSize

def set_figsize(width: int, height: int) -> None:
    global _FigSize
    _FigSize = (width, height)

def _plot_sales(
    data_source,
    labeler=None,
    tick_params_fn=None,
    annotation_positioner=None,
    ymax: Optional[int] = None,
    ybottom: Optional[int] = None,
    xgrid: Optional[int] = None,
    ygrid: Optional[int] = None,
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

    fig, ax = plt.subplots(figsize=_FigSize)
    plt.rcParams['font.family'] = 'Hiragino Sans'
    plt.rcParams['axes.unicode_minus'] = False
    # 背景の透明化
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

    return (fig, df)


def plot_cumulative_sales_by_delta(hw: List[str] = [], ymax:Optional[int]=None,
                                   xgrid: Optional[int] = None, ygrid: Optional[int] = None,
                                   mode:str = "week",
            
                                   begin:Optional[int] = None,
                                   end:Optional[int] = None,
                                   event_mask : Optional[he.EventMasks] = None,
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
        df = hs.pivot_cumulative_sales_by_delta(df, hw=hw, mode=mode, begin=begin, end=end)
        if mode == "month":
            title_key = '月'
        elif mode == "year":
            title_key = '年'
        else:
            title_key = '週'
        return (df, title_key)
    
    def labeler(title_key: str) -> AxisLabels:
        return AxisLabels(
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


def plot_sales(hw: List[str] = [], mode: Optional[str] = "week",
               begin: Optional[datetime] = None, end: Optional[datetime] = None,
               ymax: Optional[int] = None,
               xgrid: Optional[int] = None, ygrid: Optional[int] = None,
               event_mask: Optional[he.EventMasks] = None,
               area: bool = False,
               ticklabelsize: Optional[int] = None,
               ) -> tuple[Figure, pd.DataFrame]:
    """
    各ハードウェアの販売台数推移をプロットする（default = 週単位）

    Args:
        hw: プロットしたいハードウェア名のリスト。[]の場合は全ハードウェアを対象
        mode: "month"の場合は月次、"week"の場合は週単位、"year"の場合は年単位の販売台数をプロットする (defaultは"week")
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
        - mode="year"の場合:
            - index: year (int64): report_dateの年
            - columns: hw (string): ゲームハードの識別子
            - values: yearly_units (int64): 年次販売台数
    """
    def data_source():
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
        return (df, title_key)

    def labeler(title_key: str) -> AxisLabels:
        return AxisLabels(
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
        tick_params_fn = lambda: TickParams(labelsize=ticklabelsize)
            
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


def plot_sales_by_delta(hw: List[str] = [], ymax:Optional[int]=None,
                        xgrid: Optional[int] = None, ygrid: Optional[int] = None,
                        mode:str = "week", 
                        begin:Optional[int] = None,
                        end:Optional[int] = None,
                        event_mask:Optional[he.EventMasks] = None,
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
        df = hs.pivot_sales_by_delta(df, hw=hw, mode=mode, begin=begin, end=end)
        if mode == "month":
            title_key = '月'
        elif mode == "year":
            title_key = '年'
        else:
            title_key = '週'
        return (df, title_key)
    
    def labeler(title_key: str) -> AxisLabels:
        return AxisLabels(
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
                          begin: Optional[datetime] = None,
                          end: Optional[datetime] = None,
                          ymax:Optional[int]=None, xgrid: Optional[int] = None,
                          event_mask:Optional[he.EventMasks] = None,
                          ygrid: Optional[int] = None) -> tuple[Figure, pd.DataFrame]:
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
        df = hs.pivot_cumulative_sales(df, hw=hw, begin=begin, end=end)
        if mode == "week":
            title_key = '週'
        elif mode == "month":
            df = df.resample('ME').last()
            title_key = '月'
        elif mode == "year":
            df = df.resample('Y').last()
            title_key = '年'
        return (df, title_key)
    
    def labeler(title_key: str) -> AxisLabels:
        return AxisLabels(
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
                      ymax:Optional[int]=None,
                      xgrid: Optional[int] = None,
                      ygrid: Optional[int] = None) -> tuple[Figure, pd.DataFrame]:
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
        df = hs.cumsum_diffs(df, cmplist)
        title_key = '週'
        return (df, title_key)
    
    def labeler(title_key: str) -> AxisLabels:
        return AxisLabels(
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
                         ymax:Optional[int]=None,
                         ybottom:Optional[int]=None,
                         xgrid: Optional[int] = None,
                         ygrid: Optional[int] = None) -> tuple[Figure, pd.DataFrame]:
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
        pv1 = hs.pivot_cumulative_sales_by_delta(df, hw=[base_hw, compare_hw])
        pv1[f'{compare_hw}累計_{base_hw}累計差'] = pv1[compare_hw] - pv1[base_hw]
        pv2 = pv1.loc[:, [f'{compare_hw}累計_{base_hw}累計差']]
        # カラムの値がNaNの行を取り除く
        pv2.dropna(inplace=True)
        title_key = '週'
        return (pv2, title_key)
    
    def labeler(title_key: str) -> AxisLabels:
        return AxisLabels(
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

    fig, ax = plt.subplots(figsize=get_figsize())
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
        monthly_df = hs.monthly_sales(hard_sales_df)
        hw_df = monthly_df.loc[monthly_df["hw"] == hw].copy()
        pivot_hw_df = hw_df.pivot(index="month", columns="year", values="monthly_units")
        return pivot_hw_df
    
    def labeler() -> AxisLabels:
        return AxisLabels(
            title=f"{hw} 月間販売台数",
            xlabel="月",
            ylabel="販売台数",
            legend="年"
        )
        
    tick_params_fn = None
    if ticklabelsize is not None:
        tick_params_fn = lambda: TickParams(labelsize=ticklabelsize)
            
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
        monthly_df = hs.monthly_sales(hard_sales_df)
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
    
    def labeler() -> AxisLabels:
        return AxisLabels(
            title=f"月間販売台数",
            xlabel="月",
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
        monthly_df = hs.monthly_sales(hard_sales_df)
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
    
    def labeler() -> AxisLabels:
        return AxisLabels(
            title=f"月間販売台数",
            xlabel="月",
            ylabel="販売台数",
            legend="ハード_年"
        )

    tick_params_fn = None
    if ticklabelsize is not None:
        tick_params_fn = lambda: TickParams(labelsize=ticklabelsize)
            
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
        yearly_df = hs.yearly_sales(hard_sales_df)
        hw_df = yearly_df.loc[yearly_df["hw"].isin(hw)].copy()
        pivot_hw_df = hw_df.pivot(index="year", columns="hw", values="yearly_units")
        return pivot_hw_df
    
    def color_generator(hard_list: List[str]) -> List[str]:
        return hi.get_hard_colors(hard_list)
    
    def labeler() -> AxisLabels:
        return AxisLabels(
            title=f"年間販売台数",
            xlabel="年",
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
        monthly_df = hs.monthly_sales(hard_sales_df, begin=begin, end=end, maker_mode=True)
        target_month_df = monthly_df.loc[monthly_df["month"] == month].copy()
        target_month_df = target_month_df.set_index("year")
        target_month_df = target_month_df.loc[:, ["monthly_units", 'maker_name']]
        target_month_wide_df = target_month_df.pivot_table(index="year", columns="maker_name", 
                                                           values="monthly_units", fill_value=0)
        return target_month_wide_df
    
    def color_generator(maker_list: List[str]) -> List[str]:
        return hi.get_maker_colors(maker_list)                                  
    
    def labeler() -> AxisLabels:
        return AxisLabels(
            title=f"{month}月ハード販売台数",
            xlabel="年",
            ylabel="販売台数",
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
        delta_yearly_df = hs.delta_yearly_sales(hard_sales_df)
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
    
    def labeler() -> AxisLabels:
        return AxisLabels(
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
        pvmaker_df = hs.pivot_maker(hard_sales_df, 
                                    begin_year=begin.year if begin else None,
                                    end_year=end.year if end else None)
        # pvmaker_dfはカラム名がメーカーのDFである｡これをシェア率に変換する
        pvshare_df = pvmaker_df.div(pvmaker_df.sum(axis=1), axis=0) * 100.0
        return pvshare_df
    
    def color_generator(maker_list: List[str]) -> List[str]:
        return hi.get_maker_colors(maker_list)
    
    def labeler() -> AxisLabels:
        return AxisLabels(
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

def plot_maker_share_pie(begin_year:Optional[int] = None, 
                         end_year:Optional[int] = None) -> tuple[Figure, pd.DataFrame]:
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
    maker_sales = hs.pivot_maker(df, begin_year=begin_year, end_year=end_year)

    n = len(maker_sales)
    fig, axes = plt.subplots(1, n, figsize=(4*n, 4))
    plt.rcParams['font.family'] = 'Hiragino Sans'
    plt.rcParams['axes.unicode_minus'] = False
    # 背景の透明化
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

    return (fig, maker_sales)