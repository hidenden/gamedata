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
    10月4日は4機種合計で47,284台となり、前週から2.7%減少しました。PS5、Switch、Xbox Series X|Sは増加しましたが、Switch2の減少が市場全体を押し下げています。

    Switch2は26,200台で前週比18.6%減となり、3週ぶりに3万台を下回りました。PS5は12,768台で31.2%増、Switchは7,704台で22.2%増、Xbox Series X|Sは612台で69.1%増です。順位は先週から変わらず、Switch2が首位、PS5が2位を維持しました。Switchの累計は36,994,564台となり、3,700万台まで残り5,436台です。

    今週の[ファミ通のソフト週販](https://www.famitsu.com/article/202610/90441)では、PS5向け「ACE COMBAT8」が63,013本で1位、「真・三國無双2 with 猛将伝 Remastered」が18,724本で2位となりました。両作がPS5本体の販売を牽引し、週販は前週から31.2%増の12,768台へ伸びています。PS5の増加は3週連続です。次回10月11日集計ではSwitch2、PS5の「KINGDOM HEARTS Collection」、次々回10月18日集計では両機種の「Call of Duty:Modern Warfare4」が販売を支えるかに注目です。

    一方、Switch2は10月中に週3万台へ回復するのは難しいと見ています。10月6日に発表・予約開始となった「Nintendo Switch2選べるソフトセット」は11月12日発売で、ソフト同梱により最大4,980円お得な構成です。次回集計以降、発売前の11月8日集計までは購入待ちが通常の本体販売を押し下げると考えられます。既に発表されている10月29日発売の「ゼルダの伝説40周年記念モデル」も、発売日が近づくほど意識され、10月中の買い控えを強めるでしょう。
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
    Switch2は前週から5,998台減の26,200台となり、2週連続の減少です。「ファイアーエムブレム万紫千紅」の発売週に34,341台まで伸びた後、32,198台、26,200台と下がっており、9月後半の上昇は持続しませんでした。直近4週平均は30,270台へ上がりましたが、これは9月の高い週販を含むためで、今週の販売は13週平均の29,875台も下回っています。

    PS5は前週から3,038台増の12,768台となり、3週連続で上昇しました。ソフト週販1位の「ACE COMBAT8」（63,013本）と2位の「真・三國無双2 with 猛将伝 Remastered」（PS5版18,724本）が本体販売を牽引し、直近4週平均も8,208台から9,460台へ上がっています。Switchは7,704台へ増加したものの、直近4週平均は6,818台でPS5を下回ります。Xbox Series X|Sも612台へ増えましたが、順位はSwitch2、PS5、Switch、Xbox Series X|Sの順で変わらず、PS5の2位は3週連続です。

    今後のSwitch2は新作の発売が続く一方、「選べるソフトセット予約開始」と10月29日発売の「ゼルダの伝説40周年記念モデル」による購入待ちの影響で､10月中に週3万台へ戻るのは難しく、
    新作の牽引があっても本体販売の回復が抑えられる可能性が高いでしょう。
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
        y2=665000,
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
    PS5の2026年累計は10月4日時点で451,401台です。前年同時期の665,273台を32.1%、2024年同時期の1,105,836台を59.2%下回っています。歴代PlayStationとの比較ではPS3の2014年同時期384,900台を17.3%上回る一方、PS4の2018年同時期1,231,266台には大きく届きません。

    52週平均の12,795台を年換算した年間販売の目安は約665,000台で、2025年通年の879,204台を下回ります。今週は12,768台まで回復し、ほぼ52週平均に並びましたが、この上昇が年末商戦まで持続するかが焦点です。発売からの累計は7,749,611台で、800万台まで残り250,389台となりました。52週平均での到達は約20週後の2027年2月で、年内の到達には販売ペースの上積みが必要です。
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
        y2=942000,
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
    Switchの2026年累計は10月4日時点で578,403台です。前年同時期の1,156,776台から50.0%減、2024年同時期の2,219,833台から73.9%減となり、世代交代後の縮小が続いています。

    52週平均の18,116台を年換算した年間販売の目安は約942,000台で、2025年通年の1,520,384台を下回ります。足元の直近4週平均は6,818台と52週平均より大幅に低く、年末の販売が伸びなければこの目安も下振れするでしょう。一方、発売からの累計は36,994,564台となり、3,700万台まで残り5,436台です。52週平均でも直近4週平均でも次回10月11日集計で到達する計算となり、今週の7,704台を維持できれば節目を超えます。
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
        y2=4232000,
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
    Switch2の2026年累計は10月4日時点で2,602,486台です。前年同時期の2,154,061台を20.8%上回っていますが、前年は6月発売であるため、前年比には販売期間の違いも含まれます。発売70週時点の累計は6,386,553台で、同時点のSwitchを約181万台、PS5を約494万台上回る普及ペースです。

    52週平均の81,394台を年換算した年間販売の目安は約4,232,000台で、2025年通年の3,784,067台を上回ります。累計700万台までは残り613,447台で、52週平均なら約8週後の11月29日集計に到達する計算です。この場合は発売78週となり、Switchの97週、PS5の252週より早い到達となります。

    ただし、52週平均には前年の年末商戦や今年春の高い販売が含まれ、直近4週平均の30,270台とは大きな差があります。「選べるソフトセット発売」を待つ動きと「ゼルダの伝説40周年記念モデル」を待つ動きから、10月中の週3万台への回復は難しいと見ています。直近4週平均でも700万台到達は2027年2月末ごろとなるため、実際の到達時期は11月の新モデル発売後と年末商戦の伸びに左右されるでしょう。
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
    Switch2の10月販売は初週で26,200台です。前年10月初週の44,439台を41.0%下回り、前週の32,198台からも18.6%減少しました。9月は4週間で119,161台、前年10月は4週間で358,399台でした。今月も10月25日集計までの4週間となり、今週の水準を単純に延ばすと月間104,800台です。

    「Nintendo Switch2選べるソフトセット」と「ゼルダの伝説40周年記念モデル」の影響で10月中に週3万台へ回復するのは難しいと見ています。
    残り3週も3万台未満なら、10月販売は116,200台未満となり、9月を下回ります。記念モデルの発売週は11月1日集計に入るため、
    発売時の上積みも10月分には含まれません。新作による押し上げと購入待ちによる押し下げが重なる中、
    10月は9月より弱い販売を見込み、回復は11月以降の動きを確認したいところです。
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
    Switchの10月販売は初週で7,704台です。前週から22.2%増えた一方、前年10月初週の24,109台からは68.0%減少しました。9月の月間販売は31,161台、前年10月は96,080台で、今月も前年を大きく下回る出足です。

    10月は4週間の集計となり、直近4週平均の6,818台を4倍すると27,272台、今週の7,704台を4倍すると30,816台です。この水準が続けば月間販売は2.7万～3.1万台程度で、9月と同程度かやや下回る見通しです。次回集計での累計3,700万台到達が見込まれる一方、月間の販売規模は前年の3割前後にとどまる計算となります。
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
    PS5の10月販売は初週で12,768台です。前週から31.2%増加しましたが、前年10月初週の27,344台からは53.3%減となっています。9月の月間販売は32,831台、前年10月は64,732台でした。

    今週は「ACE COMBAT8」が63,013本でソフト週販1位、「真・三國無双2 with 猛将伝 Remastered」のPS5版が18,724本で2位となりました。両作がPS5本体の販売を牽引し、9月後半からの上昇が続いています。次回の「KINGDOM HEARTS Collection」、次々回の「Call of Duty:Modern Warfare4」も販売を支える可能性があります。

    10月の4週間について、直近4週平均の9,460台を延ばすと37,840台、今週の水準なら51,072台です。この二つのペースでは月間3.8万～5.1万台程度となり、9月からの回復は見込める一方、前年10月には届きません。新作が続く期間の上昇を月末まで維持できるかが焦点です。
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
    Xbox Series X|Sの10月販売は初週で612台です。前週の362台から69.1%増加し、4週連続の増加となりました。一方、前年10月初週の837台からは26.9%減です。9月の月間販売は918台、前年10月は2,253台でした。

    10月の4週間について、直近4週平均の351台を延ばすと1,404台、今週の612台を延ばすと2,448台です。どちらのペースでも9月を上回りますが、前年10月を超えるには今週に近い販売の継続が必要です。販売規模が小さく週ごとの変動も大きいため、初週の伸びが月末まで続くかを確認したいところです。
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
    10月4日時点の累計販売はPS5が7,749,611台、Switch2が6,386,553台で、差は1,363,058台です。今週はSwitch2がPS5を13,432台上回り、累計差は縮まりましたが、前週の22,468台より縮小幅は小さくなっています。

    52週平均ではSwitch2が週81,394台、PS5が12,795台で、この差が続く機械的な試算では約20週後の2027年2月に逆転します。一方、直近4週平均の差は週20,810台で、このペースなら約66週後の2028年1月です。Switch2の52週平均には前年の年末商戦や今年春の高い販売が含まれるため、二つの試算には大きな開きがあります。

    10月は「選べるソフトセット発売」と「ゼルダの伝説40周年記念モデル」を待つ動きでSwitch2の週3万台への回復が難しいと見ており、短期的には累計差の縮小が鈍る可能性があります。実際の逆転時期を判断するには、11月の発売後に購入待ちの需要がどこまで販売へ移るかと、PS5の新作による上昇が続くかを見極める必要があります。
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
    発売70週時点のSwitch2累計は6,386,553台で、歴代2位を維持しています。首位のDSは6,728,371台で、差は前週の158,223台から341,818台へ広がりました。3DSは6,351,586台で、Switch2のリードは前週の75,720台から34,967台へ縮まっています。GBAには約75万台、Switchには約181万台の差をつけています。

    次の71週時点の3DS累計は6,416,853台です。Switch2が上回るには次週に30,301台以上が必要で、30,300台なら同数となります。今週は26,200台にとどまり、10月中の週3万台への回復も購入待ちで難しいと見ているため、次回集計で歴代3位へ下がる可能性が高いでしょう。直近4週平均の30,270台を維持しても、3DSに30台届かない計算です。

    DSは71週時点で6,946,582台、72週時点で700万台を超えており、Switch2が短期的に首位へ戻るのは難しい状況です。52週平均ではSwitch2の700万台到達は発売78週の計算となりますが、足元の販売と購入待ちを考えると後ろ倒しの可能性があります。11月の新モデル発売後に販売が回復するかが、今後の歴代順位を左右するでしょう。
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
    2026年第4四半期は初週で47,284台となりました。前年の第4四半期初週96,748台を51.1%、2024年の76,760台を38.4%下回る出足です。Switch2が26,200台で全体の55.4%を占め、PS5が12,768台、Switchが7,704台、Xbox Series X|Sが612台で続きます。

    第3四半期は617,823台で、2001年以降の完了した四半期では最低でした。前年の第4四半期は2,308,689台、2024年は1,345,463台まで伸びており、今期も年末商戦の寄与が重要になります。ただし10月はSwitch2のゼルダモデル､ソフトバンドル版を待つ動きが販売を抑えると見られ、11月以降にどこまで取り戻せるかが焦点です。
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
    2026年の主要4機種のハード販売は10月4日時点で合計3,649,810台です。Switch2が2,602,486台で全体の71.3%を占め、Switchの578,403台、PS5の451,401台、Xbox Series X|Sの17,520台が続きます。表の全機種合計はPS4の275台を含む3,650,085台です。

    主要4機種では前年同時期の4,003,134台を8.8%下回る一方、2024年同時期の3,413,279台は6.9%上回っています。Switch2は前年から448,425台増えましたが、Switchは578,373台、PS5は213,872台減り、両機種の落ち込みがSwitch2の増加を上回りました。今週はPS5などが増加したもののSwitch2の減少を補えず、前年との差は前週より広がっています。10月の購入待ちと11月以降の新モデル発売・年末商戦を通じて、市場全体をどこまで積み上げられるかが重要になります。
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
    2026年のメーカー別シェアは10月4日時点で任天堂が87.1%、ソニーが12.4%、マイクロソフトが0.5%です。任天堂は前週の87.4%からやや低下し、ソニーは12.2%から上昇しましたが、任天堂のシェアは2025年通年の85.3%、2024年の66.2%を上回っています。Switch2だけで主要4機種の71.3%を占めることが、高い任天堂シェアを支えています。

    主要4機種の52週平均を年換算した販売台数に基づく年間シェアの目安は、任天堂が約88.3%、ソニーが約11.4%、マイクロソフトが約0.4%です。ただしSwitch2の52週平均には前年の年末商戦や今年春の高い販売が含まれ、足元の販売とは差があります。10月は新モデルの購入待ちで任天堂のシェアが下がる場面も考えられますが、11月の発売後と年末商戦でどこまで需要を取り込むかによって、実際の年間シェアは変動するでしょう。
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
