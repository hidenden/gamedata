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
    Switch2は下げ止まり2,734台増加して25,793台でした｡
    Nintendo Direct効果も多少はあったのでしょう｡
    駆け込み需要の反動は続いていますが､
    谷底を抜けたと見ていいでしょう｡


    Switchはさらに減少して4,933台でした｡5,000台を切るのは初めてで歴代最低記録更新です｡
    駆け込み需要の反動もありますが､
    店頭在庫が無い影響が大きいと考えられます｡
    回復は供給側次第なので今後の見込みは難しいですね｡

    Switch2, Switchが駆け込み､価格変更､在庫切れで販売台数を上下に激しく変化させる一方､
    8千台で揺るがないPS5の販売台数｡ここまで全く連動しないとは思いませんでした｡これが「住み分け」というやつでしょうか｡
    ボーナス週(再来週)くらいは上振れしそうです｡
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
    Switch2が他の機種と近い水準まで落ち込んできました｡
    Switch2が4万台を切る水準がいつまで続くのかが焦点です｡
    (このままずっと4万台を切るようだと価格の影響が大きいと考えられます｡)
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
    全機種低水準継続中です｡
    5月とは一転して6月は記録的な低水準になる可能性もあります｡
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
def ps5_yearly_cumulative_chart():
    _chart = g.chart_line_ycumulative_by_hw_year(
        hw_years=[("PS5", 2024), ("PS5", 2025), ("PS5", 2026)],
        annotation_level=31,
    )
    _chart = g.chart_line_guide(
        _chart,
        x=165,
        y=301582,
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
    Vitaよりは上ですが｡
    """)
    return


@app.cell(hide_code=True)
def md_switch_yearly_cumulative_title():
    mo.md(r"""
    ### Switch(2024年, 2025年, 2026年)
    """)
    return


@app.cell
def switch_yearly_cumulative_chart():
    _chart = g.chart_line_ycumulative_by_hw_year(
        hw_years=[("NSW", 2024), ("NSW", 2025), ("NSW", 2026)],
        annotation_level=39,
    )
    _chart = g.chart_line_guide(
        _chart,
        x=165,
        y=455749,
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
    このまま供給が回復しないと年間販売数が70万台を切る可能性があります｡
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Switch2(2025年, 2026年)
    """)
    return


@app.cell
def _():
    _chart = g.chart_line_ycumulative_by_hw_year(
        hw_years=[("NS2", 2025), ("NS2", 2026)],
        annotation_level=25,
    )
    _chart = g.chart_line_guide(
        _chart,
        x=165,
        y=2129998,
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
    6月も半分経過してSwitch2の前年同月比は4%です｡
    6月最終値としては10%前後になる見込みです｡
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
    2026年6月に前年を超えそうなのはXbox Series X|Sだけです｡
    前年比150%を超える可能性もあります｡
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
def _(ns2_info, ps5_info):
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
        x=date(2026, 6, 14),
        y=ns2_info["total_units"],
        x2=date(2027, 1, 31),
        y2=8150000,
        stroke=[5, 4],
        size=2,
        color="#af000080",
    )
    _chart = g.chart_line_guide(
        base_chart=_chart,
        x=date(2026, 6, 14),
        y=ps5_info["total_units"],
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
    Switch2は600万台まで9万台に迫ってます｡今までなら2週間で超えたはずですが､現状では3週間かかりそうです｡
    Switch2の低迷が長くなると､Switch2がPS5の国内累計を追い抜くのは2027年1月後半になる可能性があります｡
    """)
    return


@app.cell
def md_ns2_sales_weeks_title(ns2_info):
    _ns2_weeks = ns2_info["sales_weeks"]
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
def _():

    g.style_df(g.rename_columns(g.reached_unit_summary(n=5914065, all=False)))
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
    Switch2の販売台数減少で､相対的にSONYのシェアが上昇し､任天堂のシェアが89.3%から89.1%に低下しました｡
    """)
    return


if __name__ == "__main__":
    app.run()
