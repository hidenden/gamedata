# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "altair==6.2.2",
#     "marimo>=0.23.14",
#     "pandas>=2.3.3",
#     "polars==1.42.1",
#     "pyarrow>=23.0.1",
# ]
# [tool.marimo.display]
# theme = "system"
# ///

import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")

with app.setup:
    # 標準ライブラリ
    from datetime import date, datetime
    from pathlib import Path
    import sys

    # サードパーティライブラリ
    import marimo as mo
    import altair as alt
    import polars as pl
    # import polars.selectors as cs

    import scipy as sp
    import statsmodels.api as sm
    import holidays as holidays
    import ruptures as rpt
    import vl_convert as vlc

    # プロジェクト内モジュール
    import gamedata as g
    from gamedata import catalog



@app.cell
def mode_set():
    _args = mo.cli_args()
    is_publish = True if _args.get("publish") else False

    if not is_publish:
        g.disable_styler()
        alt.theme.enable("edit")
    else:
        alt.theme.enable("publish")

    return (is_publish,)


@app.cell
def load_data():
    hard_sales_all_df: pl.DataFrame = g.load_hard_sales(True)
    annotation_all_df: pl.DataFrame = g.load_hard_annotation(no_cache=True)

    return (hard_sales_all_df,)


@app.cell
def report_setup(hard_sales_all_df: pl.DataFrame, is_publish):
    # レポート日付
    from report_config import get_config

    config = get_config()
    report_date: datetime = config["date"]

    def show_title(d: datetime):
        last_updated_str = d.strftime("%Y-%m-%d")
        mode: str = "**DRAFT**" if not is_publish else ""
        return mo.md(f"# 国内ゲームハード週販レポート ({last_updated_str}) {mode}")

    [ns2_info, ps5_info, nsw_info] = g.hard_sales_summary(
        hard_sales_all_df, hw=["NS2", "PS5", "NSW"]
    )

    return ns2_info, report_date, show_title


@app.cell
def _(hard_sales_all_df: pl.DataFrame):
    _df_latest = g.extract_latest(hard_sales_all_df, 1)
    switch2_latest = _df_latest.filter(pl.col("hw") == "NS2").row(0, named=True)
    switch_latest = _df_latest.filter(pl.col("hw") == "NSW").row(0, named=True)
    ps5_latest = _df_latest.filter(pl.col("hw") == "PS5").row(0, named=True)

    return ps5_latest, switch2_latest, switch_latest


@app.cell
def show_title_cell(report_date: datetime, show_title):
    show_title(report_date)

    return


@app.cell(hide_code=True)
def md_prologue():
    mo.md(r"""
    * ハードウェアの販売データはファミ通の調査結果を基にしています。
    * 複数週合算の集計値は処理上の都合により、週次値に調整しています｡
    * [過去の週販レポート](../index.html)
    """)
    return


@app.cell(hide_code=True)
def md_weekly_summary_title():
    mo.md(r"""
    ## 直近4週間のハード売上／累計推移
    """)
    return


@app.cell
def units_by_date_hw_table(
    hard_sales_all_df: pl.DataFrame,
    report_date: datetime,
):
    _table = g.units_by_date_hw_table(
        hard_sales_all_df, begin=g.weeks_before(report_date, 3), end=report_date
    )
    mo.hstack(items=[_table], justify="start", wrap=True)

    return


@app.cell(hide_code=True)
def md_top():
    mo.md(r"""
    9月27日は4機種合計で48,596台となり、前週から0.9%増加しました。PS5、Switch、Xbox Series X|Sが増加した一方、Switch2は減少しました。

    Switch2は32,198台で前週比6.2%減となりましたが、首位を維持しています。
    PS5は9,730台で24.0%増え、Switchの6,306台を上回って2位を維持しました。
    Switchは10.5%増加し、Xbox Series X|Sも362台へ増加しましたが、販売規模は引き続き小さい状態です。

    今週はPS5向け「SILENT HILL:Townfall」の時期と重なり、PS5は前週から増加しました。ただし直近4週平均は8,208台であり、ハード牽引効果が持続するかはなお見極めが必要です。2026年第3四半期は617,823台で終了し、2001年以降の全四半期で最低となりました。
    """)
    return


@app.cell(hide_code=True)
def md_weekly_sales_trend():
    mo.md(r"""
    ## 週販推移
    """)
    return


@app.cell
def weekly_sales_trend(report_date: datetime):
    _begin = g.report_begin(report_date)
    _end = report_date
    _chart = g.chart_line_sales(
        hw=["NSW", "NS2", "PS5", "XSX"],
        begin=_begin,
        end=_end,
        annotation_level=32,
        padding_end=2,
    )

    weekly_chart = mo.ui.altair_chart(_chart)
    mo.vstack(items=[weekly_chart], justify="start")

    return


@app.cell(hide_code=True)
def md_weekly_sales_trend_1():
    mo.md(r"""
 
    """)
    return


@app.cell(hide_code=True)
def md_weekly_sales_trend_2():
    mo.md(r"""
    ### 週販推移(拡大)
    """)
    return


@app.cell
def weekly_sales_trend_2(report_date: datetime):
    _begin = date(2026, 2, 15)
    _end = report_date
    _chart = g.chart_line_sales(
        hw=["NSW", "PS5", "XSX", "NS2"],
        begin=_begin,
        end=_end,
        annotation_level=30,
        ymax=55000,
        padding_end=1,
        value_label=True,
    )
    weekly_big_chart = mo.ui.altair_chart(_chart)
    mo.vstack(items=[weekly_big_chart], justify="start")

    return


@app.cell(hide_code=True)
def md_weekly_chart():
    mo.md(r"""
    Switch2は32,198台で前週から2,143台減り、5週ぶりの減少となりました。直近4週平均は29,790台、13週平均は30,383台で、足元はおおむね3万台前後の横ばい圏にあります。9月後半に見られた上昇は一服しましたが、首位は維持しています。
    ビッグタイトルが牽引した後は大きく落ち込むパターンが多いSwitch2ですが､万紫千紅直後は微減で維持しています｡
    これが全体としての上昇基調を示すものならいいのですが､今後に注目です｡

    PS5は9,730台へ24.0%増加し、直近4週平均も8,208台へ上昇しました。Switchは6,306台へ10.5%増加したものの、直近4週平均では7,790台でPS5を下回っています。順位はSwitch2、PS5、Switch、Xbox Series X|Sの順で先週から変わっていません。今週の「SILENT HILL:Townfall」に続き、次回の「ACE COMBAT8」がPS5の上昇を持続させられるかを確認したいところです。
    """)
    return


@app.cell(hide_code=True)
def md_yearly_cumulative_comparison_title():
    mo.md(r"""
    ## 年間累計比較
    """)
    return


@app.cell(hide_code=True)
def md_yearly_cumulative_comparison_1():
    mo.md(r"""
 
    """)
    return


@app.cell(hide_code=True)
def md_ps5_yearly_cumulative_title():
    mo.md(r"""
    ### PlayStation 5(2024年, 2025年, 2026年)
    """)
    return


