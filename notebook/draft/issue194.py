import marimo

__generated_with = "0.23.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return


@app.cell
def _():
    # 標準ライブラリ
    from datetime import datetime, timedelta, date

    # サードパーティライブラリ
    import polars as pl
    # import polars.selectors as cs

    # プロジェクト内モジュール
    import gamedata as g


    return g, pl


@app.cell
def _(g, pl):
    df_all:pl.DataFrame = g.load_hard_sales()
    return (df_all,)


@app.cell
def _(df_all: "pl.DataFrame", pl):
    (df_all
    .select([
        pl.col('hw'),
        pl.col('maker_name'),
        pl.col('launch_date')
    ])
    .unique()
    .sort(by=['maker_name', 'launch_date'], descending=[True, False])
    .select([
        pl.col('hw'),
    ])
    ).to_series(0).to_list()

    return


if __name__ == "__main__":
    app.run()
