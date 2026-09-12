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
    9月6日は4機種の合計が43,759台となり､前週から12.9%増加しました｡Switch2､Switch､PS5はいずれも前週を上回りましたが､販売水準はなお低調です｡

    Switch2は24,281台で前週比9.1%増でした｡2週連続で3万台を下回っており､夏場の需要の弱さが続いています｡Switchは11,591台で31.0%増と大きく伸び､7月5日以来9週ぶりに1万台を超えました｡PS5の7,760台を2週連続で上回っています｡Xbox Series X|Sは127台で前週から減少し､小規模な販売が続いています｡

    9月13日集計は両タイトルの発売前に当たるため､直接的な影響は見込みにくい週です｡9月15日のPS5向け「Wolverine」と9月17日のSwitch2向け「FE万紫千紅」の影響は､9月20日集計で確認したいところです｡
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
        annotation_level=50,
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
    Switch2は24,281台まで増加したものの､直近4週平均は25,015台へ低下しており､3万台回復には至っていません｡夏休み後の需要がどこまで持ち直すかが注目点です｡9月17日の「FE万紫千紅」の発売後データは9月20日集計から反映されるため､9月13日集計では発売前の水準を確認することになります｡

    Switchは直近4週平均で8,515台となり､PS5の7,872台を上回りました｡単週でも2週連続でSwitchがPS5を上回っており､足元ではSwitchの方が強い動きです｡ただし両機種とも販売規模は小さく､9月15日のPS5向け「Wolverine」を含む新作投入後もこの順位が続くかを見極める必要があります｡
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
        y2=637000,
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
    PS5の2026年累計は9月6日時点で413,562台です｡前年同時期の590,931台を30.0%下回り､2024年同時期の1,063,634台に対しては61.1%少ない水準です｡歴代PlayStationと比べても､PS3の2014年同時期の363,427台には近い一方､PS4の2018年同時期の1,159,050台には大きく届きません｡

    52週平均による年間販売予測は637,227台です｡2025年通年の879,204台を下回る見込みで､過去1年の販売水準を織り込んだ試算です｡9月15日の「Wolverine」の発売後データは9月20日集計からの材料ですが､足元の週販は1万台を下回っており､年末までに予測を上振れするには継続的な回復が必要です｡
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
        y2=869000,
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
    Switchの2026年累計は9月6日時点で551,129台です｡前年同時期の1,073,896台から48.7%減､2024年同時期の1,978,746台から72.1%減となり､発売からの経過に伴う縮小が続いています｡

    52週平均による年間販売予測は869,052台です｡足元ではPS5を上回る週が続いているものの､2025年通年の1,520,384台を大きく下回る見込みです｡直近4週平均は8,515台と13週平均の7,718台を上回っており､短期的には持ち直しも見られますが､年間の縮小基調を変えるほどの水準ではありません｡
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
        y2=3850000,
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
    Switch2の2026年累計は9月6日時点で2,481,406台です｡前年同時期の1,980,483台を25.3%上回っていますが､前年は6月発売であるため､前年比には販売期間の違いも含まれます｡発売66週時点の累計は6,265,473台で､同時点のSwitchを約187万台上回る高い普及ペースです｡

    52週平均による年間販売予測は3,846,958台です｡2025年通年の3,784,067台をわずかに上回る計算ですが､この平均には発売直後の高い販売水準も含まれます｡直近4週平均は25,015台にとどまるため､年末までの達成には､足元の週販水準からの継続的な回復が必要です｡
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
    Switch2の9月第1週の販売は24,281台で､前年同週の46,403台を47.7%下回りました｡前週の22,265台からは増加しましたが､夏場に続き3万台を下回る水準です｡

    8月は139,165台と7月を1.8%上回ったものの､前年8月の319,690台には届きませんでした｡9月は低い水準から始まっており､月後半に販売水準をどこまで持ち直せるかが焦点です｡
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
    Switchの9月第1週の販売は11,591台で､前年同週の24,175台を52.1%下回りました｡前週比では31.0%増となり､PS5を2週連続で上回っています｡

    8月は38,211台と7月から15.6%増加しましたが､前年8月の94,517台に対しては低い水準でした｡9月も前年を下回る出足であり､直近4週平均が8,515台まで持ち直しているものの､縮小基調に変化は見られません｡
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
    PS5の9月第1週の販売は7,760台で､前年同週の31,695台を75.5%下回りました｡前週の7,351台からは5.6%増えたものの､Switchを2週連続で下回っています｡

    8月は43,810台で前年同月を12.3%上回りましたが､月後半には週販が1万台を割り込みました｡9月は弱い出足となっており､9月15日発売予定の「Wolverine」の影響は9月20日集計から確認することになります｡
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
    Xbox Series X|Sの9月第1週の販売は127台で､前年同週の160台を20.6%下回りました｡前週の298台からは減少し､直近4週平均も157台にとどまっています｡

    8月販売は659台で､7月の1,131台から41.7%減少しました｡8月1日の値上げ実施後も販売規模は極めて小さく､単週ごとの変動はあるものの､9月も回復の兆しは限定的です｡
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
    9月6日時点の累計販売はPS5が7,711,772台､Switch2が6,265,473台で､差は1,446,299台です｡今週はSwitch2がPS5を16,521台上回り､差を縮めました｡

    52週平均ではSwitch2が週82,404台､PS5が13,497台で推移しており､この差が続く機械的な試算では約21週後の2027年2月ごろに逆転します｡ただしSwitch2の52週平均には発売直後の高い販売が含まれます｡直近4週平均の差は週約1.7万台であり､こちらを基準にすると逆転は約84週後の2028年春ごろです｡年末商戦に向けてSwitch2の販売がどこまで持ち直すかが､両試算の隔たりを縮める鍵になります｡
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
        annotation_level=23,
        mode="week",
        with_point=False,
        multi_line=True,
    )
    _chart = g.chart_rule_xy(
        base_chart=_chart,
        x=ns2_info["sales_weeks"],
        y=ns2_info["total_units"],
        stroke=[5, 2],
        size=2,
        color="#00000060",
    )
    _chart = g.chart_line_guide(
        base_chart=_chart,
        x=ns2_info["sales_weeks"],
        y=ns2_info["total_units"],
        x2=ns2_info["sales_weeks"] + 20,
        y2=6850000,
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
    発売66週時点のSwitch2累計は6,265,473台で､同時点のDSを184,130台､3DSを200,164台上回り､歴代最速の普及ペースを維持しています｡GBAに対しても約79万台の差をつけています｡

    ただしDSはこの時期に週129,044台､3DSも週51,804台を販売していました｡Switch2は直近4週平均が約2.5万台で､今週も24,281台にとどまります｡需要回復が限定的なら､DS・3DSとの差は今後縮まる可能性があります｡
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
    2026年第3四半期は9月6日までの10週間で477,511台です｡前年同期の1,089,637台を56.2%､2024年同期の884,949台を46.0%下回っています｡

    Switch2は300,094台で前年同期から63.0%減となった一方､PS5は92,635台で前年同期の99,658台に近い水準です｡市場全体の減少は､Switch2とSwitchの前年からの縮小が主な要因です｡四半期後半に販売水準をどこまで持ち直せるかが注目されます｡
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
    2026年のハード販売は9月6日時点で合計3,462,214台です｡前年同時期の3,671,358台を5.7%下回る一方､2024年同時期の3,140,869台は10.2%上回っています｡

    Switch2が2,481,406台で全体の71.7%を占め､Switchの551,129台､PS5の413,562台が続きます｡Switch2が市場規模を支える構図は続いていますが､前年の同時期と比べるとSwitch2とSwitchの販売減が全体を押し下げています｡9月20日集計で販売水準が改善するかを確認したいところです｡
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
    2026年のメーカー別シェアは9月6日時点で任天堂が87.6%､ソニーが11.9%､マイクロソフトが0.5%です｡前年同時期の任天堂シェア83.2%､2024年同時期の63.0%を上回り､任天堂優位が一段と強まっています｡

    52週平均を年末まで延長した試算では､任天堂の年間シェアは87.7%､ソニーは11.9%､マイクロソフトは0.4%です｡Switch2だけで市場全体の71.7%を占めており､任天堂の高いシェアを支えています｡ただしSwitch2の52週平均には発売直後の販売が含まれるため､年末に向けた実際のシェアは今後の週販次第で変動します｡
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
        annotation_dfに含まれる来週､再来週のイベント情報を確認し､それが将来に与える影響の予想も含めて記述する｡
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
