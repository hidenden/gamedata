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
    g.set_dispfunc(func=None)
    return (hw_list,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # plot_bar.py
    """)
    return


@app.cell
def _(hw_list, mo):
    ui_hw = mo.ui.dropdown(options=hw_list, value="PS5", label="ハード")
    ui_begin_date = mo.ui.date(value="2023-01-01", label="開始日")
    ui_end_date = mo.ui.date(value="2026-04-01", label="終了日")

    mo.vstack(items=[ui_hw, ui_begin_date, ui_end_date])
    return ui_begin_date, ui_end_date, ui_hw


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## plot_monthly_bar_by_year
    """)
    return


@app.cell
def _(g, mo, ui_begin_date, ui_end_date, ui_hw):
    _out = g.plot_monthly_bar_by_year(
        hw=ui_hw.value,
        begin=ui_begin_date.value,
        end=ui_end_date.value)
    mo.vstack(_out)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## plot_quarterly_bar_by_year
    """)
    return


@app.cell
def _(g, mo, ui_begin_date, ui_end_date, ui_hw):
    (_fig, _df) = g.plot_quarterly_bar_by_year(
        hw=ui_hw.value,
        begin=ui_begin_date.value,
        end=ui_end_date.value)
    mo.vstack([_fig, _df])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## plot_monthly_bar_by_hard
    """)
    return


@app.cell
def _(hw_list, mo):

    ui_hws = mo.ui.multiselect(options=hw_list, value=["NSW", "PS5"])
    ui_stacked = mo.ui.checkbox(label="stacked")
    ui_ticksize = mo.ui.number(start=3, stop=11, value=8, label="label size")
    mo.vstack(items=[ui_hws, ui_stacked, ui_ticksize])

    return ui_hws, ui_stacked, ui_ticksize


@app.cell
def _(g, mo, ui_begin_date, ui_end_date, ui_hws, ui_stacked, ui_ticksize):
    (_fig, _df) = g.plot_monthly_bar_by_hard(
        hw=ui_hws.value,
        begin=ui_begin_date.value,
        end=ui_end_date.value,
        ticklabelsize=ui_ticksize.value,
        stacked=ui_stacked.value)
    mo.vstack([_fig, _df])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## plot_quarterly_bar_by_hard
    """)
    return


@app.cell
def _(g, mo, ui_begin_date, ui_end_date, ui_hws, ui_stacked, ui_ticksize):
    (_fig, _df) = g.plot_quarterly_bar_by_hard(
        hw=ui_hws.value,
        begin=ui_begin_date.value,
        end=ui_end_date.value,
        ticklabelsize=ui_ticksize.value,
        stacked=ui_stacked.value)

    mo.vstack([_fig, _df])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## plot_yearly_bar_by_hard
    """)
    return


@app.cell
def _(g, mo, ui_begin_date, ui_end_date, ui_hws, ui_stacked, ui_ticksize):
    (_fig, _df) = g.plot_yearly_bar_by_hard(
        hw=ui_hws.value,
        begin=ui_begin_date.value,
        end=ui_end_date.value,
        ticklabelsize=ui_ticksize.value,
        stacked=ui_stacked.value)
    mo.vstack([_fig, _df])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## plot_monthly_bar_by_hard_year
    """)
    return


@app.cell
def _(mo):
    ui_hy_number = mo.ui.number(2, stop=5, value=2, label="比較対象の数")
    ui_hy_number
    return (ui_hy_number,)


@app.cell
def _(hw_list, mo, ui_hy_number):
    hwy_ui = mo.ui.array([
        mo.ui.array([
            mo.ui.dropdown(options=hw_list, label="HW"),
            mo.ui.number(start=2001, stop=2026, label="年", value=2025)
        ]) for _i in range(ui_hy_number.value)
        ]
    )
    mo.vstack([mo.hstack(hwy_ui_line, justify="start") for hwy_ui_line in hwy_ui])
    return (hwy_ui,)


@app.cell
def _(hwy_ui):
    # hard_yearsから hwyのtupleの配列に変換する
    hwy_list = [(hy[0], hy[1]) for hy in hwy_ui.value if hy[0]]
    return (hwy_list,)


@app.cell
def _(g, hwy_list, mo):
    mo.vstack(g.plot_monthly_bar_by_hard_year(hwy=hwy_list))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## plot_quarterly_bar_by_hard_year
    """)
    return


@app.cell
def _(g, hwy_list, mo):
    (_fig, _df) = g.plot_quarterly_bar_by_hard_year(hwy=hwy_list)
    mo.vstack([_fig, _df])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## plot_yearly_bar_by_month
    """)
    return


@app.cell
def _(mo):
    ui_month_num = mo.ui.number(start=1, stop=12, value=12)
    ui_month_num
    return (ui_month_num,)


@app.cell
def _(
    g,
    mo,
    ui_begin_date,
    ui_end_date,
    ui_month_num,
    ui_stacked,
    ui_ticksize,
):
    (_fig, _df) = g.plot_yearly_bar_by_month(
        month=ui_month_num.value, 
        begin=ui_begin_date.value,
        end=ui_end_date.value,
        stacked=ui_stacked.value,
        ticklabelsize=ui_ticksize.value
        )
    mo.vstack([_fig, _df])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## plot_delta_yearly_bar
    """)
    return


@app.cell
def _(mo):
    ui_delta_range = mo.ui.range_slider(start=0, stop=15, step=1, value=[0, 10], full_width=True)
    ui_delta_range
    return (ui_delta_range,)


@app.cell
def _(g, mo, ui_delta_range, ui_hws):
    (_fig, _df) = g.plot_delta_yearly_bar(hw=ui_hws.value,
        delta_begin=ui_delta_range.value[0],
        delta_end=ui_delta_range.value[1]
    )
    mo.vstack([_fig, _df])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## plot_maker_share_bar
    """)
    return


@app.cell
def _(mo):
    ui_begin_year = mo.ui.number(start=2001, stop=2026, value=2015)
    ui_end_year = mo.ui.number(start=2001, stop=2026, value=2026)
    return ui_begin_year, ui_end_year


@app.cell
def _(date, g, mo, ui_begin_year, ui_end_year):
    _begin = date(ui_begin_year.value, 1, 1)
    _end = date(year=ui_end_year.value, month=12, day=31)
    (_fig, _) = g.plot_maker_share_bar(begin=_begin, end=_end)
    mo.vstack(items=[ui_begin_year, ui_end_year, _fig])

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # plot_pie.py
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## plot_maker_share_pie
    """)
    return


@app.cell
def _(mo):
    pie_begin = mo.ui.number(start=2001, stop=2026, value=2023)
    pie_end = mo.ui.number(start=2001, stop=2026, value=2026)
    return pie_begin, pie_end


@app.cell
def _(g, mo, pie_begin, pie_end):
    mo.vstack([
        pie_begin, pie_end,
        g.plot_maker_share_pie(begin_year=pie_begin.value, end_year=pie_end.value)[0]
        ])
    return


if __name__ == "__main__":
    app.run()
