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


@app.cell
def _():
    an_df = g.load_hard_annotation(True)
    df_all = g.load_hard_sales(True)
    return


@app.cell
def _():
    _chart = g.chart_line_sales(
        hw=["NS2"],  ymax=750000,
        size=(1920, 480),
        padding_begin=1, padding_end=2,
        value_label=True,
        annotation_level=35,
    )

    _weekly_chart = mo.ui.altair_chart(_chart)
    mo.hstack(items=[_weekly_chart], justify="start", wrap=True)
    return


@app.cell
def _():
    hw_periods = [
        { "hw" : "PS5", "begin": datetime(2020,11,15), "label": "PS5発売後1年"},
        { "hw" : "NSW", "begin": datetime(2017,3,3), "label": "Switch発売後1年"},
        { "hw" : "NS2", "begin": datetime(2025,6,5), "label": "Switch2発売後1年"},
        { "hw" : "PS4", "begin": datetime(2014,2,22), "label": "PS4発売後1年"},
        { "hw" : "3DS", "begin": datetime(2011,2,26), "label": "3DS発売後1年"},
        { "hw" : "Wii", "begin": datetime(2006,12,2), "label": "Wii発売後1年"},
    ]

    g.chart_line_weekly_by_hw_date(
        hw_periods=hw_periods,
        end=52,
        size=(3800, 1024),
        ymax=750000,
        value_label = True,
    )
    return


if __name__ == "__main__":
    app.run()
