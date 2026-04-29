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
    return (g,)


@app.cell
def _(g):
    df_all = g.load_hard_sales()
    return


@app.cell
def _(mo):
    end = mo.ui.number(label="累積グラフ週数", value=52, start=10, stop=1000, step=20)
    return (end,)


@app.cell
def _(g):
    event_select = g.EventSelect()
    event_widget = event_select.widget
    return event_select, event_widget


@app.cell
def _(g):
    hwselect = g.HwSelect(default_list=["NS2", "PS5", "NSW"])
    hw_widget = hwselect.widget
    return hw_widget, hwselect


@app.cell
def _(end, event_select, event_widget, g, hw_widget, hwselect, mo):
    hw_widget
    event_widget
    (_fig1, _df1) = g.plot_cumulative_sales(hwselect.value, event_mask=event_select.value)
    (_fig2, _df2) = g.plot_cumulative_sales_by_delta(hw=hwselect.value, end=end.value, event_mask = event_select.value)
    mo.vstack([hwselect, event_select, end, _fig1, _fig2,_df1,  _df2])
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
