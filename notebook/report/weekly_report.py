# /// script
# [tool.marimo.display]
# theme = "system"
# ///

import marimo

__generated_with = "0.23.5"
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
    ## 直近4週間のハード売り上げ／累計推移
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
    Switch2日本語版の値上げ直前の週販です｡
    非常に強い駆け込み需要により先週から3万台増加し24万7千台を販売しました｡
    これは歴代2位の記録です｡
    """)
    return


@app.cell
def weekly_sales_ranking():
    g.style_df(g.weekly_sales_ranking(rank_n=10, hw=["NS2"]))
    return


@app.cell(hide_code=True)
def md_weekly_summary_2():
    mo.md(r"""
    Switch2の駆け込み需要は年末商戦を越える勢いでした｡
    値上げを商戦期に転換する任天堂の作戦勝ちです｡
    来週以降はしばらくこの反動があります｡2万台前後の水準が一ヶ月程度続く可能性があります｡
    ただビッグタイトルがリリースされるタイミングで販売台数は戻ってくるでしょう｡
    """)
    return


@app.cell(hide_code=True)
def md_weekly_summary_3():
    mo.md(r"""
    Switchから半減して1万台を割り込みました｡
    来週以降､値上げの影響で落ち込むのは間違いないと思いますが､
    SwitchはSwitch2と異なり､落ち込んだらそのまま低下し､販売数が戻らない可能性も高く､PS5を下回る週が増えるでしょう｡

    PS5も減少して9000台を割り込みました｡
    しかし､次回集計からは『日本最安値のゲーム機』となるので､その効果が現れるか注目です｡

    Xbox Series X|Sが倍増しました｡
    Forza Horizon 6の影響が強く現れていると考えられます｡
    FH6は口コミで評判を広げており､しばらくは好調が続くと良いですね｡
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
    _chart = g.chart_line_sales(begin=_begin, end=_end, annotation_level=32)

    _weekly_chart = mo.ui.altair_chart(_chart)
    mo.hstack(items=[_weekly_chart], justify="start", wrap=True)
    return


@app.cell(hide_code=True)
def md_weekly_sales_trend_1():
    mo.md(r"""
    Switch2駆け込み需要の高いピークが現れています｡
    ただし､年末商戦とは異なり､来週からは激しい落ち込みが予想されます｡
    駆け込み需要直前が45000台前後だったので､ここから半減の2万2千台前後がしばらく続くと予想しますが､
    こればっかりは分かりませんね｡
    """)
    return


@app.cell(hide_code=True)
def md_weekly_sales_trend_2():
    mo.md(r"""
    ### 週販推移(Switch2以外)
    """)
    return


@app.cell
def weekly_sales_trend_2(report_date: datetime):
    _begin = date(2026, 2, 1)
    _end = report_date
    _chart = g.chart_line_sales(
        hw=["NSW", "PS5", "XSX"], begin=_begin, end=_end, annotation_level=50
    )
    mo.hstack(items=[mo.ui.altair_chart(_chart)], justify="start", wrap=True)
    return


@app.cell(hide_code=True)
def md_weekly_sales_trend_3():
    mo.md(r"""
    Switch2以外は1万台を割り込む寂しい水準です｡
    次回集計ではSwitch2,Switchが値上げされます｡PS5へのプラス影響としては現れるか注目です｡
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
    各年の1月からの累計を比較し､今年が今までと比べてどの程度のペースで販売できているかを比較します｡
    """)
    return


@app.cell(hide_code=True)
def md_ps5_yearly_cumulative_title():
    mo.md(r"""
    ### PlayStation 5(2024年, 2025年, 2026年)
    """)
    return


@app.cell
def _():
    return


@app.cell
def ps5_yearly_cumulative_chart():
    _chart = g.chart_line_ycumulative_by_hw_year(
        hw_years=[("PS5", 2024), ("PS5", 2025), ("PS5", 2026)],
        annotation_level=31,
    )
    _chart = g.chart_line_guide(
        _chart,
        x=139,
        y=267706,
        x2=365,
        y2=600000,
        stroke=[3, 2],
        size=2,
        color="#ff000080",
    )

    mo.ui.altair_chart(_chart)
    return


