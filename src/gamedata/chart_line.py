# 標準ライブラリ
from datetime import date, datetime, timedelta
from typing import List

import altair as alt

# サードパーティライブラリ
import polars as pl

from . import hard_info as hi
from . import hard_annotation as ha

# プロジェクト内モジュール
# プロジェクト内モジュール
from . import hard_sales as hs
from . import hard_sales_long as hsl
from .mode import Mode, parse_mode


def _chart_line_sales(
    src_df: pl.DataFrame,
    alt_x: alt.X,
    alt_y: alt.Y,
    color: alt.Color,
    ymin: int = 0,
    ymax: int | None = None,
    title: str | None = None,
    with_point: bool = True,
    tooltip: List[alt.Tooltip] | None = None,
    multi_line: bool = False,
    text_angle: int = 0,
) -> alt.Chart | alt.LayerChart | alt.FacetChart:
    """売上のチャートを作成する関数

    Args:
        src_df: データフレーム
        annotation_joinner: アノテーション結合関数
        labeler: ラベル付け関数（オプション）

    Returns:
        alt.Chart | alt.LayerChart | alt.FacetChart: 売上のチャート
    """
    # Y上限の設定
    if ymax is not None:
        alt_y = alt_y.scale(domain=[ymin, ymax], clamp=True)

    # チャートの作成
    base_chart = alt.Chart(src_df).encode(x=alt_x, y=alt_y, color=color)
    chart = base_chart.mark_line(point=with_point)

    # dfがカラム note を持っている場合は、mark_text()でアノテーション名を表示する
    if "note" in src_df.columns:
        annotation_chart = (
            base_chart.transform_filter(alt.datum.note != None)
            .mark_text(
                align="center", baseline="bottom", dx=5, dy=-10, angle=text_angle
            )
            .encode(text="note:N")
        )
        chart += annotation_chart

    if title is not None:
        chart = chart.properties(title=title)
    if tooltip is not None:
        chart = chart.encode(tooltip=tooltip)

    if multi_line:
        ### Multi-line対応
        xf = alt_x.to_dict()["field"]
        yf = alt_y.to_dict()["field"]
        nearest = alt.selection_point(
            nearest=True, on="pointerover", fields=[xf], empty=False
        )
        selectors = (
            alt.Chart(src_df)
            .mark_point()
            .encode(x=alt_x, opacity=alt.value(0))
            .add_params(nearest)
        )
        when_near = alt.when(nearest)
        points = base_chart.mark_point().encode(
            opacity=when_near.then(alt.value(1)).otherwise(alt.value(0))
        )
        text = base_chart.mark_text(align="left", dx=10, dy=-15).encode(
            text=when_near.then(yf).otherwise(alt.value(" "))
        )
        rules = (
            alt.Chart(src_df)
            .mark_rule(color="gray")
            .encode(x=alt_x)
            .transform_filter(nearest)
        )
        chart = alt.layer(chart, selectors, points, rules, text)
        if ymax is not None:
            chart = chart.encode(y=alt_y)  # Y軸のスケールを再適用
        ### Multi-line対応ここまで

    return chart


