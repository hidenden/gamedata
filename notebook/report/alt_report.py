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
def md_alt_title():
    mo.md(r"""
    # Alternative Report
    """)
    return


@app.cell
def load_hard_sales():
    df_all = g.load_hard_sales()
    return (df_all,)


@app.cell(hide_code=True)
def md_ns2_ps5_gap_title():
    mo.md(r"""
    ## Switch2がPS5まで200万台差に迫る
    """)
    return


@app.cell(hide_code=True)
def md_ns2_ps5_gap_1():
    mo.md(r"""
    Switch2とPS5の累計差が200万台を切りました｡

    当初の616万台差から416万台分詰めて200万台差まで迫るのに要した期間はわずか50週間｡
    Switchは406万台差から206万台分詰めて200万台差まで迫るのに78週間を要しました｡
    現在の推移だと､78週経過する頃にはSwitch2はPS5に追いつくと見られます｡
    """)
    return


@app.cell
def ns2_ps5_cumulative_difference_chart():
    _ps5_last = g.sales_value(hw="PS5", index_week=-1, cumulative=True)
    _ns2_last = g.sales_value(hw="NS2", index_week=-1, cumulative=True)
    _ns2_ps5_diff = _ps5_last - _ns2_last

    _chart = g.chart_line_cumsum_diffs(
        cmplist=[("NSW", "PS4"), ("NS2", "PS5")],
        multi_line=True,
        annotation_level=29,
    )

    _chart = g.chart_line_guide(
        base_chart=_chart,
        x=50,
        y=_ns2_ps5_diff,
        x2=78,
        y2=0,
        stroke=[5, 4],
        size=2,
        color="#00a0FF",
    )

    _chart = g.chart_rule_xy(
        base_chart=_chart, y=_ns2_ps5_diff, stroke=[1, 0], size=2, color="#189beca7"
    )

    _chart = g.chart_rule_xy(
        base_chart=_chart, y=1, stroke=[10, 0], size=2, color="#000000"
    )
    mo.ui.altair_chart(_chart)
    return


@app.cell
def _():
    _chart = g.chart_line_cumulative(
        hw=["NS2", "PS5"],
        begin=datetime(2025, 3, 20),
        annotation_level=30,
        multi_line=True,
        mode="week",
    )
    _chart = g.chart_line_guide(
        base_chart=_chart,
        x=date(2026, 5, 28),
        y=5833462,
        x2=date(2027, 1, 31),
        y2=8600000,
        stroke=[5, 4],
        size=2,
        color="#af0000",
    )
    _chart = g.chart_line_guide(
        base_chart=_chart,
        x=date(2026, 5, 28),
        y=7567489,
        x2=date(2027, 1, 31),
        y2=8100000,
        stroke=[5, 4],
        size=2,
        color="#0040a0",
    )   

    chart_cumulative = mo.ui.altair_chart(_chart)
    chart_cumulative
    return


@app.cell
def _(df_all):
    _m13w = g.extract_latest(df_all).filter(pl.col("hw") == "NS2")["ma13w"].item()
    _m13w
    return


@app.cell
def _(df_all):
    _m13w = g.extract_latest(df_all).filter(pl.col("hw") == "PS5")["ma13w"].item()
    _m13w
    return


if __name__ == "__main__":
    app.run()
