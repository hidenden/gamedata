# 標準ライブラリ
from datetime import date, datetime
from typing import List

import altair as alt

# サードパーティライブラリ
import polars as pl

from . import hard_event as he
from . import hard_info as hi

# プロジェクト内モジュール
# プロジェクト内モジュール
from . import hard_sales as hs
from . import hard_sales_long as hsl


def _chart_line_sales(
    src_df: pl.DataFrame,
    alt_x: alt.X,
    alt_y: alt.Y,
    color: alt.Color,
    ymin: int = 0,
    ymax: int | None = None,
    title: str | None = None,
    event_joinner=lambda df: df,
    with_point: bool = True,
    legend_orient: str = "top-right",
) -> alt.Chart:
    """売上のチャートを作成する関数

    Args:
        src_df: データフレーム
        event_joinner: イベント結合関数
        labeler: ラベル付け関数（オプション）

    Returns:
        alt.Chart: 売上のチャート
    """
    # データの取得とイベントの結合
    df: pl.DataFrame = event_joinner(src_df)

    # Y上限の設定
    if ymax is not None:
        alt_y = alt_y.scale(domain=[ymin, ymax])

    # チャートの作成
    base_chart = alt.Chart(df).encode(x=alt_x, y=alt_y, color=color)
    chart = base_chart.mark_line()
    if with_point:
        chart += base_chart.mark_point()

    # dfがカラム evenv_name を持っている場合は、mark_text()でイベント名を表示する
    if "event_name" in df.columns:
        event_chart = (
            base_chart.transform_filter(alt.datum.event_name != None)
            .mark_text(align="center", baseline="middle", dx=10, dy=-10)
            .encode(text="event_name:N")
        )
        chart += event_chart

    chart = chart.properties().configure(autosize={"type": "pad"})
    if title is not None:
        chart = chart.properties(title=title)
    chart = chart.configure_legend(orient=legend_orient)
    # chart = chart.properties(usermeta={"embedOptions": {"actions": False}})

    return chart


def chart_line_sales(
    hw: List[str] = [],
    mode: str = "week",
    begin: datetime | date | None = None,
    end: datetime | date | None = None,
    ymin: int = 0,
    ymax: int | None = None,
    event_mask: he.EventMasks | None = None,
) -> alt.Chart:
    """売上のチャートを作成する関数

    Args:
        hw: ハードウェアのリスト
        mode: 集計モード（例: "week", "month"）
        begin: 集計開始日
        end: 集計終了日
        event_mask: イベントマスク（オプション）

    Returns:
        alt.Chart: 売上のチャート
    """
    # データソースの定義
    src_df: pl.DataFrame = hs.load_hard_sales()

    if mode == "month":
        df = hsl.monthly_sales_long(src_df, hw=hw, begin=begin, end=end)
        alt_x = alt.X("year_month:T", title="年月")
        alt_y = alt.Y("monthly_units:Q", title="販売台数")
        title = "月次販売台数"
    elif mode == "quarter":
        df = hsl.quarterly_sales_long(src_df, hw=hw, begin=begin, end=end)
        alt_x = alt.X("quarter:O", title="四半期")
        alt_y = alt.Y("quarterly_units:Q", title="販売台数")
        title = "四半期販売台数"
    elif mode == "year":
        df = hsl.yearly_sales_long(src_df, hw=hw, begin=begin, end=end)
        alt_x = alt.X("year:O", title="年")
        alt_y = alt.Y("yearly_units:Q", title="販売台数")
        title = "年次販売台数"
    else:
        df = hsl.sales_long(src_df, hw=hw, begin=begin, end=end)
        alt_x = alt.X("report_date:T", title="日付")
        alt_y = alt.Y("units:Q", title="販売台数")
        title = "週次販売台数"

    # ハードウェアごとの色を取得
    current_hw = hw if hw else hs.get_hw(df)
    hw_colors = hi.get_hard_colors(current_hw)
    alt_color = alt.Color(
        "hw:N", scale=alt.Scale(domain=current_hw, range=hw_colors), title="ハード"
    )

    # イベント結合関数の定義
    def event_joinner(df: pl.DataFrame) -> pl.DataFrame:
        if (event_mask is not None) and (mode == "week"):
            event_df = he.mask_event(he.load_hard_event(), event_mask)
            df_with_event = df.join(
                other=event_df,
                left_on=["report_date", "hw"],
                right_on=["report_date", "hw"],
                how="left",
            )
            return df_with_event
        else:
            return df

    # チャートの作成
    return _chart_line_sales(
        src_df=df,
        alt_x=alt_x,
        alt_y=alt_y,
        ymax=ymax,
        ymin=ymin,
        color=alt_color,
        title=title,
        event_joinner=event_joinner,
    )


