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

__generated_with = "0.24.0"
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
def _():
    df_sales_all: pl.DataFrame = g.load_hard_sales(True)
    annotation_df: pl.DataFrame = g.load_hard_annotation(no_cache=True)
    return (df_sales_all,)


@app.cell
def report_setup(df_sales_all: pl.DataFrame, is_publish):
    # レポート日付
    from report_config import get_config

    config = get_config()
    report_date: datetime = config["date"]

    def show_title(d: datetime):
        last_updated_str = d.strftime("%Y-%m-%d")
        mode: str = "**DRAFT**" if not is_publish else ""
        return mo.md(f"# 国内ゲームハード週販レポート ({last_updated_str}) {mode}")

    [ns2_info, ps5_info, nsw_info] = g.hard_sales_summary(
        df_sales_all, hw=["NS2", "PS5", "NSW"]
    )
    return ns2_info, report_date, show_title


@app.cell
def _(df_sales_all: pl.DataFrame):
    _df_latest = g.extract_latest(df_sales_all, 1)
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
def units_by_date_hw_table(df_sales_all: pl.DataFrame, report_date: datetime):
    _table = g.units_by_date_hw_table(
        df_sales_all, begin=g.weeks_before(report_date, 3), end=report_date
    )
    mo.hstack(items=[_table], justify="start", wrap=True)
    return


