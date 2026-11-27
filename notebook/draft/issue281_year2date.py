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
    df_all = g.load_hard_sales()
    return (df_all,)


@app.cell
def _(df_all):
    df_all
    return


@app.cell
def _(df_all):
    ydf = g.yearly_cumulative_by_hwy_long(df_all,
            hw_years=[("NS2", 2026), ("NSW", 2026), ("PS5", 2026)],
    )
    return (ydf,)


@app.cell
def _(ydf):
    ydf
    return


@app.cell
def _():
    _chart = g.chart_line_ycumulative_by_hw_year(
            hw_years=[("NS2", 2026), ("NSW", 2018), ("NSW", 2019)],
            multi_line=True,
    )
    mo.ui.altair_chart(_chart)
    return


@app.cell
def _():
    _chart = g.chart_line_ycumulative_by_hw_year(
            hw_years=[("PS5", 2024), ("PS5", 2025), ("PS5", 2026)],
            annotation_level=30,
    )
    mo.ui.altair_chart(_chart)
    return


@app.cell
def _(df_all):
    _df = g.yearly_cumulative_long(df_all, year=2025)
    _df
    return


@app.cell
def _():
    _chart = g.chart_line_ycumulative(year=2026, multi_line=True, annotation_level=15)
    mo.ui.altair_chart(_chart)
    return


if __name__ == "__main__":
    app.run()
