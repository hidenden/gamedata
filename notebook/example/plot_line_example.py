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
    g.set_dispfunc(func=None)
    return (df_all,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # plot_line.py
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### パラメータの設定
    """)
    return


@app.cell
def _(df_all: "pl.DataFrame", g, mo):
    _uia = []

    # 相対期間の設定
    ui_begin_number = mo.ui.number(label="相対期間Begin:", value=0)
    ui_end_number = mo.ui.number(label="相対期間End:", value=52)
    _uia.append(ui_begin_number)
    _uia.append(ui_end_number)

    # 開始､終了日付の設定
    ui_begin_date = mo.ui.date(value="2025-01-01", label="開始日")
    ui_end_date = mo.ui.date(label="終了日")
    _uia.append(ui_begin_date)
    _uia.append(ui_end_date)

    # HW選択
    hw_list = g.get_hw(df_all)
    ui_hw = mo.ui.multiselect(options=hw_list, value=["NSW", "NS2", "PS5"], label="HWを選択")
    _uia.append(ui_hw)

    # 集計モード
    ui_period_mode = mo.ui.dropdown(options=["week", "month", "quarter", "year"], value="week", label="集計モード")
    _uia.append(ui_period_mode)

    # Event mask
    ui_event = mo.ui.dropdown(options=["short", "middle", "long"], value="middle", label="イベントマスク")
    _uia.append(ui_event)

    mo.vstack(items=_uia)
    return (
        hw_list,
        ui_begin_date,
        ui_begin_number,
        ui_end_date,
        ui_end_number,
        ui_event,
        ui_hw,
        ui_period_mode,
    )


@app.cell
def _(g, ui_event):
    # Event mask converter
    event_mask_dict = {
        "short": g.EVENT_MASK_SHORT,
        "middle": g.EVENT_MASK_MIDDLE,
        "long": g.EVENT_MASK_LONG,
    }
    current_event_mask = event_mask_dict[ui_event.value]
    return (current_event_mask,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## plot_cumulative_sale_by_delta
    """)
    return


@app.cell
def _(
    current_event_mask,
    g,
    mo,
    ui_begin_number,
    ui_end_number,
    ui_hw,
    ui_period_mode,
):
    _event = current_event_mask
    if ui_period_mode.value != "week":
        _event = None

    current_mode = ui_period_mode.value
    if ui_period_mode.value == "quarter":
        current_mode = "month"

    _plot = g.plot_cumulative_sales_by_delta(
        hw=ui_hw.value,
        mode=current_mode,
        begin=ui_begin_number.value,
        end=ui_end_number.value,
        event_mask=_event
        )

    mo.vstack(_plot)                                                 
    return (current_mode,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## plot_sales
    """)
    return


@app.cell
def _(
    current_event_mask,
    g,
    mo,
    ui_begin_date,
    ui_end_date,
    ui_hw,
    ui_period_mode,
):
    _plot = g.plot_sales(hw=ui_hw.value,
                        begin=ui_begin_date.value,
                        end=ui_end_date.value,
                        mode=ui_period_mode.value,
                        event_mask=current_event_mask)
    mo.vstack(_plot)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## plot_sales_by_delta
    """)
    return


@app.cell
def _(
    current_event_mask,
    current_mode,
    g,
    mo,
    ui_begin_number,
    ui_end_number,
    ui_hw,
):
    _plot = g.plot_sales_by_delta(
        hw=ui_hw.value,
        begin=ui_begin_number.value, 
        end=ui_end_number.value, 
        mode=current_mode,
        event_mask=current_event_mask)
    
    mo.vstack(_plot)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## plot_cumulative_sales
    """)
    return


@app.cell
def _(current_event_mask, g, mo, ui_hw, ui_period_mode):
    from cffi.cffi_opcode import F_PACKED
    _plot = g.plot_cumulative_sales(
        hw=ui_hw.value, 
        mode=ui_period_mode.value, 
        event_mask=current_event_mask)
    mo.vstack(_plot)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## plot_sales_with_offset
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
def _(g, hw_periods_ui, mo, period_end, ui_items):
    hw_periods = [
        {
            "hw": _ui[0],
            "begin": _ui[1],
            "label": f"{_ui[0]} {_ui[1]}"    
        } for _ui in hw_periods_ui.value
    ]

    _plot = g.plot_sales_with_offset(hw_periods=hw_periods, end=period_end.value)
    mo.vstack(ui_items + list(_plot))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## plot_cumsum_diffs
    """)
    return


@app.cell
def _(g, mo):
    _cmplist = [("NSW", "PS4"), ("NS2", "PS5")]
    _plot = g.plot_cumsum_diffs(_cmplist)
    mo.vstack(_plot)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## plot_sales_pase_diff
    """)
    return


@app.cell
def _(g, mo):
    _plot = g.plot_sales_pase_diff(base_hw='PS4', compare_hw='PS5')
    mo.vstack(_plot)

    return


if __name__ == "__main__":
    app.run()
