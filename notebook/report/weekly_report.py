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

__generated_with = "0.25.2"
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
def load_data():
    hard_sales_all_df: pl.DataFrame = g.load_hard_sales(True)
    annotation_all_df: pl.DataFrame = g.load_hard_annotation(no_cache=True)
    return (hard_sales_all_df,)


@app.cell
def report_setup(hard_sales_all_df: pl.DataFrame, is_publish):
    # レポート日付
    from report_config import get_config

    config = get_config()
    report_date: datetime = config["date"]

    def show_title(d: datetime):
        last_updated_str = d.strftime("%Y-%m-%d")
        mode: str = "**DRAFT**" if not is_publish else ""
        return mo.md(f"# 国内ゲームハード週販レポート ({last_updated_str}) {mode}")

    [ns2_info, ps5_info, nsw_info] = g.hard_sales_summary(
        hard_sales_all_df, hw=["NS2", "PS5", "NSW"]
    )
    return ns2_info, report_date, show_title


@app.cell
def _(hard_sales_all_df: pl.DataFrame):
    _df_latest = g.extract_latest(hard_sales_all_df, 1)
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
def units_by_date_hw_table(
    hard_sales_all_df: pl.DataFrame,
    report_date: datetime,
):
    _table = g.units_by_date_hw_table(
        hard_sales_all_df, begin=g.weeks_before(report_date, 3), end=report_date
    )
    mo.hstack(items=[_table], justify="start", wrap=True)
    return


@app.cell(hide_code=True)
def md_top():
    mo.md(r"""
    10月18日は4機種合計で37,607台となり、前週から7.0%減少しました。Switch2は21,854台で2.5%減、PS5は10,667台で10.4%減、Switchは4,857台で16.3%減、Xbox Series X|Sは229台で21.0%減と、2週続けて全機種が前週を下回っています。

    特にSwitchは、これまで最低だった6月14日の4,933台を76台下回り、本データの全期間で過去最低を更新しました。前週に累計3,700万台へ到達した一方、足元の新規販売は縮小が続いています。

    [ファミ通のソフト週販](https://www.famitsu.com/article/202610/91765)では「テイルズ オブ エターニア リマスター」がSwitch2版17,911本、PS5版10,390本で新登場し、Switch向け「キャッスルヴァニア ベルモンドカース」も15,630本を販売しました。Switch2、PS5の「Call of Duty:Modern Warfare4」の発売も重なりましたが、複数の新作が市場全体のハード販売を前週以上へ押し上げるまでには至りませんでした。

    PS5では、10月13日に発表された11月19日発売の[「PS5DE日本語版ミッドナイトブラック」](https://blog.ja.playstation.com/2026/10/13/20261013-ps5-dej-black-announcement-s/)を待つ購入の先送りが下押し要因になると見ています。今週はその発表を含む集計期間に入り、減少に購入待ちが関係した可能性があります。発売時には需要を集めると考えていますが、そこまでの週販には慎重な見方が必要です。

    次回10月25日集計にはSwitch2の「Nintendo Switch Sports Resort」が入ります。次々回11月1日集計は10月29日発売の「ゼルダの伝説40周年記念モデル」本体モデルが集計に含まれるので､そこで販売台数を大きく伸ばすことが期待されます。
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

    weekly_chart = mo.ui.altair_chart(_chart)
    mo.vstack(items=[weekly_chart], justify="start")
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
    _begin = date(2026, 2, 15)
    _end = report_date
    _chart = g.chart_line_sales(
        hw=["NSW", "PS5", "XSX", "NS2"],
        begin=_begin,
        end=_end,
        annotation_level=30,
        ymax=55000,
        padding_end=1,
        value_label=True,
    )
    weekly_big_chart = mo.ui.altair_chart(_chart)
    mo.vstack(items=[weekly_big_chart], justify="start")
    return


@app.cell(hide_code=True)
def md_weekly_chart():
    mo.md(r"""
    Switch2は9月20日の34,341台から4週連続で減少しました。ただし今週の減少幅は566台で、前週の3,780台より小さくなっています。直近4週平均は28,790台から25,668台へ低下し、13週平均の29,151台も下回りました。下げの勢いは弱まったものの、9月後半の上昇を取り戻す動きにはまだ至っていません。

    PS5は2週連続の減少ですが、3週続けて1万台を保ちました。直近4週平均は10,564台から11,269台へ上昇しています。低かった9月の週が対象から外れた影響で、今週の週販の減少と平均の上昇が同時に起きています。Switch2との差の縮小は止まり、週間順位はSwitch2、PS5、Switch、Xbox Series X|Sの順で変わりません。PS5の2位は5週連続です。

    Switchは直近4週平均が6,168台、13週平均が7,300台で、短い期間ほど弱い販売となっています。Xbox Series X|Sも2週続けて減少しました。次週はSwitch2の下げが止まるか、PS5が1万台を維持できるかが、上位2機種の線の動きを見る際の焦点です。
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
        y2=661000,
        stroke=[3, 2],
        size=2,
        color="#ff000080",
    )
    ps5_yearly_cumulative_chart = mo.ui.altair_chart(_chart)
    mo.vstack(items=[ps5_yearly_cumulative_chart], justify="start")
    return


