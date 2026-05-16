# 標準ライブラリ
from datetime import date, datetime
from typing import List

import altair as alt

# サードパーティライブラリ
import polars as pl

from . import hard_info as hi

# プロジェクト内モジュール
# プロジェクト内モジュール
from . import hard_sales as hs
from . import hard_sales_long as hsl
from . import hard_sales_filter as hsf
from .mode import Mode, parse_mode


def _chart_bar_sales(
    src_df: pl.DataFrame,
    alt_x: alt.X,
    alt_y: alt.Y,
    color: alt.Color,
    ymin: int = 0,
    ymax: int | None = None,
    title: str | None = None,
    xoffset: str | None = None,
    legend_orient: str = "top-right",
    tooltip: List[alt.Tooltip] | None = None,
) -> alt.Chart:
    """売上の棒グラフを作成する内部関数

    Args:
        src_df: データフレーム
        alt_x: X軸の設定
        alt_y: Y軸の設定
        color: カラーの設定
        ymin: Y軸の最小値
        ymax: Y軸の最大値（オプション）
        title: チャートのタイトル（オプション）
        xoffset: X軸のオフセット（オプション）
        legend_orient: 凡例の位置（オプション）
        tooltip: ツールチップの設定（オプション）

    Returns:
        alt.Chart: 売上の棒グラフ
    """

    # Y上限の設定
    if ymax is not None:
        alt_y = alt_y.scale(domain=[ymin, ymax])

    base_chart = alt.Chart(src_df).encode(
        x=alt_x,
        y=alt_y,
        color=color,
    )
    chart = base_chart.mark_bar()

    if title is not None:
        chart = chart.properties(title=title)
    if xoffset is not None:
        chart = chart.encode(xOffset=xoffset)
    if tooltip is not None:
        chart = chart.encode(tooltip=tooltip)
    chart = chart.configure_legend(orient=legend_orient)
    chart = chart.properties(usermeta={"embedOptions": {"actions": True}})
    return chart


def chart_bar_sales(
    hw: list[str] = [],
    begin: datetime | date | None = None,
    end: datetime | date | None = None,
    mode: str = "month",
    stacked: bool = False,
    ymax: int | None = None,
) -> alt.Chart:
    """ハード別の月次売上棒グラフを作成する関数
    Args:
        hw: ハードのリスト
        begin: データの開始日（オプション）
        end: データの終了日（オプション）
        mode: 集計の単位（"month", "quarter", または"year"、デフォルトは"month"）
        stacked: 棒グラフを積み上げ表示するかどうか（デフォルトはFalse）
        ymax: Y軸の最大値（オプション）

    Returns:
        alt.Chart: ハード別の月次売上棒グラフ
    """
    df_all = hs.load_hard_sales()

    mode_enum = parse_mode(mode)
    if mode_enum == Mode.MONTH:
        src_df = hsl.monthly_sales_long(df_all, hw=hw, begin=begin, end=end)
        alt_x = alt.X(
            "year_month:O",
            title="年月",
            axis=alt.Axis(format="%Y-%m", formatType="time"),
        )
        alt_y = alt.Y("monthly_units:Q", title="販売台数")
        title = "月次販売台数"
        tooltip = [
            alt.Tooltip("hw:N", title="ハード"),
            alt.Tooltip("monthly_units:Q", title="販売台数"),
        ]
    elif mode_enum == Mode.QUARTER:
        src_df = hsl.quarterly_sales_long(df_all, hw=hw, begin=begin, end=end)
        alt_x = alt.X("quarter:O", title="四半期")
        alt_y = alt.Y("quarterly_units:Q", title="販売台数")
        title = "四半期販売台数"
        tooltip = [
            alt.Tooltip("hw:N", title="ハード"),
            alt.Tooltip("quarter:O", title="四半期"),
            alt.Tooltip("quarterly_units:Q", title="販売台数"),
        ]
    elif mode_enum == Mode.YEAR:
        src_df = hsl.yearly_sales_long(df_all, hw=hw, begin=begin, end=end)
        alt_x = alt.X("year:O", title="年")
        alt_y = alt.Y("yearly_units:Q", title="販売台数")
        title = "年次販売台数"
        tooltip = [
            alt.Tooltip("hw:N", title="ハード"),
            alt.Tooltip("year:O", title="年"),
            alt.Tooltip("yearly_units:Q", title="販売台数"),
        ]
    else:
        raise ValueError(
            "modeは'month', 'quarter', または 'year'のいずれかでなければなりません"
        )

        # ハードウェアごとの色を取得
    current_hw = hs.get_hw(src_df)
    hw_colors = hi.get_hard_colors(current_hw)
    alt_color = alt.Color(
        "hw:N", title="ハード", scale=alt.Scale(domain=current_hw, range=hw_colors)
    )
    xoffset = "hw:N" if not stacked else None

    return _chart_bar_sales(
        src_df=src_df,
        alt_x=alt_x,
        alt_y=alt_y,
        color=alt_color,
        title=title,
        ymax=ymax,
        ymin=0,
        xoffset=xoffset,
        tooltip=tooltip,
    )


