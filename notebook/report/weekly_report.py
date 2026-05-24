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
def _():
    _args = mo.cli_args()
    is_publish = True if _args.get("publish") else False

    if not is_publish:
        g.disable_styler()
        alt.theme.enable("edit")
    else:
        alt.theme.enable("publish")
    return (is_publish,)


@app.cell
def _(is_publish):
    # レポート日付
    from report_config import get_config

    config = get_config()
    report_date: datetime = config["date"]

    def show_title(d: datetime):
        last_updated_str = d.strftime("%Y-%m-%d")
        mode: str = "**DRAFT**" if not is_publish else ""
        return mo.md(f"# 国内ゲームハード週販レポート ({last_updated_str}) {mode}")

    df_all = g.load_hard_sales(True)
    [ns2_info, ps5_info, nsw_info] = g.hard_sales_summary(
        df_all, hw=["NS2", "PS5", "NSW"]
    )
    return df_all, ns2_info, ps5_info, report_date, show_title


@app.cell
def _(report_date: datetime, show_title):
    show_title(report_date)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    * ハードウェアの販売データはファミ通の調査結果を基にしています。
    * 複数週合算の集計値は処理上の都合により、週次値に調整しています｡
    * [過去の週販レポート](../index.html)
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 直近4週間のハード売り上げ／累計推移
    """)
    return


@app.cell
def _(df_all, report_date: datetime):
    _table = g.units_by_date_hw_table(
        df_all, begin=g.weeks_before(report_date, 3), end=report_date
    )
    mo.hstack(items=[_table], justify="start", wrap=True)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Switch2日本語版が5月25日以降､1万円値上げされる影響が強く出た週販です｡
    [(当社商品およびサービスの価格変更に関するお知らせ)](https://www.nintendo.co.jp/corporate/release/2026/260508.html)

    以下にSwitch2の週間販売のTOP10を示します｡
    今週の217,922台は歴代3位です｡これは年末商戦期の12月7日の203,398台を超えています｡
    """)
    return


@app.cell
def _():
    g.style_df(g.weekly_sales_ranking(rank_n=10, hw=["NS2"]))
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    任天堂は今回の値上げを相当前に計画して､時間をかけて準備し､駆け込み需要に備えて年末商戦級の供給体制を準備していたものと見られます｡

    次回集計は値上げ直前日を含むので(供給が途絶えなければ)今週と同等の販売台数が期待できます｡
    (こういうデータは後から見返した時に「なんでこんな時期にこんなスパイクあるの?」となりがち)
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Switchは先週とほぼ変わらず｡需要がSwitch2に集中していることと､供給制約の影響と思われます｡

    PS5は1万台を割り込みましたが､この時期はこんなものです｡
    毎年､6月はセールがあるので､それを期待した直前の落ち込みの可能性もあります｡
    ただPS5DE日本語版で常時セール状態とも言えるので､今年のSIEはどうすんでしょうか｡

    地味ですが､Xbox Series X|Sが増えています｡FH6の影響が出始めてるのか?
    FH6の効果が明確に出るとすると次回集計なので､Microsoftがチャンスを逃さずXboxを供給することを期待したいところです｡
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 週販推移
    """)
    return


@app.cell
def _(report_date: datetime):
    _begin = g.report_begin(report_date)
    _end = report_date
    _chart = g.chart_line_sales(begin=_begin, end=_end, annotation_level=15)

    _weekly_chart = mo.ui.altair_chart(_chart)
    mo.hstack(items=[_weekly_chart], justify="start", wrap=True)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    5月に年末商戦期がやってきたような推移です｡
    これだけ需要が集中すると､値上げ直後は相当な落ち込みがありそうです｡
    スプラトゥーン・レイダース頃までは戻らないかも知れません｡
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### 週販推移(Switch2以外)
    """)
    return


