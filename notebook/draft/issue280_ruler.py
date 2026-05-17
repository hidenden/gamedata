# /// script
# [tool.marimo.display]
# theme = "system"
# ///

import marimo

__generated_with = "0.23.6"
app = marimo.App(width="medium")

with app.setup:
    # 標準ライブラリ
    from datetime import date, datetime

    import marimo as mo
    import altair as alt

    # サードパーティライブラリ
    import polars as pl

    # import polars.selectors as cs
    # プロジェクト内モジュール
    import gamedata as g


@app.function
def chart_rule_xy(base_chart: alt.Chart,
                  x: int|str|float|None = None,
                  y: int|float|None = None,
                  stroke :[int, int] = [1, 0],
                  size: int = 2,
                  color:str = "black") -> alt.LayerChart | alt.Chart:
    if x is None and y is None:
        raise ValueError("x or y must be provided")
    value_x = x if x is not None else 0
    value_y = y if y is not None else 0

    rule_df = pl.DataFrame(data = {"x": [value_x],"y": [value_y],})
    out_chart = base_chart
    if x:
        v_rule = (alt.Chart(rule_df)
                  .mark_rule(strokeDash=stroke, size=size, color=color)
                  .encode(x="x", tooltip=alt.value(None)))
        out_chart += v_rule
    if y:
        h_rule = (alt.Chart(rule_df)
                  .mark_rule(strokeDash=stroke, size=size, color=color)
                  .encode(y="y", tooltip=alt.value(None)))
        out_chart += h_rule
    return out_chart


@app.function
def chart_line_guide(base_chart: alt.Chart,
                  x: int|str|float,
                  y: int|float,
                  x2: int|str|float,
                  y2: int|float,
                  stroke :[int, int] = [1, 0],
                  size: int = 2,
                    color:str = "black") -> alt.LayerChart | alt.Chart:
    rule_df = pl.DataFrame(data = {"x": [x, x2],"y": [y, y2]})
    rule_chart = (alt.Chart(rule_df)
                  .mark_line(strokeDash=stroke, size=size, color=color)
                  .encode(x="x", y="y", tooltip=alt.value(None)))
    return (base_chart + rule_chart)


@app.cell
def _():
    chart1 = g.chart_line_cumulative_delta(
        hw=["NS2", "NSW", "PS5", "3DS", "DS", "GBA", "PS2", "Wii"],
        end=60,
        event_mask=g.EVENT_MASK_MIDDLE,
        mode="week",
        with_point=False,
    )

    return (chart1,)


@app.cell
def _(chart1):
    ov1 = chart_rule_xy(chart1, x=49, stroke=[4, 2], size=4, color="yellow")
    c1 = mo.ui.altair_chart(ov1)
    c1
    return


@app.cell
def _():
    chart2 = g.chart_line_cumulative_delta(
        hw=["NS2", "NSW", "PS5", "3DS", "DS", "GBA", "PS2", "Wii"],
        end=60,
        event_mask=g.EVENT_MASK_MIDDLE,
        mode="week",
        with_point=False,
    )

    return (chart2,)


@app.cell
def _(chart2):
    ov2 = chart_rule_xy(chart2, y=4000000, stroke=[3, 1], size=4, color="purple")
    c2 = mo.ui.altair_chart(ov2)
    c2
    return


@app.cell
def _():
    chart3 = g.chart_line_cumulative_delta(
        hw=["NS2", "NSW", "PS5", "3DS", "DS", "GBA", "PS2", "Wii"],
        end=60,
        event_mask=g.EVENT_MASK_MIDDLE,
        mode="week",
        with_point=False,
    )
    return (chart3,)


@app.cell
def _(chart3):
    ov3 = chart_rule_xy(chart3, x=30, y=4000000, stroke=[3, 1], size=4, color="purple")
    c3 = mo.ui.altair_chart(ov3)
    c3
    return


@app.cell
def _():
    chart4 = g.chart_line_cumulative_delta(
        hw=["NS2", "NSW", "PS5", "3DS", "DS", "GBA", "PS2", "Wii"],
        end=60,
        event_mask=g.EVENT_MASK_MIDDLE,
        mode="week",
        with_point=False,
    )

    return (chart4,)


@app.cell
def _(chart4):
    ov4 = chart_line_guide(chart4, 
                            x=49, y = 5350000, 
                            x2=60, y2=6000000, 
                            stroke=[4, 2], size=4, color="blue")
    c4 = mo.ui.altair_chart(ov4)
    c4
    return


if __name__ == "__main__":
    app.run()