@app.cell
def ps5_yearly_cumulative_chart(ps5_latest):
    _chart = g.chart_line_ycumulative_by_hw_year(
        hw_years=[("PS5", 2024), ("PS5", 2025), ("PS5", 2026)],
        annotation_level=31,
    )
    _df = mo.ui.altair_chart(_chart).dataframe

    _chart = g.chart_line_guide(
        _chart,
        x=ps5_latest["report_date"].timetuple().tm_yday,
        y=_df.filter(pl.col("report_date") == ps5_latest["report_date"]).row(
            0, named=True
        )["yearly_sum_units"],
        x2=365,
        y2=680000,
        stroke=[3, 2],
        size=2,
        color="#ff000080",
    )
    ps5_yearly_cumulative_chart = mo.ui.altair_chart(_chart)
    mo.vstack(items=[ps5_yearly_cumulative_chart], justify="start")

    return


@app.cell
def ps5_heatmap_chart():
    _chart = g.chart_heatmap(
        hw="PS5",
        mode="week",
        scale_scheme="plasma",
        scale_type="sqrt",
    )
    ps5_heatmap_chart = mo.ui.altair_chart(_chart)
    mo.vstack(items=[ps5_heatmap_chart], justify="start")

    return


@app.cell(hide_code=True)
def md_ps5_yearly():
    mo.md(r"""
    PS5の2026年累計は9月27日時点で438,633台です。前年同時期の637,929台を31.2%下回り、2024年同時期の1,093,285台に対しては59.9%少ない水準です。歴代PlayStationとの比較ではPS3の2014年同時期379,929台を15.5%上回る一方、PS4の2018年同時期1,217,718台には大きく届きません。

    52週平均による年間販売予測は約680,000台で、2025年通年の879,204台を下回る見込みです。
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
 
    """)
    return


@app.cell(hide_code=True)
def md_switch_yearly_cumulative_title():
    mo.md(r"""
    ### Switch(2024年, 2025年, 2026年)
    """)
    return


@app.cell
def switch_yearly_cumulative_chart(switch_latest):
    _chart = g.chart_line_ycumulative_by_hw_year(
        hw_years=[("NSW", 2024), ("NSW", 2025), ("NSW", 2026)],
        annotation_level=39,
    )
    _df = mo.ui.altair_chart(_chart).dataframe
    _chart = g.chart_line_guide(
        _chart,
        x=switch_latest["report_date"].timetuple().tm_yday,
        y=_df.filter(pl.col("report_date") == switch_latest["report_date"]).row(
            0, named=True
        )["yearly_sum_units"],
        x2=365,
        y2=958000,
        stroke=[3, 2],
        size=2,
        color="#ff000080",
    )
    switch_yearly_cumulative_chart = mo.ui.altair_chart(_chart)
    mo.vstack(items=[switch_yearly_cumulative_chart], justify="start")

    return


@app.cell
def switch_heatmap_chart():
    _chart = g.chart_heatmap(
        hw="NSW",
        mode="week",
        scale_scheme="plasma",
        scale_type="sqrt",
    )
    switch_heatmap_chart = mo.ui.altair_chart(_chart)
    mo.vstack(items=[switch_heatmap_chart], justify="start")

    return


@app.cell(hide_code=True)
def md_switch_yearly():
    mo.md(r"""
    Switchの2026年累計は9月27日時点で570,699台です。前年同時期の1,132,667台から49.6%減、2024年同時期の2,156,026台から73.5%減となり、発売からの経過に伴う縮小が続いています。

    52週平均による年間販売予測は約958,000台で、2025年通年の1,520,384台を下回る見込みです。累計は36,986,860台となり、3,700万台まで残り13,140台です。直近4週平均の7,790台を維持できれば10月前半に到達する計算ですが、週ごとの振れには注意が必要です。
    """)
    return


@app.cell(hide_code=True)
def switch2_yearly_cumulative_title():
    mo.md(r"""
    ### Switch2(2025年, 2026年)
    """)
    return


@app.cell
def switch2_yearly_cumulative_chart(switch2_latest):
    _chart = g.chart_line_ycumulative_by_hw_year(
        hw_years=[("NS2", 2025), ("NS2", 2026)],
        annotation_level=25,
    )
    _df = mo.ui.altair_chart(_chart).dataframe

    _chart = g.chart_line_guide(
        _chart,
        x=switch2_latest["report_date"].timetuple().tm_yday,
        y=_df.filter(pl.col("report_date") == switch2_latest["report_date"]).row(
            0, named=True
        )["yearly_sum_units"],
        x2=365,
        y2=4251000,
        stroke=[3, 2],
        size=2,
        color="#ffa00080",
    )
    switch2_yearly_cumulative_chart = mo.ui.altair_chart(_chart)
    mo.vstack(items=[switch2_yearly_cumulative_chart], justify="start")

    return


@app.cell
def switch2_heatmap_chart():
    _chart = g.chart_heatmap(
        hw="NS2",
        mode="week",
        scale_scheme="plasma",
        scale_type="log",
    )
    _chart = _chart.properties(height=200)
    switch2_heatmap_chart = mo.ui.altair_chart(_chart)
    mo.vstack(items=[switch2_heatmap_chart], justify="start")

    return


@app.cell(hide_code=True)
def md_switch2_yearly():
    mo.md(r"""
    Switch2の2026年累計は9月27日時点で2,576,286台です。前年同時期の2,109,622台を22.1%上回っていますが、前年は6月発売であるため、前年比には販売期間の違いも含まれます。発売69週時点の累計は6,360,353台で、同時点のSwitchを約184万台、PS5を約493万台上回る普及ペースです。

    52週平均による年間販売予測は約4,251,000台で、2025年通年の3,784,067台を上回る計算です。累計700万台までは残り639,647台で、52週平均なら11月下旬に到達します。ただし直近4週平均の29,790台では到達時期が大きく後ろ倒しになるため、予測には幅があります。今週は32,198台へ減少したものの、2026年累計はPS5の438,633台の約5.9倍で、市場を支える構図は続いています。
    """)
    return


@app.cell(hide_code=True)
def md_monthly_sales_trend_title():
    mo.md(r"""
    ## 月間販売推移
    """)
    return


@app.cell(hide_code=True)
def md_ns2_monthly_sales_title():
    mo.md(r"""
    ### Nintendo Switch2: 月間販売台数
    """)
    return


@app.cell
def switch2_monthly_sales_chart(report_date: datetime):
    _begin = g.years_ago(report_date)
    _end = report_date
    switch2_monthly_bar = mo.ui.altair_chart(
        g.chart_bar_hwsales_by_year(begin=_begin, end=_end, hw="NS2")
    )
    ns2_df = switch2_monthly_bar.dataframe
    ns2_df_pivot = ns2_df.pivot(index="month", on="year", values="monthly_units")
    mo.vstack(items=[switch2_monthly_bar], justify="start")

    return (ns2_df_pivot,)


