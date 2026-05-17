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
    report_date = config["date"]

    def show_title(d: datetime):
        last_updated_str = d.strftime("%Y-%m-%d")
        mode: str = "**DRAFT**" if not is_publish else ""
        return mo.md(f"# 国内ゲームハード週販レポート ({last_updated_str}) {mode}")

    df_all = g.load_hard_sales()
    [ns2_info, ps5_info, nsw_info] = g.hard_sales_summary(
        df_all, hw=["NS2", "PS5", "NSW"]
    )
    return df_all, ns2_info, ps5_info, report_date, show_title


@app.cell
def _(report_date, show_title):
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
def _(df_all, report_date):
    _table = g.units_by_date_hw_table(
        df_all, begin=g.weeks_before(report_date, 3), end=report_date
    )
    mo.hstack(items=[_table], justify="start", wrap=True)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    (今週は2週合算集計なので処理の都合上2分割して5/3, 5/10に割り振ってます)

    5月8日の夕刻､Nintendo Switch2, Switchの値上げが発表されました｡
    [(当社商品およびサービスの価格変更に関するお知らせ)](https://www.nintendo.co.jp/corporate/release/2026/260508.html)

    Switch2日本語版は5月25日以降､1万円値上げされます｡
    このニュースが流れた直後から安いうちにSwitch2を買おうとする人が殺到し､
    駆け込み需要が発生しました｡

    2週分割の換算値でも4月までの平均販売台数の約2倍を超えます｡
    実際には5月10日週に集中したと思われるので､5月10日に15万台/週程度の販売があったと推測されます｡
    Switch2週販ランキングTOP10に入る可能性もあったので､2週合算集計なのが惜しまれます｡

    駆け込み需要はSwitchの方には明確に現れていません｡
    今更駆け込みでSwitchを買うような人は少数でしょう｡
    価格上昇率の大きなLiteの確保はアリだと思いますが､こちらは店頭在庫が厳しいようです｡
    次回集計でSwitchの落ち込み､Switch2への集中が明確に現れると思われます｡

    駆け込み需要の集計機会はあと2回あります｡
    任天堂が潤沢に追加出荷を行うのか?
    通常通りの出荷で､どこかで完全に品切れになってしまうのか?
    このあたりも注目されます｡

    PS5は悪くないペースだと思います｡
    値上げ以降続いていた PS5 Proの増加が落ち着きました｡

    1219台 → 3066台 → 4330台 → 5248台(合算なので2600台/週程度)
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 週販推移
    """)
    return


@app.cell
def _(report_date):
    _begin = g.report_begin(report_date)
    _end = report_date
    _chart = g.chart_line_sales(begin=_begin, end=_end, event_mask=g.EVENT_MASK_MIDDLE)
    _weekly_chart = mo.ui.altair_chart(_chart)
    mo.hstack(items=[_weekly_chart], justify="start", wrap=True)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Switch2が下げ止まったと思ったら､駆け込みで需要で急上昇です｡
    需要的には､あと2週間この状態のはずですが､
    実際にどの程度の販売数になるかは､任天堂の出荷数によって決まります｡
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### 週販推移(拡大)
    """)
    return


@app.cell
def _(report_date):
    _begin = date(2026, 1, 1)
    _end = report_date
    _chart = g.chart_line_sales(
        begin=_begin, end=_end, ymax=120000, event_mask=g.EVENT_MASK_MIDDLE
    )
    mo.hstack(items=[mo.ui.altair_chart(_chart)], justify="start", wrap=True)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    注目点は､値上げ後のSwitchとPS5の逆転が起きるかどうか｡
    PS5が増える理由はありませんが､Switchが落ち込むことでPS5が上に行く可能性は高いと考えます｡
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## FY27(2027年3月期) 日本のSwitch2販売予想

    今年度のSwitch2販売計画が[2026年3月期 決算説明資料](https://www.nintendo.co.jp/ir/pdf/2026/260508_4.pdf)で発表されました｡
    (台数は全てセルインと思われます)

    - FY27予想 1650万台(World wide:セルイン)
    - FY26実績 1986万台(World wide:セルイン)
    - 2027年3月末(22か月間)でNintendo Switchの22か月累計を超える見込み

    同資料で公開された､FY26の地域別のSwitch2販売台数を元に､地域別の比率を求めると以下の値になります｡

     日本 | 米大陸 | 欧州 | その他 |
    |----|--------|------|-------|
    | 28.5% | 33.9% | 22.2% | 15.4% |

    この比率が続くなら､日本の今年度のSwitch2販売台数は470万になります｡

    以下に､各会計年度の四半期ごとのNintendo Switchの日本での販売実績を示します｡
    (年をFiscal Yearで示してます｡日本人の年度感覚から表記が1年ズレてますのでご注意ください)
    """)
    return


@app.cell
def _(df_all):

    _df1 = g.quarterly_sales_long(
        df_all, hw=["NSW"], begin=datetime(2017, 4, 1), end=datetime(2025, 3, 31)
    )
    _df2 = _df1.pivot(index=["fiscal_year"], on="fq_num", values="quarterly_units")
    # 各行の最後にカラムfiscal_year以外のカラムの合計値を追加
    _df3 = _df2.with_columns(pl.sum_horizontal(pl.exclude("fiscal_year")).alias("会計年度合計"))
    g.style_df(_df3)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    年間470万台を超えているのはFY2020(Lite､剣盾)､FY2021(コロナ､あつ森)､
    FY2022(OLEDモデル)の3年度のみです｡
    470万台というのはなかなかに高い値です｡

    また､ワールドワイドでは発売後から22ヶ月後(96週)の累計販売台数がNintendo Switchを超える見込みとのこと
    なので､日本での22ヶ月後(96週)後の様子を見てみます｡
    """)
    return


