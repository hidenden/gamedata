import marimo

__generated_with = "0.23.3"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    # 標準ライブラリ
    from datetime import datetime, timedelta, date

    # サードパーティライブラリ
    import polars as pl
    # import polars.selectors as cs

    # プロジェクト内モジュール
    import gamedata as g
    g.set_dispfunc(func=None)
    return date, g, mo


@app.cell
def _(g, mo):
    hw_select = g.HwSelect(hw_list=["GBA", "DS", "3DS", "PSP", "Vita", "NSW", "NS2"])
    hw_widget = hw_select.widget
    event_select = g.EventSelect()
    event_widget = event_select.widget
    mode_select = mo.ui.dropdown(options=["week", "month", "quarter", "year"], value="week")
    return event_select, event_widget, hw_select, hw_widget, mode_select


@app.cell
def _(date, mo):
    begin_date = mo.ui.date(start=date(2001, 1, 1), value=date(2011,12, 1))
    end_date = mo.ui.date(start=date(2001, 1, 1), value=date(2012,11,30))
    mo.hstack(items=[begin_date, end_date], justify="start")
    return begin_date, end_date


@app.cell
def _(
    begin_date,
    end_date,
    event_select,
    event_widget,
    g,
    hw_select,
    hw_widget,
    mo,
    mode_select,
):
    hw_widget
    event_widget
    (_fig, _df) = g.plot_sales(hw=hw_select.value,
                            mode=mode_select.value,
                             begin=begin_date.value, 
                             end=end_date.value, 
                             event_mask=event_select.value)
    mo.vstack([hw_select, event_select, mode_select,
    _fig, _df], justify="start")
    return


if __name__ == "__main__":
    app.run()