@app.cell
def ps5_heatmap_chart():
    _chart = g.chart_heatmap(
        hw="PS5",
        mode="week",
        scale_scheme="plasma",
        scale_type="sqrt",
    )
    ps5_heatmap_chart = mo.ui.altair_chart(_chart)
    mo.vstack(items=[ps5_heatmap_chart], justify="start")
    return


@app.cell(hide_code=True)
def md_ps5_yearly():
    mo.md(r"""
    PS5の2026年累計は10月18日時点で473,979台です。前年同時期の692,158台を31.5%、2024年同時期の1,128,955台を58.0%下回っています。PS3の2014年同時期393,555台に対しては20.4%多い一方、PS4の2018年同時期1,276,615台には62.9%届かず、過去のPlayStationと比べても年間販売は低い水準です。

    52週平均の12,712台を年換算した年間販売の目安は約661,000台で、2025年通年の879,204台を24.8%下回ります。年初来の前年割れ幅は前週の31.9%からわずかに改善していますが、前年との差はなお218,179台あります。

    発売からの累計は7,772,189台で、800万台まで残り227,811台です。52週平均を維持した場合は約18週後の2027年2月に到達する計算です。年内に超えるには残り10週で週平均約22,780台が必要となり、足元の1万台前後からの販売拡大が条件になります。
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
        y2=906000,
        stroke=[3, 2],
        size=2,
        color="#ff000080",
    )
    switch_yearly_cumulative_chart = mo.ui.altair_chart(_chart)
    mo.vstack(items=[switch_yearly_cumulative_chart], justify="start")
    return


@app.cell
def switch_heatmap_chart():
    _chart = g.chart_heatmap(
        hw="NSW",
        mode="week",
        scale_scheme="plasma",
        scale_type="sqrt",
    )
    switch_heatmap_chart = mo.ui.altair_chart(_chart)
    mo.vstack(items=[switch_heatmap_chart], justify="start")
    return


@app.cell(hide_code=True)
def md_switch_yearly():
    mo.md(r"""
    Switchの2026年累計は10月18日時点で589,066台です。前年同時期の1,203,638台から51.1%減、2024年同時期の2,333,768台から74.8%減となり、年初来の前年割れ幅は前週より広がりました。年間の目安は、週17,419台という52週平均を基準に約906,000台で、2025年通年の1,520,384台を約4割下回ります。

    発売からの累計は37,005,227台となりました。先週の大台到達後も記録は伸びていますが、52週平均に対して直近4週平均は6,168台と低く、年末の上積みが弱ければ年間の目安からも下振れします。3,800万台まで残り994,773台を売るには、この足元の平均でも3年以上の販売が必要です。本体の供給が長く続くことを前提とするため、次の大台は長期販売が続いた場合の上振れとして捉えたいところです。
    """)
    return


@app.cell(hide_code=True)
def switch2_yearly_cumulative_title():
    mo.md(r"""
    ### Switch2(2025年, 2026年)
    """)
    return


@app.cell
def switch2_yearly_cumulative_chart(switch2_latest):
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
        y2=4028000,
        stroke=[3, 2],
        size=2,
        color="#ffa00080",
    )
    switch2_yearly_cumulative_chart = mo.ui.altair_chart(_chart)
    mo.vstack(items=[switch2_yearly_cumulative_chart], justify="start")
    return


@app.cell
def switch2_heatmap_chart():
    _chart = g.chart_heatmap(
        hw="NS2",
        mode="week",
        scale_scheme="plasma",
        scale_type="log",
    )
    _chart = _chart.properties(height=200)
    switch2_heatmap_chart = mo.ui.altair_chart(_chart)
    mo.vstack(items=[switch2_heatmap_chart], justify="start")
    return


@app.cell(hide_code=True)
def md_switch2_yearly():
    mo.md(r"""
    2026年のSwitch2販売は10月18日までに2,646,760台となりました。前年同時期の2,402,587台を10.2%上回っていますが、伸び率は前週の19.3%から大きく縮まりました。前年は「Pokemon LEGENDS ZA」の発売週に201,684台を販売しており、今週はその高い実績との比較に入ったことが影響しています。前年超過分は424,003台から244,173台へ減少しました。

    52週平均は77,466台で、年間に換算すると約4,028,000台です。2025年通年の3,784,067台より6.5%多い水準ですが、前年の年末商戦や今年春の高い販売を含む平均であり、直近4週平均の25,668台とは開きがあります。

    累計700万台までは残り569,173台となりました。52週平均なら約8週後の12月13日集計、発売80週で到達する計算で、Switchの97週、PS5の252週より早い到達です。一方、直近4週平均で延ばすと2027年3月末までかかります。年内到達には残り10週で週平均約56,920台が必要で、11月以降の明確な回復が条件となります。
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
def switch2_monthly_sales_chart(report_date: datetime):
    _begin = g.years_ago(report_date)
    _end = report_date
    switch2_monthly_bar = mo.ui.altair_chart(
        g.chart_bar_hwsales_by_year(begin=_begin, end=_end, hw="NS2")
    )
    ns2_df = switch2_monthly_bar.dataframe
    ns2_df_pivot = ns2_df.pivot(index="month", on="year", values="monthly_units")
    mo.vstack(items=[switch2_monthly_bar], justify="start")
    return (ns2_df_pivot,)


@app.cell
def switch2_monthly_sales_table(ns2_df_pivot, report_date: datetime):
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
    Switch2の10月販売は3週累計で70,474台です。前年同月の最初の3週292,965台から75.9%減となりました。残りは10月25日集計の1週で、今週のペースを延ばすと月間92,328台、直近4週平均なら96,142台です。9月の119,161台を19.3～22.5%、前年10月の358,399台を73.2～74.2%下回る計算となります。

    11月12日の「選べるソフトセット発売」を待つ動きは、引き続き通常の本体購入を抑えると見ています。ソフト同梱で最大4,980円お得な構成のため、発売前の11月8日集計までは先送りが続くでしょう。ゼルダ記念モデルも発売が近づくほど意識されるため、10月の最終週に週3万台へ戻るのは難しいと考えています。

    9月と同数に届くには最終週だけで48,687台が必要です。記念モデルの発売週は11月1日集計に入るので、発売時の上積みは10月分に含まれません。今月は新作の牽引だけでこの差を埋められるかという状況ですが、購入待ちを踏まえると急増は見込みにくいでしょう。
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
    switch_monthly_bar = mo.ui.altair_chart(
        g.chart_bar_hwsales_by_year(begin=_begin, end=_end, hw="NSW", ymax=480000)
    )
    ns_df = switch_monthly_bar.dataframe
    ns_df_pivot = ns_df.pivot(index="month", on="year", values="monthly_units")
    mo.vstack(items=[switch_monthly_bar], justify="start")
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
    Switchの10月販売は3週累計で18,367台です。前年同月の最初の3週70,971台を74.1%下回り、月初からの低調な推移が続いています。残り1週を今週の販売水準で延ばすと月間23,224台、直近4週平均なら24,535台となります。

    この二つのペースでは9月の31,161台から21.3～25.5%減、前年10月の96,080台から74.5～75.8%減です。9月並みへ戻すために必要な最終週の12,794台は、今週の約2.6倍という高い水準です。
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
    ps5_monthly_bar = mo.ui.altair_chart(
        g.chart_bar_hwsales_by_year(begin=_begin, end=_end, hw="PS5", ymax=480000)
    )
    ps5_df = ps5_monthly_bar.dataframe
    ps5_df_pivot = ps5_df.pivot(index="month", on="year", values="monthly_units")
    mo.vstack(items=[ps5_monthly_bar], justify="start")
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
    PS5の10月販売は3週累計で35,346台となり、9月の月間32,831台を既に超えました。一方、前年同月の最初の3週54,229台からは34.8%減で、前月からの回復と前年割れが並行しています。

    最終週を今週と同じペースで延ばすと月間46,013台、直近4週平均なら46,615台です。9月を40.2～42.0%上回る一方、前年10月の64,732台には28.0～28.9%届きません。前年並みに届くには最終週に29,386台が必要で、月末まで前年割れが続く見通しです。
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Xbox Series X|S: 月間販売台数
    """)
    return


@app.cell
def xsx_monthly_sales_chart(report_date: datetime):
    _begin = g.years_ago(report_date)
    _end = report_date
    xsx_monthly_bar = mo.ui.altair_chart(
        g.chart_bar_hwsales_by_year(begin=_begin, end=_end, hw="XSX")
    )
    xsx_df = xsx_monthly_bar.dataframe
    xsx_df_pivot = xsx_df.pivot(index="month", on="year", values="monthly_units")
    mo.vstack(items=[xsx_monthly_bar], justify="start")
    return (xsx_df_pivot,)


@app.cell
def xsx_monthly_sales_table(report_date: datetime, xsx_df_pivot):
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
    Xbox Series X|Sの10月販売は3週累計で1,131台です。前年同月の最初の3週1,262台から10.4%減ですが、9月の月間918台は23.2%上回っています。初週の612台だけで現在の月間累計の54.1%を占めており、月初の販売が全体を押し上げています。

    残り1週を今週の229台で延ばすと月間1,360台、直近4週平均なら1,504台です。9月からは約5～6割の増加を見込む一方、前年10月の2,253台に対しては33.2～39.6%少ない水準です。
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
    cumulative_chart = mo.ui.altair_chart(_chart)
    mo.vstack(items=[cumulative_chart], justify="start")
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### 累計販売推移(Switch2, PS5拡大)
    """)
    return


