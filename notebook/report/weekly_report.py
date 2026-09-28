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
    hard_sales_df: pl.DataFrame = g.load_hard_sales(True)
    annotation_df: pl.DataFrame = g.load_hard_annotation(no_cache=True)

    return (hard_sales_df,)


@app.cell
def report_setup(hard_sales_df: pl.DataFrame, is_publish):
    # レポート日付
    from report_config import get_config

    config = get_config()
    report_date: datetime = config["date"]

    def show_title(d: datetime):
        last_updated_str = d.strftime("%Y-%m-%d")
        mode: str = "**DRAFT**" if not is_publish else ""
        return mo.md(f"# 国内ゲームハード週販レポート ({last_updated_str}) {mode}")

    [ns2_info, ps5_info, nsw_info] = g.hard_sales_summary(
        hard_sales_df, hw=["NS2", "PS5", "NSW"]
    )

    return ns2_info, report_date, show_title


@app.cell
def _(hard_sales_df: pl.DataFrame):
    _df_latest = g.extract_latest(hard_sales_df, 1)
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
def units_by_date_hw_table(hard_sales_df: pl.DataFrame, report_date: datetime):
    _table = g.units_by_date_hw_table(
        hard_sales_df, begin=g.weeks_before(report_date, 3), end=report_date
    )
    mo.hstack(items=[_table], justify="start", wrap=True)

    return


