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
    df_annotation: pl.DataFrame = g.load_hard_annotation()
    df_annotation
    return


@app.cell
def _():
    _df = g.get_annotation(level=20, mode="w", begin=date(2024, 1, 1), end=date(2026, 12, 31))
    _df
    return


@app.cell
def _():
    df_all = g.load_hard_sales()
    df_all
    return


if __name__ == "__main__":
    app.run()