def chart_line_sales(
    hw: List[str] = [],
    mode: str = "week",
    begin: datetime | date | None = None,
    end: datetime | date | None = None,
    ymin: int = 0,
    ymax: int | None = None,
    annotation_level: int | None = None,
    with_point: bool = True,
    multi_line: bool = False,
) -> alt.Chart | alt.LayerChart | alt.FacetChart:
    """売上のチャートを作成する関数

    Args:
        hw: ハードウェアのリスト
        mode: 集計モード（例: "week", "month"）
        begin: 集計開始日
        end: 集計終了日
        annotation_level: アノテーションレベル（オプション）

    Returns:
        alt.Chart: 売上のチャート
    """
    # データソースの定義
    src_df: pl.DataFrame = hs.load_hard_sales()

    mode_enum = parse_mode(mode)

    if mode_enum == Mode.MONTH:
        df = hsl.monthly_sales_long(src_df, hw=hw, begin=begin, end=end)
        alt_x = alt.X("year_month:T", title="年月")
        alt_y = alt.Y("monthly_units:Q", title="販売台数")
        title = "月次販売台数"
    elif mode_enum == Mode.QUARTER:
        df = hsl.quarterly_sales_long(src_df, hw=hw, begin=begin, end=end)
        alt_x = alt.X("quarter:O", title="四半期")
        alt_y = alt.Y("quarterly_units:Q", title="販売台数")
        title = "四半期販売台数"
    elif mode_enum == Mode.YEAR:
        df = hsl.yearly_sales_long(src_df, hw=hw, begin=begin, end=end)
        alt_x = alt.X("year:O", title="年")
        alt_y = alt.Y("yearly_units:Q", title="販売台数")
        title = "年次販売台数"
    elif mode_enum == Mode.WEEK:
        df = hsl.sales_long(src_df, hw=hw, begin=begin, end=end)
        x_min = df["report_date"].min()
        x_max = df["report_date"].max() + timedelta(days=7)  # 1週間の余裕を持たせる
        scale = alt.Scale(domain=[x_min, x_max])
        alt_x = alt.X(
            "report_date:T",
            title="日付",
            scale=scale,
            axis=alt.Axis(
                format={
                    "year": "%Y",
                    "month": "%Y-%m",
                    "week": "%m-%d",
                    "day": "%m-%d",
                }
            ),
        )
        alt_y = alt.Y("units:Q", title="販売台数")
        title = "週次販売台数"
    else:
        raise ValueError(
            "modeは'week', 'month', 'quarter', 'year'のいずれかを指定してください。"
        )

    # ハードウェアごとの色を取得
    current_hw = hw if hw else hs.get_hw(df)
    hw_colors = hi.get_hard_colors(current_hw)
    alt_color = alt.Color(
        "hw:N", scale=alt.Scale(domain=current_hw, range=hw_colors), title="ハード"
    )

    # Tooltipの定義
    tooltip = [
        alt.Tooltip("hw:N", title="ハード"),
        alt.Tooltip("report_date:T", title="日付", format="%Y-%m-%d"),
        alt.Tooltip("units:Q", title="販売台数"),
    ]

    # アノテーションテーブルの結合
    if annotation_level is not None:
        df = ha.join_annotation(df, level=annotation_level, mode=mode)

    # チャートの作成
    return _chart_line_sales(
        src_df=df,
        alt_x=alt_x,
        alt_y=alt_y,
        ymax=ymax,
        ymin=ymin,
        color=alt_color,
        title=title,
        with_point=with_point,
        multi_line=multi_line,
        tooltip=tooltip,
    )


def chart_line_weekly_by_hw_date(
    hw_periods: List[dict] = [],
    end: int = 52,
    ymax: int | None = None,
    ymin: int = 0,
    multi_line: bool = False,
) -> alt.Chart | alt.LayerChart | alt.FacetChart:
    """
    各ハードウェアの異なる期間の販売台数推移を、各期間の開始点を揃えてプロットする
    Args:
        hw_periods: プロットしたいハードウェア名と期間のリスト。各要素は以下のキーを持つ辞書:
            - 'hw' (str, required): ハードウェアの識別子
            - 'begin' (datetime, required): 集計開始日
            - 'label' (str, optional): 列名（省略時はhw名を使用）
        end: 各期間の最大週数（デフォルトは52週）
        ymax: Y軸の上限値（省略時は自動調整）
    Returns:
        alt.Chart | alt.LayerChart | alt.FacetChart: 作成されたAltairチャートオブジェクト
    """

    # データソースの定義
    df_all = hs.load_hard_sales()
    src_df = hsl.sales_with_offset_long(df_all, hw_periods=hw_periods, end=end)

    alt_x = alt.X("offset_week:Q", title="週数")
    alt_y = alt.Y("units:Q", title="販売台数")
    alt_color = alt.Color("label:N", title="ハード:時期").legend(orient="top-left")

    # Tooltipの定義
    tooltip = [
        alt.Tooltip("hw:N", title="ハード"),
        alt.Tooltip("report_date:T", title="日付", format="%Y-%m-%d"),
        alt.Tooltip("units:Q", title="販売台数"),
    ]

    # チャートの作成
    return _chart_line_sales(
        src_df=src_df,
        alt_x=alt_x,
        alt_y=alt_y,
        ymax=ymax,
        ymin=ymin,
        title="週販推移比較",
        color=alt_color,
        tooltip=tooltip,
        multi_line=multi_line,
    )


