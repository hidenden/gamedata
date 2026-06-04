from datetime import date, datetime
from typing import Literal, List
import altair as alt


# プロジェクト内モジュール
from . import hard_sales as hs
from . import hard_sales_long as hsl
from .mode import Mode, parse_mode


def chart_heatmap(
    hw: str | List[str],
    mode: Literal["week", "month"] = "month",
    begin: date | datetime | None = None,
    end: date | datetime | None = None,
    scale_type: Literal["linear", "log", "sqrt"] = "log",
    scale_scheme: Literal[
        "viridis", "magma", "inferno", "plasma", "cividis", "turbo"
    ] = "plasma",
    grid: bool = False,
) -> alt.LayerChart | alt.Chart:
    """指定ハードの販売台数ヒートマップを作成する。

    Args:
        hw: 対象ハードの識別子。(例: "NSW", "PS5") 文字列1つまたは文字列のリスト。
        mode: 集計粒度。"week" は週次、"month" は月次。
        begin: 集計開始日。None の場合はデータ先頭から。
        end: 集計終了日。None の場合はデータ末尾まで。
        scale_type: カラースケールの種類（"linear" または "log"）。
        scale_scheme: カラースキーム名。
        grid: グリッド線を表示するかどうか。

    Returns:
        年 x 週（または月）で販売台数を表す Altair ヒートマップ。

    Raises:
        ValueError: mode が "week" または "month" 以外の場合。
    """
    if isinstance(hw, str):
        hw_key = [hw]
        alt_row = None
    else:
        hw_key = hw
        alt_row = alt.Row(shorthand="hw:N", title="ハード")

    df_all = hs.load_hard_sales()
    scale = alt.Scale(scheme=scale_scheme, type=scale_type)
    mode_enum = parse_mode(mode)
    if mode_enum == Mode.WEEK:
        src_df = hsl.sales_long(df_all, hw=hw_key, begin=begin, end=end)
        alt_x = alt.X(shorthand="yweek:O", title="週", axis=alt.Axis(grid=grid))
        alt_y = alt.Y(shorthand="year:O", title="年", axis=alt.Axis(grid=grid))
        alt_color = alt.Color(shorthand="units:Q", title="販売台数", scale=scale)
        title = "週次ヒートマップ"
    elif mode_enum == Mode.MONTH:
        src_df = hsl.monthly_sales_long(df_all, hw=hw_key, begin=begin, end=end)
        alt_x = alt.X(shorthand="month:O", title="月", axis=alt.Axis(grid=grid))
        alt_y = alt.Y(shorthand="year:O", title="年", axis=alt.Axis(grid=grid))
        alt_color = alt.Color(
            shorthand="monthly_units:Q", title="販売台数", scale=scale
        )
        title = "月次ヒートマップ"
    else:
        raise ValueError("modeは 'week'または 'month'のいずれかでなければなりません")

    base_chart = alt.Chart(src_df).encode(
        x=alt_x,
        y=alt_y,
        color=alt_color,
    )
    if alt_row:
        base_chart = base_chart.encode(row=alt_row)

    chart = base_chart.mark_rect().properties(
        title=title,
    )
    return chart