@app.cell
def switch2_monthly_sales_table(ns2_df_pivot, report_date: datetime):
    _this_year = report_date.year
    # my_ns2_df2 = ns2_df_pivot.drop(str(_this_year - 2))
    my_ns2_df2 = ns2_df_pivot
    my_ns2_df2 = my_ns2_df2.with_columns(
        YoY=pl.col(str(_this_year)) / pl.col(str(_this_year - 1))
    )
    g.style_df(g.rename_columns(my_ns2_df2))

    return


@app.cell(hide_code=True)
def md_switch2_monthly():
    mo.md(r"""
    Switch2の9月販売は119,161台で確定しました。8月の139,165台から14.4%減、前年9月の175,542台から32.1%減です。最終週は32,198台で前週から6.2%減となり、9月後半の増加基調は月末に一服しました。

    直近4週平均は29,790台で、10月に入っても3万台前後の販売水準が続くかが焦点です。9月は前年の発売直後に近い高水準との比較になるため前年比の下落は大きいものの、年初からの累計は前年同時期を上回っています。
    """)
    return


@app.cell(hide_code=True)
def md_switch_monthly_sales_title():
    mo.md(r"""
    ### Nintendo Switch: 月間販売台数
    """)
    return


@app.cell
def switch_monthly_sales_chart(report_date: datetime):
    _begin = g.years_ago(report_date)
    _end = report_date
    switch_monthly_bar = mo.ui.altair_chart(
        g.chart_bar_hwsales_by_year(begin=_begin, end=_end, hw="NSW", ymax=480000)
    )
    ns_df = switch_monthly_bar.dataframe
    ns_df_pivot = ns_df.pivot(index="month", on="year", values="monthly_units")
    mo.vstack(items=[switch_monthly_bar], justify="start")

    return (ns_df_pivot,)


@app.cell
def switch_monthly_sales_table(ns_df_pivot, report_date: datetime):
    _this_year = report_date.year
    my_ns_df2 = ns_df_pivot.drop(str(_this_year - 2))
    my_ns_df2 = my_ns_df2.with_columns(
        YoY=pl.col(str(_this_year)) / pl.col(str(_this_year - 1))
    )
    g.style_df(g.rename_columns(my_ns_df2))

    return


@app.cell(hide_code=True)
def md_switch_monthly():
    mo.md(r"""
    Switchの9月販売は31,161台で確定しました。8月の38,211台から18.4%減、前年9月の82,946台から62.4%減です。最終週は6,306台へ前週比10.5%増となりましたが、月間では縮小傾向が続きます。

    直近4週平均は7,790台で、PS5の8,208台を下回っています。3,700万台到達を目前に控える一方、月間販売は前年の4割未満となっており、世代交代後の需要縮小が鮮明です。
    """)
    return


@app.cell(hide_code=True)
def md_ps5_monthly_sales_title():
    mo.md(r"""
    ### PlayStation 5: 月間販売台数
    """)
    return


@app.cell
def ps5_monthly_sales_chart(report_date: datetime):
    _begin = g.years_ago(report_date)
    _end = report_date
    ps5_monthly_bar = mo.ui.altair_chart(
        g.chart_bar_hwsales_by_year(begin=_begin, end=_end, hw="PS5", ymax=480000)
    )
    ps5_df = ps5_monthly_bar.dataframe
    ps5_df_pivot = ps5_df.pivot(index="month", on="year", values="monthly_units")
    mo.vstack(items=[ps5_monthly_bar], justify="start")

    return (ps5_df_pivot,)


@app.cell
def ps5_monthly_sales_table(ps5_df_pivot, report_date: datetime):
    _this_year = report_date.year
    my_ps5_df2 = ps5_df_pivot.drop(str(_this_year - 2))
    my_ps5_df2 = my_ps5_df2.with_columns(
        YoY=pl.col(str(_this_year)) / pl.col(str(_this_year - 1))
    )
    g.style_df(g.rename_columns(my_ps5_df2))

    return


@app.cell(hide_code=True)
def md_ps5_monthly():
    mo.md(r"""
    PS5の9月販売は32,831台で確定しました。8月の43,810台から25.1%減、前年9月の78,693台から58.3%減です。
    例年9月のPSはTGSにあわせてセール期間になり売上が上昇します｡
    しかし､今年は値下げ済みのPS5DE日本語版をこれ以上値下げすることが出来ず､有効なセールス施策が出来なかった影響が出ています｡
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Xbox Series X|S: 月間販売台数
    """)
    return


@app.cell
def xsx_monthly_sales_chart(report_date: datetime):
    _begin = g.years_ago(report_date)
    _end = report_date
    xsx_monthly_bar = mo.ui.altair_chart(
        g.chart_bar_hwsales_by_year(begin=_begin, end=_end, hw="XSX")
    )
    xsx_df = xsx_monthly_bar.dataframe
    xsx_df_pivot = xsx_df.pivot(index="month", on="year", values="monthly_units")
    mo.vstack(items=[xsx_monthly_bar], justify="start")

    return (xsx_df_pivot,)


@app.cell
def xsx_monthly_sales_table(report_date: datetime, xsx_df_pivot):
    _this_year = report_date.year
    my_xsx_df2 = xsx_df_pivot.drop(str(_this_year - 2))
    my_xsx_df2 = my_xsx_df2.with_columns(
        YoY=pl.col(str(_this_year)) / pl.col(str(_this_year - 1))
    )
    g.style_df(g.rename_columns(my_xsx_df2))

    return


@app.cell(hide_code=True)
def md_xsx_monthly():
    mo.md(r"""
    Xbox Series X|Sの9月販売は918台で確定しました。8月の659台から39.3%増加した一方、前年9月の1,121台からは18.1%減です。最終週は362台で前週の271台から33.6%増加しました。

    直近4週平均は230台で、月間では前月を上回ったものの販売規模そのものは小さい状態が続いています。月ごとの変動率だけでなく、週販の絶対水準を見ながら推移を確認したいところです。
    """)
    return


@app.cell(hide_code=True)
def md_cumulative_sales_trend_title():
    mo.md(r"""
    ## 累計販売推移
    """)
    return


