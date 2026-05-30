import marimo

__generated_with = "0.23.6"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo

    # 標準ライブラリ
    from datetime import date, datetime, timedelta

    # サードパーティライブラリ
    import polars as pl
    # import polars.selectors as cs

    # プロジェクト内モジュール
    import gamedata as g

    g.set_dispfunc(func=None)


@app.cell
def ui_hw_select_01():
    # HW select widget
    hw_select = g.HwSelect(default_list=["NSW", "PS5"], force_any=True)
    hw_widget = hw_select.widget

    # Stack指定
    stack_widget = mo.ui.switch(label="Stack mode", value=False)
    return hw_select, hw_widget, stack_widget


@app.cell
def hw_select(hw_select, hw_widget, stack_widget):
    hw_widget
    hw_list = hw_select.value
    _chart = g.chart_bar_sales(
        hw=hw_list, begin=datetime(2000, 1, 1), stacked=stack_widget.value, mode="year"
    )
    _mo_chart = mo.ui.altair_chart(_chart)
    mo.vstack([hw_select, stack_widget, _mo_chart, _mo_chart.dataframe])
    return


@app.cell
def ui_hw_select_area_02():
    # HW select widget
    hw_select_area = g.HwSelect(default_list=[])
    hw_widget_area = hw_select_area.widget
    return hw_select_area, hw_widget_area


@app.cell
def hw_select_area(hw_select_area, hw_widget_area):
    hw_widget_area
    _chart = g.chart_bar_sales(
        hw=hw_select_area.value,
        mode="year",
        begin=datetime(2001, 1, 1),
        stacked=True,
    )
    mo.vstack([hw_select_area, _chart])
    return


@app.cell
def ui_year_end_03():
    # 年を入力するNumber UI
    year_end = mo.ui.number(
        label="シェア確認年", value=2026, start=2002, stop=2026, step=1
    )
    return (year_end,)


@app.cell
def year_end(year_end):
    year_begin = year_end.value - 2

    _pie_chart = g.chart_pie_yearly_share_by_maker(
        begin_year=year_begin,
        end_year=year_end.value,
    )
    _end_date = datetime(year_end.value, 12, 31)
    _begin_date = _end_date - timedelta(days=365 * 7)
    _bar_chart = g.chart_hbar_yearly_share_by_maker(
        begin=_begin_date,
        end=_end_date,
    )

    mo.vstack([year_end, _pie_chart, _bar_chart])
    return


if __name__ == "__main__":
    app.run()
