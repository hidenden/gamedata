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

__generated_with = "0.26.0"
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
    hard_sales_all_df: pl.DataFrame = g.load_hard_sales2(True)
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


@app.cell(hide_code=True)
def md_prologue():
    mo.md(r"""
    * ハードウェアの販売データはファミ通の調査結果を基にしています。
    * 複数週合算の集計値は処理上の都合により、週次値に調整しています｡
    * [過去の週販レポート](../index.html)
    """)


@app.cell(hide_code=True)
def md_weekly_summary_title():
    mo.md(r"""
    ## 直近4週間のハード売上／累計推移
    """)


@app.cell
def units_by_date_hw_table(
    hard_sales_all_df: pl.DataFrame,
    report_date: datetime,
):
    _table = g.units_by_date_hw_table(
        hard_sales_all_df, begin=g.weeks_before(report_date, 3), end=report_date
    )
    mo.hstack(items=[_table], justify="start", wrap=True)


@app.cell(hide_code=True)
def md_top():
    mo.md(r"""
    11月22日集計の主要4機種は合計83,402台で、前週から43.8%増えました。PS5は41,472台で前週の3.72倍となり、Switch2は36,817台で13.2%減。Switchは4,362台、Xbox Series X|Sは751台と、いずれも前週を上回りました。

    11月19日発売の「グランド・セフト・オートVI（GTAVI）」は、PS5版が国内のファミ通推計で200,759本を販売し、初登場で首位。Xbox Series X|S版も同日発売でした。国内では、ソフトの初動に合わせてPS5本体も大きく伸びました。「PS5DE日本語版ミッドナイトブラック」も同日に発売され、本体を買うきっかけが重なった週です。[ファミ通の11月16日～22日集計](https://www.famitsu.com/article/202611/95209)

    ミッドナイトブラックモデルはソニーストアをはじめほとんどの通販サイトで販売終了｡
    ヨドバシ.comなど一部のサイトに在庫が僅かに残っている状況です｡
    来週の週販台数に影響があるほどの台数は残っていないと思われます｡
    来週はGTAVI 2週目の牽引効果のみどこまで台数を維持できるか注目です｡

    Xboxに関しては本体牽引効果わずかでした｡日本市場への供給台数がわずかであり､せっかくのチャンスを活かせていません｡

    Switch2では「ゼルダの伝説 時のオカリナ」が35,295本で2位に入りました。次々回の12月6日集計には、Switch2の「ドラクエモンスターズ4」と「モンスターハンターワイルズ(Switch2版)」が入ります。12月の第1週に本体をどこまで押し上げられるか注目です。
    """)


@app.cell(hide_code=True)
def md_weekly_sales_trend():
    mo.md(r"""
    ## 週販推移
    """)


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


@app.cell(hide_code=True)
def md_weekly_sales_trend_1():
    mo.md(r"""

    """)


@app.cell(hide_code=True)
def md_weekly_sales_trend_2():
    mo.md(r"""
    ### 週販推移(拡大)
    """)


@app.cell
def weekly_sales_trend_2(report_date: datetime):
    _begin = date(2026, 2, 15)
    _end = report_date
    _chart = g.chart_line_sales(
        hw=["NSW", "PS5", "XSX", "NS2"],
        begin=_begin,
        end=_end,
        annotation_level=30,
        ymax=75000,
        padding_end=1,
        value_label=True,
    )
    weekly_big_chart = mo.ui.altair_chart(_chart)
    mo.vstack(items=[weekly_big_chart], justify="start")


@app.cell(hide_code=True)
def md_weekly_chart():
    mo.md(r"""
    Switch2発売から77週目にして、PS5が初めて週間販売で上回りました。先週はSwitch2が31,266台先行していましたが、今週はPS5が4,655台上回っています。PlayStationがSwitch/Switch2を上回るのは2025年3月9日集計以来、89週ぶりです。前回はモンスターハンターワイルズ効果で 2025/3/2, 2025/3/9の2週連続でPS5がSwitchを上回りました｡GTVIがこれに匹敵するハード牽引力があるかどうか注目です｡

    Switch2の週販は3週連続で減少しています。4週平均は46,508台から50,264台に上がりましたが、比較的少なかった10月25日集計が平均から外れたためで、直近の折れ線は下向きです。Switchは週販が反発しても4週平均は4,779台まで低下し、Xbox Series X|Sは4週平均が898台に上昇しました。
    """)


@app.cell(hide_code=True)
def md_yearly_cumulative_comparison_title():
    mo.md(r"""
    ## 年間累計比較
    """)


@app.cell(hide_code=True)
def md_yearly_cumulative_comparison_1():
    mo.md(r"""

    """)