def chart_line_cumulative(
    hw: List[str] = [],
    mode: str = "week",
    begin: datetime | date | None = None,
    end: datetime | date | None = None,
    ymin: int = 0,
    ymax: int | None = None,
    annotation_level: int | None = None,
    multi_line: bool = False,
) -> alt.Chart | alt.LayerChart | alt.FacetChart:
    """累計販売台数のチャートを作成する関数
    Args:
        hw: ハードウェアのリスト
        mode: 集計モード（例: "week", "month"）
        begin: 集計開始日
        end: 集計終了日
        annotation_level: アノテーションレベル（オプション）
    Returns:
        alt.Chart | alt.LayerChart | alt.FacetChart: 累計販売台数のチャート
    """
    df_all = hs.load_hard_sales()
    mode_enum = parse_mode(mode)
    src_df = hsl.cumulative_sales_long(df_all, hw=hw, mode=mode, begin=begin, end=end)
    alt_x = alt.X(
        "report_date:T",
        title="販売年月",
        axis=alt.Axis(format="%Y-%m", formatType="time"),
    )
    alt_y = alt.Y("sum_units:Q", title="累計販売台数")
    title = "累計販売台数"

    # ハードウェアごとの色を取得
    current_hw = hw if hw else hs.get_hw(src_df)
    hw_colors = hi.get_hard_colors(current_hw)
    alt_color = alt.Color(
        "hw:N", scale=alt.Scale(domain=current_hw, range=hw_colors), title="ハード"
    ).legend(orient="top-left")

    if annotation_level is not None:
        src_df = ha.join_annotation(src_df, level=annotation_level, mode=mode)

    return _chart_line_sales(
        src_df=src_df,
        alt_x=alt_x,
        alt_y=alt_y,
        ymax=None,
        ymin=ymin,
        color=alt_color,
        title="累計販売台数",
        with_point=False,
        multi_line=multi_line,
    )


def chart_line_cumulative_delta(
    hw: List[str] = [],
    mode: str = "week",
    begin: int | None = None,
    end: int | None = None,
    ymin: int = 0,
    ymax: int | None = None,
    annotation_level: int | None = None,
    index_mode: bool = True,
    with_point: bool = False,
    multi_line: bool = False,
) -> alt.Chart | alt.LayerChart | alt.FacetChart:
    """相対累計販売台数のチャートを作成する関数
    Args:
        hw: ハードウェアのリスト
        mode: "week"、"month"または"year"を指定。週単位の集計なら"week"、月単位の集計なら"month"、年単位の集計なら"year"を指定。
        begin: 集計開始（経過期間の最小値）
        end: 集計終了（経過期間の最大値）
        annotation_level: アノテーションレベル（オプション）
    Returns:
        alt.Chart: 相対累計販売台数のチャート
    """
    df_all = hs.load_hard_sales()
    mode_enum = parse_mode(mode)
    src_df = hsl.cumulative_sales_by_delta_long(
        df_all, hw=hw, mode=mode, begin=begin, end=end
    )
    alt_y = alt.Y("sum_units:Q", title="相対累計販売台数")
    title = "相対累計販売台数"
    if mode_enum == Mode.MONTH:
        col_name = "index_month" if index_mode else "delta_month"
        alt_x = alt.X(f"{col_name}:Q", title="月数")
    elif mode_enum == Mode.YEAR:
        col_name = "index_year" if index_mode else "delta_year"
        alt_x = alt.X(f"{col_name}:Q", title="年数")
    elif mode_enum == Mode.WEEK:
        col_name = "index_week" if index_mode else "delta_week"
        alt_x = alt.X(
            f"{col_name}:Q", title="週数", axis=alt.Axis(grid=True, tickCount=20)
        )
    else:
        raise ValueError("modeは'week', 'month', 'year'のいずれかを指定してください。")

    if index_mode and end is not None:
        alt_x = alt_x.scale(domain=[1, end + 1])

    # ハードウェアごとの色を取得
    current_hw = hw if hw else hs.get_hw(src_df)
    hw_colors = hi.get_hard_colors(current_hw)
    alt_color = alt.Color(
        "hw:N", scale=alt.Scale(domain=current_hw, range=hw_colors), title="ハード"
    ).legend(orient="top-left")

    if annotation_level is not None:
        src_df = ha.join_annotation(
            src_df, level=annotation_level, mode=mode, delta=True
        )

    return _chart_line_sales(
        src_df=src_df,
        alt_x=alt_x,
        alt_y=alt_y,
        ymax=ymax,
        color=alt_color,
        title="相対累計販売台数",
        with_point=with_point,
        multi_line=multi_line,
    )


