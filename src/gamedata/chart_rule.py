from typing import Literal, List, Optional
import altair as alt
import polars as pl


def chart_rule_xy(
    base_chart: alt.Chart,
    x: int | str | float | None = None,
    y: int | float | None = None,
    stroke: [int, int] = [1, 0],
    size: int = 2,
    color: str = "black",
) -> alt.LayerChart | alt.Chart:
    """基準チャートに縦線・横線のガイドルールを重ねる。

    Args:
        base_chart: ルールを重ねるベースの Altair チャート。
        x: 縦線の位置。`None` の場合は縦線を描画しない。
        y: 横線の位置。`None` の場合は横線を描画しない。
        stroke: 線種を指定する `strokeDash` パターン。
        size: 線の太さ。
        color: 線の色。

    Returns:
        ルール線を重ねたチャート。

    Raises:
        ValueError: `x` と `y` の両方が `None` の場合。
    """
    if x is None and y is None:
        raise ValueError("x or y must be provided")
    value_x = x if x is not None else 0
    value_y = y if y is not None else 0

    rule_df = pl.DataFrame(
        data={
            "x": [value_x],
            "y": [value_y],
        }
    )
    out_chart = base_chart
    if x:
        v_rule = (
            alt.Chart(rule_df)
            .mark_rule(strokeDash=stroke, size=size, color=color)
            .encode(x="x", tooltip=alt.value(None))
        )
        out_chart += v_rule
    if y:
        h_rule = (
            alt.Chart(rule_df)
            .mark_rule(strokeDash=stroke, size=size, color=color)
            .encode(y="y", tooltip=alt.value(None))
        )
        out_chart += h_rule
    return out_chart


def chart_line_guide(
    base_chart: alt.Chart,
    x: int | str | float,
    y: int | float,
    x2: int | str | float,
    y2: int | float,
    stroke: [int, int] = [1, 0],
    size: int = 2,
    color: str = "black",
) -> alt.LayerChart | alt.Chart:
    """基準チャートに2点を結ぶ補助線を重ねる。

    Args:
        base_chart: 補助線を重ねるベースの Altair チャート。
        x: 始点の x 座標。
        y: 始点の y 座標。
        x2: 終点の x 座標。
        y2: 終点の y 座標。
        stroke: 線種を指定する `strokeDash` パターン。
        size: 線の太さ。
        color: 線の色。

    Returns:
        補助線を重ねたチャート。
    """
    rule_df = pl.DataFrame(data={"x": [x, x2], "y": [y, y2]})
    rule_chart = (
        alt.Chart(rule_df)
        .mark_line(strokeDash=stroke, size=size, color=color)
        .encode(x="x", y="y", tooltip=alt.value(None))
    )
    return base_chart + rule_chart