def chart_bar_hwsales_by_year(
    hw: str,
    begin: datetime | date | None = None,
    end: datetime | date | None = None,
    mode: str = "month",
    ymax: int | None = None,
) -> alt.Chart:
    """
    指定したハードウェアの月間販売台数を年別に棒グラフで表示する

    Args:
        hw: ハードウェア名
        begin: データの開始日（オプション）
        end: データの終了日（オプション）
        mode: 集計の単位（"month", "quarter",デフォルトは"month"）
        ymax: Y軸の最大値（オプション）
    Returns:
        alt.Chart: 年別の月間販売台数を表示する棒グラフ
    """
    df_all = hs.load_hard_sales()

    mode_enum = parse_mode(mode)
    if mode_enum == Mode.MONTH:
        src_df = hsl.monthly_sales_long(df_all, hw=[hw], begin=begin, end=end)
        alt_x = alt.X("month:O", title="月")
        alt_y = alt.Y("monthly_units:Q", title="販売台数")
        title = "月間販売推移"
        tooltip = [
            alt.Tooltip("hw:N", title="ハード"),
            alt.Tooltip("year:O", title="年"),
            alt.Tooltip("month:O", title="月"),
            alt.Tooltip("monthly_units:Q", title="販売台数"),
        ]
    elif mode_enum == Mode.QUARTER:
        src_df = hsl.quarterly_sales_long(df_all, hw=[hw], begin=begin, end=end)
        alt_x = alt.X("q_num:O", title="四半期")
        alt_y = alt.Y("quarterly_units:Q", title="販売台数")
        title = "四半期販売推移"
        tooltip = [
            alt.Tooltip("hw:N", title="ハード"),
            alt.Tooltip("year:O", title="年"),
            alt.Tooltip("q_num:O", title="四半期"),
            alt.Tooltip("quarterly_units:Q", title="販売台数"),
        ]
    else:
        raise ValueError("modeは'month'または'quarter'のいずれかでなければなりません")

    alt_color = alt.Color("year:O", title="年")
    xoffset = "year:O"

    return _chart_bar_sales(
        src_df=src_df,
        alt_x=alt_x,
        alt_y=alt_y,
        color=alt_color,
        title=title,
        ymax=ymax,
        xoffset=xoffset,
        legend_orient="top-left",
        tooltip=tooltip,
    )