@app.cell(hide_code=True)
def md_top():
    mo.md(r"""
    9月6日は4機種の合計が43,759台となり､前週から12.9%増加しました｡Switch2､Switch､PS5はいずれも前週を上回りましたが､販売水準はなお低調です｡

    Switch2は24,281台で前週比9.1%増でした｡2週連続で3万台を下回っており､夏場の需要の弱さが続いています｡

    Switchは11,591台で31.0%増と大きく伸び､7月5日以来9週ぶりに1万台を超えました｡PS5の7,760台を2週連続で上回っています｡Xbox Series X|Sは127台で前週から減少し､小規模な販売が続いています｡
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

    _weekly_chart = mo.ui.altair_chart(_chart)
    mo.hstack(items=[_weekly_chart], justify="start", wrap=True)
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
    _begin = date(2026, 1, 15)
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
    mo.hstack(items=[mo.ui.altair_chart(_chart)], justify="start", wrap=True)
    return


@app.cell(hide_code=True)
def md_weekly_chart():
    mo.md(r"""
    Switch2は24,281台まで増加したものの､直近4週平均は25,015台へ低下しており､3万台回復には至っていません｡夏休み後の需要がどこまで持ち直すかが注目点です｡
    次回集計にはNintendo Directの影響が反映されますが､時のオカリナモデルの本体が発表された影響で､本体買い控えの可能性も考えられます。

    Switchは直近4週平均で8,515台となり､PS5の7,872台を上回りました｡単週でも2週連続でSwitchがPS5を上回っており､足元ではSwitchの方が強い動きです｡
    ただし両機種とも販売規模は小さく､この順位が定着するかは今後の推移を見極める必要があります｡
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

    mo.ui.altair_chart(_chart)
    return


@app.cell
def _():
    _chart = g.chart_heatmap(
        hw="PS5",
        mode="week",
        scale_scheme="plasma",
        scale_type="sqrt",
    )
    _chart_ui = mo.ui.altair_chart(_chart)
    _chart_ui
    return


@app.cell(hide_code=True)
def md_ps5_yearly():
    mo.md(r"""
    PS5の2026年累計は9月6日時点で413,562台です｡前年同時期の590,931台を30.0%下回り､2024年同時期の1,063,634台に対しては61.1%少ない水準です｡

    52週平均による予測では年間販売予測は637,227台です｡2025年通年の879,204台を下回る見込みですが､直近の低調な週販だけではなく､過去1年の販売水準を織り込んだ予測です｡
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
    mo.ui.altair_chart(_chart)
    return


@app.cell
def _():
    _chart = g.chart_heatmap(
        hw="NSW",
        mode="week",
        scale_scheme="plasma",
        scale_type="sqrt",
    )
    _chart_ui = mo.ui.altair_chart(_chart)
    _chart_ui
    return


@app.cell(hide_code=True)
def md_switch_yearly():
    mo.md(r"""
    Switchの2026年累計は9月6日時点で551,129台です｡前年同時期の1,073,896台から48.7%減､2024年同時期の1,978,746台から72.1%減となり､発売からの経過に伴う縮小が続いています｡

    52週平均による予測では年間販売予測は869,052台です｡足元ではPS5を上回る週が続いているものの､2025年通年の1,520,384台を大きく下回る見込みです｡
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Switch2(2025年, 2026年)
    """)
    return


@app.cell
def _(switch2_latest):
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
    mo.ui.altair_chart(_chart)
    return


@app.cell
def _():
    _chart = g.chart_heatmap(
        hw="NS2",
        mode="week",
        scale_scheme="plasma",
        scale_type="log",
    )
    _chart = _chart.properties(height=200)
    _chart_ui = mo.ui.altair_chart(_chart)
    _chart_ui
    return


@app.cell(hide_code=True)
def md_switch2_yearly():
    mo.md(r"""
    Switch2の2026年累計は9月6日時点で2,481,406台です｡前年同時期の1,980,483台を25.3%上回っていますが､前年は6月発売であるため､前年比には販売期間の違いも含まれます｡

    52週平均による予測では年間販売予測は3,846,958台です｡2025年通年の3,784,067台をわずかに上回る計算ですが､この平均には発売直後の高い販売水準も含まれるため､足元の週販だけからは達成を見込みにくい水準です｡
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
def _(report_date: datetime):
    _begin = g.years_ago(report_date)
    _end = report_date
    _chart_bar = mo.ui.altair_chart(
        g.chart_bar_hwsales_by_year(begin=_begin, end=_end, hw="NS2")
    )
    ns2_df = _chart_bar.dataframe
    ns2_df_pivot = ns2_df.pivot(index="month", on="year", values="monthly_units")
    mo.vstack(items=[_chart_bar], justify="start")
    return (ns2_df_pivot,)


@app.cell
def _(ns2_df_pivot, report_date: datetime):
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

    8月は139,165台と7月をわずかに上回ったものの､前年8月の319,690台には届きませんでした｡
    9月は月初の低い水準から始まっており､月後半に「ファイアーエムブレム 万紫千紅 (9月17日発売)」がどこまで需要を押し上げるかが焦点です｡
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
    _chart_bar = mo.ui.altair_chart(
        g.chart_bar_hwsales_by_year(begin=_begin, end=_end, hw="NSW", ymax=480000)
    )
    ns_df = _chart_bar.dataframe
    ns_df_pivot = ns_df.pivot(index="month", on="year", values="monthly_units")
    mo.vstack(items=[_chart_bar], justify="start")
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

    8月は38,211台と7月から15.6%増加しましたが､前年8月の94,517台に対しては低い水準でした｡9月も前年を下回る出足であり､縮小基調に変化は見られません｡
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
    _chart_bar = mo.ui.altair_chart(
        g.chart_bar_hwsales_by_year(begin=_begin, end=_end, hw="PS5", ymax=480000)
    )
    ps5_df = _chart_bar.dataframe
    ps5_df_pivot = ps5_df.pivot(index="month", on="year", values="monthly_units")
    mo.vstack(items=[_chart_bar], justify="start")
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

    8月は43,810台で前年同月を12.3%上回りましたが､月後半には週販が1万台を割り込みました｡9月は弱い出足となっており､
    前年の販促効果を上回る材料がなければ前年同月比は大きく低下する可能性があります｡
    9月15日発売のInsomniac期待の新作 Marvel's Wolverine がどこまでハード販売を押し上げるかが注目点です｡
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Xbox Series X|S: 月間販売台数
    """)
    return


@app.cell
def _(report_date: datetime):
    _begin = g.years_ago(report_date)
    _end = report_date
    _chart_bar = mo.ui.altair_chart(
        g.chart_bar_hwsales_by_year(begin=_begin, end=_end, hw="XSX")
    )
    xsx_df = _chart_bar.dataframe
    xsx_df_pivot = xsx_df.pivot(index="month", on="year", values="monthly_units")
    mo.vstack(items=[_chart_bar], justify="start")
    return (xsx_df_pivot,)


@app.cell
def _(report_date: datetime, xsx_df_pivot):
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

    8月販売は659台で､7月の1,131台から41.7%減少しました｡単週ごとの変動はあるものの､販売規模は引き続き極めて小さい状態です｡
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
    chart_cumulative = mo.ui.altair_chart(_chart)
    chart_cumulative
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### 累計販売推移(Switch2, PS5拡大)
    """)
    return


@app.cell
def _(ps5_latest, report_date: datetime, switch2_latest):
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

    直近4週平均でもSwitch2がPS5を週約1.7万台上回っています｡この差が続けば追いつくまで約84週を要する計算で､逆転時期は2028年春ごろが目安となります｡年内の逆転には､年末商戦で大幅な販売加速が必要です｡
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
def _(df_sales_all: pl.DataFrame, ns2_info):
    _d1 = (
        df_sales_all.filter(pl.col("index_week") == ns2_info["sales_weeks"])
        .filter(pl.col("hw").is_in(["NS2", "NSW", "3DS", "GBA", "DS"]))
        .select("hw", "index_week", "report_date", "sum_units")
        .sort("sum_units", descending=True)
    )
    g.style_df(g.rename_columns(_d1))
    return


@app.cell(hide_code=True)
def md_cumulative_top():
    mo.md(r"""
    発売66週時点のSwitch2累計は6,265,473台で､同時点のDSを184,130台､3DSを200,164台上回り､歴代最速の普及ペースを維持しています｡GBAに対しても約79万台の差をつけています｡

    ただしDSはこの時期に週10万台を超える販売を記録しており､3DSも週5万台前後で推移していました｡Switch2が直近4週平均の約2.5万台で推移する場合､両機種との差は今後急速に縮まる可能性があります｡
    """)
    return


@app.cell(hide_code=True)
def md_yearly_sales_title():
    mo.md(r"""
    ## 年単位の状況
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### 四半期ごとの状況
    """)
    return


@app.cell
def _():
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

    Switch2は300,094台で前年同期から63.0%減となった一方､PS5は92,635台で前年同期の99,658台に近い水準です｡市場全体の減少は､Switch2とSwitchの前年からの縮小が主な要因です｡
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
    _year_bar = mo.ui.altair_chart(
        g.chart_bar_sales(
            mode="year",
            stacked=True,
            begin=g.years_ago(report_date, 10),
            end=report_date,
        )
    )
    year_df = _year_bar.dataframe
    mo.vstack([_year_bar])
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

    Switch2が2,481,406台で全体の71.7%を占め､Switchの551,129台､PS5の413,562台が続きます｡Switch2が市場規模を支える構図は続いていますが､前年の同時期と比べるとNintendo Switch 2とSwitchの販売減が全体を押し下げています｡
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

    Switch2だけで市場全体の71.7%を占めており､任天堂の高いシェアを支えています｡一方､ソニーは前年同時期の16.1%から低下し､マイクロソフトも1%未満の状態が続いています｡
    """)
    return


@app.cell
def _():
    _md_summaries = [
        {"cell_name": "md_top",
        "description": "今週の売上概況を､主に先週と比較しながら説明する｡節目となるような変化があれば､それも記述する"},
        {"cell_name": "md_weekly_chart",
         "description": "週間販売折れ線グラフの説明､先週と比較しつつ､機種同士の比較や､今後の見通しを含めて解説"},
        {"cell_name": "md_ps5_yearly",
         "description": "PS5の今年の販売状況を昨年､一昨年と比較､年末までの見通しについて記述"},
        {"cell_name": "md_switch_yearly",
         "description": "Switchの今年の販売状況を昨年､一昨年と比較､年末までの見通しについて記述"},
        {"cell_name": "md_switch2_yearly",
         "description": "Switch2の今年の販売状況を昨年と比較､年末までの見通しについて記述"},
        {"cell_name": "md_switch2_monthly",
         "description": "Switch2の今月の販売状況を昨年同月､先月と比較して説明｡その月の最終週には一ヶ月のサマリーを､それ以外は月末時点での見通しを記述"},
        {"cell_name": "md_switch_monthly",
         "description": "Switchの今月の販売状況を昨年同月､先月と比較して説明｡その月の最終週には一ヶ月のサマリーを､それ以外は月末時点での見通しを記述"},
        {"cell_name": "md_ps5_monthly",
         "description": "PS5の今月の販売状況を昨年同月､先月と比較して説明｡その月の最終週には一ヶ月のサマリーを､それ以外は月末時点での見通しを記述"},
        {"cell_name": "md_xsx_monthly",
         "description": "Xbox Series X|S の今月の販売状況を昨年同月､先月と比較して説明｡その月の最終週には一ヶ月のサマリーを､それ以外は月末時点での見通しを記述"},
        {"cell_name": "md_cumulative_ps5_switch2",
         "description": "PS5とSwitch2の累計比較記事｡特にSwitch2がPS5に追いつく時期の予想も込めて記述"},
        {"cell_name": "md_cumulative_top",
         "description": "歴代のハードの初期の累計推移を比較する記事｡特にSwitch2を他機種と比較した状況､今後の見通しを記述"},
        {"cell_name": "md_quarterly",
         "description": "各年の四半期販売状況と今期の状況を比較して短く解説"},
        {"cell_name": "md_yearly_hard",
         "description": "各年の各ハードの状況と､今年の状況を比較して短く解説"},
        {"cell_name": "md_yearly_maker_share",
         "description": "各年の各ハードのメーカーシェアの状況と､今年の状況を比較し短く解説"}        
    ]

    def get_bodytext_cells():
        """
        Return the list of body text cell summaries.

        Returns:
            list: A list of dictionaries containing cell names and their descriptions.
        """
        return _md_summaries

    def get_bodytext_description_by_cell_name(cell_name):
        """
        Return the description of a body text cell by its cell name.

        Args:
            cell_name (str): The name of the cell.

        Returns:
            str: The description of the cell if found, otherwise None.
        """
        for cell in _md_summaries:
            if cell["cell_name"] == cell_name:
                return cell["description"]
        return None

    return


if __name__ == "__main__":
    app.run()
