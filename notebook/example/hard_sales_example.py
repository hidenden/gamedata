import marimo

__generated_with = "0.23.6"
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
    from datetime import datetime, timedelta, date

    # サードパーティライブラリ
    import polars as pl
    # import polars.selectors as cs

    # プロジェクト内モジュール
    import gamedata as g

    return date, g, pl


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
def _(df_all: "pl.DataFrame", pl):
    ns_df = df_all.filter(
        pl.col("hw") == "NS2").filter(
            pl.col("index_week") <= 45).filter(
                pl.col("index_week") > 40)
    ns_df
    return


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
def _(df_all: "pl.DataFrame", g):
    hw_list = g.get_hw(df_all)
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
    number = mo.ui.number(start=7, stop=3650, step=1, value=365, label="Active HWと判定する範囲(日数)")
    number
    return (number,)


@app.cell
def _(g, number):
    _hw_active_list = g.get_active_hw(days = number.value)
    _hw_active_list
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## derived columns
    """)
    return


@app.cell
def _(df_all: "pl.DataFrame", pl):
    df_diff: pl.DataFrame = df_all
    df_diff
    return (df_diff,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## rolling mean columns
    """)
    return


@app.cell
def _(df_all: "pl.DataFrame", pl):
    _rolling_df = df_all.select(pl.col("report_date"), 
    pl.col("hw"), pl.col("units"), 
    pl.col("ma4w"), pl.col("ma13w"), pl.col("ma52w"))
    _rolling_df
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## add_week_number
    """)
    return


@app.cell
def _(df_diff: "pl.DataFrame", g, pl):
    _df2: pl.DataFrame = g.add_week_number(df_diff)
    _df2.columns
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
    _df_filtered = g.date_filter(df_all, begin_date.value, end_date.value)
    _df_filtered
    return


@app.cell
def _(date, mo):
    begin_date = mo.ui.date(label="開始日", value=date(2017,3,3))
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
    maker_mode = mo.ui.switch(label="メーカー別集計", value=False)
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
def _(date, hw_list, mo):
    hw_options = hw_list
    hw_multiselect = mo.ui.multiselect(options=hw_options, label="ハードウェアを選択してください", value=['NSW', "PS5", "NS2"])
    extract_date = mo.ui.date(label="抽出日を選択してください", value=date(2026, 3, 25))

    mo.vstack([hw_multiselect, extract_date], justify="start", align="stretch")
    return extract_date, hw_multiselect


@app.cell
def _(df_all: "pl.DataFrame", extract_date, g, hw_multiselect):
    g.extract_by_date(df_all, target_date = extract_date.value, hw = hw_multiselect.value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## extract_latest
    """)
    return


@app.cell
def _(mo):
    # 数値を入力する
    latest_weeks = mo.ui.number(start=1, stop=12, step=1, label="週数を入力してください")
    latest_weeks
    return (latest_weeks,)


@app.cell
def _(df_all: "pl.DataFrame", g, latest_weeks):
    g.extract_latest(df_all, weeks = latest_weeks.value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## extract_total
    """)
    return


@app.cell
def _(mo):
    compact_flag = mo.ui.checkbox(label="compactモード", value=False)
    return (compact_flag,)


@app.cell
def _(compact_flag, df_all: "pl.DataFrame", g, mo):
    _df = g.extract_total(df_all, compact = compact_flag.value)
    mo.vstack([
        compact_flag,
        _df,

    ], justify="start", align="stretch")    
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## hard_sales_summary
    """)
    return


@app.cell
def _(g):
    hwselect = g.HwSelect(force_any = True, default_list = ["NS2"])
    hw_widget = hwselect.widget
    return hw_widget, hwselect


@app.cell
def _(df_all: "pl.DataFrame", g, hw_widget, hwselect, mo):
    hw_widget
    _summarys = g.hard_sales_summary(df_all, hw = hwselect.value)
    mo.vstack([
        hwselect,
        _summarys
    ], justify="start", align="stretch")    
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## maker_sales_summary
    """)
    return


@app.cell
def _(g):
    maker_select = g.MakerSelect(default_list = ["Nintendo"], force_any = True)
    maker_widget = maker_select.widget
    return maker_select, maker_widget


@app.cell
def _(df_all: "pl.DataFrame", g, maker_select, maker_widget, mo):
    maker_widget
    _maker_summary = g.maker_sales_summary(df_all, makers = maker_select.value)
    mo.vstack([
        maker_select,
        _maker_summary
    ], justify="start", align="stretch")
    return


if __name__ == "__main__":
    app.run()