def chart_hbar_yearly_share_by_maker(
    begin: datetime | date | None = None, end: datetime | date | None = None
) -> alt.Chart:
    """メーカー別の年次シェアを100%積み上げ横棒グラフで表示する。

    Args:
        begin: 集計開始日（オプション）。
        end: 集計終了日（オプション）。

    Returns:
        alt.Chart: 年ごとのメーカーシェアと割合ラベルを表示するチャート。
    """
    _df_all = hs.load_hard_sales()
    _df = hsl.maker_long(_df_all, begin_year=begin, end_year=end)
    _df = _df.with_columns(
        (
            (pl.col("yearly_pct").cum_sum().over("year") - pl.col("yearly_pct") / 2)
            / 100
        ).alias("mid_point"),
        (pl.col("yearly_pct").round(1).cast(pl.String) + "%").alias("pct_label"),
    )

    maker_list = hs.get_maker(_df)
    maker_color = hi.get_maker_colors(maker_list)
    _base = alt.Chart(_df).encode(
        y=alt.Y("year:O", sort="descending", title="年"),
        x=alt.X("yearly_pct:Q", stack="normalize", title="シェア(%)"),
        color=alt.Color(
            "maker_name:N",
            title="メーカー",
            scale=alt.Scale(domain=maker_list, range=maker_color),
        ),
        order=alt.Order("mid_point:Q"),
    )

    _bars = _base.mark_bar()
    _text = _base.mark_text(size=12, baseline="middle").encode(
        detail="maker_name:N",
        color=alt.value("white"),
        text=alt.Text("pct_label:N"),
        x=alt.X("mid_point:Q"),
    )
    return (
        (_bars + _text)
        .properties(
            title="メーカーシェア",
        )
        .configure_legend(
            orient="top-left",
            strokeColor="white",
            padding=10,
            fillColor="#88888880",
            cornerRadius=5,
        )
    )


def chart_bar_sales_by_hard_year(
    hwy: list[tuple[str, int]],
    mode: str = "month",
    stacked: bool = False,
    ymax: int | None = None,
) -> alt.Chart:
    """ハード別の月次売上棒グラフを作成する関数
    Args:
        hwy: ハードと年のタプルのリスト
        mode: 集計の単位（"month", "quarter", デフォルトは"month"）
        stacked: 棒グラフを積み上げ表示するかどうか（デフォルトはFalse）
        ymax: Y軸の最大値（オプション）

    Returns:
        alt.Chart: ハード別の月次売上棒グラフ
    """
    df_all = hs.load_hard_sales()

    def data_source(df_all, hwy, fn):
        dfs = []
        for h, y in hwy:
            df = fn(df_all, hw=[h], begin=datetime(y, 1, 1), end=datetime(y, 12, 31))
            dfs.append(df)
        return pl.concat(dfs)

    mode_enum = parse_mode(mode)
    if mode_enum == Mode.MONTH:
        src_df = data_source(df_all, hwy, hsl.monthly_sales_long)
        alt_x = alt.X("month:O", title="月")
        alt_y = alt.Y("monthly_units:Q", title="販売台数")
        title = "月次販売台数"
        tooltip = [
            alt.Tooltip("hw:N", title="ハード"),
            alt.Tooltip("year:N", title="年"),
            alt.Tooltip("month:N", title="月"),
            alt.Tooltip("monthly_units:Q", title="販売台数"),
        ]
    elif mode_enum == Mode.QUARTER:
        src_df = data_source(df_all, hwy, hsl.quarterly_sales_long)
        alt_x = alt.X("q_num:O", title="四半期")
        alt_y = alt.Y("quarterly_units:Q", title="販売台数")
        title = "四半期販売台数"
        tooltip = [
            alt.Tooltip("hw:N", title="ハード"),
            alt.Tooltip("quarter:O", title="四半期"),
            alt.Tooltip("quarterly_units:Q", title="販売台数"),
        ]
    else:
        raise ValueError(
            "modeは'month', 'quarter', または 'year'のいずれかでなければなりません"
        )

    src_df = src_df.with_columns(
        pl.concat_str([pl.col("hw"), pl.lit("_"), pl.col("year")]).alias("hw_year")
    )

    alt_color = alt.Color("hw_year:N", title="ハード_年")
    xoffset = "hw_year:N" if not stacked else None

    return _chart_bar_sales(
        src_df=src_df,
        alt_x=alt_x,
        alt_y=alt_y,
        color=alt_color,
        title=title,
        ymax=ymax,
        ymin=0,
        xoffset=xoffset,
        tooltip=tooltip,
    )


