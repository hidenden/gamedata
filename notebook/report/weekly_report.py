# /// script
# [tool.marimo.display]
# theme = "system"
# ///

import marimo

__generated_with = "0.23.6"
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
    return df_all, ns2_info, report_date, show_title


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
    Switch2日本語版の値上げ直後の週販は､前週から21万台減の31,751台でした｡
    これはSwitch2の週販ワースト記録です｡これまでのワーストは2025年8月24日の35,359台でした｡
    これはSwitch2の品薄時期の週販で､これまで唯一4万台を割り込んだ記録でした｡
    一方､今回は在庫十分のまま4万台を割り込んだ初のケースです｡

    今後､Nintendo Direct, Star Fox, スプラトゥーン・レイダース, ELDEN RINGなどで
    話題性を高めて販売数を回復していくことが期待されます｡
    """)
    return


@app.cell(hide_code=True)
def md_weekly_summary_3():
    mo.md(r"""
    Switchの6,201台も最低記録です｡これまでの最低は2026年2月8日の8,892台でした｡一気に2,000台以上減少しました｡
    Switchの場合は値上げと在庫不足のダブルパンチで大きく減少したと考えられます｡
    この先､回復していくのかどうか､このまま終息に向かうのか注目されます｡

    PS5も減少して8,373台となりました｡ゲーム機最安値(日本語版)のチャンスを活かせていません｡
    「価格」はゲーム機の機種選択において関係ないとまでは言えませんが､支配的な要因ではないのでしょう｡
    PS5DE日本語版の低価格を維持する必要があるのかどうか､疑問を感じる結果です｡

    Xbox Series X|Sは(比較)好調を維持しています｡
    Forza Horizon 6の影響が続いています｡
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
        hw=["NSW", "NS2", "PS5", "XSX"], begin=_begin, end=_end, annotation_level=32,
        padding_end = 1,
    )

    _weekly_chart = mo.ui.altair_chart(_chart)
    mo.hstack(items=[_weekly_chart], justify="start", wrap=True)
    return


@app.cell(hide_code=True)
def md_weekly_sales_trend_1():
    mo.md(r"""
    Switch2の値上げが始まり極端に落ち込みました｡
    Switch2は週販が極端に動くケースが多く､発売から1年経過しても平常時の週販水準が判別できない状況です｡
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
        hw=["NSW", "PS5", "XSX", "NS2"], begin=_begin, end=_end, annotation_level=50, ymax=50000, padding_end=1
    )
    mo.hstack(items=[mo.ui.altair_chart(_chart)], justify="start", wrap=True)
    return


@app.cell(hide_code=True)
def md_weekly_sales_trend_3():
    mo.md(r"""
    Switch2以外はいずれも1万台を割り込み､減少傾向が続く寂しい週販です｡
    6月は(E3は無くなりましたが)各プラットフォームがプロモーションを強化する月です｡今月は週販が回復していくことを期待したいですね｡
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
    各年の1月からの累計を比較し、今年が過去と比べてどの程度のペースで販売できているかを確認します。
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
        x=151,
        y=284752,
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
    昨年と同程度で推移しています｡
    昨年はMHWsによる牽引分があったため、その差がマイナス要因になっています。
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
        x=151,
        y=442945,
        x2=365,
        y2=700000,
        stroke=[3, 2],
        size=2,
        color="#ff000080",
    )
    mo.ui.altair_chart(_chart)
    return


@app.cell(hide_code=True)
def md_switch_yearly_cumulative_1():
    mo.md(r"""
    5月25日の値上げにより販売ペースが落ちました｡現状のペースだと昨年の半分程度になる可能性が高いです｡
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
        x=151,
        y=2081146,
        x2=365,
        y2=4200000,
        stroke=[3, 2],
        size=2,
        color="#ffa00080",
    )
    mo.ui.altair_chart(_chart)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    予想ラインは調整しましたが､正直､この先がどうなっていくかは､今週の結果だけから予想するのは難しいです。
    この落ち込みがこのまま続くのか､今回が特別な落ち込みなのか､今後の週販の動きに注目する必要があります｡
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
    return


@app.cell(hide_code=True)
def md_monthly_sales_trend_1():
    mo.md(r"""
    2026年の5月のハード販売台数が80万台を超えました｡
    5月の月間販売台数としてDSブームの2006年、2007年に次ぐ歴代3位の記録であり、今後この記録を超えるのは困難でしょう｡
    Switch2の値上げは年末商戦期に匹敵するピークを作り出しました｡
    """)
    return


@app.cell
def may_monthly_sales_chart():
    _chart = g.chart_bar_month_year(
        month=5, begin_year=2001, end_year=2026, stacked=True
    )
    _chart = g.chart_rule_xy(
        base_chart=_chart, y=843000, stroke=[10, 3], size=2, color="#00000080"
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

    _chart = g.chart_rule_xy(_chart, y=711991, stroke=[2, 3], size=3, color="#d06080")

    mo.ui.altair_chart(_chart)
    return


@app.cell(hide_code=True)
def md_ns2_monthly_sales_1():
    mo.md(r"""
    Switch2は値上げ後も3万台超を販売し､2026年5月の販売台数が71万台を超えました｡
    第2のロンチとも言える盛り上がりでした｡
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
    Switchの2026年5月は前年比73%でした｡
    ここから先は値上げの影響も出るため､さらに落ち込むと予想されます｡
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
    PS5の5月は5万台を超え､前年比156%と､昨年と比べて好調なペースでした｡
    ただし、この好調さも今月までで、
    昨年6月はセールの影響で販売を伸ばしたため､今年の6月は昨年比で落ち込む可能性が高いです｡
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
        padding_end = 6,
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
def _():
    _chart = g.chart_line_cumulative(
        hw=["NS2", "PS5"],
        begin=datetime(2025, 3, 20),
        end=datetime(2026, 12, 31),
        annotation_level=30,
        multi_line=True,
        mode="week",
        padding_end=36
    )
    _chart = g.chart_line_guide(
        base_chart=_chart,
        x=date(2026, 5, 31),
        y=5865213,
        x2=date(2027, 1, 31),
        y2=8400000,
        stroke=[5, 4],
        size=2,
        color="#af000080",
    )
    _chart = g.chart_line_guide(
        base_chart=_chart,
        x=date(2026, 5, 31),
        y=7582962,
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
    Switch2の値上げ後のトレンドが大きく下がらない限りは2026年内にSwitch2はPS5の国内累計を追い抜くでしょう｡
    """)
    return


@app.cell
def md_ns2_sales_weeks_title(ns2_info):
    _ns2_weeks = ns2_info["sales_weeks"]
    mo.md(f"### Switch2: {_ns2_weeks}週目の状況")
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
        y2=7000000,
        stroke=[2, 3],
        size=2,
        color="#800000",
    )
    cd_chart = mo.ui.altair_chart(_chart)
    mo.vstack(items=[cd_chart], justify="start")
    return


@app.cell(hide_code=True)
def md_ns2_cumulative_delta_1():
    mo.md(r"""
    駆け込み需要の影響で､Switch2の歴代最速記録は当面維持される見込みです｡
    Switch2値上げ後の販売ペースが明らかになると､予想が変わる可能性はあります｡
    (このSwitch2の推移､後年見たら絶対年末商戦と誤認して混乱するやつなので､ほんと注意が必要)
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
    Switch2とSwitch値上げに伴う販売台数の減少により､任天堂のシェアは89.6%から89.5%に低下しました｡
    もっと低下するかと思いましたが､PS5も伸びていないので､あまり変化がありませんでした｡
    """)
    return


if __name__ == "__main__":
    app.run()
