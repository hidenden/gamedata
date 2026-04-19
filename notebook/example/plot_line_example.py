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

    return g, pl


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
    uia = []

    # 相対期間の設定
    ui_begin_number = mo.ui.number(label="相対期間Begin:", value=0)
    ui_end_number = mo.ui.number(label="相対期間End:", value=52)
    uia.append(ui_begin_number)
    uia.append(ui_end_number)

    # 開始､終了日付の設定
    ui_begin_date = mo.ui.date(value="2025-01-01", label="開始日")
    ui_end_date = mo.ui.date(label="終了日")
    uia.append(ui_begin_date)
    uia.append(ui_end_date)

    # HW選択
    hw_list = g.get_hw(df_all)
    ui_hw = mo.ui.multiselect(options=hw_list, value=["NSW", "NS2", "PS5"], label="HWを選択")
    uia.append(ui_hw)

    # 集計モード
    ui_period_mode = mo.ui.dropdown(options=["week", "month", "quarter", "year"], value="week", label="集計モード")
    uia.append(ui_period_mode)

    # Event mask
    ui_event = mo.ui.dropdown(options=["short", "middle", "long"], value="middle", label="イベントマスク")
    uia.append(ui_event)

    mo.vstack(items=uia)
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
    ui_begin_number,
    ui_end_number,
    ui_hw,
    ui_period_mode,
):
    event1 = current_event_mask
    if ui_period_mode.value != "week":
        event1 = None

    mode1 = ui_period_mode.value
    if ui_period_mode.value == "quarter":
        mode1 = "month"

    (pcsd_fig, pcsd_df) = g.plot_cumulative_sales_by_delta(
        hw=ui_hw.value,
        mode=mode1,
        begin=ui_begin_number.value,
        end=ui_end_number.value,
        event_mask=event1
        )

    pcsd_fig                                                        
    return mode1, pcsd_df


@app.cell
def _(pcsd_df):
    pcsd_df
    return


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
    ui_begin_date,
    ui_end_date,
    ui_hw,
    ui_period_mode,
):
    (ps_fig, ps_df) = g.plot_sales(hw=ui_hw.value,
                                    begin=ui_begin_date.value,
                                    end=ui_end_date.value,
                                    mode=ui_period_mode.value,
                                    event_mask=current_event_mask)
    ps_fig
    return (ps_df,)


@app.cell
def _(ps_df):
    ps_df
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## plot_sales_by_delta
    """)
    return


@app.cell
def _(current_event_mask, g, mode1, ui_begin_number, ui_end_number, ui_hw):
    (psd_fig, psd_df) = g.plot_sales_by_delta(
        hw=ui_hw.value,
        begin=ui_begin_number.value, 
        end=ui_end_number.value, 
        mode=mode1,
        event_mask=current_event_mask)
    
    psd_fig


    return (psd_df,)


@app.cell
def _(psd_df):
    psd_df
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## plot_cumulative_sales
    """)
    return


@app.cell
def _(current_event_mask, g, ui_hw, ui_period_mode):
    (pcs_fig, pcs_df) = g.plot_cumulative_sales(
        hw=ui_hw.value, 
        mode=ui_period_mode.value, 
        event_mask=current_event_mask)
    pcs_fig
    return (pcs_df,)


@app.cell
def _(pcs_df):
    pcs_df
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## plot_sales_with_offset
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
def _(g, hw_periods_ui, period_end):
    hw_periods = []

    for ii, ui in enumerate(hw_periods_ui):
        if ui["hw_dropdown"].value:
            hw = ui["hw_dropdown"].value
            bd = ui["begin_date"].value
            lv = f"{hw} {bd}"
            period_element = {
                "hw": hw,
                "begin": bd,
                "label": lv    
            }
            hw_periods.append(period_element)

    (pso_fig, pso_df) = g.plot_sales_with_offset(hw_periods=hw_periods, end=period_end.value)
    pso_fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## plot_cumsum_diffs
    """)
    return


@app.cell
def _(g):
    cmplist = [("NSW", "PS4"), ("NS2", "PS5")]
    (pcd_fig, pcd_df) = g.plot_cumsum_diffs(cmplist)
    pcd_fig

    return (pcd_df,)


@app.cell
def _(pcd_df):
    pcd_df
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## plot_sales_pase_diff
    """)
    return


@app.cell
def _(g):
    (pspd_fig, pspd_df) = g.plot_sales_pase_diff(base_hw='PS4', compare_hw='PS5')
    pspd_fig

    return (pspd_df,)


@app.cell
def _(pspd_df):
    pspd_df
    return


if __name__ == "__main__":
    app.run()