@app.cell(hide_code=True)
def md_top():
    mo.md(r"""
    9月20日は4機種合計で48,164台となり、前週から10.6%増加しました。Switch2とPS5、Xbox Series X|Sが増加した一方、Switchは減少しました。

    Switch2は34,341台で前週比21.2%増となり、4週連続で増加しました。PS5は7,847台で4.7%増え、5,705台へ24.5%減少したSwitchを上回って2位に戻りました。Switchの週販は発売後3番目に低い水準です。Xbox Series X|Sは271台へ増加しましたが、販売規模は引き続き小さくなっています。

    今週はSwitch2向けの「ファイアーエムブレム万紫千紅(9/17)」の時期と重なり、Switch2の増加を後押ししました｡一方、PS5は「Marvel's Wolverine(9/15)」があったものの増加は小幅で、
    ハード牽引効果は限定的です。次回集計では「SILENT HILL:Townfall(9/24)」、次々回では「ACE COMBAT8(10/2)」が反映されるため、PS5の販売水準が持ち直すかを確認したいところです。
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
    Switch2は34,341台で前週から6,000台増え、直近4週平均も27,307台へ上昇しました。4週連続の増加は2025年11月23日以来です。
    グラフで見ると力強い上昇ですがお盆前の水準には戻っていません｡
    「ファイアーエムブレム万紫千紅(9/17)」によるハード牽引効果と回復基調が重なったものと思われます｡

    PS5は7,847台へ4.7%増加し、5,705台へ24.5%減少したSwitchを上回って3週ぶりに2位へ戻りました。ただし直近4週平均はSwitchが8,426台、PS5が7,613台で、平均ではなおSwitchが上回っています。PS5は次回の「SILENT HILL:Townfall(9/24)」、次々回の「ACE COMBAT8(10/2)」が販売を支えられるかが焦点です。Xbox Series X|Sは271台へ増えましたが、他機種との差は大きい状態が続いています。
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
        y2=687000,
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
    PS5の2026年累計は9月20日時点で428,903台です。前年同時期の621,018台を30.9%下回り、2024年同時期の1,082,486台に対しては60.4%少ない水準です。歴代PlayStationとの比較ではPS3の2014年同時期374,636台を14.5%上回る一方、PS4の2018年同時期1,197,198台には大きく届きません。

    52週平均による年間販売予測は約687,000台で、2025年通年の879,204台を下回る見込みです。今週は7,847台へ小幅に増えましたが、直近4週平均は7,613台にとどまります。「Marvel's Wolverine(9/15)」の時期にも大きな上昇は見られず、次回以降の「SILENT HILL:Townfall(9/24)」「ACE COMBAT8(10/2)」が年末へ向けた回復材料になるかが注目されます。
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
        y2=975000,
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
    Switchの2026年累計は9月20日時点で564,393台です。前年同時期の1,109,557台から49.1%減、2024年同時期の2,081,675台から72.9%減となり、発売からの経過に伴う縮小が続いています。

    52週平均による年間販売予測は約975,000台で、2025年通年の1,520,384台を下回る見込みです。累計は36,980,554台となり、3,700万台まで残り19,446台です。52週平均では約1週分ですが、今週は発売後3番目に低い5,705台、直近4週平均も8,426台であり、到達は次回から10月前半にかけてとなる可能性が高いでしょう。
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
        y2=4260000,
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
    Switch2の2026年累計は9月20日時点で2,544,088台です。前年同時期の2,065,472台を23.2%上回っていますが、前年は6月発売であるため、前年比には販売期間の違いも含まれます。発売68週時点の累計は6,328,155台で、同時点のSwitchを約185万台、PS5を約493万台上回る普及ペースです。

    52週平均による年間販売予測は約4,263,000台で、2025年通年の3,784,067台を上回る計算です。累計700万台までは残り671,845台で、52週平均なら約8週後の11月中旬に到達します。ただし直近4週平均の27,307台では約25週を要するため、予測には幅があります。「ファイアーエムブレム万紫千紅(9/17)」の効果により､4週連続で販売が増えたことは明るい材料です。2026年累計はPS5の428,903台の約5.9倍で、市場を支える構図は続いています。
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
    Switch2の9月第3週の販売は34,341台で、前週の28,341台から21.2%増加しました。9月は3週合計で86,963台となり、4週連続で増加しています。

    8月の139,165台に並ぶには最終週に52,202台、前年9月の175,542台に並ぶには88,579台が必要です。9月の3週平均を単純に延長すると月間約116,000台となり、8月と前年同月をともに下回る見通しです。「ファイアーエムブレム万紫千紅(9/17)」による牽引効果を月末まで維持できるかが焦点です。
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
    Switchの9月第3週の販売は5,705台で、前週の7,559台から24.5%減少しました。発売後3番目に低い週販となり、9月は3週合計で24,855台です。

    8月の38,211台に並ぶには最終週に13,356台、前年9月の82,946台に並ぶには58,091台が必要です。9月の3週平均を単純に延長した月間見通しは約33,000台で、8月を13%程度、前年同月を60%程度下回ります。直近4週平均ではPS5を上回っているものの、足元の減少から月末に大きく持ち直す材料は限られます。
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
    PS5の9月第3週の販売は7,847台で、前週の7,494台から4.7%増加しました。9月は3週合計で23,101台となっています。

    8月の43,810台に並ぶには最終週に20,709台、前年9月の78,693台に並ぶには55,592台が必要です。9月の3週平均を単純に延長した月間見通しは約31,000台で、8月、前年同月のいずれも下回ります。「PS5DE日本語版新規購入キャンペーン ~3/31(9/14)」「Marvel's Wolverine(9/15)」「東京ゲームショウ2026 9/17~9/21」の時期の増加は小幅でした。月末の「SILENT HILL:Townfall(9/24)」で販売水準を引き上げられるかが注目されます。
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
    Xbox Series X|Sの9月第3週の販売は271台で、前週の158台から71.5%増加しました。9月は3週合計で556台です。

    8月の659台を上回るには最終週に104台が必要で、直近4週平均214台を維持すれば前月を上回る見込みです。一方、前年9月の1,121台に並ぶには565台が必要で、前年同月には届きにくい状況です。週ごとの増加率は大きいものの、販売規模そのものは引き続き小さくなっています。
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
    9月20日時点の累計販売はPS5が7,727,113台、Switch2が6,328,155台で、差は1,398,958台です。今週はSwitch2がPS5を26,494台上回り、150万台を下回っている差がさらに縮まりました。

    52週平均ではSwitch2が週81,975台、PS5が13,213台で推移しており、この差が続く機械的な試算では約20週後の2027年2月ごろに逆転します。ただしSwitch2の52週平均には発売直後の高い販売が含まれます。直近4週平均の差は週19,694台で、こちらを基準にすると逆転は約71週後の2028年2月ごろです。Switch2は4週連続で増加しており、この回復が続くかによって逆転時期は大きく変わります。
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
        y2=6930000,
        stroke=[2, 3],
        size=2,
        color="#800000",
    )
    cd_chart = mo.ui.altair_chart(_chart)
    mo.vstack(items=[cd_chart], justify="start")

    return


@app.cell
def cumulative_top_chart(hard_sales_df: pl.DataFrame, ns2_info):
    cumulative_tops_df = (
        hard_sales_df.filter(pl.col("index_week") == ns2_info["sales_weeks"])
        .filter(pl.col("hw").is_in(["NS2", "NSW", "3DS", "GBA", "DS"]))
        .select("hw", "index_week", "report_date", "sum_units")
        .sort("sum_units", descending=True)
    )
    g.style_df(g.rename_columns(cumulative_tops_df))

    return


@app.cell(hide_code=True)
def md_cumulative_top():
    mo.md(r"""
    発売68週時点のSwitch2累計は6,328,155台です。同時点のDSは6,356,952台で、Switch2を28,797台上回りました。Switch2は発売67週まで維持していた歴代首位をDSに譲り、2位となっています。一方、3DSは6,228,239台でSwitch2が99,916台上回り、GBAには約78万台、Switchには約185万台の差をつけています。

    今週のSwitch2は34,341台まで増えましたが、同じ68週目のDSは135,791台でした。次週のDS累計6,518,576台を再び上回るには190,422台以上が必要で、当面はDSが首位を広げる可能性が高いでしょう。3DSに対しては、71週目までの3週間で合計88,699台、週平均約29,600台を販売すれば2位を維持できます。直近4週平均27,307台のままでは71週目の10月11日ごろに3DSにも上回られる計算で、「ファイアーエムブレム万紫千紅(9/17)」後の増加を維持できるかが焦点です。
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
    2026年第3四半期は9月20日までの12週間で569,227台です。同じ暦日までの前年同期1,174,990台を51.6%、2024年同期947,473台を39.9%下回っています。Switch2が362,776台で全体の63.7%を占め、PS5が107,976台、Switchが96,129台で続きます。

    今週は市場全体が前週比10.6%増となりましたが、前年までの四半期水準との差は大きいままです。四半期末の次回集計では「SILENT HILL:Townfall(9/24)」が反映されるため、PS5を中心に最後の1週でどこまで積み増せるかを確認したいところです。
    """)
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
    2026年の主要4機種のハード販売は9月20日時点で合計3,553,930台です。Switch2が2,544,088台で全体の71.6%を占め、Switchの564,393台、PS5の428,903台、Xbox Series X|Sの16,546台が続きます。

    前年同時期の3,821,793台を7.0%下回る一方、2024年同時期の3,250,859台は9.3%上回っています。Switch2は前年から478,616台増えましたが、Switchは545,164台、PS5は192,115台減少し、両機種の落ち込みがSwitch2の増加を上回りました。Switch2は4週連続で回復しており、この流れを年末まで維持できるかが市場全体の見通しを左右します。
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
    2026年のメーカー別シェアは9月20日時点で任天堂が87.5%、ソニーが12.1%、マイクロソフトが0.5%です。Switch2だけで主要4機種の71.6%を占めることが、高い任天堂シェアを支えています。任天堂のシェアは2025年通年の85.3%、2024年の66.2%を上回っています。

    52週平均を年換算した試算では、年間シェアは任天堂が約88.1%、ソニーが約11.6%、マイクロソフトが約0.4%です。Switch2の52週平均には発売直後の高い販売が含まれる一方、足元では4週連続で増加しています。今後の販売が直近の回復を維持できるかによって、実際の年末シェアは変動するでしょう。
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
        変化があればそれについて言及する｡トピックとなる変化の例としては100万台単位の節目､歴代最高､最低の販売台数である｡
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
        折れ線グラフの解説なので､数値の変化や傾向を説明するのが重要である｡
        md_topと内容的に重複してもよいが､表現が全く同じにならないよう工夫する｡
         """,
        },
        {
            "cell_name": "md_ps5_yearly",
            "calc_cells": ["ps5_yearly_cumulative_chart", "ps5_heatmap_chart"],
            "description": """
         PS5の今年の販売状況を昨年､一昨年と比較､年末までの見通しについて記述｡将来予想は52週平均を用いる｡
         100万台単位を節目とし､節目の到達時期が3ヶ月以内である場合は特に言及する｡
         その際には､過去のPS3, PS4の状況との比較を行い､考察を加える｡
         """,
        },
        {
            "cell_name": "md_switch_yearly",
            "calc_cells": ["switch_yearly_cumulative_chart", "switch_heatmap_chart"],
            "description": """
         Switchの今年の販売状況を昨年､一昨年と比較､年末までの見通しについて記述
         将来予想は52週平均を用いる｡
         100万台単位を節目とし､節目の到達時期が3ヶ月以内である場合は特に言及する｡
         """,
        },
        {
            "cell_name": "md_switch2_yearly",
            "calc_cells": ["switch2_yearly_cumulative_chart", "switch2_heatmap_chart"],
            "description": """
         Switch2の今年の販売状況を昨年と比較､年末までの見通しについて記述
         将来予想は52週平均を用いる｡
         100万台単位を節目とし､節目の到達時期が3ヶ月以内である場合は特に言及する｡
         その際には､前世代機であるSwitchの状況､ ライバル機であるPS5の状況との比較を行い､考察を加える｡
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
