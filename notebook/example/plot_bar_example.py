import marimo

__generated_with = "0.23.6"
app = marimo.App(width="medium")


@app.cell
def calc_cell_01():
    import marimo as mo

    return (mo,)


@app.cell
def calc_cell_02():
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
def sales_cell(g, pl):
    df_all: pl.DataFrame = g.load_hard_sales()
    hw_list = g.get_hw(df_all)
    g.set_dispfunc(func=None)
    return (hw_list,)


@app.cell(hide_code=True)
def md_plot_bar(mo):
    mo.md(r"""
    # plot_bar.py
    """)
    return


@app.cell
def hw_list(hw_list, mo):
    ui_hw = mo.ui.dropdown(options=hw_list, value="PS5", label="ハード")
    ui_begin_date = mo.ui.date(value="2023-01-01", label="開始日")
    ui_end_date = mo.ui.date(value="2026-04-01", label="終了日")

    mo.vstack(items=[ui_hw, ui_begin_date, ui_end_date])
    return ui_begin_date, ui_end_date, ui_hw


@app.cell(hide_code=True)
def md_plot_monthly_bar_by_year(mo):
    mo.md(r"""
    ## plot_monthly_bar_by_year
    """)
    return


@app.cell
def ui_begin_date(g, mo, ui_begin_date, ui_end_date, ui_hw):
    _out = g.plot_monthly_bar_by_year(
        hw=ui_hw.value,
        begin=ui_begin_date.value,
        end=ui_end_date.value)
    mo.vstack(_out)
    return


@app.cell(hide_code=True)
def md_plot_quarterly_bar_by_year(mo):
    mo.md(r"""
    ## plot_quarterly_bar_by_year
    """)
    return


@app.cell
def ui_begin_date_2(g, mo, ui_begin_date, ui_end_date, ui_hw):
    (_fig, _df) = g.plot_quarterly_bar_by_year(
        hw=ui_hw.value,
        begin=ui_begin_date.value,
        end=ui_end_date.value)
    mo.vstack([_fig, _df])
    return


@app.cell(hide_code=True)
def md_plot_monthly_bar_by_hard(mo):
    mo.md(r"""
    ## plot_monthly_bar_by_hard
    """)
    return


@app.cell
def ui_cell(g, mo):
    ui_hws = g.HwSelect(default_list=["NSW", "PS5"])
    ui_hws_widget = ui_hws.widget
    ui_stacked = mo.ui.switch(label="stacked", value=False)
    ui_ticksize = mo.ui.number(start=3, stop=11, value=8, label="label size")
    mo.vstack(items=[ui_hws, ui_stacked, ui_ticksize])
    return ui_hws, ui_hws_widget, ui_stacked, ui_ticksize


@app.cell
def ui_begin_date_3(
    g,
    mo,
    ui_begin_date,
    ui_end_date,
    ui_hws,
    ui_hws_widget,
    ui_stacked,
    ui_ticksize,
):
    ui_hws_widget
    (_fig, _df) = g.plot_monthly_bar_by_hard(
        hw=ui_hws.value,
        begin=ui_begin_date.value,
        end=ui_end_date.value,
        ticklabelsize=ui_ticksize.value,
        stacked=ui_stacked.value)
    mo.vstack([_fig, _df])
    return


@app.cell(hide_code=True)
def md_plot_quarterly_bar_by_hard(mo):
    mo.md(r"""
    ## plot_quarterly_bar_by_hard
    """)
    return


@app.cell
def ui_begin_date_4(
    g,
    mo,
    ui_begin_date,
    ui_end_date,
    ui_hws,
    ui_hws_widget,
    ui_stacked,
    ui_ticksize,
):
    ui_hws_widget
    (_fig, _df) = g.plot_quarterly_bar_by_hard(
        hw=ui_hws.value,
        begin=ui_begin_date.value,
        end=ui_end_date.value,
        ticklabelsize=ui_ticksize.value,
        stacked=ui_stacked.value)

    mo.vstack([_fig, _df])
    return


@app.cell(hide_code=True)
def md_plot_yearly_bar_by_hard(mo):
    mo.md(r"""
    ## plot_yearly_bar_by_hard
    """)
    return


@app.cell
def ui_begin_date_5(
    g,
    mo,
    ui_begin_date,
    ui_end_date,
    ui_hws,
    ui_hws_widget,
    ui_stacked,
    ui_ticksize,
):
    ui_hws_widget
    (_fig, _df) = g.plot_yearly_bar_by_hard(
        hw=ui_hws.value,
        begin=ui_begin_date.value,
        end=ui_end_date.value,
        ticklabelsize=ui_ticksize.value,
        stacked=ui_stacked.value)
    mo.vstack([_fig, _df])
    return


