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
    df_annotation: pl.DataFrame = g.load_hard_annotation(True)
    df_annotation
    return (df_annotation,)


@app.cell
def _(df_annotation: pl.DataFrame):
    _dfm = g.summarize_annotation(df_annotation, mode="month")
    _dfm
    return


@app.cell
def _():
    df_all = g.load_hard_sales()
    df_all
    return (df_all,)


@app.cell
def _(df_all):
    _df = g.sales_long(df_all)
    _df = g.join_annotation(_df)
    _df
    return


@app.cell
def _(df_all):
    _df = g.sales_by_delta_long(df_all)
    _df = g.join_annotation(_df, delta=True)
    _df
    return


@app.cell
def _(df_all):
    _df = g.monthly_sales_long(df_all)
    _df = g.join_annotation(_df, mode="month")
    _df
    return


@app.cell
def _():
    return


@app.cell
def _(df_all):
    _df = g.sales_by_delta_long(df_all, mode="month")
    _df = g.join_annotation(_df, delta=True, mode="month")
    _df
    return


if __name__ == "__main__":
    app.run()
