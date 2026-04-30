import marimo

__generated_with = "0.23.3"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    # 標準ライブラリ
    from datetime import datetime, timedelta, date

    # サードパーティライブラリ
    import polars as pl
    # import polars.selectors as cs

    # プロジェクト内モジュール
    import gamedata as g
    g.set_dispfunc(func=None)
    return datetime, g, timedelta


@app.cell
def _(g, mo):
    # HW select widget
    hw_select = g.HwSelect(default_list=["NSW", "PS5"], force_any=True)
    hw_widget = hw_select.widget

    # Stack指定
    stack_widget = mo.ui.checkbox(label="Stack mode", value=False)
    return hw_select, hw_widget, stack_widget


@app.cell
def _(datetime, g, hw_select, hw_widget, mo, stack_widget):
    hw_widget
    hw_list = hw_select.value
    (_fig, _df) = g.plot_yearly_bar_by_hard(hw=hw_list,
                                       begin=datetime(2000,1,1),
                                       stacked=stack_widget.value, 
                                       ticklabelsize=8)
    mo.vstack([hw_select, stack_widget,  _fig, _df])
    return


@app.cell
def _(g):
    # HW select widget
    hw_select_area = g.HwSelect(default_list=[])
    hw_widget_area = hw_select_area.widget
    return hw_select_area, hw_widget_area


@app.cell
def _(datetime, g, hw_select_area, hw_widget_area, mo):
    hw_widget_area
    (_fig, _df) = g.plot_sales(hw=hw_select_area.value,mode='year', begin=datetime(2001,1,1), area=True)
    mo.vstack([hw_select_area, _fig, _df])
    return


@app.cell
def _(mo):
    # 年を入力するNumber UI
    year_end = mo.ui.number(label="シェア確認年", value=2026, start=2002, stop=2026, step=1)
    return (year_end,)


@app.cell
def _(datetime, g, mo, timedelta, year_end):
    year_begin = year_end.value - 2

    (_pie_fig, _pie_df) = g.plot_maker_share_pie(begin_year=year_begin, end_year=year_end.value)
    _end_date = datetime(year_end.value, 12, 31)
    _begin_date = _end_date - timedelta(days=365*7)
    (_bar_fig, _) = g.plot_maker_share_bar(begin=_begin_date, end=_end_date)

    mo.vstack([year_end, _pie_fig, _pie_df, _bar_fig])
    return


if __name__ == "__main__":
    app.run()
