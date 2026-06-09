# /// script
# [tool.marimo.display]
# theme = "system"
# ///

import marimo

__generated_with = "0.23.6"
app = marimo.App(width="medium")

with app.setup:
    # 標準ライブラリ
    from datetime import date, datetime

    import marimo as mo
    import altair as alt

    # サードパーティライブラリ
    import polars as pl

    # import polars.selectors as cs
    # プロジェクト内モジュール
    import gamedata as g


@app.cell
def _():
    _df = g.load_hard_sales()
    hw_all = g.get_hw_all()
    df_all = _df.filter(pl.col("hw").is_in(hw_all))
    return (df_all,)


@app.cell
def _(df_all):
    _df = df_all.with_columns(
        ((pl.col("units") - pl.col("ma4w"))/pl.col("ma4w")).alias("deviation")
    )
    _df = _df.select(
        pl.col("report_date"),
        pl.col("delta_week"),
        pl.col("hw"),
        pl.col("units"),
        pl.col("ma4w"),
        pl.col("deviation")
    )
    _df = (_df
        .filter(pl.col("deviation").is_not_null())
        .filter(pl.col("delta_week")< 52)
    )
    df_dev = _df
    return (df_dev,)


@app.cell
def _(df_dev):
    df_dev_agg = df_dev.group_by(["hw"]).agg(
        pl.col("deviation").std().alias("deviation_std"),
        pl.col("deviation").mean().alias("deviation_mean"),
        pl.col("deviation").var().alias("deviation_var"),
        pl.col("deviation").skew(bias=False).alias("deviation_skew_nobias"),
        pl.col("deviation").kurtosis(bias=False).alias("deviation_kurt_nobias"),
    ).sort(by="deviation_std", descending=True)

    return (df_dev_agg,)


@app.cell
def _(df_dev_agg):
    df_dev_agg.sort(by="deviation_std", descending=True).sort(by="deviation_std", descending=True)

    return


if __name__ == "__main__":
    app.run()