@app.cell
def switch2_ps5_cumulative_chart(
    ps5_latest,
    report_date: datetime,
    switch2_latest,
):
    _chart = g.chart_line_cumulative(
        hw=["NS2", "PS5"],
        begin=datetime(2025, 5, 20),
        end=datetime(2026, 12, 31),
        annotation_level=19,
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
    10月18日時点の累計差は1,341,362台で、PS5が7,772,189台、Switch2が6,430,827台です。今週の差の縮小は11,187台となり、前週の10,509台からわずかに増えました。

    52週平均の差は週64,754台で、このペースなら約21週後の2027年3月に逆転する計算です。直近4週平均の差は週14,399台となり、こちらでは約94週後の2028年8月までかかります。今週だけの縮小幅は増えていても、短期の平均差は前週の18,226台から小さくなったため、足元を基準とした逆転時期はさらに後ろへ動きました。

    この二つの時期は、それぞれの平均差を将来も固定した場合の試算です。
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
        annotation_level=18,
        mode="week",
        with_point=False,
        multi_line=True,
    )
    _chart = g.chart_line_guide(
        base_chart=_chart,
        x=ns2_info["sales_weeks"],
        y=ns2_info["total_units"],
        x2=85,
        y2=7000000,
        stroke=[2, 3],
        size=2,
        color="#800000",
    )
    cd_chart = mo.ui.altair_chart(_chart)
    mo.vstack(items=[cd_chart], justify="start")
    return


