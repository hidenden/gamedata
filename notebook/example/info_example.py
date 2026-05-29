import marimo

__generated_with = "0.23.1"
app = marimo.App(width="medium")


@app.cell
def calc_cell_01():
    import marimo as mo

    return (mo,)


@app.cell
def calc_cell_02():
    # 標準ライブラリ
    from datetime import datetime, timedelta, date
    # サードパーティライブラリ
    import polars as pl
    # import polars.selectors as cs

    # プロジェクト内モジュール
    import gamedata as g

    return (g,)


@app.cell
def sales_cell(g):
    base_df = g.load_hard_sales()
    return (base_df,)


@app.cell(hide_code=True)
def md_hard_info(mo):
    mo.md(r"""
    # hard_info.py
    """)
    return


@app.cell(hide_code=True)
def md_load_hard_info(mo):
    mo.md(r"""
    ## load_hard_info
    """)
    return


@app.cell
def sales_cell_2(g):
    hard_info = g.load_hard_info()
    hard_info
    return


@app.cell(hide_code=True)
def md_get_hard_colors(mo):
    mo.md(r"""
    ## get_hard_colors
    """)
    return


@app.cell
def base_df(base_df, g, mo):
    hw_list = g.get_hw(base_df)
    ui_hw = mo.ui.multiselect(options=hw_list, value=["NSW", "NS2", "PS5", "XSX"])
    ui_hw
    return (ui_hw,)


@app.cell
def ui_hw(g, ui_hw):
    hw_colors = g.get_hard_colors(hw=ui_hw.value)
    hw_colors
    return


@app.cell(hide_code=True)
def md_get_maker_colors(mo):
    mo.md(r"""
    ## get_maker_colors
    """)
    return


@app.cell
def base_df_2(base_df, g, mo):
    makers = g.get_maker(base_df)
    ui_maker = mo.ui.multiselect(options=makers, value=["SONY", "Nintendo"])
    ui_maker
    return (ui_maker,)


@app.cell
def ui_maker(g, ui_maker):
    maker_colors = g.get_maker_colors(maker=ui_maker.value)
    maker_colors
    return


@app.cell(hide_code=True)
def md_get_hard_names(mo):
    mo.md(r"""
    ## get_hard_names
    """)
    return


@app.cell
def ui_hw_2(g, ui_hw):
    hw_names = g.get_hard_names(hw=ui_hw.value)
    hw_names
    return


@app.cell(hide_code=True)
def md_get_hard_dict(mo):
    mo.md(r"""
    ## get_hard_dict
    """)
    return


@app.cell
def cell(g):
    hard_dict = g.get_hard_dict()
    hard_dict
    return


if __name__ == "__main__":
    app.run()
