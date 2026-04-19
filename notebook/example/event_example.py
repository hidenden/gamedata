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

    return date, g

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

@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## delta_event
    """)
    return

@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## mask_event
    """)
    return

@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## filter_event
    """)
    return

@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## add_event_positions
    """)
    return

@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## add_event_positions_delta
    """)
    return

if __name__ == "__main__":
    app.run()
