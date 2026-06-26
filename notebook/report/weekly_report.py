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
    Switch2は642台増えて2万6千台です｡回復していると言うより「下がらなかった」レベルですね｡
    今後 Star Fox, リズム天国とリリースが続くので､
    それが販売台数の回復にどのように影響するか注目したいところです｡


    Switchが下げ止まりました｡
    今後5000台前後で推移するのか､ここから上昇していくのか｡
    リズム天国に合わせてLiteの本体出荷が行われると､回復の起爆剤になるかも知れません｡

    PS5は5週間ぶりに8千台から脱して9449台となりました｡
    次週はボーナス効果が期待できるので1万台に回復する可能性があります｡
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
        ymax=40000,
        padding_end=1,
        value_label=True,
    )
    mo.hstack(items=[mo.ui.altair_chart(_chart)], justify="start", wrap=True)
    return


@app.cell(hide_code=True)
def md_weekly_sales_trend_3():
    mo.md(r"""
    全機種が同じ調子で上がるのは珍しいですね､低水準ではありますが｡
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
        y2=570000,
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
    過去のPS機種との同時期(週数)比較だとPS5は歴代据置機では最低の状況が続いています｡
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
        y2=650000,
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
    店頭在庫が無く最低水準が続いています｡
    リズム天国週に本体供給が回復するか注目されます｡
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
        y2=3900000,
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
    販売台数の低迷が続いています｡
    この状況が続くと年末ブースト込みで昨年の販売台数に近い値になってしまう可能性があります｡
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
    6月最終値としては前年比10%を割り込みそうです｡
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
    Switchの2026年6月も厳しい状況です｡前年同月比30%前後となる見込みです｡
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
    PS5もペースが上がりません｡
    前年同月比で50%前後となる見込みです｡
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
    Xbox Series X|Sは前年同月比を上回ったただ一つの機種になりました｡
    最終的に前年比150%程度になりそうです｡
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
        y2=8050000,
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
    Switch2は累計594万台で
    PS5通常版の累計592万台を超えました｡
    PS5全体を超えるのは2027年1月になりそうです｡

    600万台まで6万台に迫ってますが､今のペースだと600万台超えは3週間後です｡
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
        y2=6800000,
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
    Switch2の歴代普及最速はあと15週間(3ヶ月半)程度は維持できるでしょう｡
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
    Switch2は同時期のSwitchを約200万台上回る状況は続いています｡
    """)
    return


@app.cell
def _(switch2_latest):

    g.style_df(g.rename_columns(g.reached_unit_summary(n=switch2_latest["sum_units"], all=False)))
    return


@app.cell(hide_code=True)
def md_ns2_cumulative_delta_1():
    mo.md(r"""
    Switch2はSwitchの1.7倍､PS5の3.6倍の販売ペースを維持しています｡
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
    2026年上期としては､2020年の水準には達しませんが､2018年､2019年 2022年､2024年､2025年は超えそうです｡
    Switch2, Switchの値上げの影響が下期にどう響いてくるか注目したいところです｡
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
    Switch2の販売台数減少で､相対的にSONYのシェアが上昇し､任天堂のシェアが89.1%から89.0%に低下しました｡
    """)
    return


if __name__ == "__main__":
    app.run()