@app.cell
def cumulative_sales_trend_chart(report_date: datetime):
    _chart = g.chart_line_cumulative(
        hw=["NSW", "NS2", "PS5", "XSX"],
        begin=datetime(2017, 3, 1),
        end=report_date,
        annotation_level=12,
        multi_line=True,
        mode="week",
        padding_end=6,
    )
    cumulative_chart = mo.ui.altair_chart(_chart)
    mo.vstack(items=[cumulative_chart], justify="start")

    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### 累計販売推移(Switch2, PS5拡大)
    """)
    return


@app.cell
def switch2_ps5_cumulative_chart(
    ps5_latest,
    report_date: datetime,
    switch2_latest,
):
    _chart = g.chart_line_cumulative(
        hw=["NS2", "PS5"],
        begin=datetime(2025, 5, 20),
        end=datetime(2026, 12, 31),
        annotation_level=30,
        multi_line=True,
        mode="week",
        padding_end=36,
    )
    _chart = g.chart_line_guide(
        base_chart=_chart,
        x=report_date.date(),
        y=switch2_latest["sum_units"],
        x2=date(2027, 1, 31),
        y2=7800000,
        stroke=[5, 4],
        size=2,
        color="#af000080",
    )
    _chart = g.chart_line_guide(
        base_chart=_chart,
        x=report_date.date(),
        y=ps5_latest["sum_units"],
        x2=date(2027, 1, 31),
        y2=7980000,
        stroke=[5, 4],
        size=2,
        color="#0040a080",
    )

    _chart_ns2_cumulative = mo.ui.altair_chart(_chart)
    _chart_ns2_cumulative

    return


@app.cell(hide_code=True)
def md_cumulative_ps5_switch2():
    mo.md(r"""
    9月27日時点の累計販売はPS5が7,736,843台、Switch2が6,360,353台で、差は1,376,490台です。今週はSwitch2がPS5を22,468台上回り、累計差は前週から縮まりました。

    52週平均ではSwitch2が週81,745台、PS5が13,075台で推移しており、この差が続く機械的な試算では約20週後の2027年2月ごろに逆転します。ただしSwitch2の52週平均には発売直後の高い販売が含まれます。直近4週平均の差は週21,582台で、こちらを基準にすると逆転は2027年末ごろまで後ろ倒しになります。足元のSwitch2販売が3万台前後で推移するかによって、逆転時期は大きく変わるでしょう。
    """)
    return


@app.cell
def md_ns2_sales_weeks_title(switch2_latest):
    _ns2_weeks = switch2_latest["index_week"]
    mo.md(f"### Switch2: {_ns2_weeks}週目の累計状況")

    return


@app.cell
def ns2_cumulative_delta_chart(ns2_info):
    _chart = g.chart_line_cumulative_delta(
        hw=[
            "NS2",
            "NSW",
            "3DS",
            "DS",
            "GBA",
        ],
        end=ns2_info["sales_weeks"] + 20,
        annotation_level=18,
        mode="week",
        with_point=False,
        multi_line=True,
    )
    _chart = g.chart_line_guide(
        base_chart=_chart,
        x=ns2_info["sales_weeks"],
        y=ns2_info["total_units"],
        x2=85,
        y2=7000000,
        stroke=[2, 3],
        size=2,
        color="#800000",
    )
    cd_chart = mo.ui.altair_chart(_chart)
    mo.vstack(items=[cd_chart], justify="start")

    return


@app.cell
def cumulative_top_chart(hard_sales_all_df: pl.DataFrame, ns2_info):
    cumulative_tops_df = (
        hard_sales_all_df.filter(pl.col("index_week") == ns2_info["sales_weeks"])
        .filter(pl.col("hw").is_in(["NS2", "NSW", "3DS", "GBA", "DS"]))
        .select("hw", "index_week", "report_date", "sum_units")
        .sort("sum_units", descending=True)
    )
    g.style_df(g.rename_columns(cumulative_tops_df))

    return


@app.cell(hide_code=True)
def md_cumulative_top():
    mo.md(r"""
    発売69週時点のSwitch2累計は6,360,353台です。同時点のDSは6,518,576台で、Switch2を158,223台上回り、Switch2は歴代2位です。一方、3DSは6,284,633台でSwitch2が75,720台上回り、GBAには約78万台、Switchには約184万台の差をつけています。

    次週のDS累計は6,728,371台まで伸びるため、DSとの差は当面広がる可能性が高いでしょう。3DSに対しては70週時点で6,351,586台、71週時点で6,416,853台となります。直近4週平均の29,790台を基準にすると、Switch2は3DSとの差を保てるかが10月前半の焦点です。歴代2位を維持するには、足元の3万台前後の販売を続ける必要があります。
    """)
    return


@app.cell(hide_code=True)
def md_yearly_sales_title():
    mo.md(r"""
    ## 年単位の状況
    """)
    return


@app.cell(hide_code=True)
def md_quarterly_title():
    mo.md(r"""
    ### 四半期ごとの状況
    """)
    return


@app.cell
def quarterly_sales_chart():
    _c1 = g.chart_bar_yearly_by_mode(
        begin=date(2016, 1, 1),
    )
    quarter_chart = mo.ui.altair_chart(_c1)
    mo.vstack([quarter_chart])

    return


@app.cell(hide_code=True)
def md_quarterly():
    mo.md(r"""
    2026年第3四半期は13週間で617,823台となりました。前年同期の1,325,743台を53.4%、2024年同期の1,094,959台を43.6%下回っています。Switch2が394,974台で全体の63.9%を占め、PS5が117,706台、Switchが102,435台で続きます。

    2001年以降の全四半期と比較しても、617,823台は最低の販売台数です。最終週は市場全体で前週比0.9%増となりましたが、四半期全体の低水準を覆すには至りませんでした。
    """)
    return


@app.cell
def _(hard_sales_all_df: pl.DataFrame):
    actual_target_date = date(2026, 9, 27)
    actual_source_date = hard_sales_all_df.select(pl.col("report_date").max()).item()

    if actual_source_date < actual_target_date:
        raise ValueError(
            f"9月27日の確定値が未取得です（最新実績日: {actual_source_date}）"
        )

    hardware_actual_df = (
        hard_sales_all_df
        .filter(pl.col("report_date") == actual_target_date)
        .select(
            "hw",
            "full_name",
            pl.col("units").alias("sep_27_units"),
            pl.col("ma4w").alias("four_week_avg"),
        )
        .join(
            hard_sales_all_df
            .filter(
                (pl.col("report_date") >= date(2026, 9, 1))
                & (pl.col("report_date") <= actual_target_date)
            )
            .group_by("hw")
            .agg(pl.col("units").sum().alias("sep_units")),
            on="hw",
        )
        .join(
            hard_sales_all_df
            .filter((pl.col("year") == 2026) & (pl.col("q_num") == 3))
            .group_by("hw")
            .agg(pl.col("units").sum().alias("q3_units")),
            on="hw",
        )
        .sort("hw")
    )

    _hardware_actual_display_df = hardware_actual_df.select(
        pl.col("hw").alias("ハード"),
        pl.col("full_name").alias("名称"),
        pl.col("four_week_avg").alias("直近4週平均（参考）"),
        pl.col("sep_27_units").alias("9月27日実績"),
        pl.col("sep_units").alias("2026年9月実績"),
        pl.col("q3_units").alias("2026年第3四半期実績"),
    )

    _hardware_actual_total_df = hardware_actual_df.select(
        pl.lit("TOTAL").alias("ハード"),
        pl.lit("合計").alias("名称"),
        pl.col("four_week_avg").sum().alias("直近4週平均（参考）"),
        pl.col("sep_27_units").sum().alias("9月27日実績"),
        pl.col("sep_units").sum().alias("2026年9月実績"),
        pl.col("q3_units").sum().alias("2026年第3四半期実績"),
    )

    hardware_actual_summary_df = pl.concat(
        [_hardware_actual_display_df, _hardware_actual_total_df],
        how="vertical",
    )

    return (hardware_actual_df,)


@app.cell
def _(hard_sales_all_df: pl.DataFrame, hardware_actual_df):
    q3_actual_total = hardware_actual_df.select(pl.col("q3_units").sum()).item()
    q3_actual_weeks = (
        hard_sales_all_df
        .filter((pl.col("year") == 2026) & (pl.col("q_num") == 3))
        .select(pl.col("report_date").n_unique())
        .item()
    )

    q3_historical_df = (
        hard_sales_all_df
        .filter(
            (pl.col("year") >= 2001)
            & (pl.col("year") <= 2025)
            & (pl.col("q_num") == 3)
        )
        .group_by("year")
        .agg(
            pl.col("units").sum().alias("q3_units"),
            pl.col("report_date").n_unique().alias("q3_weeks"),
        )
        .with_columns(
            (pl.col("q3_units") / pl.col("q3_weeks"))
            .round(0)
            .cast(pl.Int64)
            .alias("weekly_units")
        )
        .sort("year")
    )

    q3_history_comparison_df = (
        q3_historical_df
        .with_columns(pl.lit("実績").alias("区分"))
        .vstack(
            pl.DataFrame(
                {
                    "year": [2026],
                    "q3_units": [q3_actual_total],
                    "q3_weeks": [q3_actual_weeks],
                    "weekly_units": [round(q3_actual_total / q3_actual_weeks)],
                    "区分": ["実績"],
                },
                schema={
                    "year": pl.Int16,
                    "q3_units": pl.Int64,
                    "q3_weeks": pl.UInt32,
                    "weekly_units": pl.Int64,
                    "区分": pl.String,
                },
            )
        )
        .sort("year")
    )

    _q3_ranked_df = q3_history_comparison_df.with_columns(
        pl.col("q3_units").rank("ordinal", descending=True).alias("rank_desc")
    )
    q3_actual_rank = (
        _q3_ranked_df
        .filter(pl.col("year") == 2026)
        .select("rank_desc")
        .item()
    )

    _q3_2025_total = (
        q3_historical_df.filter(pl.col("year") == 2025).select("q3_units").item()
    )
    _q3_min_row = q3_historical_df.sort("q3_units").row(0, named=True)
    _q3_weekly_min_row = q3_historical_df.sort("weekly_units").row(0, named=True)
    _q3_historical_median = round(
        q3_historical_df.select(pl.col("q3_units").median()).item()
    )

    q3_evaluation_metrics = {
        "actual_total": q3_actual_total,
        "actual_weeks": q3_actual_weeks,
        "rank": q3_actual_rank,
        "rank_total": q3_history_comparison_df.height,
        "prior_year_total": _q3_2025_total,
        "prior_year_delta": q3_actual_total - _q3_2025_total,
        "prior_year_pct": round((q3_actual_total / _q3_2025_total - 1) * 100, 1),
        "historical_min_year": _q3_min_row["year"],
        "historical_min_total": _q3_min_row["q3_units"],
        "historical_min_delta": q3_actual_total - _q3_min_row["q3_units"],
        "historical_min_pct": round(
            (q3_actual_total / _q3_min_row["q3_units"] - 1) * 100,
            1,
        ),
        "historical_median": _q3_historical_median,
        "median_pct": round((q3_actual_total / _q3_historical_median - 1) * 100, 1),
        "weekly_actual": round(q3_actual_total / q3_actual_weeks),
        "weekly_min_year": _q3_weekly_min_row["year"],
        "weekly_min": _q3_weekly_min_row["weekly_units"],
        "weekly_min_pct": round(
            (q3_actual_total / q3_actual_weeks / _q3_weekly_min_row["weekly_units"] - 1)
            * 100,
            1,
        ),
    }

    q3_evaluation_df = pl.DataFrame(
        {
            "比較基準": [
                "2026年第3四半期実績",
                "2025年第3四半期実績",
                f"過去最低（{_q3_min_row['year']}年）",
                "2001〜2025年の中央値",
            ],
            "販売台数": [
                q3_actual_total,
                _q3_2025_total,
                _q3_min_row["q3_units"],
                _q3_historical_median,
            ],
            "2026年実績との差": [
                0,
                q3_actual_total - _q3_2025_total,
                q3_actual_total - _q3_min_row["q3_units"],
                q3_actual_total - _q3_historical_median,
            ],
            "差率（%）": [
                0.0,
                q3_evaluation_metrics["prior_year_pct"],
                q3_evaluation_metrics["historical_min_pct"],
                q3_evaluation_metrics["median_pct"],
            ],
        }
    )

    return (q3_actual_total,)


@app.cell
def _(hard_sales_all_df: pl.DataFrame, q3_actual_total):
    q1_q3_historical_wide_df = (
        hard_sales_all_df
        .filter(
            (pl.col("year") >= 2001)
            & (pl.col("year") <= 2025)
            & pl.col("q_num").is_in([1, 2, 3])
        )
        .group_by(["year", "q_num"])
        .agg(pl.col("units").sum().alias("units"))
        .pivot(on="q_num", index="year", values="units", aggregate_function="first")
        .rename({"1": "q1_units", "2": "q2_units", "3": "q3_units"})
        .with_columns(
            (pl.col("q1_units") + pl.col("q2_units")).alias("h1_units"),
            (pl.col("q1_units") + pl.col("q2_units") + pl.col("q3_units")).alias("q1_q3_units"),
        )
        .select("year", "q1_units", "q2_units", "q3_units", "h1_units", "q1_q3_units")
        .sort("year")
    )

    _q1_2026_units = hard_sales_all_df.filter(
        (pl.col("year") == 2026) & (pl.col("q_num") == 1)
    ).select(pl.col("units").sum()).item()
    _q2_2026_units = hard_sales_all_df.filter(
        (pl.col("year") == 2026) & (pl.col("q_num") == 2)
    ).select(pl.col("units").sum()).item()

    q1_q3_2026_df = pl.DataFrame(
        {
            "year": [2026],
            "q1_units": [_q1_2026_units],
            "q2_units": [_q2_2026_units],
            "q3_units": [q3_actual_total],
            "h1_units": [_q1_2026_units + _q2_2026_units],
            "q1_q3_units": [_q1_2026_units + _q2_2026_units + q3_actual_total],
        },
        schema={
            "year": pl.Int16,
            "q1_units": pl.Int64,
            "q2_units": pl.Int64,
            "q3_units": pl.Int64,
            "h1_units": pl.Int64,
            "q1_q3_units": pl.Int64,
        },
    )
    q1_q3_all_years_df = q1_q3_historical_wide_df.vstack(q1_q3_2026_df)

    def _q1_q3_metric(_column):
        _value = q1_q3_2026_df.select(_column).item()
        _median = round(q1_q3_historical_wide_df.select(pl.col(_column).median()).item())
        _rank_desc = q1_q3_all_years_df.with_columns(
            pl.col(_column).rank("ordinal", descending=True).alias("rank")
        ).filter(pl.col("year") == 2026).select("rank").item()
        _prior_year_value = q1_q3_historical_wide_df.filter(
            pl.col("year") == 2025
        ).select(_column).item()
        return {
            "value": _value,
            "median": _median,
            "median_pct": round((_value / _median - 1) * 100, 1),
            "low_rank": q1_q3_all_years_df.height - _rank_desc + 1,
            "rank_total": q1_q3_all_years_df.height,
            "yoy_delta": _value - _prior_year_value,
            "yoy_pct": round((_value / _prior_year_value - 1) * 100, 1),
        }

    q1_q3_evaluation_metrics = {
        "1Q": _q1_q3_metric("q1_units"),
        "2Q": _q1_q3_metric("q2_units"),
        "3Q": _q1_q3_metric("q3_units"),
        "上期": _q1_q3_metric("h1_units"),
        "1〜3Q累計": _q1_q3_metric("q1_q3_units"),
    }

    q1_q3_evaluation_df = pl.DataFrame(
        {
            "期間": ["1Q", "2Q", "3Q", "1〜3Q累計"],
            "2026年販売台数": [
                q1_q3_evaluation_metrics["1Q"]["value"],
                q1_q3_evaluation_metrics["2Q"]["value"],
                q1_q3_evaluation_metrics["3Q"]["value"],
                q1_q3_evaluation_metrics["1〜3Q累計"]["value"],
            ],
            "2001〜2025年中央値": [
                q1_q3_evaluation_metrics["1Q"]["median"],
                q1_q3_evaluation_metrics["2Q"]["median"],
                q1_q3_evaluation_metrics["3Q"]["median"],
                q1_q3_evaluation_metrics["1〜3Q累計"]["median"],
            ],
            "平均との差率（%）": [
                q1_q3_evaluation_metrics["1Q"]["median_pct"],
                q1_q3_evaluation_metrics["2Q"]["median_pct"],
                q1_q3_evaluation_metrics["3Q"]["median_pct"],
                q1_q3_evaluation_metrics["1〜3Q累計"]["median_pct"],
            ],
            "低い方からの順位（26年中）": [
                q1_q3_evaluation_metrics["1Q"]["low_rank"],
                q1_q3_evaluation_metrics["2Q"]["low_rank"],
                q1_q3_evaluation_metrics["3Q"]["low_rank"],
                q1_q3_evaluation_metrics["1〜3Q累計"]["low_rank"],
            ],
            "前年比（%）": [
                q1_q3_evaluation_metrics["1Q"]["yoy_pct"],
                q1_q3_evaluation_metrics["2Q"]["yoy_pct"],
                q1_q3_evaluation_metrics["3Q"]["yoy_pct"],
                q1_q3_evaluation_metrics["1〜3Q累計"]["yoy_pct"],
            ],
        }
    )

    q1_q3_history_long_df = q1_q3_all_years_df.select(
        "year", "q1_units", "q2_units", "q3_units"
    ).unpivot(index="year", variable_name="quarter", value_name="units").with_columns(
        pl.col("quarter").replace({"q1_units": "1Q", "q2_units": "2Q", "q3_units": "3Q"}),
        pl.lit("実績").alias("区分"),
    )

    return q1_q3_evaluation_df, q1_q3_evaluation_metrics, q1_q3_history_long_df


@app.cell
def _(q1_q3_evaluation_df, q1_q3_evaluation_metrics, q1_q3_history_long_df):
    _q1 = q1_q3_evaluation_metrics["1Q"]
    _q2 = q1_q3_evaluation_metrics["2Q"]
    _q3 = q1_q3_evaluation_metrics["3Q"]
    _h1 = q1_q3_evaluation_metrics["上期"]
    _ytd = q1_q3_evaluation_metrics["1〜3Q累計"]

    _quarter_chart_base = alt.Chart(q1_q3_history_long_df)
    _quarter_history_chart = _quarter_chart_base.transform_filter(
        alt.datum.year < 2026
    ).mark_line(point=True).encode(
        x=alt.X("year:O", title="年"),
        y=alt.Y("units:Q", title="販売台数"),
        color=alt.Color("quarter:N", title="四半期"),
        tooltip=[
            alt.Tooltip("year:O", title="年"),
            alt.Tooltip("quarter:N", title="四半期"),
            alt.Tooltip("units:Q", title="販売台数", format=","),
        ],
    )
    _quarter_2026_points = _quarter_chart_base.transform_filter(
        alt.datum.year == 2026
    ).mark_point(filled=True, size=110).encode(
        x=alt.X("year:O", title="年"),
        y=alt.Y("units:Q", title="販売台数"),
        color=alt.Color("quarter:N", title="四半期"),
        tooltip=[
            alt.Tooltip("year:O", title="年"),
            alt.Tooltip("quarter:N", title="四半期"),
            alt.Tooltip("区分:N", title="区分"),
            alt.Tooltip("units:Q", title="販売台数", format=","),
        ],
    )

    mo.vstack([
        mo.md(f"""
    ## 2026年1〜3Qの歴史比較

    **結論：3Qが特異的に弱いです。** 年初から弱含みではあるものの、歴史的な低水準に落ち込んだのは3Qです。

    - **1Q** は{_q1['value']:,}台です。中央値比{_q1['median_pct']:+.1f}%で、低い方から{_q1['low_rank']}位です。やや低めですが、過去最低圏ではありません。
    - **2Q** は{_q2['value']:,}台です。中央値比{_q2['median_pct']:+.1f}%で、低い方から{_q2['low_rank']}位です。おおむね歴史的な中央値の水準です。
    - **上期累計** は{_h1['value']:,}台です。中央値比{_h1['median_pct']:+.1f}%で、前年上期比は{_h1['yoy_pct']:+.1f}%です。
    - **3Q実績** は{_q3['value']:,}台です。中央値比{_q3['median_pct']:+.1f}%で、低い方から{_q3['low_rank']}位（最下位）です。前年同期比は{_q3['yoy_pct']:+.1f}%です。
    - **1〜3Q累計** は{_ytd['value']:,}台で、中央値比{_ytd['median_pct']:+.1f}%、低い方から{_ytd['low_rank']}位です。上期の弱さよりも、3Qの急落が累計を大きく押し下げています。
    """),
        q1_q3_evaluation_df,
        (_quarter_history_chart + _quarter_2026_points).properties(
            width=720, height=340, title="1〜3Qのハード販売台数推移（2001年以降）"
        ),
    ])

    return


@app.cell
def _(hard_sales_all_df: pl.DataFrame):
    _quarter_rank_historical_df = hard_sales_all_df.filter(
        (pl.col("year") >= 2001) & (pl.col("year") <= 2025)
    ).group_by(["year", "q_num"]).agg(
        pl.col("units").sum().alias("販売台数"),
        pl.col("report_date").n_unique().alias("週数"),
    ).with_columns(
        (pl.col("販売台数") / pl.col("週数")).round(0).cast(pl.Int64).alias("週平均販売台数"),
        pl.lit("実績").alias("区分"),
    )
    _quarter_rank_2026_df = hard_sales_all_df.filter(
        (pl.col("year") == 2026) & pl.col("q_num").is_in([1, 2, 3])
    ).group_by(["year", "q_num"]).agg(
        pl.col("units").sum().alias("販売台数"),
        pl.col("report_date").n_unique().alias("週数"),
    ).with_columns(
        (pl.col("販売台数") / pl.col("週数")).round(0).cast(pl.Int64).alias("週平均販売台数"),
        pl.lit("実績").alias("区分"),
    )
    quarterly_rank_all_df = pl.concat([
        _quarter_rank_historical_df, _quarter_rank_2026_df
    ]).with_columns(
        pl.col("販売台数").rank("ordinal", descending=True).alias("販売台数順位"),
        pl.col("週平均販売台数").rank("ordinal", descending=True).alias("週平均順位"),
    ).sort(["year", "q_num"])

    _quarter_rank_current = quarterly_rank_all_df.filter(
        (pl.col("year") == 2026) & (pl.col("q_num") == 3)
    ).row(0, named=True)
    _quarter_rank_previous_min = quarterly_rank_all_df.filter(
        ~((pl.col("year") == 2026) & (pl.col("q_num") == 3))
    ).sort("販売台数").row(0, named=True)
    quarterly_rank_metrics = {
        "rank": _quarter_rank_current["販売台数順位"],
        "weekly_rank": _quarter_rank_current["週平均順位"],
        "count": quarterly_rank_all_df.height,
        "previous_min_year": _quarter_rank_previous_min["year"],
        "previous_min_quarter": _quarter_rank_previous_min["q_num"],
        "previous_min_units": _quarter_rank_previous_min["販売台数"],
        "previous_min_delta": _quarter_rank_current["販売台数"] - _quarter_rank_previous_min["販売台数"],
        "previous_min_pct": round((_quarter_rank_current["販売台数"] / _quarter_rank_previous_min["販売台数"] - 1) * 100, 1),
    }
    quarterly_rank_lowest_df = quarterly_rank_all_df.with_columns(
        pl.format("{}Q{}", pl.col("year"), pl.col("q_num")).alias("四半期")
    ).select(
        "四半期", "区分", "販売台数", "週数", "週平均販売台数", "販売台数順位", "週平均順位"
    ).sort("販売台数")

    return quarterly_rank_lowest_df, quarterly_rank_metrics


@app.cell
def _(q3_actual_total, quarterly_rank_metrics):
    _quarter_rank = quarterly_rank_metrics
    mo.vstack([
        mo.md(f"""
    ## 全四半期に対する2026年3Qの順位

    2001年1Q〜2026年3Qの**103四半期**を比較すると、2026年3Q実績の{q3_actual_total:,}台は **{_quarter_rank['rank']}位 / {_quarter_rank['count']}位（最下位）** です。13週あたりの週平均でも **{_quarter_rank['weekly_rank']}位 / {_quarter_rank['count']}位（最下位）** です。

    従来の最低は{_quarter_rank['previous_min_year']}年{_quarter_rank['previous_min_quarter']}Qの{_quarter_rank['previous_min_units']:,}台で、2026年3Qは **{abs(_quarter_rank['previous_min_delta']):,}台（{_quarter_rank['previous_min_pct']:+.1f}%）**下回ります。
    """),
 
    ])

    return


@app.cell
def _(quarterly_rank_lowest_df):
    _quarterly_bottom10 = quarterly_rank_lowest_df.head(10)
    _quarterly_bottom10_bar = alt.Chart(_quarterly_bottom10).mark_bar().encode(
        y=alt.Y("四半期:N", sort=alt.SortField(field="販売台数", order="ascending"), title=None),
        x=alt.X("販売台数:Q", title="販売台数"),
        color=alt.condition(alt.datum.四半期 == "2026Q3", alt.value("#e45756"), alt.value("#4c78a8")),
        tooltip=[
            alt.Tooltip("四半期:N", title="四半期"), alt.Tooltip("区分:N", title="区分"),
            alt.Tooltip("販売台数:Q", title="販売台数", format=","), alt.Tooltip("週数:Q", title="週数"),
            alt.Tooltip("週平均販売台数:Q", title="週平均", format=","),
        ],
    )
    _quarterly_bottom10_text = alt.Chart(_quarterly_bottom10).mark_text(align="left", dx=4).encode(
        y=alt.Y("四半期:N", sort=alt.SortField(field="販売台数", order="ascending")),
        x=alt.X("販売台数:Q"), text=alt.Text("販売台数:Q", format=","),
    )
    mo.vstack([
        mo.md("## 四半期集計ワースト10"),
        (_quarterly_bottom10_bar + _quarterly_bottom10_text).properties(
            width=720, height=330, title="2001年以降の四半期販売台数：ワースト10"
        ),
        mo.md("赤は2026年3Qの確定実績、青はその他の実績値です。"),
    ])

    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### 機種ごとの状況
    """)
    return