@app.cell(hide_code=True)
def md_ps5_yearly_cumulative_title():
    mo.md(r"""
    ### PlayStation 5(2024年, 2025年, 2026年)
    """)


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
        y2=637000,
        stroke=[3, 2],
        size=2,
        color="#ff000080",
    )
    ps5_yearly_cumulative_chart = mo.ui.altair_chart(_chart)
    mo.vstack(items=[ps5_yearly_cumulative_chart], justify="start")


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


@app.cell(hide_code=True)
def md_ps5_yearly():
    mo.md(r"""
    PS5の2026年累計は570,520台で、前年同時期の760,727台を25.0%、2024年の1,292,270台を55.9%下回ります。前年との差は先週の27%弱から縮まりました。過去の据置機と比べると、2014年のPS3（415,204台）を上回り、2018年のPS4（1,375,108台）には届いていません。

    残り5週を52週平均の13,250台で進むと、年末は約63.7万台で、前年通年から27.6%減る計算です。発売以来の累計800万台までは残り131,270台です。同じペースなら2027年1月31日集計で到達し、年内に達するには週平均26,254台が必要です。

    年間販売では、PS5はSwitchの613,099台に42,579台差まで迫りました。残り5週で週平均8,516台以上の差をつければ逆転します。Switchが直近4週平均の4,779台前後で推移するなら、PS5は週平均約1.33万台が目安です。Switchが年末商戦で週平均8,000台まで伸びる場合は、PS5にも約1.65万台が必要になります。

    「GTAVI」発売後も本体需要が続き、次週にPS5が2万台、その後4週を平均1.2万台で販売した場合、Switchが足元のペースならPS5が約1,500台差で上回る計算です。新色も同日に出たため、まずは翌週にどこまで販売が残るかに注目です。
    """)


@app.cell(hide_code=True)
def _():
    mo.md(r"""

    """)


@app.cell(hide_code=True)
def md_switch_yearly_cumulative_title():
    mo.md(r"""
    ### Switch(2024年, 2025年, 2026年)
    """)


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
        y2=690000,
        stroke=[3, 2],
        size=2,
        color="#ff000080",
    )
    switch_yearly_cumulative_chart = mo.ui.altair_chart(_chart)
    mo.vstack(items=[switch_yearly_cumulative_chart], justify="start")


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


@app.cell(hide_code=True)
def md_switch_yearly():
    mo.md(r"""
    Switchの2026年累計は613,099台です。前年同時期から54.0%減、2024年から76.9%減となりました。52週平均の15,424台を残り5週に当てはめると、年間約69.0万台で、前年通年の半分を下回ります。

    任天堂の世界向け出荷計画を前年の季節配分と今上期の日本比率で按分すると、国内10～12月の参考規模は約13.4万台です。ファミ通ベースの国内実売は8週で42,400台。残り5週で同規模に達するには週平均約1.8万台が必要で、足元の4週平均の約3.8倍に当たります。会社の販売計画と店頭推計では集計対象が異なるため、ここでは規模の目安として比べています。[任天堂の決算説明資料](https://www.nintendo.co.jp/ir/pdf/2026/261105_3.pdf#page=15)
    """)


@app.cell(hide_code=True)
def switch2_yearly_cumulative_title():
    mo.md(r"""
    ### Switch2(2025年, 2026年)
    """)


@app.cell
def switch2_yearly_cumulative_chart(switch2_latest):
    _chart = g.chart_line_ycumulative_by_hw_year(
        hw_years=[("NS2", 2025), ("NS2", 2026)],
        annotation_level=19,
    )
    _df = mo.ui.altair_chart(_chart).dataframe

    _chart = g.chart_line_guide(
        _chart,
        x=switch2_latest["report_date"].timetuple().tm_yday,
        y=_df.filter(pl.col("report_date") == switch2_latest["report_date"]).row(
            0, named=True
        )["yearly_sum_units"],
        x2=365,
        y2=3230000,
        stroke=[3, 2],
        size=2,
        color="#ffa00080",
    )
    switch2_yearly_cumulative_chart = mo.ui.altair_chart(_chart)
    mo.vstack(items=[switch2_yearly_cumulative_chart], justify="start")


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


