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
    from datetime import datetime, timedelta, date
    # サードパーティライブラリ
    import polars as pl
    # import polars.selectors as cs

    # プロジェクト内モジュール
    import gamedata as g

    return (g,)


@app.cell
def _(g):
    base_df = g.load_hard_sales()
    return (base_df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # hard_event.py
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## load_hard_event
    """)
    return


@app.cell
def _(g):
    event_df = g.load_hard_event()
    event_df
    return (event_df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## delta_event
    """)
    return


@app.cell
def _(event_df, g):
    info_df = g.load_hard_info()
    delta_event_df = g.delta_event(event_df, info_df)
    delta_event_df
    return (delta_event_df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## mask_event
    """)
    return


@app.cell
def _(mo):
    event_name = mo.ui.dropdown(options=["short", "middle", "long"], label="EVENTマスクタイプ", value="long")
    event_name
    return (event_name,)


@app.cell
def _(event_name, g):
    event_dict = {
        "short" : g.EVENT_MASK_SHORT,
        "middle": g.EVENT_MASK_MIDDLE,
        "long": g.EVENT_MASK_LONG,
    }
    current_event_mask = event_dict[event_name.value]

    return (current_event_mask,)


@app.cell
def _(current_event_mask, delta_event_df, g):
    masked_event_df = g.mask_event(delta_event_df, event_mask=current_event_mask)
    masked_event_df

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## filter_event
    """)
    return


@app.cell
def _(base_df, g, mo):
    ui_event_start_date = mo.ui.date(value="2017-03-03")
    ui_event_end_date = mo.ui.date()
    hw_list = g.get_hw(base_df)
    ui_event_hw = mo.ui.multiselect(options=hw_list, value=["PS5", "NSW", "NS2"])
    mo.vstack(items=[ui_event_start_date,
        ui_event_end_date,
        ui_event_hw])
    return ui_event_end_date, ui_event_hw, ui_event_start_date


@app.cell
def _(
    current_event_mask,
    delta_event_df,
    g,
    ui_event_end_date,
    ui_event_hw,
    ui_event_start_date,
):
    filtered_event_df = g.filter_event(delta_event_df, 
        start_date=ui_event_start_date.value, 
        end_date=ui_event_end_date.value, 
        hw=ui_event_hw.value,
        event_mask=current_event_mask
        )
    filtered_event_df
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## add_event_positions
    """)
    return


@app.cell
def _(
    base_df,
    current_event_mask,
    event_df,
    g,
    ui_event_end_date,
    ui_event_start_date,
):
    data_df = g.date_filter(base_df, 
        begin=ui_event_start_date.value,
        end=ui_event_end_date.value)
    pivot_df = g.pivot_sales(data_df)

    event_pos_df = g.add_event_positions(event_df, pivot_df, event_mask=current_event_mask)
    event_pos_df

    return (data_df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## add_event_positions_delta
    """)
    return


@app.cell
def _(current_event_mask, data_df, delta_event_df, g):
    pivot_delta_df = g.pivot_sales_by_delta(data_df)
    event_pos_delta_df = g.add_event_positions_delta(delta_event_df, pivot_delta_df, event_mask=current_event_mask)
    event_pos_delta_df


    return


if __name__ == "__main__":
    app.run()
