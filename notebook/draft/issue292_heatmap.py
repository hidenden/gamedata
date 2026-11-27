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
    mdf = g.monthly_sales_long(df = df_all, hw=["PS5"])
    mdf
    return df_all, mdf


@app.cell
def _(mdf):
    _chart = alt.Chart(mdf).mark_rect().encode(
        x="month:O", y="year:O",
        color="monthly_units:Q"
    )

    _chart
    return


@app.cell
def _(df_all):
    wdf = g.monthly_sales_long(df = df_all, hw=["NSW"])
    return (wdf,)


@app.cell
def _(wdf):
    _chart = alt.Chart(wdf).mark_rect().encode(
        x="month:O", y="year:O",
        color="monthly_units:Q",
    )

    _chart
    return


@app.cell
def _():
    Stype="log"
    return (Stype,)


@app.cell
def _(Stype):
    _c = g.chart_heatmap(hw="NS2", mode="week", scale_scheme="plasma", scale_type=Stype)
    _chart =mo.ui.altair_chart(_c)
    mo.vstack([_chart])
    return


@app.cell
def _():
    _c = g.chart_heatmap(hw="NSW", mode="week", grid=False, scale_type="sqrt")
    _chart =mo.ui.altair_chart(_c)
    mo.vstack([_chart])
    return


@app.cell
def _():
    _c = g.chart_heatmap(hw="PS5", mode="week", grid=False, scale_type="sqrt")
    _chart =mo.ui.altair_chart(_c)
    mo.vstack([_chart])
    return


@app.cell
def _():
    _c = g.chart_heatmap(hw=["NSW", "PS5", "NS2"], mode="month",scale_type="log")
    _chart =mo.ui.altair_chart(_c)
    mo.vstack([_chart])
    return


@app.cell
def _():
    _c = g.chart_heatmap(hw=["NSW", "PS5", "NS2"], mode="month", scale_scheme="plasma", scale_type="log", grid=False)
    _chart =mo.ui.altair_chart(_c)
    mo.vstack([_chart])
    return


if __name__ == "__main__":
    app.run()
