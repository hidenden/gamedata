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
    # hard_info.py
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## load_hard_info
    """)
    return


@app.cell
def _(g):
    hard_info = g.load_hard_info()
    hard_info
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## get_hard_colors
    """)
    return


@app.cell
def _(base_df, g, mo):
    hw_list = g.get_hw(base_df)
    ui_hw = mo.ui.multiselect(options=hw_list, value=["NSW", "NS2", "PS5", "XSX"])
    ui_hw
    return (ui_hw,)


@app.cell
def _(g, ui_hw):
    hw_colors = g.get_hard_colors(hw=ui_hw.value)
    hw_colors
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## get_maker_colors
    """)
    return


@app.cell
def _(base_df, g, mo):
    makers = g.get_maker(base_df)
    ui_maker = mo.ui.multiselect(options=makers, value=["SONY", "Nintendo"])
    ui_maker
    return (ui_maker,)


@app.cell
def _(g, ui_maker):
    maker_colors = g.get_maker_colors(maker=ui_maker.value)
    maker_colors
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## get_hard_names
    """)
    return


@app.cell
def _(g, ui_hw):
    hw_names = g.get_hard_names(hw=ui_hw.value)
    hw_names
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## get_hard_dict
    """)
    return


@app.cell
def _(g):
    hard_dict = g.get_hard_dict()
    hard_dict
    return


if __name__ == "__main__":
    app.run()
