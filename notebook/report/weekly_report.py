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

__generated_with = "0.23.8"
app = marimo.App(width="medium")

with app.setup:
    # 標準ライブラリ
    from datetime import date, datetime
    from pathlib import Path
    import sys

    import marimo as mo
    import altair as alt

    # サードパーティライブラリ
    import polars as pl

    # import polars.selectors as cs
    # プロジェクト内モジュール
    #_src_dir = Path.cwd() / "src"
    #if str(_src_dir) not in sys.path:
    #    sys.path.insert(0, str(_src_dir))
    import gamedata as g


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
    return df_all, ns2_info, ps5_info, report_date, show_title


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
def md_weekly_summary_1():
    mo.md(r"""
    39万本販売したリズム天国が任天堂ハードを牽引しました｡
    Switch2は7,918台増加し､5週ぶりに3万台超えて32,797台でした｡
    Switchも3,720台増加し､7週ぶりに1万台超えで10,788台でした｡

    この増加が一時的なものか､
    値上げ後に低迷していた販売ペースを元に戻していくきっかけになるのか､注目です｡

    2028年1月以降の新規タイトルのディスク提供終了の話題で世界を騒然とさせているPS5｡
    発表は7月1日だったので今週の週販にはその影響が含まれます｡
    今週のPS5は1,017台増加の10,913台でした｡増えています｡増加はボーナス効果でしょうか｡
    ディスク提供終了告知の影響は日本では見られませんでした｡

    既に日本のPS5販売量の97%がドライブ無しモデルであり､
    日本におけるPlayStationの売場減少・縮小はここ数年来の傾向です｡
    ディスク終了に影響を受ける部分は､削ぎ落とされ済みと考えたほうが良いでしょう｡
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
    全機種低水準推移が続いており､全体推移グラフでは直近の様子が見にくい状態です｡
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
        ymax=36000,
        padding_end=1,
        value_label=True,
    )
    mo.hstack(items=[mo.ui.altair_chart(_chart)], justify="start", wrap=True)
    return


@app.cell(hide_code=True)
def md_weekly_sales_trend_3():
    mo.md(r"""
    XBOXも含め全機種上昇です｡特にSwitch2の上昇量は顕著で､値上げ実施後の最高記録です｡
    PS5は6週間連続でSwitchを上回り続けています(今週はギリギリですが)｡
    この PS5 > Switch が､いつまで続くかも注目です｡
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
        y=_df.filter(pl.col("report_date") == ps5_latest["report_date"]).row(0, named=True)["yearly_sum_units"],
        x2=365,
        y2=590000,
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


@app.cell
def _(df_all: pl.DataFrame, ps5_info):
    _d1 = (
        df_all.filter(pl.col("index_week") == ps5_info["sales_weeks"])
        .filter(pl.col("hw").is_in(["PS5", "PS4", "PS3", "PS2", "PSP", "Vita"]))
        .select("hw", "index_week", "report_date", "sum_units")
    )
    g.style_df(g.rename_columns(_d1))
    return


@app.cell(hide_code=True)
def md_ps5_yearly_cumulative_1():
    mo.md(r"""
    PS5の週販は安定しています｡295週目のPS5はPS4の同時期と比べ約80万台下回る状況が続いていますが､
    追いつけていませんが離されてもいません｡
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
        y=_df.filter(pl.col("report_date") == switch_latest["report_date"]).row(0, named=True)["yearly_sum_units"],
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
def md_switch_yearly_cumulative_1():
    mo.md(r"""
    7週ぶりに1万台を回復しました｡これが続くのか､ここから上昇するのか注目です｡
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
    switch2_latest["report_date"].timetuple().tm_yday
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
        y=_df.filter(pl.col("report_date") == switch2_latest["report_date"]).row(0, named=True)["yearly_sum_units"],
        x2=365,
        y2=3750000,
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
def _():
    mo.md(r"""
    ヒートマップで暗黒状態が続いていましたが､少し変化が見られる今週｡
    スプラトゥーンレイダースをきっかけに完全回復できるかどうか注目です｡
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
def md_ns2_monthly_sales_1():
    mo.md(r"""
    昨年7月はロンチの影響が残る44万台でしたが､今年の7月は12万~20万台に落ち着くと予想されます｡
    どこまで伸びるかはスプラトゥーンレイダースの販売状況次第です｡
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
def md_switch_monthly_sales_1():
    mo.md(r"""
    Switchの6月前年比は32%と大幅減少でしたが､
    7月は幾分ましになって､前年比80%程度に落ち着くと予想されます｡
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
def md_ps5_monthly_sales_1():
    mo.md(r"""
    2025年7月のPS5は､わずか28,959台でした｡これは2025年のワースト月です｡
    一方､7月初週の状況が継続するならば､今年の7月は前年を超える可能性が高いです｡
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
def _():
    mo.md(r"""
    Xbox Series X|Sは
    7月第1週で前年同月比60%に達しています｡
    今年の7月は昨年よりも好調に推移すると予想されます｡
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
        y2=7900000,
        stroke=[5, 4],
        size=2,
        color="#af000080",
    )
    _chart = g.chart_line_guide(
        base_chart=_chart,
        x=report_date.date(),
        y=ps5_latest["sum_units"],
        x2=date(2027, 1, 31),
        y2=8050000,
        stroke=[5, 4],
        size=2,
        color="#0040a080",
    )

    _chart_ns2_cumulative = mo.ui.altair_chart(_chart)
    _chart_ns2_cumulative
    return


@app.cell(hide_code=True)
def md_cumulative_sales_trend_1():
    mo.md(r"""
    Switch2は累計599万台で600万台まで1800台に迫っています｡600万台到達は来週確実です｡
    Switch2の販売ペースの鈍化が続いた場合､累計800万台到達はPS5の方が早くなる可能性があります｡
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


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Switch2の歴代普及最速は69週目(あと12週)程度は維持できるでしょう｡
    """)
    return


@app.cell
def _(df_all: pl.DataFrame, ns2_info):
    _d1 = (
        df_all.filter(pl.col("index_week") == ns2_info["sales_weeks"])
        .filter(pl.col("hw").is_in(["NS2", "NSW", "GC", "WiiU", "Wii", "3DS"]))
        .select("hw", "index_week", "report_date", "sum_units")
    )
    g.style_df(g.rename_columns(_d1))
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Switch2は同時期のSwitchを約191万台上回る状況です｡
    Switch2値上げ後の低迷が続いており､Switchとの差が縮小しつつあります｡
    """)
    return


@app.cell
def _(switch2_latest):

    g.style_df(g.rename_columns(g.reached_unit_summary(n=switch2_latest["sum_units"], all=False)))
    return


@app.cell(hide_code=True)
def md_ns2_cumulative_delta_1():
    mo.md(r"""
    Switch2の販売ペースはSwitchの1.7→1.6倍となり､
    累計としては依然として高いペースは維持しているものの､値上げ後の低迷でSwitchに迫られつつあります｡
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
    _c1 = g.chart_bar_yearly_by_mode(begin=date(2016,1,1),  )
    _c2 = mo.ui.altair_chart(_c1)
    _c2
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    2026年上期としては､5月のSwitch2駆け込み需要の影響で2017年､2020年に近い水準で約300万台でした｡
    ただし3Q以降は今までのようなペースは難しそうです｡
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
def md_yearly_maker_share_1():
    mo.md(r"""
    Switch2､Switchの販売台数減少で､相対的にSONYのシェアが上昇し続けています｡ 任天堂のシェアが88.8%から88.6%に低下しました｡
    """)
    return


@app.cell
def ps5_switch_sales_streak(df_all: pl.DataFrame):
    # PS5とSwitchの週次販売台数を同じ集計日で比較する
    def _calculate_ps5_switch_streaks(sales_df: pl.DataFrame):
        comparison = (
            sales_df
            .filter(pl.col("hw").is_in(["PS5", "NSW"]))
            .select("report_date", "hw", "units")
            .pivot(
                index="report_date",
                on="hw",
                values="units",
                aggregate_function="last",
            )
            # 片方のデータがない週は、公平に比較できないため除外する
            .drop_nulls(["PS5", "NSW"])
            .sort("report_date")
            .with_columns(
                (pl.col("PS5") > pl.col("NSW")).alias("ps5_above_switch")
            )
        )

        # PS5 > Switchが真で、集計日が7日間隔の行を連続区間にまとめる
        runs = []
        current_run = []
        for row in comparison.to_dicts():
            is_next_week = (
                not current_run
                or (row["report_date"] - current_run[-1]["report_date"]).days == 7
            )
            if row["ps5_above_switch"] and is_next_week:
                current_run.append(row)
            else:
                if current_run:
                    runs.append(current_run)
                current_run = [row] if row["ps5_above_switch"] else []
        if current_run:
            runs.append(current_run)

        latest_date = comparison["report_date"].max()
        run_records = [
            {
                "start_date": run[0]["report_date"],
                "end_date": run[-1]["report_date"],
                "weeks": len(run),
                "ps5_units": sum(row["PS5"] for row in run),
                "switch_units": sum(row["NSW"] for row in run),
                "units_diff": sum(row["PS5"] - row["NSW"] for row in run),
                "is_current": run[-1]["report_date"] == latest_date,
            }
            for run in runs
        ]

        # 継続週数の長い順に並べ、同じ週数には同じ順位を付ける
        streaks = (
            pl.DataFrame(run_records)
            .with_columns(
                pl.col("weeks")
                .rank(method="dense", descending=True)
                .cast(pl.Int16)
                .alias("rank")
            )
            .select(
                "rank",
                "weeks",
                "start_date",
                "end_date",
                "ps5_units",
                "switch_units",
                "units_diff",
                "is_current",
            )
            .sort(["weeks", "start_date"], descending=[True, False])
        )
        return comparison.sort("report_date", descending=True), streaks


    ps5_switch_comparison, ps5_switch_streaks = _calculate_ps5_switch_streaks(df_all)
    ps5_switch_streak = int(
        ps5_switch_streaks.filter(pl.col("is_current"))["weeks"].item()
    )

    # 全連続区間を長い順に表示し、現在進行中の区間を識別できるようにする
    mo.vstack(
        [
            mo.md(
                f"**現在は{ps5_switch_streak}週連続。"
                "全期間の最長記録と比較した一覧です。**"
            ),
            mo.ui.table(ps5_switch_streaks, pagination=True, page_size=15),
        ]
    )
    return


@app.cell
def nintendo_2026_quarterly_forecast(df_all: pl.DataFrame):
    # 過去の四半期構成比から、任天堂ハードの2026年販売台数を予測する
    def _forecast_nintendo_2026(sales_df: pl.DataFrame):
        # gamedataの既存関数で、2015～2025年のメーカー別・暦年四半期別販売を集計する
        historical = (
            g.quarterly_sales(
                sales_df,
                begin=date(2015, 1, 1),
                end=date(2025, 12, 31),
                maker_mode=True,
            )
            .filter(pl.col("maker_name") == "Nintendo")
            .select("year", "q_num", "quarter", "quarterly_units")
            .with_columns(
                pl.col("quarterly_units").sum().over("year").alias("yearly_units")
            )
            # 各年の年間販売台数に占める四半期販売台数の比率を求める
            .with_columns(
                (pl.col("quarterly_units") / pl.col("yearly_units")).alias(
                    "quarter_ratio"
                )
            )
            .sort(["year", "q_num"])
        )

        # 11年間について、四半期ごとの年間構成比を単純平均する
        average_ratios = (
            historical.group_by("q_num")
            .agg(
                pl.col("quarter_ratio").mean().alias("average_ratio"),
                pl.col("quarterly_units").mean().round().cast(pl.Int64).alias(
                    "average_units"
                ),
            )
            .with_columns(
                (pl.col("average_ratio") * 100).round(2).alias("average_pct")
            )
            .sort("q_num")
        )

        # 2026年は完了済みのQ1・Q2だけを実績値として取得する
        actual_2026_h1 = (
            g.quarterly_sales(
                sales_df,
                begin=date(2026, 1, 1),
                end=date(2026, 6, 30),
                maker_mode=True,
            )
            .filter(pl.col("maker_name") == "Nintendo")
            .select("q_num", "quarter", "quarterly_units")
            .sort("q_num")
        )

        # 上期実績 ÷ 過去平均の上期構成比で、2026年の年間販売を逆算する
        h1_units = int(actual_2026_h1["quarterly_units"].sum())
        h1_ratio = float(
            average_ratios.filter(pl.col("q_num").is_in([1, 2]))[
                "average_ratio"
            ].sum()
        )
        annual_forecast = round(h1_units / h1_ratio)

        # 逆算した年間値を、過去平均のQ3・Q4構成比で配分する
        q3_forecast = round(
            annual_forecast
            * average_ratios.filter(pl.col("q_num") == 3)["average_ratio"].item()
        )
        q4_forecast = round(
            annual_forecast
            * average_ratios.filter(pl.col("q_num") == 4)["average_ratio"].item()
        )
        forecast = pl.DataFrame(
            {
                "period": ["2026Q1", "2026Q2", "2026Q3", "2026Q4", "2026年"],
                "status": ["実績", "実績", "予測", "予測", "予測"],
                "units": [
                    actual_2026_h1["quarterly_units"][0],
                    actual_2026_h1["quarterly_units"][1],
                    q3_forecast,
                    q4_forecast,
                    annual_forecast,
                ],
            }
        )
        return historical, average_ratios, forecast


    (
        nintendo_quarterly_history,
        nintendo_quarterly_average_ratios,
        nintendo_2026_forecast,
    ) = _forecast_nintendo_2026(df_all)

    # 年別実績、季節構成比、2026年予測をまとめて表示する
    mo.vstack(
        [
            mo.md("## 任天堂ハードの暦年四半期販売と2026年予測"),
            mo.md("### 2015～2025年の四半期販売台数と年間構成比"),
            mo.ui.table(nintendo_quarterly_history, pagination=True, page_size=12),
            mo.md("### 四半期構成比の11年間平均"),
            nintendo_quarterly_average_ratios,
            mo.md("### 2026年予測（Q1・Q2実績から逆算）"),
            nintendo_2026_forecast,
        ]
    )
    return nintendo_2026_forecast, nintendo_quarterly_history


@app.cell
def nintendo_yearly_comparison(
    nintendo_2026_forecast,
    nintendo_quarterly_history,
):
    # 2026年予測を、2015～2025年の任天堂ハード年間販売台数と比較する
    nintendo_yearly_comparison = (
        nintendo_quarterly_history.group_by("year")
        .agg(pl.col("quarterly_units").sum().alias("units"))
        .with_columns(pl.lit("実績").alias("status"))
        .vstack(
            pl.DataFrame(
                {
                    "year": [2026],
                    "units": [
                        nintendo_2026_forecast.filter(
                            pl.col("period") == "2026年"
                        )["units"].item()
                    ],
                    "status": ["予測"],
                },
                schema={"year": pl.Int16, "units": pl.Int64, "status": pl.String},
            )
        )
        .sort("year")
    )

    _nintendo_2026_units = nintendo_yearly_comparison.filter(
        pl.col("year") == 2026
    )["units"].item()
    _nintendo_2026_rank = (
        nintendo_yearly_comparison.filter(pl.col("units") > _nintendo_2026_units).height
        + 1
    )
    _nintendo_nearest_year = (
        nintendo_yearly_comparison.filter(pl.col("year") != 2026)
        .with_columns(
            (pl.col("units") - _nintendo_2026_units).abs().alias("absolute_difference")
        )
        .sort("absolute_difference")
        .row(0, named=True)
    )
    _nintendo_difference = _nintendo_2026_units - _nintendo_nearest_year["units"]
    _nintendo_difference_pct = _nintendo_difference / _nintendo_nearest_year["units"]

    nintendo_yearly_comparison_chart = (
        alt.Chart(nintendo_yearly_comparison)
        .mark_bar()
        .encode(
            x=alt.X("year:O", title="年"),
            y=alt.Y("units:Q", title="年間販売台数"),
            color=alt.Color(
                "status:N",
                title="区分",
                scale=alt.Scale(
                    domain=["実績", "予測"], range=["#4C78A8", "#F58518"]
                ),
            ),
            tooltip=[
                alt.Tooltip("year:O", title="年"),
                alt.Tooltip("units:Q", title="販売台数", format=","),
                alt.Tooltip("status:N", title="区分"),
            ],
        )
        .properties(width=650, height=320)
    )

    mo.vstack(
        [
            mo.md("### 任天堂ハード年間販売台数との比較"),
            mo.md(
                f"2026年予測は **{_nintendo_2026_units:,}台**で、"
                f"2015～2026年の12年中 **{_nintendo_2026_rank}位**に相当します。"
                f"最も近い{_nintendo_nearest_year['year']}年"
                f"（{_nintendo_nearest_year['units']:,}台）を"
                f"{_nintendo_difference:,}台（{_nintendo_difference_pct:.1%}）上回る水準です。"
            ),
            mo.ui.altair_chart(nintendo_yearly_comparison_chart),
            mo.ui.table(
                nintendo_yearly_comparison.sort("units", descending=True),
                pagination=False,
            ),
        ]
    )
    return


if __name__ == "__main__":
    app.run()