@app.cell
def cumulative_top_chart(hard_sales_all_df: pl.DataFrame, ns2_info):
    cumulative_tops_df = (
        hard_sales_all_df.filter(pl.col("index_week") == ns2_info["sales_weeks"])
        .filter(pl.col("hw").is_in(["NS2", "NSW", "3DS", "GBA", "DS"]))
        .select("hw", "index_week", "report_date", "sum_units")
        .sort("sum_units", descending=True)
    )
    g.style_df(g.rename_columns(cumulative_tops_df))
    return


@app.cell(hide_code=True)
def md_cumulative_top():
    mo.md(r"""
    発売72週時点のSwitch2累計は6,430,827台で、歴代3位を維持しています。2位の3DSは6,468,783台となり、差は前週の7,880台から37,956台へ拡大しました。首位DSはこの72週で700万台を突破し、累計7,142,963台、Switch2との差は712,136台となっています。

    次の73週時点の3DS累計は6,515,416台です。Switch2が再び上回るには次週に84,590台以上が必要で、今週の約3.9倍に当たります。新作による上積みがあっても、短期で2位を取り戻すには大きな販売の変化が必要です。

    一方、同じ72週のGBAは5,731,090台、Switchは4,665,680台です。Switch2はそれぞれ約70万台、約177万台上回っており、DSや3DSには後れを取る一方、前世代機より速い普及は維持しています。
    """)
    return