def chart_line_cumsum_diffs(
    cmplist: list[tuple[str, str]],
    ymax: int | None = None,
    multi_line: bool = False,
    annotation_level: int | None = None,
) -> alt.Chart | alt.LayerChart | alt.FacetChart:
    """複数ハードウェア間の累計販売台数差分を示す折れ線チャートを作成する関数

    カレンダー上の同じ日付における異なるハードウェア間の累計販売台数の差分を時系列で
    プロットします。追いつかれた週以降のデータはデフォルトでフィルタリングされます。

    Args:
        cmplist: 比較するハードウェアペアのリスト。各要素は(hw_new, hw_old)の形式で、
            hw_oldの累計販売台数からhw_newの累計販売台数を引いた差分を計算します。
            例: [("NS2", "PS5"), ("NSW", "PS4")]
        ymax: Y軸の上限値（オプション）。指定しない場合は自動調整

    Returns:
        alt.Chart: 累計販売台数差を示すAltairチャート
    """
    df_all = hs.load_hard_sales()
    src_df = hsl.cumsum_diffs_long(df_all, cmplist)

    alt_y = alt.Y("cumsum_diff:Q", title="累計販売台数差")
    alt_x = alt.X("index_week:Q", title="販売開始からの週数")

    alt_color = alt.Color("pair_name:N", title="比較ハード").legend(orient="top-right")

    # Tooltipの定義
    tooltip = [
        alt.Tooltip("hw_new:N", title="ハード"),
        alt.Tooltip("report_date:T", title="日付", format="%Y-%m-%d"),
        alt.Tooltip("index_week:Q", title="週数"),
        alt.Tooltip("sum_units_new:Q", title="累計販売台数"),
        alt.Tooltip("cumsum_diff:Q", title="累計販売台数差"),
    ]

    if annotation_level is not None:
        src_df = ha.join_annotation(
            src_df, level=annotation_level, mode="week", hw_col="hw_new", delta=True
        )

    return _chart_line_sales(
        src_df=src_df,
        alt_x=alt_x,
        alt_y=alt_y,
        ymax=ymax,
        color=alt_color,
        title="累計販売台数差",
        with_point=False,
        tooltip=tooltip,
        multi_line=multi_line,
    )


def chart_line_pase_diffs(
    cmplist: list[tuple[str, str]],
    ymax: int | None = None,
    multi_line: bool = False,
) -> alt.Chart | alt.LayerChart | alt.FacetChart:
    """複数ハードウェア間の販売ペース差を示す折れ線チャートを作成する関数

    各ハードウェアの発売後の相対的な経過週数における累計販売台数を比較し、
    普及ペースの違いを可視化します。

    Args:
        cmplist: 比較するハードウェアペアのリスト。各要素は(hw_new, hw_old)の形式で、
            hw_oldとhw_newの発売後の相対週数で累計販売台数を比較します。
            例: [("PS5", "PS4"), ("PS5", "PS3")]
        ymax: Y軸の上限値（オプション）。指定しない場合は自動調整

    Returns:
        alt.Chart | alt.LayerChart: 販売ペース差を示すAltairチャート
    """
    df_all = hs.load_hard_sales()
    src_df = hsl.sales_pase_diffs_long(df_all, cmplist)

    alt_y = alt.Y("pase_diff:Q", title="累計販売台数差分")
    alt_x = alt.X("index_week:Q", title="販売開始からの週数")

    alt_color = alt.Color("pair_name:N", title="比較ハード").legend(orient="top-left")

    # Tooltipの定義
    tooltip = [
        alt.Tooltip("pair_name:N", title="比較ハード"),
        alt.Tooltip("report_date_new:T", title="日付(新)", format="%Y-%m-%d"),
        alt.Tooltip("index_week:Q", title="週数"),
        alt.Tooltip("sum_units_new:Q", title="累計販売台数(新)"),
        alt.Tooltip("pase_diff:Q", title="累計販売台数差分"),
    ]

    return _chart_line_sales(
        src_df=src_df,
        alt_x=alt_x,
        alt_y=alt_y,
        ymax=ymax,
        color=alt_color,
        title="販売ペース差",
        with_point=False,
        tooltip=tooltip,
        multi_line=multi_line,
    )


