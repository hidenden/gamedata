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

__generated_with = "0.25.1"
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

    return annotation_all_df, hard_sales_all_df


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
    10月11日は4機種合計で40,427台となり、前週から14.5%減少しました。全機種が前週を下回り、Switch2は22,420台で14.4%減、PS5は11,911台で6.7%減、Switchは5,806台で24.6%減、Xbox Series X|Sは290台で52.6%減となっています。

    今週の節目はSwitchの累計3,700万台到達です。一方、Switch2は発売後の同じ週数で比較した累計で3DSを下回り、歴代2位から3位へ下がりました。現役機種の週間順位は変わらず、Switch2が首位、PS5が2位を維持しています。

    [ファミ通のソフト週販](https://www.famitsu.com/article/202610/91095)では「KINGDOM HEARTS Collection」のSwitch2版が23,411本で1位、PS5版が6,261本で5位となりました。PS5では「ACE COMBAT8」も13,801本で3位に残り、前週に本体を牽引した新作の需要が続いています。ただし新作の発売が重なっても両機種のハード販売は減っており、今週は市場全体を押し上げるまでには至りませんでした。

    次回10月18日集計ではSwitch2、PS5の「Call of Duty:Modern Warfare4」、次々回10月25日集計ではSwitch2の「Nintendo Switch Sports Resort」が販売を支えるかに注目です。Switch2ではソフトセットの予約開始後に本体販売がさらに下がっており、購入待ちの影響も考えられます。

    集計後の10月13日には、11月19日発売の[「PS5DE日本語版ミッドナイトブラック」](https://blog.ja.playstation.com/2026/10/13/20261013-ps5-dej-black-announcement-s/)が発表されました。予約開始は10月20日です。SNSでの人気を踏まえ、発売時には販売を伸ばすと見ていますが、その分、発売前には希望する色を待つ買い控えが予想されます。次回集計以降の減少要因になるでしょう。
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
    Switch2は9月20日の34,341台を頂点に、32,198台、26,200台、22,420台と3週続けて下がりました。直近4週平均も30,270台から28,790台へ低下し、13週平均の29,388台を下回っています。9月後半に広がった他機種との差が、再び縮小する形となっています。

    PS5は3週連続の増加が止まりましたが、減少幅は857台にとどまり、2週連続で1万台を維持しました。直近4週平均は9,460台から10,564台へ上がり、13週平均の9,237台を上回っています。Switch2との週間販売差は前週の13,432台から10,509台へ縮小しました。

    Switchは前週の増加から反落し、直近4週平均も6,818台から6,380台へ低下しました。Xbox Series X|Sは4週続いた増加が一服しています。PS5は4週連続の2位で、今週も順位の入れ替わりはありません。次週はPS5が1万台を保つか、Switch2が下げ止まるかによって、上位2機種の距離が変わってきます。
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
        y2=662000,
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
    PS5の2026年累計は10月11日時点で463,312台です。前年同時期の680,073台を31.9%、2024年同時期の1,117,640台を58.5%下回っています。PS3の2014年同時期389,346台に対しては19.0%多い一方、PS4の2018年同時期1,256,748台には大きく届かず、過去のPlayStationと比べても高い年間販売水準ではありません。

    52週平均の12,739台を年換算した年間販売の目安は約662,000台で、2025年通年の879,204台を下回ります。年初来の前年割れ幅は前週の32.1%から31.9%へわずかに縮まりましたが、年間で前年に並ぶには残り11週で415,892台、週平均約37,810台が必要です。

    発売からの累計は7,761,522台で、800万台まで残り238,478台です。52週平均を維持した場合の到達は約19週後の2027年2月となり、年内到達には残り11週で週平均約21,680台が必要です。同じ発売309週時点でPS3は約825万台、PS4は約881万台に達しており、PS5は累計でも両機種を下回っています。
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
        y2=925000,
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
    Switchの2026年累計は10月11日時点で584,209台です。前年同時期の1,179,925台から50.5%減、2024年同時期の2,274,915台から74.3%減となり、前年の半分弱の販売にとどまっています。年間の目安は、週17,782台という52週平均を基準に約925,000台です。2025年通年の1,520,384台からの縮小を見込んでいます。足元はこの平均より低く、年末商戦での上積みが乏しければ目安からの下振れも考えられます。

    発売からの累計は37,000,370台となり、今週3,700万台を突破しました。発売502週での到達です。既にDSの国内累計約3,260万台を上回っており、普及台数では記録を伸ばす一方、今年の販売規模は後継機への移行に伴い縮小しています。節目の達成と年間需要の減少が並行している点が、現在のSwitchの特徴です。
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
        y2=4208000,
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
    Switch2の2026年累計は10月11日時点で2,624,906台です。前年同時期の2,200,903台を19.3%上回りますが、前年は6月発売だったため販売期間が異なります。今年のPS5の約5.7倍、Switchの約4.5倍を売り上げており、市場の中心を担う構図は続いています。

    52週平均は80,924台で、年間に換算すると約4,208,000台となります。2025年通年の3,784,067台より多い水準ですが、前年の年末商戦や今年春の高い販売を含む平均であり、足元の需要をそのまま示す値ではありません。

    累計700万台までは残り591,027台です。52週平均なら約8週後の12月6日集計、発売79週で到達する計算となり、Switchの97週、PS5の252週を上回る普及速度です。一方、直近4週平均で延ばすと2027年3月までかかります。年内の到達には残り11週で週平均約53,730台が必要で、足元からの明確な回復が条件となります。
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
    Switch2の10月販売は2週累計で48,620台です。前年同月の最初の2週91,281台から46.7%減となりました。月間全体では9月が119,161台、前年10月が358,399台で、今月は10月25日集計までの4週間です。残り2週を今週と同じペースで延ばすと93,460台、直近4週平均なら106,200台となり、9月を10.9～21.6%下回る計算です。

    10月6日の「選べるソフトセット予約開始」によって、11月12日の「選べるソフトセット発売」を待つ理由が生まれました。ソフト同梱で最大4,980円お得な構成のため、11月8日集計までは通常の本体購入を先送りする動きが続くと見ています。既に発表済みの10月29日発売「ゼルダの伝説40周年記念モデル」も、発売日が近づくほど購入待ちを強めるでしょう。

    こうした条件から、10月中に週3万台へ戻るのは引き続き難しいと見ています。記念モデル発売週の販売は11月1日集計に入るため、10月分には発売時の上積みが含まれません。今月の評価では新作ソフトの本数だけでなく、販売が11月へずれる影響も考慮する必要があります。
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
    Switchの10月販売は2週累計で13,510台です。前年同月の最初の2週47,258台を71.4%下回っています。前年10月の月間96,080台に対しても大きく弱い推移です。

    残り2週を今週の販売水準で延ばすと月間25,122台、直近4週平均なら26,270台となり、9月の31,161台を15.7～19.4%下回ります。初週の増加を2週目に維持できなかったため、今月は2.5万～2.6万台程度を基準とし、月後半に持ち直せるかを確認したいところです。
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
    PS5の10月販売は2週累計で24,679台です。前年同月の最初の2週42,144台から41.4%減となっていますが、9月の月間32,831台に対しては既に75.2%まで積み上がりました。

    残り2週を今週のペースで延ばすと月間48,501台、直近4週平均なら45,807台となり、単純延長では9月を約4～5割上回ります。ただし今後は新色を待つ購入層の先送りが加わるため、この4.6万～4.9万台という目安には下振れ余地があります。前年10月の64,732台に届くには残り2週で40,053台が必要で、月後半に大幅な加速がない限り前年割れが続く見通しです。
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
    Xbox Series X|Sの10月販売は2週累計で902台です。前年同月の最初の2週1,074台から16.0%減となる一方、9月の月間918台にはほぼ並びました。今週は290台へ反落したため、初週の612台を基準にした強い見通しは修正する必要があります。

    残り2週を今週の水準で延ばすと月間1,482台、直近4週平均なら1,670台です。どちらも9月を上回りますが、前年10月の2,253台には届きません。
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
    ## Switch 3700万台の軌跡
    """)
    return


@app.cell
def switch_37m(
    annotation_all_df: pl.DataFrame,
    hard_sales_all_df: pl.DataFrame,
    report_date: datetime,
):
    # 3,700万台到達週までの実績で、100万台ごとの区間を固定する。
    _switch_all = hard_sales_all_df.filter(
        (pl.col("hw") == "NSW") & (pl.col("report_date") <= report_date.date())
    ).sort("report_date")
    _reach_37m = _switch_all.filter(pl.col("sum_units") >= 37_000_000).head(1)
    if _reach_37m.is_empty():
        raise ValueError("この集計日ではSwitchの3,700万台到達を確認できません。")
    _reach_date = _reach_37m["report_date"][0]
    _switch_sales = _switch_all.filter(pl.col("report_date") <= _reach_date)
    _ds_sales = hard_sales_all_df.filter(
        (pl.col("hw") == "DS") & (pl.col("report_date") <= _reach_date)
    ).sort("report_date")

    def _milestone_rows(sales, annotations, limit):
        rows = []
        previous_week = 0
        previous_units = 0
        previous_date = None
        for million in range(1, limit + 1):
            reached = sales.filter(pl.col("sum_units") >= million * 1_000_000)
            if reached.is_empty():
                break
            row = reached.row(0, named=True)
            weeks = row["index_week"] - previous_week
            period_units = row["sum_units"] - previous_units
            events = annotations.filter(pl.col("annotation_date") <= row["report_date"])
            if previous_date is None:
                events = events.filter(pl.col("annotation_date") >= row["launch_date"])
            else:
                events = events.filter(pl.col("annotation_date") > previous_date)
            # descを優先し、空文字・NULLのときだけnoteへフォールバックする。
            events = events.with_columns(
                pl.when(pl.col("desc").fill_null("").str.strip_chars() != "")
                .then(pl.col("desc").str.strip_chars())
                .otherwise(pl.col("note").fill_null("").str.strip_chars())
                .alias("event_label")
            ).filter(pl.col("event_label") != "")
            # 重要度で2件を選び、選んだ出来事を時系列で表示する。
            selected = (
                events.sort(["level", "annotation_date", "id"], nulls_last=True)
                .head(2)
                .sort(["annotation_date", "id"])
            )
            labels = [
                f"{event['annotation_date']:%Y-%m-%d} {event['event_label']}"
                for event in selected.to_dicts()
            ]
            rows.append(
                {
                    "threshold_units": million * 1_000_000,
                    "report_date": row["report_date"],
                    "index_week": row["index_week"],
                    "period_weeks": weeks,
                    "period_units": period_units,
                    "weekly_average_units": round(period_units / weeks),
                    "cumulative_units": row["sum_units"],
                    "event_1": labels[0] if labels else "",
                    "event_2": labels[1] if len(labels) > 1 else "",
                    "event_ids": selected["id"].to_list(),
                    "event_count": events.height,
                }
            )
            previous_week = row["index_week"]
            previous_units = row["sum_units"]
            previous_date = row["report_date"]
        return pl.DataFrame(rows, schema_overrides={"event_ids": pl.List(pl.Int64)})

    switch_37m_milestones_df = _milestone_rows(
        _switch_sales, annotation_all_df.filter(pl.col("hw") == "NSW"), 37
    )
    switch_37m_ds_milestones_df = _milestone_rows(
        _ds_sales, annotation_all_df.filter(pl.col("hw") == "DS"), 32
    )
    switch_37m_comparison_df = (
        _switch_sales.select(
            "index_week", "report_date", pl.col("sum_units").alias("switch_units")
        )
        .join(
            _ds_sales.select("index_week", pl.col("sum_units").alias("ds_units")),
            on="index_week",
        )
        .sort("index_week")
        .with_columns(gap=pl.col("switch_units") - pl.col("ds_units"))
    )
    _crossings = switch_37m_comparison_df.with_columns(
        previous_gap=pl.col("gap").shift(1)
    ).filter((pl.col("gap") > 0) & (pl.col("previous_gap") <= 0))
    _ds_final = _ds_sales.row(-1, named=True)
    _switch_final = _switch_sales.row(-1, named=True)
    _same_ds_final = switch_37m_comparison_df.filter(
        pl.col("index_week") == _ds_final["index_week"]
    ).row(0, named=True)
    switch_37m_metrics = {
        "switch_final": _switch_final,
        "ds_final": _ds_final,
        "same_52": switch_37m_comparison_df.filter(pl.col("index_week") == 52).row(
            0, named=True
        ),
        "same_ds_final": _same_ds_final,
        "max_ds_lead": switch_37m_comparison_df.sort("gap").row(0, named=True),
        "relative_cross": _crossings.row(-1, named=True),
        "ds_final_cross": _switch_sales.filter(
            pl.col("sum_units") > _ds_final["sum_units"]
        ).row(0, named=True),
        "switch_peak_year": _switch_sales.group_by("year")
        .agg(pl.col("units").sum())
        .sort("units", descending=True)
        .row(0, named=True),
        "ds_peak_year": _ds_sales.group_by("year")
        .agg(pl.col("units").sum())
        .sort("units", descending=True)
        .row(0, named=True),
        "fastest_million": switch_37m_milestones_df.sort(
            ["period_weeks", "threshold_units"]
        ).row(0, named=True),
        "period_36m": switch_37m_milestones_df.filter(
            pl.col("threshold_units") == 36_000_000
        ).row(0, named=True),
        "period_37m": switch_37m_milestones_df.filter(
            pl.col("threshold_units") == 37_000_000
        ).row(0, named=True),
        "after_ds_final_weeks": _switch_final["index_week"] - _ds_final["index_week"],
        "after_ds_final_units": _switch_final["sum_units"]
        - _same_ds_final["switch_units"],
    }

    mo.md(f"""
    {_switch_final["launch_date"]:%Y年%m月%d日}発売のNintendo Switchは、
    {_reach_date:%Y年%m月%d日}集計で国内累計**{_switch_final["sum_units"]:,}台**となり、
    発売**{_switch_final["index_week"]}週目**に3,700万台を突破しました。
    100万台ごとの到達履歴から、普及の加速と成熟の過程を振り返ります。
    """)

    return (
        switch_37m_ds_milestones_df,
        switch_37m_metrics,
        switch_37m_milestones_df,
    )


@app.cell(hide_code=True)
def switch_37m_history_table(switch_37m_milestones_df):
    _heatmap_min = switch_37m_milestones_df["period_weeks"].min()
    _heatmap_range = max(
        switch_37m_milestones_df["period_weeks"].max() - _heatmap_min, 1
    )

    def _style_required_weeks(_row_id, _column_name, _value):
        if _column_name != "必要週数" or _value is None:
            return {}
        _fraction = min(max((float(_value) - _heatmap_min) / _heatmap_range, 0), 1)
        _rgb = tuple(
            round(_light + (_dark - _light) * _fraction)
            for _light, _dark in zip((247, 250, 255), (32, 88, 163))
        )
        _linear = [
            (_channel / 255) / 12.92
            if _channel / 255 <= 0.04045
            else ((_channel / 255 + 0.055) / 1.055) ** 2.4
            for _channel in _rgb
        ]
        _luminance = sum(
            _weight * _channel
            for _weight, _channel in zip((0.2126, 0.7152, 0.0722), _linear)
        )
        return {
            "backgroundColor": f"rgb({_rgb[0]}, {_rgb[1]}, {_rgb[2]})",
            "color": "#ffffff" if _luminance < 0.179 else "#000000",
            "fontWeight": "600",
        }

    _display = switch_37m_milestones_df.select(
        pl.col("threshold_units")
        .map_elements(lambda value: f"{value // 10_000:,}万台", return_dtype=pl.String)
        .alias("台数"),
        pl.col("report_date").dt.strftime("%Y-%m-%d").alias("到達日"),
        pl.col("index_week").cast(pl.Int64).alias("週数"),
        pl.col("period_weeks").cast(pl.Int64).alias("必要週数"),
        pl.when(pl.col("event_count") == 0)
        .then(pl.lit(""))
        .when(pl.col("event_count") == 1)
        .then(pl.col("event_1"))
        .otherwise(
            pl.concat_str([pl.col("event_1"), pl.col("event_2")], separator=" ／ ")
        )
        .alias("出来事"),
    )
    switch_37m_history_table = mo.ui.table(
        _display,
        pagination=False,
        selection=None,
        show_column_summaries=False,
        show_data_types=False,
        format_mapping={
            "週数": "{:,.0f}".format,
            "必要週数": "{:,.0f}".format,
        },
        style_cell=_style_required_weeks,
        header_tooltip={
            "必要週数": "濃い青ほど、次の100万台に達するまで長い期間を要した区間です。"
        },
        wrapped_columns=["出来事"],
        column_widths={
            "台数": 90,
            "到達日": 105,
            "週数": 65,
            "必要週数": 80,
            "出来事": 420,
        },
        label="Switch：100万台ごとの到達履歴（37行）",
    )
    mo.vstack(
        [
            mo.md("""
    ### 100万台ごとの到達履歴

    到達日は初めて節目を超えた週の集計日、週数は発売週を1とした経過週数です。
    必要週数は直前の節目の到達週との差で、最初の100万台は発売週から数えています。
        """),
            switch_37m_history_table,
        ]
    )

    return


@app.cell(hide_code=True)
def switch_37m_ds_chart(switch_37m_metrics):
    _last_week = switch_37m_metrics["switch_final"]["index_week"]
    switch_37m_ds_chart = g.chart_line_cumulative_delta(
        hw=["DS", "NSW"],
        mode="week",
        begin=1,
        end=_last_week,
        ymax=40_000_000,
        annotation_level=10,
        index_mode=True,
        with_point=False,
        multi_line=True,
        size=(900, 420),
    ).properties(title="Nintendo DSとNintendo Switch：発売週を揃えた累計販売")
    _chart_view = mo.ui.altair_chart(switch_37m_ds_chart)
    mo.vstack(
        [
            mo.md("### DSとSwitchの累計の伸び方"),
            _chart_view,
            mo.md(f"""
    横軸はそれぞれの発売週から数えた週数で、同じ暦の日付を比較したものではありません。
    DSは本データの最終集計である{switch_37m_metrics["ds_final"]["index_week"]}週
    （{switch_37m_metrics["ds_final"]["report_date"]:%Y-%m-%d}）、
    Switchは3,700万台に到達した{_last_week}週までを表示しています。
        """),
        ]
    )

    return


@app.cell(hide_code=True)
def switch_37m_ds_analysis(
    switch_37m_ds_milestones_df,
    switch_37m_metrics,
    switch_37m_milestones_df,
):
    _m = switch_37m_metrics
    _sw = switch_37m_milestones_df
    _ds = switch_37m_ds_milestones_df
    _sw_10m = _sw.filter(pl.col("threshold_units") == 10_000_000)["index_week"][0]
    _ds_10m = _ds.filter(pl.col("threshold_units") == 10_000_000)["index_week"][0]
    _sw_20m = _sw.filter(pl.col("threshold_units") == 20_000_000)["index_week"][0]
    _ds_20m = _ds.filter(pl.col("threshold_units") == 20_000_000)["index_week"][0]

    mo.md(f"""
    ### 発売1年の規模は近く、加速した時期が異なる

    発売52週の累計はSwitchが{_m["same_52"]["switch_units"]:,}台、
    DSが{_m["same_52"]["ds_units"]:,}台で、差は約20万台でした。
    両機種とも最初の1年で大きな普及基盤を築きましたが、その後はDSの伸びが先行します。
    1,000万台到達はDSが{_ds_10m}週、Switchが{_sw_10m}週、
    2,000万台はそれぞれ{_ds_20m}週、{_sw_20m}週です。
    同じ経過週数でのDSの最大リードは{_m["max_ds_lead"]["index_week"]}週時点の
    **{-_m["max_ds_lead"]["gap"]:,}台**に達しました。

    ただし、DSは12月、Switchは3月の発売で、年末商戦を迎える経過週数が異なります。
    DSの100万台到達は4週、Switchは17週でしたが、初期の速さを比べる際には
    この発売時期の違いも考慮する必要があります。

    ### DSは早期の急拡大、Switchは中盤以降の持続

    暦年で販売が最大だったのはDSが{_m["ds_peak_year"]["year"]}年の
    {_m["ds_peak_year"]["units"]:,}台、Switchが{_m["switch_peak_year"]["year"]}年の
    {_m["switch_peak_year"]["units"]:,}台です。DSは発売から比較的早い段階で
    大きく普及した一方、Switchは発売4年目に最大の年間販売を記録しました。

    DSには「脳トレ」「どう森」「DSi発売」、Switchには
    「Switch Lite」「あつ森」「有機ELモデル」といった節目があります。
    ソフトと本体の更新を重ねながら累計を積み上げた点は共通しています。
    その中でSwitchは、最初の1,000万台に{_sw_10m}週かかった後、
    次の1,000万台を{_sw_20m - _sw_10m}週で売り、販売期間の中盤に加速しました。
    100万台単位で最も短い区間は600万台から700万台までの
    {_m["fastest_million"]["period_weeks"]}週で、2018年末から2019年初めに当たります。
    年末年始を含む区間なので、季節的な需要の集中が速さに寄与したと考えられます。

    ### 後半の積み上げが最終的な差を生んだ

    Switchは{_m["ds_final_cross"]["report_date"]:%Y年%m月%d日}集計、
    発売{_m["ds_final_cross"]["index_week"]}週でDSの最終累計
    **{_m["ds_final"]["sum_units"]:,}台**を上回りました。
    同じ経過週数の累計比較でも、この{_m["relative_cross"]["index_week"]}週に再逆転しています。

    DSの最終集計と同じ{_m["ds_final"]["index_week"]}週で比較すると、
    Switchは{_m["same_ds_final"]["switch_units"]:,}台で、
    既にDSを{_m["same_ds_final"]["gap"]:,}台上回っていました。
    その後の{_m["after_ds_final_weeks"]}週でさらに{_m["after_ds_final_units"]:,}台を積み上げ、
    今回の3,700万台へ到達しています。DSの早期の急拡大に対し、
    Switchは中盤の加速と長い後半の販売が累計を押し上げたと捉えられます。

    もっとも、直近の100万台には{_m["period_37m"]["period_weeks"]}週を要し、
    その前の{_m["period_36m"]["period_weeks"]}週から期間が延びています。
    区間の週平均も{_m["period_36m"]["weekly_average_units"]:,}台から
    {_m["period_37m"]["weekly_average_units"]:,}台へ低下しました。
    大きな累計を築いた持続力と、世代交代期に入った現在の減速の両方が、
    この37行の履歴に表れています。
    """)

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
    10月11日時点の累計差は1,352,549台で、PS5が7,761,522台、Switch2が6,408,973台です。今週の差の縮小は10,509台となり、前週の13,432台から鈍化しました。

    52週平均の差は週68,185台で、このペースなら約20週後の2027年2月末に逆転する計算です。直近4週平均の差は週18,226台となり、こちらでは約75週後の2028年3月までかかります。短期の平均差が前週の20,810台から縮まったため、足元を基準にした逆転時期はさらに後ろへ動きました。

    二つの逆転時期は、直近1年と直近4週それぞれの平均差が続くことを前提とした試算です。現時点では予測日の一点よりも、週当たりの縮小幅が再び拡大へ向かうかを重視したいところです。
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
    発売71週時点のSwitch2累計は6,408,973台となり、3DSの6,416,853台を7,880台下回って歴代3位へ下がりました。前週は34,967台上回っていましたが、今週の販売が3DSの同じ週の65,267台に届かず、逆転を許しています。首位DSは6,946,582台で、Switch2との差は537,609台へ広がりました。

    次の72週時点の3DS累計は6,468,783台です。Switch2が再び上回るには次週に59,811台以上が必要で、今週の販売の約2.7倍に当たります。DSは72週で700万台を超え、週販も約20万台あるため、足元の推移からは首位への復帰も見込みにくい状況です。

    一方、同じ71週のGBAは5,681,505台、Switchは4,618,363台で、Switch2はそれぞれ約73万台、約179万台上回っています。順位は下がったものの、前世代機より早い普及は維持しています。今後は3DSとの差を再び縮められる販売水準へ戻るかが焦点になります。
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
    2026年第4四半期は2週累計で87,711台です。前年同期の最初の2週181,793台を51.8%、2024年の144,100台を39.1%下回っています。初週に続いて2週目も弱く、四半期の出足は低調です。

    前年の第4四半期は2,308,689台で、第3四半期の約1.7倍でした。今年は直前の第3四半期が617,823台と、2001年以降の完了した四半期で最低にとどまっています。前年と同程度の季節的な伸びを当てはめても約108万台であり、2024年第4四半期の1,345,463台にも届きません。四半期の販売規模を取り戻すには、通常の年末需要以上の回復が必要です。
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
    2026年の主要4機種の販売は10月11日時点で合計3,690,237台となり、前年同時期の4,088,162台を9.7%下回っています。前年との差は397,925台で、前週の353,324台から広がりました。一方、2024年同時期の3,480,590台に対しては6.0%多い水準です。表の全機種合計はPS4の275台を含む3,690,512台となっています。

    前年比の内訳はSwitch2が424,003台増、Switchが595,716台減、PS5が216,761台減、Xbox Series X|Sが9,451台減です。後継機の増加だけでは他機種の減少を埋められていません。2024年通年の全機種販売4,695,363台に並ぶには、残り11週で約100万台、週平均約9.1万台が必要です。前年を下回るだけでなく、2024年の年間規模を保てるかも今後の判断材料になります。
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
    2026年のメーカー別シェアは10月11日時点で任天堂が87.0%、ソニーが12.6%、マイクロソフトが0.5%です。前週の87.1%、12.4%、0.5%に対し、任天堂がわずかに下がり、ソニーが上がりました。ソニーは今週も絶対台数では減少しており、シェアの上昇は他社より落ち込みが小さかった結果です。任天堂の比率は2025年通年の85.3%、2024年の66.2%をなお上回っています。

    主要4機種の52週平均を年換算した販売台数で年間シェアを試算すると、任天堂が約88.2%、ソニーが約11.4%、マイクロソフトが約0.4%です。試算上の任天堂の比率は現在の実績より約1.3ポイント高く、ソニーは約1.2ポイント低くなります。年間では任天堂の優位が続く見通しですが、足元では逆方向に動いており、年末商戦で各社がどれだけ販売を積み上げるかによって最終的な比率は変わるでしょう。
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