@app.cell(hide_code=True)
def md_yearly_sales_title():
    mo.md(r"""
    ## 年単位の状況
    """)
    return


@app.cell(hide_code=True)
def md_quarterly_title():
    mo.md(r"""
    ### 四半期ごとの状況
    """)
    return


@app.cell
def quarterly_sales_chart():
    _c1 = g.chart_bar_yearly_by_mode(
        begin=date(2016, 1, 1),
    )
    quarter_chart = mo.ui.altair_chart(_c1)
    mo.vstack([quarter_chart])
    return


@app.cell(hide_code=True)
def md_quarterly():
    mo.md(r"""
    2026年第4四半期は3週累計で125,318台です。前年同期の最初の3週419,486台を70.1%、2024年の218,740台を42.7%下回っています。今期の週平均は約41,773台で、直前の第3四半期が617,823台と2001年以降の完了した四半期で最低だった状況から、まだ回復は見えていません。

    2024年第4四半期の1,345,463台に並ぶには、残る10週で1,220,145台、週平均約122,015台が必要です。今期最初の3週平均の約2.9倍に当たります。前年の第4四半期はさらに多い2,308,689台であり、年末需要が強まるだけでなく、主要機種の発売後に相当の販売拡大が必要な出足となっています。
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
    yearly_bar = mo.ui.altair_chart(
        g.chart_bar_sales(
            mode="year",
            stacked=True,
            begin=g.years_ago(report_date, 10),
            end=report_date,
        )
    )
    year_df = yearly_bar.dataframe
    mo.vstack(items=[yearly_bar], justify="start")
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
    2026年の主要4機種の販売は10月18日時点で合計3,727,844台となり、前年同時期の4,325,832台を13.8%下回っています。前年との差は597,988台へ広がった一方、2024年同時期の3,555,196台に対しては4.9%多い水準です。表の全機種合計はPS4の275台を含む3,728,119台となっています。

    前年比ではSwitch2が244,173台増えましたが、Switchは614,572台、PS5は218,179台、Xbox Series X|Sは9,410台減少しました。Switch2の増加で補えているのはSwitchの減少の約4割にとどまり、世代交代が市場全体の増加につながっていません。2024年通年の全機種販売4,695,363台までの差も967,244台あり、残り10週の年末商戦でこの差を埋められるかが年間規模を判断する目安になります。
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
    2026年のメーカー別シェアは10月18日時点で任天堂が86.8%、ソニーが12.7%、マイクロソフトが0.5%です。前週の87.0%、12.6%、0.5%に対し、任天堂がわずかに低下し、ソニーが上昇しました。任天堂の比率は2025年通年の85.3%、2024年の66.2%をなお上回っています。

    PS5の今週の週間シェアは28.4%で、前週の29.5%から低下しました。それでも年初来のソニーの比率を大きく上回るため、年間累計ではソニーの構成比を押し上げています。週間と年初来でシェアの方向が異なる点に注意が必要です。

    主要4機種の52週平均を年換算した販売台数で年間シェアを試算すると、任天堂が約87.8%、ソニーが約11.8%、マイクロソフトが約0.4%です。現在の累計比率より任天堂が約1ポイント高い試算となり、任天堂中心の構成は年末まで続くと見込まれますが、ソニーが足元の高い週間比率を維持できれば実際の年末シェアはこの目安を上回るでしょう。
    """)
    return