def chart_line_ycumulative(
    hw: list[str] = [],
    year: int = 2026,
    begin: int = 1,
    end: int = 366,
    ymax: int | None = None,
    annotation_level: int | None = None,
    multi_line: bool = False,
) -> alt.Chart | alt.LayerChart | alt.FacetChart:
    """複数のハードウェアの同じ年の年次累積のチャートを作成する関数
    Args:
        hw: ハードウェアのリスト。例: ["NS2", "NSW", "PS5"]
        year: 集計対象の年
        begin: 集計開始日
        end: 集計終了日
        ymax: Y軸の上限値（オプション）。指定しない場合は自動調整
        annotation_level: 注釈レベル（オプション）
        multi_line: Trueの場合、Multi-Line-Tooltipを有効化
    Returns:
        alt.Chart: 年次累計販売台数のチャート
    """
    df_all = hs.load_hard_sales()
    src_df = hsl.yearly_cumulative_long(df_all, hw=hw, year=year, begin=begin, end=end)
    alt_x = alt.X(
        "yday:Q",
        title="年間通算日",
    )
    alt_y = alt.Y("yearly_sum_units:Q", title="年間累計販売台数")
    title = "年間累計販売台数"

    current_hw = hw if hw else hs.get_hw(src_df)
    hw_colors = hi.get_hard_colors(current_hw)
    alt_color = alt.Color(
        "hw:N", title="ハード", scale=alt.Scale(domain=current_hw, range=hw_colors)
    ).legend(orient="top-left")

    if annotation_level is not None:
        src_df = ha.join_annotation(
            src_df, level=annotation_level, mode="week", hw_col="hw"
        )

    return _chart_line_sales(
        src_df=src_df,
        alt_x=alt_x,
        alt_y=alt_y,
        ymax=ymax,
        color=alt_color,
        title=title,
        with_point=True,
        multi_line=multi_line,
    )


def chart_line_ycumulative_by_hw_year(
    hw_years: List[tuple[str, int]],
    begin: int = 1,
    end: int = 366,
    ymax: int | None = None,
    annotation_level: int | None = None,
    multi_line: bool = False,
) -> alt.Chart | alt.LayerChart | alt.FacetChart:
    """複数のハードウェアの異なる年の年次累積のチャートを作成する関数
    Args:
        hw_years: ハードウェアと年のタプルのリスト。例: [("NS2", 2026), ("NSW", 2026), ("PS5", 2026)]
        begin: 集計開始日
        end: 集計終了日
        ymax: Y軸の上限値（オプション）。指定しない場合は自動調整
        event_mask: イベントマスク（オプション）
        multi_line: Trueの場合、Multi-Line-Tooltipを有効化
    Returns:
        alt.Chart: 年次累計販売台数のチャート
    """
    df_all = hs.load_hard_sales()
    src_df = hsl.yearly_cumulative_by_hwy_long(
        df_all, hw_years=hw_years, begin=begin, end=end
    )
    alt_x = alt.X(
        "yday:Q",
        title="年間通算日",
    )
    alt_y = alt.Y("yearly_sum_units:Q", title="年間累計販売台数")
    title = "年間累計販売台数"

    alt_color = alt.Color("label:N", title="ハード年").legend(orient="top-left")

    # Tooltipの定義
    tooltip = [
        alt.Tooltip("hw:N", title="ハード"),
        alt.Tooltip("report_date:T", title="日付", format="%Y-%m-%d"),
        alt.Tooltip("yearly_sum_units:Q", title="年間累計販売台数"),
    ]

    if annotation_level is not None:
        src_df = ha.join_annotation(
            src_df, level=annotation_level, mode="week", hw_col="hw"
        )

    return _chart_line_sales(
        src_df=src_df,
        alt_x=alt_x,
        alt_y=alt_y,
        ymax=ymax,
        color=alt_color,
        title=title,
        with_point=True,
        multi_line=multi_line,
        tooltip=tooltip,
    )