@app.cell(hide_code=True)
def md_ps5_yearly_cumulative_1():
    mo.md(r"""
    昨年と同程度で推移しています｡昨年のMHWs牽引分の差がマイナスになっています｡
    11月のGTA6でブーストすれば､年間累計が2025年並になる可能性もあります｡
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
        x=139,
        y=427205,
        x2=365,
        y2=850000,
        stroke=[3, 2],
        size=2,
        color="#ff000080",
    )
    mo.ui.altair_chart(_chart)
    return


@app.cell(hide_code=True)
def md_switch_yearly_cumulative_1():
    mo.md(r"""
    2026年のSwitchは現時点では2025年の6割弱ですが､5月25日の値上げにより､さらにペースが落ちて昨年の半分以下になる可能性が高いです｡
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
        annotation_level=34,
    )
    _chart = g.chart_line_guide(
        _chart,
        x=142,
        y=2049395,
        x2=365,
        y2=4500000,
        stroke=[3, 2],
        size=2,
        color="#ffa00080",
    )
    mo.ui.altair_chart(_chart)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    2026年のSwitch2販売台数が200万台を超えました｡
    値上げ後は9月頃(240週)まではゆっくりとした上昇カーブを描くと予想されます｡
    """)
    return


@app.cell(hide_code=True)
def md_monthly_sales_trend_title():
    mo.md(r"""
    ## 月間販売推移
    """)
    return


@app.cell
def monthly_sales_trend_chart(report_date: datetime):
    _bar = g.chart_bar_sales(begin=datetime(2025, 3, 1), end=report_date, stacked=True)
    bar_chart = mo.ui.altair_chart(_bar)
    bar_chart
    return (bar_chart,)


@app.cell(hide_code=True)
def md_monthly_sales_trend_1():
    mo.md(r"""
    2026年5月の販売台数は795,517台に達しました｡現時点で2025年11月を超えました｡
    5月はあと1回集計を残しているので80万台を超えるのは確実です｡
    """)
    return


@app.cell
def monthly_sales_trend_table(bar_chart, is_publish):
    if is_publish:
        mo.stop(True)

    _s = bar_chart.dataframe.pivot(index="year_month", on="hw", values="monthly_units")
    mo.hstack(items=[_s], justify="start", wrap=True)
    return


@app.cell(hide_code=True)
def md_may_monthly_sales_comparison_1():
    mo.md(r"""
    5月の月間販売台数としてDSブームの2006年､2007年に次ぐ歴代3位の記録になりました｡
    """)
    return


@app.cell
def may_monthly_sales_chart():
    _chart = g.chart_bar_month_year(
        month=5, begin_year=2001, end_year=2026, stacked=True
    )
    _chart = g.chart_rule_xy(
        base_chart=_chart, y=720000, stroke=[10, 3], size=2, color="#00000080"
    )
    m_chart = mo.ui.altair_chart(_chart)
    m_chart
    return


@app.cell(hide_code=True)
def md_ns2_monthly_sales_title():
    mo.md(r"""
    ### Nintendo Switch2: 月間販売台数
    """)
    return


@app.cell
def ns2_monthly_sales_chart(report_date: datetime):
    _chart = g.chart_bar_sales(
        hw=["NS2"], begin=datetime(2025, 3, 1), end=report_date, stacked=True
    )

    _chart = g.chart_rule_xy(_chart, y=680240, stroke=[2, 3], size=3, color="#d06080")

    mo.ui.altair_chart(_chart)
    return


@app.cell(hide_code=True)
def md_ns2_monthly_sales_1():
    mo.md(r"""
    2026年5月のSwitch2は60万台を軽く突破し68万台に到達しました｡
    あと2万台で70万台ですが､値上げ直後にどこまで行けるか注目されます｡
    """)
    return


@app.cell(hide_code=True)
def md_switch_monthly_sales_title():
    mo.md(r"""
    ### Nintendo Switch:月間販売台数
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
    先週に続いてSwitchの駆け込み需要は発生していません｡
    値上げ後の来月以降､本格的な落ち込みが予想されます｡
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
    5月のPS5は快調とは言えませんが､昨年よりはマシな状況です｡
    あと1回集計があるので､5万台を超える可能性があります｡
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
        annotation_level=15,
        multi_line=True,
        mode="week",
    )
    chart_cumulative = mo.ui.altair_chart(_chart)
    chart_cumulative
    return


@app.cell(hide_code=True)
def md_cumulative_sales_trend_1():
    mo.md(r"""
    Switch2がPS5に急速に迫っています｡その差は174万台まで縮まりました｡
    """)
    return


@app.cell
def md_ns2_sales_weeks_title(ns2_info):
    _ns2_weeks = ns2_info["sales_weeks"]
    mo.md(f"### Switch2:{_ns2_weeks}週目の状況")
    return


@app.cell
def ns2_cumulative_delta_chart(ns2_info):
    _chart = g.chart_line_cumulative_delta(
        hw=[
            "NS2",
            "NSW",
            "PS5",
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
        y2=6900000,
        stroke=[2, 3],
        size=2,
        color="#800000",
    )
    cd_chart = mo.ui.altair_chart(_chart)
    mo.vstack(items=[cd_chart], justify="start")
    return (cd_chart,)


@app.cell
def ns2_cumulative_delta_table(cd_chart, ns2_info):
    _df = (
        cd_chart.dataframe.filter(pl.col("index_week") == ns2_info["sales_weeks"])
        .select(["hw", "sum_units"])
        .sort("sum_units", descending=True)
    )
    g.style_df(g.rename_columns(_df), bar=True)
    return


@app.cell(hide_code=True)
def md_ns2_cumulative_delta_1():
    mo.md(r"""
    駆け込み需要の影響で､Switch2の歴代最速記録は70週目(10月頃)まで続きそうです｡
    10月に入れば年末モードに突入します｡歴代最速の座をDSに譲るのは年明けになるかも知れません｡
    """)
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
    PS5DE日本語版が日本のゲーム機最安値となったことでブースト効果があるのかどうかが注目されます｡
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
    _chart = g.chart_hbar_yearly_share_by_maker(2015, 2026)
    share_chart = mo.ui.altair_chart(_chart)
    mo.vstack(items=[share_chart], justify="start")
    return


@app.cell(hide_code=True)
def md_yearly_maker_share_1():
    mo.md(r"""
    Switch2の年末商戦級の駆け込み需要の影響で任天堂のシェアが89.6%に達しました｡
    任天堂が5月に一人年末商戦をやったせいです｡
    2026年のピークはここでしょう｡この先は徐々に任天堂のシェアが低下し87%程度で落ち着くと思われます｡
    """)
    return


if __name__ == "__main__":
    app.run()
