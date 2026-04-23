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
    hw_list = g.get_hw(df_all)
    return df_all, hw_list


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # hard_sales_pivot
    """)
    return


@app.cell
def _(hw_list, mo):
    hw_multiselect = mo.ui.multiselect(options=hw_list, 
        value=['NSW', "PS5", "NS2"], label="ハードウェアを選択してください")
    return (hw_multiselect,)


@app.cell
def _(date, mo):
    begin_date = mo.ui.date(label="開始日", value=date(2017,3,3))
    end_date = mo.ui.date(label="終了日")
    date_select = mo.hstack([begin_date, end_date], justify="start",align="stretch")
    return begin_date, date_select, end_date


@app.cell
def _(mo):
    mo.md(r"""
    ## pivot_sales
    """)
    return


@app.cell
def _(
    begin_date,
    date_select,
    df_all: "pl.DataFrame",
    end_date,
    g,
    hw_multiselect,
    mo,
):
    _df = g.pivot_sales(df_all, begin=begin_date.value, end=end_date.value, hw=hw_multiselect.value)
    mo.vstack([date_select, hw_multiselect, _df], justify="start", align="stretch")
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
def _(mo):
    mode_dropdown = mo.ui.dropdown(options = ["week", "month", "year"], 
        value="week", label="集計単位を選択してください")
    mode_dropdown
    return (mode_dropdown,)


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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## pivot_sales_by_delta
    """)
    return


@app.cell
def _(mo):
    delta_begin = mo.ui.number(start=0, label="経過期間の最小値", value=0)
    delta_end = mo.ui.number(start=1, label="経過期間の最大値", value=52)

    mo.vstack([delta_begin, delta_end], justify="start", align="stretch")
    return delta_begin, delta_end


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
def _(date, hw_list, mo):
    _hwnum : int = 3
    _init_hw = ["NSW", "NS2", "PS5"]
    _init_date = [date(2017,3,3), 
        date(2025,6,5), date(2020,11,15)]

    hw_periods_ui = mo.ui.array([
        mo.ui.array([
            mo.ui.dropdown(options=hw_list, label=f"{_i+1}番目のハードウェア", value=_init_hw[_i]),
            mo.ui.date(label=f"{_i+1}番目の集計開始日", value=_init_date[_i])
        ]) for _i in range(_hwnum)
    ])
    period_end = mo.ui.number(start=1, label="期間数", value=52)

    ui_items  = [mo.hstack(_hwui, justify="start") for _hwui in hw_periods_ui]
    ui_items.append(period_end)

    return hw_periods_ui, period_end, ui_items


@app.cell
def _(df_all: "pl.DataFrame", g, hw_periods_ui, mo, period_end, ui_items):
    hw_periods = [
        {
            "hw": _ui[0],
            "begin": _ui[1],
            "label": f"{_ui[0]} {_ui[1]}"    
        } for _ui in hw_periods_ui.value
    ]

    _df = g.pivot_sales_with_offset(df_all, hw_periods=hw_periods, end=period_end.value)
    mo.vstack(items=[*ui_items , _df])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## cumsum_diff
    """)
    return


@app.cell
def _(df_all: "pl.DataFrame", g):
    _cmplist = [("NSW", "PS4"), ("NS2", "PS5")]
    g.cumsum_diffs(df_all, cmplist=_cmplist)
    return


if __name__ == "__main__":
    app.run()