def chart_line_weekly_by_hw_date(
    hw_periods: List[dict] = [], end: int = 52, ymax: int | None = None, ymin: int = 0
) -> alt.Chart:
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
        alt.Chart: 作成されたAltairチャートオブジェクト
    """

    # データソースの定義
    df_all = hs.load_hard_sales()
    src_df = hsl.sales_with_offset_long(df_all, hw_periods=hw_periods, end=end)

    alt_x = alt.X("offset_week:Q", title="週数")
    alt_y = alt.Y("units:Q", title="販売台数")
    alt_color = alt.Color("label:N", title="ハード:時期")

    # チャートの作成
    return _chart_line_sales(
        src_df=src_df,
        alt_x=alt_x,
        alt_y=alt_y,
        ymax=ymax,
        ymin=ymin,
        title="週販推移比較",
        color=alt_color,
    )


def chart_line_cumulative(
    hw: List[str] = [],
    mode: str = "week",
    begin: datetime | date | None = None,
    end: datetime | date | None = None,
    ymin: int = 0,
    ymax: int | None = None,
    event_mask: he.EventMasks | None = None,
) -> alt.Chart:
    """累計販売台数のチャートを作成する関数
    Args:
        hw: ハードウェアのリスト
        mode: 集計モード（例: "week", "month"）
        begin: 集計開始日
        end: 集計終了日
        event_mask: イベントマスク（オプション）
    Returns:
        alt.Chart: 累計販売台数のチャート
    """
    df_all = hs.load_hard_sales()
    src_df = hsl.cumulative_sales_long(df_all, hw=hw, mode=mode, begin=begin, end=end)
    alt_x = alt.X("report_date:T", title="販売年月")
    alt_y = alt.Y("sum_units:Q", title="累計販売台数")
    title = "累計販売台数"

    # ハードウェアごとの色を取得
    current_hw = hw if hw else hs.get_hw(src_df)
    hw_colors = hi.get_hard_colors(current_hw)
    alt_color = alt.Color(
        "hw:N", scale=alt.Scale(domain=current_hw, range=hw_colors), title="ハード"
    )

    def event_joinner(df: pl.DataFrame) -> pl.DataFrame:
        if (event_mask is not None) and (mode == "week"):
            event_df = he.mask_event(he.load_hard_event(), event_mask)
            df_with_event = df.join(
                other=event_df,
                left_on=["report_date", "hw"],
                right_on=["report_date", "hw"],
                how="left",
            )
            return df_with_event
        else:
            return df

    return _chart_line_sales(
        src_df=src_df,
        alt_x=alt_x,
        alt_y=alt_y,
        ymax=None,
        ymin=ymin,
        color=alt_color,
        title="累計販売台数",
        event_joinner=event_joinner,
        with_point=False,
        legend_orient="top-left",
    )


def chart_line_cumulative_delta(
    hw: List[str] = [],
    mode: str = "week",
    begin: int | None = None,
    end: int | None = None,
    ymin: int = 0,
    ymax: int | None = None,
    event_mask: he.EventMasks | None = None,
) -> alt.Chart:
    """相対累計販売台数のチャートを作成する関数
    Args:
        hw: ハードウェアのリスト
        mode: "week"、"month"または"year"を指定。週単位の集計なら"week"、月単位の集計なら"month"、年単位の集計なら"year"を指定。
        begin: 集計開始（経過期間の最小値）
        end: 集計終了（経過期間の最大値）
        event_mask: イベントマスク（オプション）
    Returns:
        alt.Chart: 相対累計販売台数のチャート
    """
    df_all = hs.load_hard_sales()
    src_df = hsl.cumulative_sales_by_delta_long(
        df_all, hw=hw, mode=mode, begin=begin, end=end
    )
    alt_y = alt.Y("sum_units:Q", title="相対累計販売台数")
    title = "相対累計販売台数"
    if mode == "month":
        alt_x = alt.X("delta_month:Q", title="月数")
    elif mode == "year":
        alt_x = alt.X("delta_year:Q", title="年数")
    else:
        alt_x = alt.X(
            "delta_week:Q", title="週数", axis=alt.Axis(grid=True, tickCount=20)
        )

    # ハードウェアごとの色を取得
    current_hw = hw if hw else hs.get_hw(src_df)
    hw_colors = hi.get_hard_colors(current_hw)
    alt_color = alt.Color(
        "hw:N", scale=alt.Scale(domain=current_hw, range=hw_colors), title="ハード"
    )

    def event_joinner(df: pl.DataFrame) -> pl.DataFrame:
        if (event_mask is not None) and (mode == "week"):
            event_df = he.mask_event(he.load_hard_event(True), event_mask)
            df_with_event = df.join(
                other=event_df,
                left_on=["delta_week", "hw"],
                right_on=["delta_week", "hw"],
                how="left",
            )
            return df_with_event
        else:
            return df

    return _chart_line_sales(
        src_df=src_df,
        alt_x=alt_x,
        alt_y=alt_y,
        ymax=ymax,
        color=alt_color,
        title="相対累計販売台数",
        event_joinner=event_joinner,
        with_point=False,
        legend_orient="top-left",
    )
