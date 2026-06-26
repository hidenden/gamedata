# /// script
# [tool.marimo.display]
# theme = "system"
# ///

import marimo

__generated_with = "0.23.9"
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
    # Alternative Report
    """)
    return


@app.cell
def load_hard_sales():
    df_all = g.load_hard_sales()
    return (df_all,)


@app.cell
def _():
    _begin = date(2020, 1, 15)
    _end = report_date
    _chart = g.chart_line_sales(
        begin=_begin,
        end=_end,
        annotation_level=10,
        padding_end=1,
        ymax=200000,
        size=(4000, 520)
    )
    mo.hstack(items=[mo.ui.altair_chart(_chart)], justify="start", wrap=True)
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


@app.cell
def md_ps5_sales_weeks_title(ps5_info):
    ps5_weeks = ps5_info["sales_weeks"]
    mo.md(f"### PS5:{ps5_weeks}週目の状況")
    return


@app.cell
def ps5_cumulative_delta_chart(ps5_info):
    _chart = g.chart_line_cumulative_delta(
        hw=["PS5", "PS4", "PS3"],
        end=ps5_info["sales_weeks"] + 60,
        mode="week",
        multi_line=True,
        annotation_level=15,
    )

    _chart = g.chart_rule_xy(
        base_chart=_chart,
        x=ps5_info["sales_weeks"],
        y=ps5_info["total_units"],
        stroke=[5, 2],
        size=2,
        color="#00000060",
    )

    _chart = g.chart_line_guide(
        base_chart=_chart,
        x=ps5_info["sales_weeks"],
        y=ps5_info["total_units"],
        x2=ps5_info["sales_weeks"] + 60,
        y2=8200000,
        stroke=[3, 3],
        size=2,
        color="#4060f0",
    )

    ps_cd_chart = mo.ui.altair_chart(_chart)
    ps_cd_chart
    return (ps_cd_chart,)


@app.cell
def ps5_cumulative_delta_table(ps_cd_chart):
    _df = (
        ps_cd_chart.dataframe.filter(pl.col("delta_week") == 284)
        .select(["hw", "sum_units"])
        .sort("sum_units", descending=True)
    )
    g.style_df(g.rename_columns(_df), bar=True)
    return


@app.cell(hide_code=True)
def md_ps5_cumulative_delta_1():
    mo.md(r"""
    PS5は､PS4,PS3に比べて販売ペースが遅い状態で安定しています｡
    PS5 DE日本語版が日本のゲーム機最安値となったことでブースト効果があるのかどうかが注目されます｡
    """)
    return


@app.cell
def _(df_all):
    src_df = g.quarterly_sales_long(df_all, hw=["NSW"])
    src_df = (
        src_df.group_by(["year", "q_num"])
        .agg(pl.col("quarterly_units").sum().alias("units"))
        .sort(["year", "q_num"])
    )

    src_df
    return


@app.cell
def _():
    _c1 = g.chart_bar_yearly_by_mode(begin=date(2016,1,1), stacked=False )
    _c2 = mo.ui.altair_chart(_c1)
    _c2
    return


@app.cell
def _():
    g.chart_bar_sales(hw=["PS5"], mode="m", begin=date(2021,1,1), end=date(2024,12,31))
    return


if __name__ == "__main__":
    app.run()
