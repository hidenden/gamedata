import marimo

__generated_with = "0.20.4"
app = marimo.App(width="medium")


@app.cell
def _():
    return


@app.cell
def _():
    ## 週販レポート
    # 標準ライブラリ
    import os
    import sys
    from pathlib import Path
    from datetime import datetime, timedelta

    # サードパーティライブラリ
    import polars as pl
    import polars.selectors as cs

    # プロジェクト内モジュール
    import gamedata as g

    return (g,)


@app.cell
def _(mo):
    mo.md(r"""
    # load_hard_sales
    """)
    return


@app.cell
def _(g):
    df1 = g.load_hard_sales()
    df1
    return (df1,)


@app.cell
def _(mo):
    mo.md(r"""
    # current_report_date
    """)
    return


@app.cell
def _(df1, g):
    g.current_report_date(df1)
    return


@app.cell
def _(mo):
    mo.md(r"""
    # get_hw
    """)
    return


@app.cell
def _(df1, g):
    g.get_hw(df1)
    return


@app.cell
def _(mo):
    mo.md(r"""
    # get_active_hw
    """)
    return


@app.cell
def _(g):
    g.get_active_hw()
    return


@app.cell
def _(mo):
    mo.md(r"""
    # with_units_diff
    """)
    return


@app.cell
def _(df1, g):
    g.with_units_diff(df1)
    return


if __name__ == "__main__":
    app.run()