@app.cell
def yearly_sales_chart(report_date: datetime):
    yearly_bar = mo.ui.altair_chart(
        g.chart_bar_sales(
            mode="year",
            stacked=True,
            begin=g.years_ago(report_date, 10),
            end=report_date,
        )
    )
    year_df = yearly_bar.dataframe
    mo.vstack(items=[yearly_bar], justify="start")

    return (year_df,)


@app.cell
def yearly_sales_table(year_df):
    year_pivot_df = year_df.pivot(index="year", on="hw", values="yearly_units")
    year_pivot_df = year_pivot_df.with_columns(
        合計=pl.sum_horizontal(pl.exclude("year", "合計"))
    )
    g.style_df(year_pivot_df)

    return


@app.cell(hide_code=True)
def md_yearly_hard():
    mo.md(r"""
    2026年の主要4機種のハード販売は9月27日時点で合計3,602,526台です。Switch2が2,576,286台で全体の71.5%を占め、Switchの570,699台、PS5の438,633台、Xbox Series X|Sの16,908台が続きます。

    前年同時期の3,906,405台を7.8%下回る一方、2024年同時期の3,336,566台は8.0%上回っています。Switch2は前年から466,664台増えましたが、Switchは561,968台、PS5は199,296台減少し、両機種の落ち込みがSwitch2の増加を上回りました。第3四半期が歴史的な低水準となったため、年末商戦で市場全体をどこまで積み上げられるかが重要になります。
    """)
    return


