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
    return


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


if __name__ == "__main__":
    app.run()
