import marimo

__generated_with = "0.23.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    # 標準ライブラリ
    import os
    import sys
    # from pathlib import Path
    from datetime import datetime, timedelta

    # サードパーティライブラリ
    import polars as pl
    # import polars.selectors as cs

    # プロジェクト内モジュール
    import gamedata as g

    return g, pl


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # hard_sales
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## load_hard_sales
    """)
    return


@app.cell
def _(g, pl):
    df_all: pl.DataFrame = g.load_hard_sales()
    df_all
    return (df_all,)


@app.cell
def _(mo):
    mo.md(r"""
    ## current_report_date
    """)
    return


@app.cell
def _(df_all: "pl.DataFrame", g):
    report_date = g.current_report_date(df_all)
    report_date
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## get_hw
    """)
    return


@app.cell
def _():
    return


@app.cell
def _(df_all: "pl.DataFrame", g):
    hw_list = g.get_hw(df_all)
    hw_list
    return (hw_list,)


@app.cell
def _(mo):
    mo.md(r"""
    ## get_active_hw
    """)
    return


@app.cell
def _(mo):
    # 数値を入力する
    number = mo.ui.number(start=7, stop=3650, step=1, label="数値を入力してください")
    number
    return (number,)


@app.cell
def _(g, number):
    hw_active_list = g.get_active_hw(days = number.value)
    hw_active_list
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## with_units_diff
    """)
    return


@app.cell
def _(df_all: "pl.DataFrame", g, pl):
    df_diff: pl.DataFrame = g.with_units_diff(df_all)
    df_diff
    return (df_diff,)


@app.cell
def _(df_diff: "pl.DataFrame", g, pl):
    df2: pl.DataFrame = g.add_week_number(df_diff)
    df2.columns
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # hard_sales_filter
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## data_filter
    """)
    return


@app.cell
def _(begin_date, df_all: "pl.DataFrame", end_date, g):
    df_filtered = g.date_filter(df_all, begin_date.value, end_date.value)
    df_filtered
    return


@app.cell
def _(mo):
    begin_date = mo.ui.date(label="開始日")
    end_date = mo.ui.date(label="終了日")
    # mo.hstack([begin_date, end_date], justify="start",
    # align="stretch")
    (begin_date, end_date)
    return begin_date, end_date


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## weekly_sales
    """)
    return


@app.cell
def _(begin_date, df_all: "pl.DataFrame", end_date, g, maker_mode):
    g.weekly_sales(df_all, begin_date.value, end_date.value, maker_mode.value)
    return


@app.cell
def _(mo):
    maker_mode = mo.ui.checkbox(label="メーカー別集計")
    maker_mode
    return (maker_mode,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## monthly_sales
    """)
    return


@app.cell
def _(begin_date, df_all: "pl.DataFrame", end_date, g, maker_mode):
    g.monthly_sales(df_all, begin_date.value, end_date.value, maker_mode.value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## quartely_sales
    """)
    return


@app.cell
def _(begin_date, df_all: "pl.DataFrame", end_date, g, maker_mode):
    g.quarterly_sales(df_all, begin_date.value, end_date.value, maker_mode.value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## yarly_sales
    """)
    return


@app.cell
def _(begin_date, df_all: "pl.DataFrame", end_date, g, maker_mode):
    g.yearly_sales(df_all, begin_date.value, end_date.value, maker_mode.value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## yarly_maker_sales
    """)
    return


@app.cell
def _(begin_date, df_all: "pl.DataFrame", end_date, g):
    g.yearly_maker_sales(df_all, begin_date.value, end_date.value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## delta_yearly_sales
    """)
    return


@app.cell
def _(df_all: "pl.DataFrame", g):
    g.delta_yearly_sales(df_all)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # hard_sales_extract
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## extract_week_reached_units
    """)
    return


@app.cell
def _(mo):
    # 数値を入力する
    threshold_number = mo.ui.number(start=1000000, stop=40000000, step=500000, label="しきい値を入力してください")
    threshold_number
    return (threshold_number,)


@app.cell
def _(df_all: "pl.DataFrame", g, threshold_number):
    g.extract_week_reached_units(df_all, threshold_number.value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## extract_by_date
    """)
    return


@app.cell
def _(df_all: "pl.DataFrame", extract_date, g, hw_multiselect):
    g.extract_by_date(df_all, target_date = extract_date.value, hw = hw_multiselect.value)
    return


@app.cell
def _(hw_list, mo):
    hw_options = hw_list
    hw_multiselect = mo.ui.multiselect(options=hw_options, label="ハードウェアを選択してください")
    extract_date = mo.ui.date(label="抽出日を選択してください")

    mo.vstack([hw_multiselect, extract_date], justify="start", align="stretch")


    return extract_date, hw_multiselect


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## extract_latest
    """)
    return


@app.cell
def _(df_all: "pl.DataFrame", g, latest_weeks):
    g.extract_latest(df_all, weeks = latest_weeks.value)
    return


@app.cell
def _(mo):
    # 数値を入力する
    latest_weeks = mo.ui.number(start=1, stop=12, step=1, label="週数を入力してください")
    latest_weeks
    return (latest_weeks,)


if __name__ == "__main__":
    app.run()
