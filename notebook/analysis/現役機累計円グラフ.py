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


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # 現役機種・累計円グラフ
    """)
    return


@app.cell
def load_hard_sales():
    df_all = g.load_hard_sales()
    return (df_all,)


@app.cell
def chart_latest_cumulative_pie(df_all):
    # 最新累計: Switch / Switch 2 / PS5 / Xbox Series の構成比を円グラフで表示する。
    _hard_order = ["NSW", "NS2", "PS5", "XSX"]
    _hard_labels = {
        "NSW": "Switch",
        "NS2": "Switch 2",
        "PS5": "PS5",
        "XSX": "Xbox Series",
    }

    latest_cumulative_totals = (
        g.extract_total(df_all.filter(pl.col("hw").is_in(_hard_order)), compact=True)
        .with_columns([
            pl.col("hw").replace(_hard_labels).alias("ハード"),
            (pl.col("sum_units") / 1_000_000).round(2).alias("累計台数（百万台）"),
        ])
        .sort(pl.col("hw").replace({code: idx for idx, code in enumerate(_hard_order)}))
    )

    _latest_totals_chart = (
        alt.Chart(latest_cumulative_totals)
        .mark_arc()
        .encode(
            theta=alt.Theta("sum_units:Q", title="累計台数"),
            color=alt.Color(
                "ハード:N",
                title="ハード",
                scale=alt.Scale(
                    domain=[_hard_labels[_code] for _code in _hard_order],
                    range=g.get_hard_colors(_hard_order),
                ),
            ),
            tooltip=[
                alt.Tooltip("ハード:N", title="ハード"),
                alt.Tooltip("report_date:T", title="最新集計日"),
                alt.Tooltip("sum_units:Q", title="累計台数", format=","),
                alt.Tooltip("累計台数（百万台）:Q", title="累計台数（百万台）"),
            ],
            order=alt.Order("sum_units:Q", sort="descending"),
        )
        .properties(width=360, height=360, title="最新累計台数の構成比")
    )

    mo.vstack([
        mo.md("### 最新累計台数の円グラフ"),
        _latest_totals_chart,
        latest_cumulative_totals.select(["ハード", "report_date", "sum_units", "累計台数（百万台）"]),
    ])
    return


if __name__ == "__main__":
    app.run()