@app.cell(hide_code=True)
def md_yearly_maker_share_title():
    mo.md(r"""
    ### 年単位のメーカーシェア
    """)
    return


@app.cell
def yearly_maker_share_chart():
    _chart = g.chart_hbar_yearly_share_by_maker(date(2015, 1, 1), date(2026, 12, 31))
    share_chart = mo.ui.altair_chart(_chart)
    mo.vstack(items=[share_chart], justify="start")

    return


@app.cell(hide_code=True)
def md_yearly_maker_share():
    mo.md(r"""
    2026年のメーカー別シェアは9月27日時点で任天堂が87.4%、ソニーが12.2%、マイクロソフトが0.5%です。Switch2だけで主要4機種の71.5%を占めることが、高い任天堂シェアを支えています。任天堂のシェアは2025年通年の85.3%、2024年の66.2%を上回っています。

    52週平均を年換算した試算では、年間シェアは任天堂が約88.1%、ソニーが約11.5%、マイクロソフトが約0.4%です。Switch2の52週平均には発売直後の高い販売が含まれる一方、足元では週3万台前後で推移しています。第4四半期にPS5がどこまで販売を伸ばせるかによって、実際の年末シェアは変動するでしょう。
    """)
    return


@app.cell
def report_metadata():
    # cell_name: 記事が含まれるマークダウンセルの名前
    # description: 各記事が含まれるマークダウンセルの内容の概要
    # calc_cells: 各記事の言及対象となる計算処理､データが含まれるセル名｡概ね記事セルの直前に配置されているセルであることが多いが､必ずしもそうでない場合もある。

    md_summaries = [
        {
            "cell_name": "md_top",
            "calc_cells": ["units_by_date_hw_table"],
            "description": """
        今週の売上概況を､主に先週と比較しながら説明する｡トピックとなりそうな変化があるか確認し､
        変化があればそれについて言及する｡トピックとなる変化の例としては100万台単位の節目､歴代最高､最低の販売台数です｡
        annotation_dfに書かれているゲーム関係のイベントが影響した可能性も考慮し､影響の有無､大小について言及する｡
        annotation_dfに含まれる次回集計､次々回集計時に該当するイベント情報を確認し､それが将来に与える影響の予想も含めて記述する｡
        """,
        },
        {
            "cell_name": "md_weekly_chart",
            "calc_cells": ["weekly_sales_trend", "weekly_sales_trend_2"],
            "description": """
        週間販売折れ線グラフの説明､先週と比較しつつ､機種同士の比較や､順位の変動､今後の見通し､考察を含めて解説｡
        久しぶり(4週間以上)の順位変動が発生した場合は､その変動について特に言及する｡
        折れ線グラフの解説なので､数値の変化や傾向を説明することが重要です｡
        md_topと内容的に重複してもよいが､表現が全く同じにならないよう工夫する｡
         """,
        },
        {
            "cell_name": "md_ps5_yearly",
            "calc_cells": ["ps5_yearly_cumulative_chart", "ps5_heatmap_chart"],
            "description": """
         PS5の今年の販売状況を昨年､一昨年と比較､年末までの見通しについて記述｡将来予想は52週平均を用いる｡
         100万台単位を節目とし､節目の到達時期が3ヶ月以内の場合は特に言及する｡
         その際には､過去のPS3, PS4の状況との比較を行い､考察を加える｡
         """,
        },
        {
            "cell_name": "md_switch_yearly",
            "calc_cells": ["switch_yearly_cumulative_chart", "switch_heatmap_chart"],
            "description": """
         Switchの今年の販売状況を昨年､一昨年と比較､年末までの見通しについて記述
         将来予想は52週平均を用いる｡
         100万台単位を節目とし､節目の到達時期が3ヶ月以内の場合は特に言及する｡
         """,
        },
        {
            "cell_name": "md_switch2_yearly",
            "calc_cells": ["switch2_yearly_cumulative_chart", "switch2_heatmap_chart"],
            "description": """
         Switch2の今年の販売状況を昨年と比較､年末までの見通しについて記述
         将来予想は52週平均を用いる｡
         100万台単位を節目とし､節目の到達時期が3ヶ月以内の場合は特に言及する｡
         その際には､前世代機のSwitchの状況､ ライバル機のPS5の状況との比較を行い､考察を加える｡
         """,
        },
        {
            "cell_name": "md_switch2_monthly",
            "calc_cells": [
                "switch2_monthly_sales_table",
                "switch2_monthly_sales_chart",
            ],
            "description": """
         Switch2の今月の販売状況を昨年同月､先月と比較して説明｡
         その月の最終週には一ヶ月のサマリーを､それ以外は月末時点での見通しを記述
         """,
        },
        {
            "cell_name": "md_switch_monthly",
            "calc_cells": ["switch_monthly_sales_table", "switch_monthly_sales_chart"],
            "description": """
         Switchの今月の販売状況を昨年同月､先月と比較して説明｡
         その月の最終週には一ヶ月のサマリーを､それ以外は月末時点での見通しを記述
         """,
        },
        {
            "cell_name": "md_ps5_monthly",
            "calc_cells": ["ps5_monthly_sales_table", "ps5_monthly_sales_chart"],
            "description": """
         PS5の今月の販売状況を昨年同月､先月と比較して説明｡
         その月の最終週には一ヶ月のサマリーを､それ以外は月末時点での見通しを記述
         """,
        },
        {
            "cell_name": "md_xsx_monthly",
            "calc_cells": ["xsx_monthly_sales_chart", "xsx_monthly_sales_table"],
            "description": """
         Xbox Series X|S の今月の販売状況を昨年同月､先月と比較して説明｡
         その月の最終週には一ヶ月のサマリーを､それ以外は月末時点での見通しを記述
         """,
        },
        {
            "cell_name": "md_cumulative_ps5_switch2",
            "calc_cells": ["switch2_ps5_cumulative_chart"],
            "description": """
         PS5とSwitch2の累計比較記事｡特にSwitch2がPS5に追いつく時期の予想を含めて記述｡
         予想には主に52週平均を用いるが､他の方法を用いて比較しても良い｡
         累計台数差の100万台､50万台単位の節目を超えた場合には､それについても言及する｡
         """,
        },
        {
            "cell_name": "md_cumulative_top",
            "calc_cells": ["ns2_cumulative_delta_chart", "cumulative_top_chart"],
            "description": """
         歴代のハードの初期の累計推移を比較する記事｡特にSwitch2を他機種と比較した状況､今後の見通しを記述｡
         Switch2の歴代一位の状況が今後どうなるのかについては特に言及する｡
         100万台単位の節目を超えた場合には､それについても言及し､過去の歴代機種や､現役の他機種との比較､考察を行う｡
         """,
        },
        {
            "cell_name": "md_quarterly",
            "calc_cells": ["quarterly_sales_chart"],
            "description": """
         各年の四半期販売状況と今期の状況を比較して短く解説
         """,
        },
        {
            "cell_name": "md_yearly_hard",
            "calc_cells": ["yearly_sales_chart", "yearly_sales_table"],
            "description": """
         各年の各ハードの状況と､今年の状況を比較して短く解説
         """,
        },
        {
            "cell_name": "md_yearly_maker_share",
            "calc_cells": ["yearly_maker_share_chart"],
            "description": """
         各年の各ハードのメーカーシェアの状況と､今年の状況を比較し解説｡
         52週平均を用いた予測値で､今年の最終的なメーカーシェアの見通しも記述する｡
         """,
        },
    ]

    return


if __name__ == "__main__":
    app.run()