@app.cell
def _():
    _chart = g.chart_line_cumulative_delta(
        hw=["NS2", "NSW", "3DS", "DS"],
        end=100,
        event_mask=g.EVENT_MASK_MIDDLE,
        mode="week",
        with_point=False,
        index_mode=True,
    )
    _chart = g.chart_rule_xy(
        base_chart=_chart,
        x=96,
        y=6889546,
        stroke=[5, 2],
        size=2,
        color="#00000060",
    )
    _chart = g.chart_line_guide(
        base_chart=_chart,
        x=44, y=5011059, 
        x2=96, y2=(5011059 + 4700000), 
        stroke=[2, 3], size=2, color="#800000"
    )

    ns2_27_chart = mo.ui.altair_chart(_chart)
    mo.vstack(items=[ns2_27_chart], justify="start")
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    セルインとセルスルーの合算なので概算になりますが､
    96週(2027年3月末)の時点でNintendo Switchを280万台程度上回る見込みです｡
    普及速度歴代一位の座はDSに譲るものの､
    Nintendo Switchとの差は昨年度末の時点で約140万台だったものが､
    今後の1年でさらに倍の差に拡大する見通しです｡

    これ *全然弱気の予想には見えません*

    なお､ゲーム機の初期の累計値は「何回年末商戦を迎えたか」で大きく数字がブレます｡
    今回はSwitchの2回目の年末商戦を含めての比較なので､フェアな比較と言えます｡
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 過去年の週販比較
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### PlayStation 5:2023年から2026年の3月1日以降
    """)
    return


@app.cell
def _():
    _offset_chart = g.chart_line_weekly_by_hw_date(
        hw_periods=[
            {"hw": "PS5", "begin": datetime(2023, 3, 1)},
            {"hw": "PS5", "begin": datetime(2024, 3, 1)},
            {"hw": "PS5", "begin": datetime(2025, 3, 1)},
            {"hw": "PS5", "begin": datetime(2026, 3, 1)},
        ],
        end=20,
    )

    _ps5_offset_chart = mo.ui.altair_chart(_offset_chart)
    _ps5_offset_chart
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    現時点で2026年のPS5は健闘しています｡前年の同時期よりも若干高い販売台数で推移しています｡
    PS5DE日本語版の価格抑制施策が功を奏しているのかもしれません｡
    ただSwitch2の国内値上げで値上げの余地が発生したので､
    今後､利益確保の値上げの動きが出てくる可能性はあります｡
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Nintendo Switch2: 2026年と, Switch 2018,2019年 3月1日以降
    """)
    return


@app.cell
def _():
    _offset_chart = g.chart_line_weekly_by_hw_date(
        hw_periods=[
            {"hw": "NSW", "begin": datetime(2018, 3, 1)},
            {"hw": "NSW", "begin": datetime(2019, 3, 1)},
            {"hw": "NS2", "begin": datetime(2026, 3, 1)},
        ],
        end=20,
    )

    _ns2_offset_chart = mo.ui.altair_chart(_offset_chart)
    _ns2_offset_chart
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    もう過去のSwitchの推移と比べる意味は無いですね｡
    FY27の目標値との比較の方が有意義だと思います｡
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 月間販売推移
    """)
    return


@app.cell
def _(report_date):
    _bar = g.chart_bar_sales(begin=datetime(2025, 3, 1), end=report_date, stacked=True)
    bar_chart = mo.ui.altair_chart(_bar)
    bar_chart
    return (bar_chart,)


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
    Switch2の駆け込み需要で5月としては記録的な販売数になる可能性があります｡
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Nintendo Switch2: 月間販売台数
    """)
    return