@app.cell(hide_code=True)
def md_plot_monthly_bar_by_hard_year(mo):
    mo.md(r"""
    ## plot_monthly_bar_by_hard_year
    """)
    return


@app.cell
def ui_cell_2(mo):
    ui_hy_number = mo.ui.number(2, stop=5, value=2, label="比較対象の数")
    ui_hy_number
    return


@app.cell
def hw_list_2(hw_list, mo):
    drop1 = mo.ui.dropdown(options=hw_list, label="HW")
    num1 = mo.ui.number(start=2001, stop=2026, label="年", value=2025)
    drop2 = mo.ui.dropdown(options=hw_list, label="HW")
    num2 = mo.ui.number(start=2001, stop=2026, label="年", value=2025)

    mo.vstack(
    [mo.hstack([drop1, num1], justify="start"),
    mo.hstack([drop2, num2], justify="start")]
    )
    return drop1, drop2, num1, num2


@app.cell
def drop1(drop1):
    print(drop1.value)
    return


@app.cell
def drop1_2(drop1, drop2, num1, num2):
    # hard_yearsから hwyのtupleの配列に変換する
    hwy_list = [(drop1.value, num1.value), (drop2.value, num2.value)]
    hwy_list
    return


@app.cell
def plot_cell(g, mo):
    _hwy_list = [('NSW', 2025), ('PS5', 2025)]

    mo.vstack(g.plot_monthly_bar_by_hard_year(hwy=_hwy_list))
    return


@app.cell(hide_code=True)
def md_plot_quarterly_bar_by_hard_year(mo):
    mo.md(r"""
    ## plot_quarterly_bar_by_hard_year
    """)
    return


@app.cell
def plot_cell_2(g, mo):
    _hwy_list = [('NSW', 2025), ('PS5', 2025)]

    (_fig, _df) = g.plot_quarterly_bar_by_hard_year(hwy=_hwy_list)
    mo.vstack([_fig, _df])
    return


@app.cell(hide_code=True)
def md_plot_yearly_bar_by_month(mo):
    mo.md(r"""
    ## plot_yearly_bar_by_month
    """)
    return


@app.cell
def ui_cell_3(mo):
    ui_month_num = mo.ui.number(start=1, stop=12, value=12)
    ui_month_num
    return (ui_month_num,)


@app.cell
def ui_begin_date_6(
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
def md_plot_delta_yearly_bar(mo):
    mo.md(r"""
    ## plot_delta_yearly_bar
    """)
    return


@app.cell
def ui_cell_4(mo):
    ui_delta_range = mo.ui.range_slider(start=0, stop=15, step=1, value=[0, 10], full_width=True)
    ui_delta_range
    return (ui_delta_range,)


@app.cell
def ui_delta_range(g, mo, ui_delta_range, ui_hws, ui_hws_widget):
    ui_hws_widget
    (_fig, _df) = g.plot_delta_yearly_bar(hw=ui_hws.value,
        delta_begin=ui_delta_range.value[0],
        delta_end=ui_delta_range.value[1]
    )
    mo.vstack([_fig, _df])
    return


@app.cell(hide_code=True)
def md_plot_maker_share_bar(mo):
    mo.md(r"""
    ## plot_maker_share_bar
    """)
    return


@app.cell
def ui_cell_5(mo):
    ui_begin_year = mo.ui.number(start=2001, stop=2026, value=2015)
    ui_end_year = mo.ui.number(start=2001, stop=2026, value=2026)
    return ui_begin_year, ui_end_year


@app.cell
def ui_begin_year(date, g, mo, ui_begin_year, ui_end_year):
    _begin = date(ui_begin_year.value, 1, 1)
    _end = date(year=ui_end_year.value, month=12, day=31)
    (_fig, _) = g.plot_maker_share_bar(begin=_begin, end=_end)
    mo.vstack(items=[ui_begin_year, ui_end_year, _fig])
    return


@app.cell(hide_code=True)
def md_plot_pie(mo):
    mo.md(r"""
    # plot_pie.py
    """)
    return


@app.cell(hide_code=True)
def md_plot_maker_share_pie(mo):
    mo.md(r"""
    ## plot_maker_share_pie
    """)
    return


@app.cell
def ui_cell_6(mo):
    pie_begin = mo.ui.number(start=2001, stop=2026, value=2023)
    pie_end = mo.ui.number(start=2001, stop=2026, value=2026)
    return pie_begin, pie_end


@app.cell
def pie_begin(g, mo, pie_begin, pie_end):
    mo.vstack([
        pie_begin, pie_end,
        g.plot_maker_share_pie(begin_year=pie_begin.value, end_year=pie_end.value)[0]
        ])
    return


if __name__ == "__main__":
    app.run()
