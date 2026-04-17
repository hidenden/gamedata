import marimo

__generated_with = "0.23.1"
app = marimo.App(width="medium")


@app.cell
def _():
    return


@app.cell
def _():
    import marimo as mo


    return (mo,)


@app.cell
def _():
    # 標準ライブラリ
    import os
    import sys
    from pathlib import Path
    from datetime import datetime, timedelta, date

    # サードパーティライブラリ
    import polars as pl
    import polars.selectors as cs

    # プロジェクト内モジュール
    import gamedata as g

    return date, g


@app.cell
def _(g):
    df_all = g.load_hard_sales()
    df_all
    return (df_all,)


@app.cell
def _(date, mo):
    # marimoを使ってカレンダーから日付を選択入力するためのウィジェットを表示する
    # カレンダー入力
    start_date = mo.ui.date(
        label="Start Date",
        value=date(2000, 1, 1),
    )
    end_date = mo.ui.date(
        label="End Date",
        value=date(2026, 4, 3),
    )
    mo.vstack([start_date, end_date])
    return end_date, start_date


@app.cell
def _(df_all, end_date, g, start_date):
    filtered_df = g.date_filter(df_all, start_date.value, end_date.value)
    filtered_df
    return


if __name__ == "__main__":
    app.run()
