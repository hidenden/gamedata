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
    # from report_config import get_config


@app.cell
def md_alt_title():
    mo.md(r"""
    # 生涯累計台数
    """)
    return


@app.cell
def load_hard_sales():
    df_all = g.load_hard_sales()
    return (df_all,)


@app.cell
def _(df_all):
    # gamedataのサマリーAPIから、全ハードの生涯累計を作成する。
    _lifetime_sales = (
        pl.DataFrame(g.hard_sales_summary(df_all))
        .select(
            "hw",
            "full_name",
            "maker_name",
            "launch_date",
            "last_report_date",
            "total_units",
        )
        .rename(
            {
                "hw": "ハード",
                "full_name": "正式名称",
                "maker_name": "メーカー",
                "launch_date": "発売日",
                "last_report_date": "最終集計日",
                "total_units": "生涯累計台数",
            }
        )
        .sort("生涯累計台数", descending=True)
    )

    # 累計順の表をnotebook上に表示する。
    mo.vstack(
        [
            mo.md("## 全ハードウェアの生涯累計台数"),
            mo.ui.table(_lifetime_sales, selection=None, pagination=False),
        ]
    )
    return


if __name__ == "__main__":
    app.run()