@app.cell(hide_code=True)
def md_switch2_yearly():
    mo.md(r"""
    Switch2は年累計で2,869,608台を販売しました。先週までの約8.9万台のリードが消え、前年同時期までの販売台数を1,150台下回りました。残り5週を52週平均の72,748台で進むと、年間約323万台で、初年の約378万台から14.6%減る計算です。

    国内10～12月の実売は8週で293,322台です。前回と同じ試算では、地域配分に日本比率21.9%を使った場合の参考規模が約161.6万台、28.3%の場合が約209万台です。残り5週に必要な週平均はそれぞれ約26.5万台と約35.9万台で、前年の残り5週平均の約18.3万台を大きく上回ります。[任天堂の決算説明資料](https://www.nintendo.co.jp/ir/pdf/2026/261105_3.pdf#page=15)

    年内に国内累計700万台へ届くには、12月27日集計までに346,325台、週平均69,265台の積み上げが必要です。52週平均で進めば発売82週で到達します。Switchの97週、PS5の252週より早い一方、足元の月内ペースからは加速が必要です。
    """)


@app.cell(hide_code=True)
def md_monthly_sales_trend_title():
    mo.md(r"""
    ## 月間販売推移
    """)


@app.cell(hide_code=True)
def md_ns2_monthly_sales_title():
    mo.md(r"""
    ### Nintendo Switch2: 月間販売台数
    """)


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


@app.cell(hide_code=True)
def md_switch2_monthly():
    mo.md(r"""
    Switch2は11月の4週で201,056台を販売し、10月通月の約2.18倍になりました。前年11月の最初の4週は402,737台だったため、同じ週数の比較では50.1%減です。今月は初週が約6.9万台だったのに対し、第4週は3万台台まで下がっています。

    最終週も今週並みなら11月は約23.8万台、11月の週平均を維持すれば約25.1万台です。月間25万台に届くには最終週に48,944台が必要です。
    """)


@app.cell(hide_code=True)
def md_switch_monthly_sales_title():
    mo.md(r"""
    ### Nintendo Switch: 月間販売台数
    """)


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


@app.cell(hide_code=True)
def md_switch_monthly():
    mo.md(r"""
    Switchの11月は4週で19,117台となり、前年の同じ4週より81.4%少なく、週平均でも10月を17.9%下回ります。今週はLiteが前週から961台増え、通常版と有機ELモデルの減少を補いました。

    最終週に4,166台で10月の月間販売と並びます。今週と同じ台数なら11月は23,479台となり、10月を196台上回る計算です。
    """)


@app.cell(hide_code=True)
def md_ps5_monthly_sales_title():
    mo.md(r"""
    ### PlayStation 5: 月間販売台数
    """)


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


@app.cell(hide_code=True)
def md_ps5_monthly():
    mo.md(r"""
    PS5の11月は4週で80,533台に達し、前年の同じ4週より38.7%多く、週平均は10月比56.8%増です。前年11月通月の93,852台に並ぶには、最終週に13,319台が必要です。

    発売週の本体増加30,336台のうち、29,914台をデジタル・エディション（DE）が占めました。DEは40,362台、Proも前週の594台から1,031台に伸び、ディスク搭載の通常モデルは79台にとどまりました。DEの新色とソフトの購入が重なりやすい条件に加え、
    GTAVIの快適なプレイ環境を求めるユーザによりProにも伸びが見られました。
    """)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Xbox Series X|S: 月間販売台数
    """)


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


@app.cell(hide_code=True)
def md_xsx_monthly():
    mo.md(r"""
    Xbox Series X|Sの11月は4週で3,591台です。前年の同じ4週の約2.1倍、10月通月の約2.1倍で、最終週が今週並みなら月間4,342台になります。

    発売週の増加はシリーズ全体で44台でした。Series Xデジタル版は338台から462台に増えましたが、通常のSeries Xは331台から232台に減り、シリーズ全体では11月8日の1,241台を下回っています。「GTAVI」のXbox版はファミ通の上位10本に入っておらず、ストアで直接購入された本数も分からないため、国内のソフト販売規模は見積もれません。少なくとも、本体週販に出た上積みは小幅でした。[ファミ通の販売集計](https://www.famitsu.com/article/202611/95209)
    """)


@app.cell(hide_code=True)
def md_cumulative_sales_trend_title():
    mo.md(r"""
    ## 累計販売推移
    """)


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


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### 累計販売推移(Switch2, PS5拡大)
    """)


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


@app.cell(hide_code=True)
def md_cumulative_ps5_switch2():
    mo.md(r"""
    発売以来の国内累計でPS5は7,868,730台、Switch2は6,653,675台です。この週は両機種の累計差が拡大し、先週の1,210,400台から1,215,055台になりました。

    52週平均ではSwitch2が毎週59,498台ずつ差を縮める計算で、このペースなら21週後の2027年4月18日集計で追いつきます。今週を含む4週平均の差30,131台を使うと41週後の2027年9月5日です。PS5の伸びが翌週以降も続くかで、短期平均を使った見通しは大きく動きます。

    それぞれの52週平均が続く場合、国内累計800万台に達するのは、PS5は週13,250台で10週後の2027年1月31日集計、Switch2は週72,748台で19週後の2027年4月4日集計の見込みです。
    """)