@app.cell
def _(report_date):
    mo.ui.altair_chart(
        g.chart_bar_sales(
            hw=["NS2"], begin=datetime(2025, 3, 1), end=report_date, stacked=True
        )
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    2026年5月のSwitch2は2週間で4月の販売数を超えました｡
    出荷が可能なら2025年10月を超えて､40万台に到達する可能性があります｡
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Nintendo Switch:月間販売台数
    """)
    return


@app.cell
def _(report_date):
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
def _(ns_df_pivot, report_date):
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
    Switch2は値上げ前の駆け込み需要が発生していますが､Switchでは発生していません｡
    在庫切れが発生しているようで､これ以上の販売数の増加は難しい状況です｡
    任天堂もSwitch2の出荷を優先するため､Swtichの今後がどうなるかは不透明です｡

    5月25日以降､有機ELモデルは47980円､Liteは29980円に値上げされます｡
    値上げ率はSwitch2よりも大きく､「高くなった感」をひしひしと感じます｡
    値上げはSwitch2以上に､Switchの販売数に影響を与える可能性が高いと思われます｡
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### PlayStation 5: 月間販売台数
    """)
    return


@app.cell
def _(report_date):
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
def _(ps5_df_pivot, report_date):
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
    5月25日以降はPS5DE日本語版が
    日本で最も安い家庭用ゲーム機になります｡
    低価格を販売数につながるかどうか､注目されます｡
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 累計販売推移
    """)
    return


@app.cell
def _(report_date):
    _chart = g.chart_line_cumulative(
        hw=["NSW", "NS2", "PS5", "XSX"],
        begin=datetime(2017, 3, 1),
        end=report_date,
        event_mask=g.EVENT_MASK_LONG,
    )
    chart_cumulative = mo.ui.altair_chart(_chart)
    chart_cumulative
    return (chart_cumulative,)


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
        hw=["NS2", "NSW", "PS5", "3DS", "DS", "GBA", "PS2", "Wii"],
        end=ns2_info["sales_weeks"] + 20,
        event_mask=g.EVENT_MASK_MIDDLE,
        mode="week",
        with_point=False,
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
        y2=6400000,
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
    この先､値上げ前の駆け込み需要と､値上げ直後の落ち込み､
    一定の時間をかけての回復の流れになります｡
    駆け込み需要のボリュームが相当に大きく､その分値上げ直後の落ち込みも大きくなる可能性があります｡
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
        hw=["PS5", "PS4"],
        end=ps5_info["sales_weeks"] + 60,
        event_mask=g.EVENT_MASK_LONG,
        mode="week",
    )

    _latest_ps5 = pl.DataFrame(
        {
            "index_week": [ps5_info["sales_weeks"]],
            "total_units": [ps5_info["total_units"]],
        }
    )

    _v_rule = (
        alt.Chart(_latest_ps5)
        .mark_rule(color="#00000060", strokeDash=[5, 2], size=2)
        .encode(x="index_week:Q", tooltip=alt.value(None))
    )
    _h_rule = (
        alt.Chart(_latest_ps5)
        .mark_rule(color="#00000060", strokeDash=[5, 2], size=2)
        .encode(y="total_units:Q", tooltip=alt.value(None))
    )

    _v_rule = (
        alt.Chart(_latest_ps5)
        .mark_rule(color="#00000060", strokeDash=[5, 2], size=2)
        .encode(x="index_week:Q", tooltip=alt.value(None))
    )
    _h_rule = (
        alt.Chart(_latest_ps5)
        .mark_rule(color="#00000060", strokeDash=[5, 2], size=2)
        .encode(y="total_units:Q", tooltip=alt.value(None))
    )

    _future_ps5 = pl.DataFrame(
        {
            "index_week": [ps5_info["sales_weeks"], ps5_info["sales_weeks"] + 60],
            "total_units": [ps5_info["total_units"], 8100000],
        }
    )
    _z_line = (
        alt.Chart(_future_ps5)
        .mark_line(color="#0000f0a0", strokeDash=[2, 3], size=2)
        .encode(x="index_week:Q", y="total_units:Q", tooltip=alt.value(None))
    )

    ps_cd_chart = mo.ui.altair_chart(_chart + _v_rule + _h_rule + _z_line)
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
    現状のペースなら来年の2月頃には累計800万台に到達する見込みです｡
    (ただ､その頃にはSwitch2に累計で逆転されているでしょう)
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 年単位の状況
    """)
    return


@app.cell
def _(report_date):
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
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    値上げ前のSwitch2駆け込み需要で任天堂のシェアは上昇し､88%を超えました｡
    """)
    return


if __name__ == "__main__":
    app.run()