@app.cell
def report_metadata():
    # cell_name: 記事が含まれるマークダウンセルの名前
    # description: 各記事が含まれるマークダウンセルの内容の概要
    # calc_cells: 各記事の言及対象となる計算処理､データが含まれるセル名｡概ね記事セルの直前に配置されているセルであることが多いが､必ずしもそうでない場合もある。

    md_summaries = [
        {
            "cell_name": "md_top",
            "calc_cells": ["units_by_date_hw_table"],
            "description": """
        今週の売上概況を､主に先週と比較しながら説明する｡トピックとなりそうな変化があるか確認し､
        変化があればそれについて言及する｡トピックとなる変化の例としては100万台単位の節目､歴代最高､最低の販売台数です｡
        annotation_dfに書かれているゲーム関係のイベントが影響した可能性も考慮し､影響の有無､大小について言及する｡
        annotation_dfに含まれる次回集計､次々回集計時に該当するイベント情報を確認し､それが将来に与える影響の予想も含めて記述する｡
        """,
        },
        {
            "cell_name": "md_weekly_chart",
            "calc_cells": ["weekly_sales_trend", "weekly_sales_trend_2"],
            "description": """
        週間販売折れ線グラフの説明､先週と比較しつつ､機種同士の比較や､順位の変動､今後の見通し､考察を含めて解説｡
        久しぶり(4週間以上)の順位変動が発生した場合は､その変動について特に言及する｡
        折れ線グラフの解説なので､数値の変化や傾向を説明することが重要です｡
        md_topと内容的に重複してもよいが､表現が全く同じにならないよう工夫する｡
         """,
        },
        {
            "cell_name": "md_ps5_yearly",
            "calc_cells": ["ps5_yearly_cumulative_chart", "ps5_heatmap_chart"],
            "description": """
         PS5の今年の販売状況を昨年､一昨年と比較､年末までの見通しについて記述｡将来予想は52週平均を用いる｡
         100万台単位を節目とし､節目の到達時期が3ヶ月以内の場合は特に言及する｡
         その際には､過去のPS3, PS4の状況との比較を行い､考察を加える｡
         """,
        },
        {
            "cell_name": "md_switch_yearly",
            "calc_cells": ["switch_yearly_cumulative_chart", "switch_heatmap_chart"],
            "description": """
         Switchの今年の販売状況を昨年､一昨年と比較､年末までの見通しについて記述
         将来予想は52週平均を用いる｡
         100万台単位を節目とし､節目の到達時期が3ヶ月以内の場合は特に言及する｡
         """,
        },
        {
            "cell_name": "md_switch2_yearly",
            "calc_cells": ["switch2_yearly_cumulative_chart", "switch2_heatmap_chart"],
            "description": """
         Switch2の今年の販売状況を昨年と比較､年末までの見通しについて記述
         将来予想は52週平均を用いる｡
         100万台単位を節目とし､節目の到達時期が3ヶ月以内の場合は特に言及する｡
         その際には､前世代機のSwitchの状況､ ライバル機のPS5の状況との比較を行い､考察を加える｡
         """,
        },
        {
            "cell_name": "md_switch2_monthly",
            "calc_cells": [
                "switch2_monthly_sales_table",
                "switch2_monthly_sales_chart",
            ],
            "description": """
         Switch2の今月の販売状況を昨年同月､先月と比較して説明｡
         その月の最終週には一ヶ月のサマリーを､それ以外は月末時点での見通しを記述
         """,
        },
        {
            "cell_name": "md_switch_monthly",
            "calc_cells": ["switch_monthly_sales_table", "switch_monthly_sales_chart"],
            "description": """
         Switchの今月の販売状況を昨年同月､先月と比較して説明｡
         その月の最終週には一ヶ月のサマリーを､それ以外は月末時点での見通しを記述
         """,
        },
        {
            "cell_name": "md_ps5_monthly",
            "calc_cells": ["ps5_monthly_sales_table", "ps5_monthly_sales_chart"],
            "description": """
         PS5の今月の販売状況を昨年同月､先月と比較して説明｡
         その月の最終週には一ヶ月のサマリーを､それ以外は月末時点での見通しを記述
         """,
        },
        {
            "cell_name": "md_xsx_monthly",
            "calc_cells": ["xsx_monthly_sales_chart", "xsx_monthly_sales_table"],
            "description": """
         Xbox Series X|S の今月の販売状況を昨年同月､先月と比較して説明｡
         その月の最終週には一ヶ月のサマリーを､それ以外は月末時点での見通しを記述
         """,
        },
        {
            "cell_name": "md_cumulative_ps5_switch2",
            "calc_cells": ["switch2_ps5_cumulative_chart"],
            "description": """
         PS5とSwitch2の累計比較記事｡特にSwitch2がPS5に追いつく時期の予想を含めて記述｡
         予想には主に52週平均を用いるが､他の方法を用いて比較しても良い｡
         累計台数差の100万台､50万台単位の節目を超えた場合には､それについても言及する｡
         """,
        },
        {
            "cell_name": "md_cumulative_top",
            "calc_cells": ["ns2_cumulative_delta_chart", "cumulative_top_chart"],
            "description": """
         歴代のハードの初期の累計推移を比較する記事｡特にSwitch2を他機種と比較した状況､今後の見通しを記述｡
         Switch2の歴代一位の状況が今後どうなるのかについては特に言及する｡
         100万台単位の節目を超えた場合には､それについても言及し､過去の歴代機種や､現役の他機種との比較､考察を行う｡
         """,
        },
        {
            "cell_name": "md_quarterly",
            "calc_cells": ["quarterly_sales_chart"],
            "description": """
         各年の四半期販売状況と今期の状況を比較して短く解説
         """,
        },
        {
            "cell_name": "md_yearly_hard",
            "calc_cells": ["yearly_sales_chart", "yearly_sales_table"],
            "description": """
         各年の各ハードの状況と､今年の状況を比較して短く解説
         """,
        },
        {
            "cell_name": "md_yearly_maker_share",
            "calc_cells": ["yearly_maker_share_chart"],
            "description": """
         各年の各ハードのメーカーシェアの状況と､今年の状況を比較し解説｡
         52週平均を用いた予測値で､今年の最終的なメーカーシェアの見通しも記述する｡
         """,
        },
    ]
    return


if __name__ == "__main__":
    app.run()
