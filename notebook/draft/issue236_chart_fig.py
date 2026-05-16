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
    _cmplist = [("PS5", "PS4"), ("PS5", "PS3")]

    pase_df = g.sales_pase_diffs_long(df_all, cmplist=_cmplist)
    pase_df
    return


@app.cell
def _():
    _cmplist = [("PS5", "PS4"), ("PS5", "PS3"), ("NS2", "NSW")]
    _chart = g.chart_line_pase_diffs(cmplist=_cmplist)
    _mo_chart = mo.ui.altair_chart(_chart)
    mo.vstack([_mo_chart], justify="start")
    return


@app.cell
def _(df_all):
    _cmplist = [("NSW", "PS4"), ("NS2", "PS5")]

    difflib_df = g.cumsum_diffs_long(df_all, cmplist=_cmplist)
    difflib_df
    return


@app.cell
def _():
    from tomlkit.parser import CTRL_CHAR_LIMIT
    _cmplist = [("NSW", "PS4"), ("NS2", "PS5")]
    _chart = g.chart_line_cumsum_diffs(cmplist=_cmplist)
    mo_chart = mo.ui.altair_chart(_chart)
    mo.vstack([mo_chart], justify="start")
    return


if __name__ == "__main__":
    app.run()
