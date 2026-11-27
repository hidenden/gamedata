# /// script
# [tool.marimo.display]
# theme = "system"
# ///

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")

with app.setup:
    # 標準ライブラリ
    from datetime import date, datetime

    import marimo as mo
    import altair as alt

    # サードパーティライブラリ
    import polars as pl
    # import polars.selectors as cs

    import scipy as sp
    import statsmodels.api as sm
    import holidays as holidays
    import ruptures as rpt
    import vl_convert as vlc

    # プロジェクト内モジュール
    import gamedata as g


@app.cell
def _():
    hard_sales_df = g.load_hard_sales()
    return (hard_sales_df,)


@app.cell
def switch_ps5_comparison_data(hard_sales_df):
    switch_ps5_weekly = (
        hard_sales_df
        .filter(pl.col("hw").is_in(["NSW", "PS5"]))
        .select("report_date", "hw", "units")
        .pivot(
            on="hw",
            index="report_date",
            values="units",
            aggregate_function="first",
        )
        .drop_nulls(["NSW", "PS5"])
        .sort("report_date")
        .with_columns((pl.col("NSW") - pl.col("PS5")).alias("diff"))
    )

    return (switch_ps5_weekly,)


@app.cell
def switch_ps5_win_interval(switch_ps5_weekly):
    latest_comparison = switch_ps5_weekly.tail(1)
    latest_report_date = latest_comparison["report_date"].item()
    previous_switch_win = (
        switch_ps5_weekly
        .filter(
            (pl.col("report_date") < latest_report_date)
            & (pl.col("diff") > 0)
        )
        .tail(1)
    )
    previous_switch_win_date = previous_switch_win["report_date"].item()
    weeks_since_previous_win = (
        latest_report_date - previous_switch_win_date
    ).days // 7
    intervening_weeks = (
        switch_ps5_weekly
        .filter(
            (pl.col("report_date") > previous_switch_win_date)
            & (pl.col("report_date") < latest_report_date)
        )
        .height
    )

    return (
        intervening_weeks,
        latest_comparison,
        latest_report_date,
        previous_switch_win,
        previous_switch_win_date,
        weeks_since_previous_win,
    )


@app.cell
def switch_ps5_analysis(
    intervening_weeks,
    latest_comparison,
    latest_report_date,
    previous_switch_win,
    previous_switch_win_date,
    weeks_since_previous_win,
):
    mo.md(f"""
    ## SwitchがPS5を上回るのは何週間ぶりか

    ### 分析方法

    1. `hard_sales_df` から `NSW`（Nintendo Switch）と `PS5` の週次販売台数を抽出。
    2. `report_date` ごとに両機種を横持ちにし、`Switch - PS5` の差分を計算。
    3. 最新週より前で差分が正だった直近の週を検索。
    4. 前回の該当週と最新週の報告日の日数差を7で割り、経過週数を算出。

    ### 結果

    - 最新週（{latest_report_date:%Y年%m月%d日}）：Switch **{latest_comparison["NSW"].item():,}台**、PS5 **{latest_comparison["PS5"].item():,}台**
    - 前回Switchが上回った週（{previous_switch_win_date:%Y年%m月%d日}）：Switch **{previous_switch_win["NSW"].item():,}台**、PS5 **{previous_switch_win["PS5"].item():,}台**
    - 日付差は **{weeks_since_previous_win}週間**。間の **{intervening_weeks}週** はすべてPS5が上回った。

    したがって、SwitchがPS5を上回ったのは **{weeks_since_previous_win}週間ぶり**です。
    """)
    return


@app.cell
def switch_ps5_sales_chart(latest_report_date, previous_switch_win_date):
    switch_ps5_chart = g.chart_line_sales(
        hw=["NSW", "PS5"],
        mode="week",
        begin=previous_switch_win_date,
        end=latest_report_date,
        with_point=True,
        multi_line=True,
        size=(720, 400),
    )
    switch_ps5_chart

    return


if __name__ == "__main__":
    app.run()