def chart_bar_yearly_delta(
    hw: list[str],
    stacked: bool = False,
    delta_begin: int | None = None,
    delta_end: int | None = None,
) -> alt.Chart:
    """
    指定した機種の経過年毎販売台数をハード別に棒グラフで表示する

    Args:
        hw: プロットしたいハードウェア名のリスト
        delta_begin: 経過年の開始（指定しない場合は0年）
        delta_end: 経過年の終了（指定しない場合は全期間）

    Returns:
        alt.Chart: 経過年毎販売台数の棒グラフ

        DataFrameのカラム構成:
        - index: delta_year (int64): 発売年から何年後か（同じ年なら0）
        - columns: hw (string): ゲームハードの識別子
        - values: yearly_units (int64): 経過年次販売台数
    """

    df_all = hs.load_hard_sales()
    df = (
        hsf.delta_yearly_sales(df_all)
        .filter(pl.col("hw").is_in(hw))
        .filter(pl.col("delta_year") >= (delta_begin if delta_begin is not None else 0))
        .filter(
            pl.col("delta_year")
            <= (delta_end if delta_end is not None else pl.max("delta_year"))
        )
    )

    alt_x = alt.X("delta_year:O", title="経過年")
    alt_y = alt.Y("yearly_units:Q", title="販売台数")
    title = "経過年毎販売台数"
    tooltip = [
        alt.Tooltip("hw:N", title="ハード"),
        alt.Tooltip("delta_year:N", title="経過年"),
        alt.Tooltip("yearly_units:Q", title="販売台数"),
    ]
    hw_list = hs.get_hw(df)
    hw_colors = hi.get_hard_colors(hw_list)
    alt_color = alt.Color(
        "hw:N", title="ハード", scale=alt.Scale(domain=hw_list, range=hw_colors)
    )
    xoffset = "hw:N" if not stacked else None

    return _chart_bar_sales(
        src_df=df,
        alt_x=alt_x,
        alt_y=alt_y,
        color=alt_color,
        title=title,
        legend_orient="top-right",
        tooltip=tooltip,
        xoffset=xoffset,
    )


def chart_bar_month_year(
    month: int,
    begin: int | None = None,
    end: int | None = None,
    stacked: bool = True,
) -> alt.Chart:
    """
    指定した月の年ごとの移り変わりをメーカーごとの棒グラフで表示する

    Args:
        month: 対象月（1-12）
        begin: 集計開始年
        end: 集計終了年(
        stacked: 棒グラフを積み上げ表示するかどうか

    Returns:
        alt.Chart: 経過年毎販売台数の棒グラフ
    """
    begin_date = datetime(begin, 1, 1) if begin is not None else None
    end_date = datetime(end, 12, 31) if end is not None else None

    df_all = hs.load_hard_sales()
    df = hsf.monthly_sales(
        df_all, maker_mode=True, begin=begin_date, end=end_date
    ).filter(pl.col("month") == month)
    alt_x = alt.X("year:O", title="年")
    alt_y = alt.Y("monthly_units:Q", title="販売台数")
    title = f"{month}月のメーカー別販売台数"

    maker_list = hs.get_maker(df)
    maker_color = hi.get_maker_colors(maker_list)

    alt_color = alt.Color(
        "maker_name:N",
        title="メーカー",
        scale=alt.Scale(domain=maker_list, range=maker_color),
    )
    xoffset = "maker_name:N" if not stacked else None

    return _chart_bar_sales(
        src_df=df,
        alt_x=alt_x,
        alt_y=alt_y,
        color=alt_color,
        title=title,
        legend_orient="top-right",
        xoffset=xoffset,
    )
