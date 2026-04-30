import marimo

__generated_with = "0.23.3"
app = marimo.App(width="medium")


@app.cell
def _():
    # 標準ライブラリ
    from datetime import datetime, timedelta, date
    # サードパーティライブラリ
    import polars as pl
    # import polars.selectors as cs
    import marimo as mo

    # プロジェクト内モジュール
    import gamedata as g
    g.set_dispfunc(func=None)
    return g, mo


@app.cell
def _(mo):
    num = mo.ui.number(start=500000, step=500000, value=5000000, label="累積台数")
    return (num,)


@app.cell
def _(g, mo, num):
    _df = g.chart_reached_unit(num.value, all=True)
    mo.vstack([num, _df])
    return


if __name__ == "__main__":
    app.run()