@app.cell
def md_ns2_sales_weeks_title(switch2_latest):
    _ns2_weeks = switch2_latest["index_week"]
    mo.md(f"### Switch2: {_ns2_weeks}週目の累計状況")


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
        x2=95,
        y2=7700000,
        stroke=[2, 3],
        size=2,
        color="#800000",
    )
    cd_chart = mo.ui.altair_chart(_chart)
    mo.vstack(items=[cd_chart], justify="start")


@app.cell
def cumulative_top_chart(hard_sales_all_df: pl.DataFrame, ns2_info):
    cumulative_tops_df = (
        hard_sales_all_df.filter(pl.col("index_week") == ns2_info["sales_weeks"])
        .filter(pl.col("hw").is_in(["NS2", "NSW", "3DS", "GBA", "DS"]))
        .select("hw", "index_week", "report_date", "sum_units")
        .sort("sum_units", descending=True)
    )
    g.style_df(g.rename_columns(cumulative_tops_df))


@app.cell(hide_code=True)
def md_cumulative_top():
    mo.md(r"""
    Switch2は発売77週時点で歴代3位です。同じ週数でDSが800万台、3DSが700万台を超え、Switch2との差はそれぞれ約144万台、約37万台になりました。次の78週にDSは30万台、3DSも10万台超を積み上げたため、上位との差はさらに広がりやすい局面です。

    前世代のSwitchに対しては、同じ77週で約173万台先行しています。週販ではSwitchが53,536台とこの週のSwitch2を上回り、2機種の累計差は先週より約1.7万台縮まりました。
    """)


@app.cell(hide_code=True)
def md_yearly_sales_title():
    mo.md(r"""
    ## 年単位の状況
    """)


@app.cell(hide_code=True)
def md_quarterly_title():
    mo.md(r"""
    ### 四半期ごとの状況
    """)


@app.cell
def quarterly_sales_chart():
    _c1 = g.chart_bar_yearly_by_mode(
        begin=date(2016, 1, 1),
    )
    quarter_chart = mo.ui.altair_chart(_c1)
    mo.vstack([quarter_chart])


@app.cell(hide_code=True)
def md_quarterly():
    mo.md(r"""
    2026年10～12月期の最初の8週で、国内ハードは472,912台を販売しました。前年の同じ8週に対して56.5%減、2024年に対して34.1%減です。PS5の増加で2024年に対する減少率は先週の37.2%から縮まりました。

    2024年の10～12月期に並ぶには、残り5週で872,551台、週平均約17.5万台が必要です。今期ここまでの週平均約5.9万台の約3倍に当たります。
    """)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### 機種ごとの状況
    """)


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


@app.cell(hide_code=True)
def md_yearly_hard():
    mo.md(r"""
    2026年の国内ハード販売は11月22日までに全機種で4,075,713台となりました。前年同時期の4,994,096台より18.4%少なく、2024年同時期は8,481台だけ上回っています。2024年通年の約470万台に並ぶには、残り5週で約62万台が必要です。

    前年同時期との約91.8万台の差のうち、Switchの減少が約71.8万台、PS5の減少が約19.0万台を占めます。Switch2は前年とほぼ同じため、世代交代による旧機種の減少を新機種の増加で補えていないのが今年の市場の特徴です。
    """)


@app.cell(hide_code=True)
def md_yearly_maker_share_title():
    mo.md(r"""
    ### 年単位のメーカーシェア
    """)


@app.cell
def yearly_maker_share_chart():
    _chart = g.chart_hbar_yearly_share_by_maker(date(2015, 1, 1), date(2026, 12, 31))
    share_chart = mo.ui.altair_chart(_chart)
    mo.vstack(items=[share_chart], justify="start")


@app.cell(hide_code=True)
def md_yearly_maker_share():
    mo.md(r"""
    2026年累計のメーカー別シェアは任天堂85.5%、ソニー14.0%、マイクロソフト0.5%です。週間ではソニー49.7%、任天堂49.4%と僅差で、先週の任天堂79.6%、ソニー19.2%から一変しました。

    主要4機種の52週平均を残り5週に当てはめると、年末のシェアは任天堂85.6%、ソニー13.9%、マイクロソフト0.5%です。任天堂は前年通年の85.3%をわずかに上回る見通しです。
    """)


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


if __name__ == "__main__":
    app.run()
