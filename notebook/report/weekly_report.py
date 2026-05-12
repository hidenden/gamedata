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
    return df_all, report_date, show_title


@app.cell
def _(report_date, show_title):
    show_title(report_date)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    * ハードウェアの販売データはファミ通の調査結果を基にしています。
    * 一部のデータは処理上の都合により、週次値に調整しています｡
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
    Switch2が7週間ぶりに下げ止まって増加しました｡先週から1500台増加の4万5千台です｡
    5万台前後で安定するのであれば特に問題ないでしょう｡
    ぽこあポケモンはパッケージ累計92万本､100万本が射程距離内です｡

    Switchは4千台下げましたが､それでも高水準の2万7千台｡
    Switch Liteの好調が続きます｡
    トモダチコレクションは累計74万本､こちらも100万本を目指せるでしょう｡

    PS5はさらに2千台増加し1万2千台です｡
    値上げ以降 PS5 Proが以下のように増え続けています｡
    よくわからない動きです｡

    1219台 → 3066台 → 4330台
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
    下げ止まったSwitch2｡ スプラトゥーン・レイダースまでは､昨年の9月頃と似た推移をたどると思われます｡
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
        begin=_begin, end=_end, ymax=80000, event_mask=g.EVENT_MASK_MIDDLE
    )
    mo.hstack(items=[mo.ui.altair_chart(_chart)], justify="start", wrap=True)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Switch2が5万前後､Switchが3万前後､PS5が1万前後で安定する状況がしばらく続きそうです｡
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
    現時点で2026年のPS5は健闘しています｡値上げがありながらも､前年の同時期よりも若干高い販売台数で推移しています｡
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
    (Switch2は昨年のデータがありませんので､Switchの2018, 2019年の推移と比較します｡)

    Switch2の販売ペースは2019年のSwitchと同じ水準で踏みとどまりました｡
    このまま5万弱で推移したとしても､
    Switchよりも若干高い販売台数で推移することになります｡
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
    4月としては40万台に届きませんでしたが､昨年4月と比較すればSwitch2分がまるまる加わった値となっており､
    悪くない状況です｡
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
    2026年4月のSwitch2の販売台数は昨年9月を超えて､20万台に到達出来ました｡
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
def _(is_publish, ns_df_pivot):
    if is_publish:
        mo.stop(True)
    g.style_df(ns_df_pivot)
    return


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
    4月のSwitchはトモコレ効果で昨年比84.7%という高い水準でした｡
    次世代機が出ていると思えない好調ぶりです｡
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
    2026年4月のPS5は昨年比で118%と好調でした｡前年同月を上回るのは2025年10月以来です｡
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


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Switch2: 47週目の状況
    """)
    return


@app.cell
def _():
    _chart = g.chart_line_cumulative_delta(
        hw=["NS2", "NSW", "PS5", "3DS", "DS", "GBA", "PS2", "Wii"],
        end=60,
        event_mask=g.EVENT_MASK_MIDDLE,
        mode="week",
    )
    cd_chart = mo.ui.altair_chart(_chart)
    cd_chart
    return (cd_chart,)


@app.cell
def _(cd_chart):
    _df = (
        cd_chart.dataframe.filter(pl.col("delta_week") == 46)
        .select(["hw", "sum_units"])
        .sort("sum_units", descending=True)
    )
    g.style_df(g.rename_columns(_df), bar=True)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    今のペースだと7月後半にはDS,3DSに抜かれそうですが､
    スプラトゥーン・レイダースの発売日が7月23日に決まったため､
    そこで加速してSwitch2の歴代最速は続きそうです｡
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### PS5: 285週目の状況
    """)
    return


@app.cell
def _():
    _chart = g.chart_line_cumulative_delta(
        hw=["PS5", "PS4"], end=300, event_mask=g.EVENT_MASK_LONG, mode="week"
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
    PS4とPS5の同時期累計差は71万台前後で安定しています｡差は開いていませんが､縮まってもいません｡
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
    Switch2の台数減少の影響で任天堂のシェアが87.8%から87.6%に若干減少しました｡
    """)
    return


if __name__ == "__main__":
    app.run()
