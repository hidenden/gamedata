# /// script
# [tool.marimo.display]
# theme = "system"
# ///

import marimo

__generated_with = "0.23.14"
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

    # レポート日付
    from report_config import get_config

    config = get_config()
    report_date: datetime = config["date"]


@app.cell
def md_alt_title():
    mo.md(r"""
    # TEMPLATE NOTEBOOK
    """)
    return


if __name__ == "__main__":
    app.run()
