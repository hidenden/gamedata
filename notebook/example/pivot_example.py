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
    from datetime import datetime, timedelta, date

    # サードパーティライブラリ
    import polars as pl
    # import polars.selectors as cs

    # プロジェクト内モジュール
    import gamedata as g

    return date, g, pl


@app.cell
def _(g, pl):
    df_all: pl.DataFrame = g.load_hard_sales()
    return (df_all,)


@app.cell
def _(df_all: "pl.DataFrame", g):
    hw_list = g.get_hw(df_all)
    return (hw_list,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # hard_sales_pivot
    """)
    return


@app.cell
def _(hw_list, mo):
    hw_options = hw_list
    hw_multiselect = mo.ui.multiselect(options=hw_options, 
        value=['NSW', "PS5", "NS2"], label="ハードウェアを選択してください")
    return (hw_multiselect,)


@app.cell
def _(date, hw_multiselect, mo):
    begin_date = mo.ui.date(label="開始日", value=date(2017,3,3))
    end_date = mo.ui.date(label="終了日")
    left = mo.hstack([begin_date, end_date], justify="start",align="stretch")
    mo.vstack([left, hw_multiselect], justify="start", align="stretch")
    return begin_date, end_date


@app.cell
def _(mo):
    mo.md(r"""
    ## pivot_sales
    """)
    return


@app.cell
def _(begin_date, df_all: "pl.DataFrame", end_date, g, hw_multiselect):
    g.pivot_sales(df_all, begin=begin_date.value, end=end_date.value, hw=hw_multiselect.value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## pivot_monthly_sales
    """)
    return


@app.cell
def _(begin_date, df_all: "pl.DataFrame", end_date, g, hw_multiselect):
    g.pivot_monthly_sales(df_all, begin=begin_date.value, end=end_date.value, hw=hw_multiselect.value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## pivot_quarterly_sales
    """)
    return


@app.cell
def _(begin_date, df_all: "pl.DataFrame", end_date, g, hw_multiselect):
    g.pivot_quarterly_sales(df_all, begin=begin_date.value, end=end_date.value, hw=hw_multiselect.value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## pivot_yearly_sales
    """)
    return


@app.cell
def _(begin_date, df_all: "pl.DataFrame", end_date, g, hw_multiselect):
    g.pivot_yearly_sales(df_all, begin=begin_date.value, end=end_date.value, hw=hw_multiselect.value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## pivot_cumulative_sales
    """)
    return


@app.cell
def _(
    begin_date,
    df_all: "pl.DataFrame",
    end_date,
    g,
    hw_multiselect,
    mode_dropdown,
):
    g.pivot_cumulative_sales(df_all, begin=begin_date.value, end=end_date.value, hw=hw_multiselect.value,
    mode=mode_dropdown.value)
    return


@app.cell
def _(mo):
    mode_dropdown = mo.ui.dropdown(options = ["week", "month", "year"], 
        value="week", label="集計単位を選択してください")
    mode_dropdown
    return (mode_dropdown,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## pivot_sales_by_delta
    """)
    return


@app.cell
def _(
    delta_begin,
    delta_end,
    df_all: "pl.DataFrame",
    g,
    hw_multiselect,
    mode_dropdown,
):
    g.pivot_sales_by_delta(df_all, begin=delta_begin.value, 
        end=delta_end.value, 
        hw=hw_multiselect.value,
        mode=mode_dropdown.value)
    return


@app.cell
def _(mo):
    delta_begin = mo.ui.number(start=0, label="経過期間の最小値", value=0)
    delta_end = mo.ui.number(start=1, label="経過期間の最大値", value=52)

    mo.vstack([delta_begin, delta_end], justify="start", align="stretch")
    return delta_begin, delta_end


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## pivot_cumulative_sales_by_delta
    """)
    return


@app.cell
def _(
    delta_begin,
    delta_end,
    df_all: "pl.DataFrame",
    g,
    hw_multiselect,
    mode_dropdown,
):
    g.pivot_cumulative_sales_by_delta(df_all, begin=delta_begin.value, 
        end=delta_end.value, 
        hw=hw_multiselect.value,
        mode=mode_dropdown.value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## pivot_maker
    """)
    return


@app.cell
def _(begin_date, df_all: "pl.DataFrame", end_date, g):
    g.pivot_maker(df_all, 
        begin_year=begin_date.value.year, 
        end_year=end_date.value.year)

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## pivot_sales_with_offset
    """)
    return


@app.cell
def _(hw_list, mo):
    hw_periods_num : int = 3
    hw_periods_ui = []

    for i in range(hw_periods_num):
        ui_elements = {}    # HWを選択するdropdown
        ui_elements["hw_dropdown"] = mo.ui.dropdown(options=hw_list, label=f"{i+1}番目のハードウェア")
        # 集計開始日の選択
        ui_elements["begin_date"] = mo.ui.date(label=f"{i+1}番目の集計開始日")
        hw_periods_ui.append(ui_elements)

    period_end = mo.ui.number(start=1, label="期間数", value=52)

    ui_items = [mo.hstack([ui["hw_dropdown"], ui["begin_date"]], justify="start", align="stretch") for ui in hw_periods_ui]
    ui_items.append(period_end)
    mo.vstack(
        ui_items,
        justify="start", align="stretch"
    )
    return hw_periods_ui, period_end


@app.cell
def _(df_all: "pl.DataFrame", g, hw_periods_ui, period_end):
    hw_periods = []

    for ii, ui in enumerate(hw_periods_ui):
        hw = ui["hw_dropdown"].value
        bd = ui["begin_date"].value
        lv = f"{hw} {bd}"
        period_element = {
            "hw": hw,
            "begin": bd,
            "label": lv    
        }
        hw_periods.append(period_element)

    g.pivot_sales_with_offset(df_all, hw_periods=hw_periods, end=period_end.value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## cumsum_diff
    """)
    return


@app.cell
def _(df_all: "pl.DataFrame", g):
    cmplist = [("NSW", "PS4"), ("NS2", "PS5")]
    g.cumsum_diffs(df_all, cmplist=cmplist)

    return


if __name__ == "__main__":
    app.run()