@app.cell
def _(report_date: datetime):
    _begin = date(2026, 2, 1)
    _end = report_date
    _chart = g.chart_line_sales(
        hw=["NSW", "PS5", "XSX"], begin=_begin, end=_end, annotation_level=50
    )
    mo.hstack(items=[mo.ui.altair_chart(_chart)], justify="start", wrap=True)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    今のところSwitch2､Switchの値上げ発表は､PS5へのプラス影響としては現れていません｡
    実際に値上げされる再来週の集計でどうなるかが注目されます｡
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Switch2がPS5まで200万台差に迫る
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Switch2とPS5の累計差が200万台を切りました｡

    当初の616万台差から416万台分詰めて200万台差まで迫るのに要した期間はわずか50週間｡
    Switchは406万台差から206万台分詰めて200万台差まで迫るのに78週間を要しました｡
    現在の推移だと､78週経過する頃にはSwitch2はPS5に追いつくと見られます｡
    """)
    return


@app.cell
def _():
    _ps5_last = g.sales_value(hw="PS5", index_week=-1, cumulative=True)
    _ns2_last = g.sales_value(hw="NS2", index_week=-1, cumulative=True)
    _ns2_ps5_diff = _ps5_last - _ns2_last

    _chart = g.chart_line_cumsum_diffs(
        cmplist=[("NSW", "PS4"), ("NS2", "PS5")],
        multi_line=True,
        annotation_level=10,
    )

    _chart = g.chart_line_guide(
        base_chart=_chart,
        x=50,
        y=_ns2_ps5_diff,
        x2=78,
        y2=0,
        stroke=[5, 4],
        size=2,
        color="#00a0FF",
    )

    _chart = g.chart_rule_xy(
        base_chart=_chart, y=_ns2_ps5_diff, stroke=[1, 0], size=2, color="#189beca7"
    )

    _chart = g.chart_rule_xy(
        base_chart=_chart, y=1, stroke=[10, 0], size=2, color="#000000"
    )
    mo.ui.altair_chart(_chart)

    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 年間累計比較
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    各年の1月からの累計を比較し､今年が今までと比べてどの程度のペースで販売できているかを比較します｡
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### PlayStation 5(2023年, 2024年, 2025年, 2026年)
    """)
    return


@app.cell
def _():
    _chart = g.chart_line_ycumulative_by_hw_year(
        hw_years=[("PS5", 2024), ("PS5", 2025), ("PS5", 2026)],
        annotation_level=20,
    )
    mo.ui.altair_chart(_chart)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    2026年のPS5は2025年のMHWsのようにハードを大きく牽引するビッグタイトルに欠けています｡
    しかし､通常時のペースは昨年と同程度で推移しています｡
    秋のGTA6までこのペースで凌ぐことが出来れば､年間累計が2025年並になる可能性もあります｡
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Switch(2024年, 2025年, 2026年)
    """)
    return


@app.cell
def _():
    _chart = g.chart_line_ycumulative_by_hw_year(
        hw_years=[("NSW", 2024), ("NSW", 2025), ("NSW", 2026)],
        annotation_level=20,
    )
    mo.ui.altair_chart(_chart)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    2026年のSwitchは2025年の半分程度の推移です｡5月25日の値上げにより､さらにペースが落ちる可能性が高いです｡
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 月間販売推移
    """)
    return


@app.cell
def _(report_date: datetime):
    _bar = g.chart_bar_sales(begin=datetime(2025, 3, 1), end=report_date, stacked=True)
    bar_chart = mo.ui.altair_chart(_bar)
    bar_chart
    return (bar_chart,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Switch2の駆け込み需要で5月の販売台数が急上昇しています｡
    最終的に70万台を超え､2025年11月の商戦期に迫る勢いです｡
    """)
    return


@app.cell
def _(bar_chart, is_publish):
    if is_publish:
        mo.stop(True)

    _s = bar_chart.dataframe.pivot(index="year_month", on="hw", values="monthly_units")
    mo.hstack(items=[_s], justify="start", wrap=True)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    歴代の5月の販売台数を見てみます｡Nintendo DSブームの2006年､2007年が突出しています｡
    次週20万台上乗せされると､2026年5月は2021年､2008年を超えて歴代3位になる見込みです｡
    """)
    return


@app.cell
def _():
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
def _():
    mo.md(r"""
    ### Nintendo Switch2: 月間販売台数
    """)
    return


@app.cell
def _(report_date: datetime):
    mo.ui.altair_chart(
        g.chart_bar_sales(
            hw=["NS2"], begin=datetime(2025, 3, 1), end=report_date, stacked=True
        )
    )
    _chart = g.chart_rule_xy(_chart, y=432360, stroke=[2, 3], size=3, color="#d06080")

    mo.ui.altair_chart(_chart)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    2026年5月のSwitch2は残り2回の集計を残しながら40万台を突破しました｡
    最終的に60万台に迫り2025年12月につぐ3番目に多く販売した月になる可能性が高いです｡
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    g
    ### Nintendo Switch:月間販売台数
    """)
    return


@app.cell
def _(report_date: datetime):
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
def _(ns_df_pivot, report_date: datetime):
    _this_year = report_date.year
    my_ns_df2 = ns_df_pivot.drop(str(_this_year - 2))
    my_ns_df2 = my_ns_df2.with_columns(
        YoY=pl.col(str(_this_year)) / pl.col(str(_this_year - 1))
    )
    g.style_df(g.rename_columns(my_ns_df2))
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    先週に続いてSwitchの駆け込み需要は発生していません｡
    値上げ後の来月以降､本格的な落ち込みが予想されます｡
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### PlayStation 5: 月間販売台数
    """)
    return


