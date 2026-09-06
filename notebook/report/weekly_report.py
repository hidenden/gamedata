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
def report_setup(is_publish):
    # レポート日付
    from report_config import get_config

    config = get_config()
    report_date: datetime = config["date"]

    def show_title(d: datetime):
        last_updated_str = d.strftime("%Y-%m-%d")
        mode: str = "**DRAFT**" if not is_publish else ""
        return mo.md(f"# 国内ゲームハード週販レポート ({last_updated_str}) {mode}")

    df_all: pl.DataFrame = g.load_hard_sales(True)
    _annotation_df: pl.DataFrame = g.load_hard_annotation(no_cache=True)
    [ns2_info, ps5_info, nsw_info] = g.hard_sales_summary(
        df_all, hw=["NS2", "PS5", "NSW"]
    )
    return df_all, ns2_info, report_date, show_title


@app.cell
def _(df_all: pl.DataFrame):
    _df_latest = g.extract_latest(df_all, 1)
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
def units_by_date_hw_table(df_all: pl.DataFrame, report_date: datetime):
    _table = g.units_by_date_hw_table(
        df_all, begin=g.weeks_before(report_date, 3), end=report_date
    )
    mo.hstack(items=[_table], justify="start", wrap=True)
    return


@app.cell(hide_code=True)
def md_top():
    mo.md(r"""
    8月30日までの1週間は､主要4機種の合計が38,761台となり､前週から16.1%増加しました｡全機種が前週を上回っていますが､全体の水準は引き続き低調です｡

    Switch2は22,265台で前週比7.4%増でした｡過去最低だった前週からは持ち直したものの､2週続けて3万台を割り込み､回復は限定的です｡

    Switchは8,847台で44.8%増と､今週最も大きく伸びました｡PS5は7,351台で14.9%増でしたが､SwitchがPS5を14週間ぶりに上回りました｡Xbox Series X|Sも298台へ倍増したものの､販売規模は依然として小さい状況です｡
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
    Switch2は22,265台まで戻しましたが､直近4週平均は27,140台へ低下しており､3万台を安定して回復するには至っていません｡8月中旬の32,780台から2万台前半へ水準を切り下げた点には注意が必要です｡

    今週はSwitchが8,847台でPS5の7,351台を上回りました｡ただし直近4週平均ではPS5が8,426台､Switchが7,494台であり､順位が定着したとはまだ言えません｡次週以降もSwitchが上回るかが､両機種の基調を見極めるポイントになります｡
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
        y2=550000,
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
    PS5の2026年累計は8月30日時点で405,802台です｡前年同時期の550,932台を26%下回り､2024年同時期の1,018,762台に対しては約60%少ない水準です｡8月は前年を上回ったものの､年間累計の減少を埋めるまでには至っていません｡

    直近4週平均の週8,426台を年末まで単純に延長すると､年間販売は55万台前後となります｡年末商戦で上振れる余地はありますが､2025年通年の879,204台に届くには大幅な販売増が必要です｡
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
        y2=680000,
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
    Switchの2026年累計は8月30日時点で539,538台です｡前年同時期の1,029,132台から48%減､2024年同時期の1,847,622台から71%減となり､発売10年目に向けて縮小が鮮明になっています｡

    直近4週平均の週7,494台を年末まで単純に延長すると､年間販売は67万台前後です｡年末商戦で一定の上積みがあっても､2025年通年の1,520,384台を大きく下回る可能性が高いでしょう｡
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
        y2=3600000,
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
    Switch2の2026年累計は8月30日時点で2,457,125台です｡前年同時期の1,892,123台を30%上回っていますが､2025年は6月発売だったため､この前年比には販売期間の違いも含まれます｡

    直近4週平均の週27,140台を年末まで単純に延長した場合､年間販売は293万台前後です｡2025年通年の3,784,067台を超えるには残り期間で約133万台､週平均では約7.8万台が必要となるため､年末商戦で大きな加速がなければ前年割れとなる見通しです｡
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
    Switch2の8月販売は139,165台で､7月の136,648台から1.8%増加しました｡一方､前年8月の319,690台に対しては43.5%にとどまっています｡

    月前半は週3万台を維持したものの､後半は2万台前半へ低下しました｡月間では前月をわずかに上回りましたが､需要の基調が回復したとは言いにくい内容です｡
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
    Switchの8月販売は38,211台で､7月の33,063台から15.6%増加しました｡月末週の8,847台への伸びが月間実績を押し上げました｡

    ただし前年8月の94,517台に対しては40.4%です｡前月からは持ち直したものの､発売からの経過を反映した縮小傾向は続いています｡
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
    PS5の8月販売は43,810台で､7月の41,065台から6.7%増加しました｡前年8月の39,004台も12.3%上回り､主要機種の中では唯一､前年同月を超えています｡

    一方で週販は月後半に1万台を割り込み､月末週は7,351台でした｡9月に前年の販促効果を上回る材料がなければ､前年同月比は再び低下する可能性があります｡
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
    Xbox Series X|Sの8月販売は659台で､7月の1,131台から41.7%減少しました｡前年8月の1,599台に対しても41.2%にとどまっています｡

    月末週は298台へ増加しましたが､直近4週平均は142台です｡単週の反発だけでは基調改善とは判断しにくく､低水準が続いています｡
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
    8月30日時点の累計販売はPS5が7,704,012台､Switch2が6,241,192台で､差は1,462,820台です｡今週はSwitch2がPS5を14,914台上回り､差を縮めました｡

    直近4週平均でもSwitch2がPS5を週約1.9万台上回っていますが､このペースでは追いつくまで1年以上かかります｡年内に逆転するには残り期間を通じて週平均で約8.6万台ずつ差を縮める必要があり､年末商戦で非常に大きな加速がなければ､逆転は2027年以降になる見通しです｡
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
def _(df_all: pl.DataFrame, ns2_info):
    _d1 = (
        df_all.filter(pl.col("index_week") == ns2_info["sales_weeks"])
        .filter(pl.col("hw").is_in(["NS2", "NSW", "3DS", "GBA", "DS"]))
        .select("hw", "index_week", "report_date", "sum_units")
        .sort("sum_units", descending=True)
    )
    g.style_df(g.rename_columns(_d1))
    return


@app.cell(hide_code=True)
def md_cumulative_top():
    mo.md(r"""
    発売65週時点のSwitch2累計は6,241,192台で､同時点の3DSを227,687台､DSを288,893台上回り､歴代最速の普及ペースを維持しています｡

    ただしDSは66週目以降に週10万台を超える伸びを見せており､Switch2が直近の週2万台台で推移すると､68週目前後にDSへ首位を明け渡す計算です｡3DSとの差もその後急速に縮まり､同じペースなら70週目前後が逆転の分岐点になります｡
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
    2026年第3四半期は8月30日までの9週間で433,752台です｡前年同期の987,204台を56%､2024年同期の804,987台を46%下回っています｡Switch2が275,813台と前年同期から64%減った影響が大きい一方､PS5は84,875台で前年同期を25%上回っています｡
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
    2026年のハード販売は8月30日時点で合計3,418,730台です｡Switch2が2,457,125台で全体の71.9%を占め､Switchの539,538台､PS5の405,802台が続きます｡

    Switch2への集中が進む一方､Switchは前年通年の1,520,384台､PS5は879,204台に対して大幅に低い進捗です｡市場全体はSwitch2が規模を支え､既存機種の縮小を補う構図になっています｡
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
    2026年のメーカー別シェアは8月30日時点で任天堂が87.7%､ソニーが11.9%､マイクロソフトが0.5%です｡任天堂は2025年通年の85.3%､2024年通年の66.2%を上回っています｡

    Switch2だけで市場全体の71.9%を占めており､任天堂優位がさらに強まりました｡一方､ソニーは2025年の14.2%から低下し､マイクロソフトも1%未満の状態が続いています｡
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
