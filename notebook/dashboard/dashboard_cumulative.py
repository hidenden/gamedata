import marimo

__generated_with = "0.23.2"
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
def _(g):
    hw_list = g.get_hw_all()
    return


@app.cell
def _(mo):

    event = mo.ui.dropdown(options=["short", "middle", "long"], value="middle", label="イベントマスク")
    end = mo.ui.number(label="累積グラフ週数", value=52, start=10, stop=1000, step=20)
    return end, event


@app.cell
def _(event, g):
    # Event mask converter
    event_mask_dict = {
        "short": g.EVENT_MASK_SHORT,
        "middle": g.EVENT_MASK_MIDDLE,
        "long": g.EVENT_MASK_LONG,
    }
    current_event_mask = event_mask_dict[event.value]
    return (current_event_mask,)


@app.cell
def _(g):
    hwselect = g.HwSelect(default_list=["NS2", "PS5"])
    hw_widget = hwselect.widget
    return hw_widget, hwselect


@app.cell
def _(current_event_mask, end, event, g, hw_widget, hwselect, mo):
    hw_widget
    (_fig1, _df1) = g.plot_cumulative_sales(hwselect.value, event_mask=current_event_mask)
    (_fig2, _df2) = g.plot_cumulative_sales_by_delta(hw=hwselect.value, end=end.value, event_mask = current_event_mask)
    mo.vstack([hwselect, event, end, _fig1, _fig2,_df1,  _df2])
    return


if __name__ == "__main__":
    app.run()