@app.cell
def _(report_date: datetime):
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
def _(ps5_df_pivot, report_date: datetime):
    _this_year = report_date.year
    my_ps5_df2 = ps5_df_pivot.drop(str(_this_year - 2))
    my_ps5_df2 = my_ps5_df2.with_columns(
        YoY=pl.col(str(_this_year)) / pl.col(str(_this_year - 1))
    )
    g.style_df(g.rename_columns(my_ps5_df2))
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    5月のPS5は残り2回の集計を残しながら前年5月を超えました｡
    昨年の5月は落ち込みが激しく､好調と言ってよいのか微妙ではありますが､大きく落ち込んでいないのはPS5DE日本語版のおかげと思われます｡
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 累計販売推移
    """)
    return


@app.cell
def _(report_date: datetime):
    _chart = g.chart_line_cumulative(
        hw=["NSW", "NS2", "PS5", "XSX"],
        begin=datetime(2017, 3, 1),
        end=report_date,
        annotation_level=5,
        multi_line=True,
    )
    chart_cumulative = mo.ui.altair_chart(_chart)
    chart_cumulative
    return (chart_cumulative,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Switch2がPS5に急速に迫っています｡
    """)
    return


@app.cell
def _(chart_cumulative, is_publish):
    if is_publish:
        mo.stop(True)
    g.style_df(
        chart_cumulative.dataframe.pivot(
            index="report_date", on="hw", values="sum_units"
        ).tail(1)
    )
    return


@app.cell
def _(ns2_info):
    _ns2_weeks = ns2_info["sales_weeks"]
    mo.md(f"### Switch2:{_ns2_weeks}週目の状況")
    return


@app.cell
def _(ns2_info):
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
        annotation_level=20,
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
        y2=6600000,
        stroke=[2, 3],
        size=2,
        color="#800000",
    )
    cd_chart = mo.ui.altair_chart(_chart)
    mo.vstack(items=[cd_chart], justify="start")
    return (cd_chart,)


@app.cell
def _(cd_chart, ns2_info):
    _df = (
        cd_chart.dataframe.filter(pl.col("index_week") == ns2_info["sales_weeks"])
        .select(["hw", "sum_units"])
        .sort("sum_units", descending=True)
    )
    g.style_df(g.rename_columns(_df), bar=True)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    駆け込み需要の影響で､Switch2の累計グラフが年末商戦期のような急上昇を見せています｡
    この先の推移を見るには値上げ後の推移が落ちくまで待つ必要があります｡
    """)
    return


@app.cell
def _(ps5_info):
    ps5_weeks = ps5_info["sales_weeks"]
    mo.md(f"### PS5:{ps5_weeks}週目の状況")
    return


@app.cell
def _(ps5_info):
    _chart = g.chart_line_cumulative_delta(
        hw=["PS5", "PS4", "PS3"],
        end=ps5_info["sales_weeks"] + 60,
        mode="week",
        multi_line=True,
        annotation_level=5,
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
def _(ps_cd_chart):
    _df = (
        ps_cd_chart.dataframe.filter(pl.col("delta_week") == 284)
        .select(["hw", "sum_units"])
        .sort("sum_units", descending=True)
    )
    g.style_df(g.rename_columns(_df), bar=True)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    PS5は､PS4,PS3に比べて販売ペースが遅い状態で安定しています｡
    この状態からPS4,PS3に追いつくペースに上がるのは困難でしょう｡
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 年単位の状況
    """)
    return


@app.cell
def _(report_date: datetime):
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
def _(year_df):
    year_pivot_df = year_df.pivot(index="year", on="hw", values="yearly_units")
    year_pivot_df = year_pivot_df.with_columns(
        合計=pl.sum_horizontal(pl.exclude("year", "合計"))
    )
    g.style_df(year_pivot_df)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### 年単位のメーカーシェア
    """)
    return


@app.cell
def _():
    _chart = g.chart_hbar_yearly_share_by_maker(2015, 2026)
    share_chart = mo.ui.altair_chart(_chart)
    mo.vstack(items=[share_chart], justify="start")
    _df: pl.DataFrame = share_chart.dataframe
    _df.sum_horizontal
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Switch2の年末商戦級の駆け込み需要の影響で任天堂のシェアが上昇｡ 88.9%に達し､次週89%を狙います｡
    """)
    return


if __name__ == "__main__":
    app.run()
