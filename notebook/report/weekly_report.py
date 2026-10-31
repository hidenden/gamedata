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
    10月25日は4機種合計で43,297台となり、前週から15.1%増加しました。PS5が16,008台で50.1%増、Switchが4,916台で1.2%増、Xbox Series X|Sが581台で153.7%増となった一方、Switch2は21,792台で0.3%減です。市場全体の増加5,690台のうち、PS5の増加が5,341台を占めました。

    [ファミ通のソフト週販](https://www.famitsu.com/article/202610/92517)では、PS5版「ファイナルファンタジー レゾナンス」が50,452本、10月23日発売のPS5版「Call of Duty:Modern Warfare4」が初週12,816本を販売しました。新作需要がPS5本体の反発を支えた可能性も否定はできませんが､従来の同レベルのタイトルのハード牽引力としては奇異な感じがします｡一方、Switch2では「Nintendo Switch Sports Resort」が64,632本で1位、「ファイナルファンタジー レゾナンス」が52,268本で2位となりましたが、本体はほぼ横ばいでした。

    10月分は今週で確定し、Switch2とSwitchはともに発売以来の月間販売の最低値を更新しました。PS5は前月から回復しており、任天堂の2機種とPS5で月間の方向が分かれています。

    次回11月1日集計は「Minecraft(Swtich2版)」に加え、10月29日発売の「ゼルダの伝説40周年記念モデル」が入ります。本体モデルを待っていた需要が販売へ移り、大きく伸びる可能性があります。次々回11月8日集計には「ゼルダの伝説 時のオカリナ」「Steller Blade Complete Edition」も控えており、モデル発売後の勢いをソフトが支えられるかが焦点です。
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
    Switch2は5週連続の減少ですが、今週の減少幅は62台に縮まり、実質的には横ばいです。直近4週平均は25,668台から23,066台へ下がり、13週平均の26,969台も下回っています。9月後半の高い週が平均の対象から外れたことで、足元の2万台前半の水準がより明確になりました。

    PS5は2週続いた減少から反発し、3週ぶりの増加となりました。16,008台は3月29日以来、30週ぶりの高水準です。直近4週平均も11,269台から12,838台へ上昇し、13週平均の9,846台を上回りました。Switch2との差は5,784台に縮まり、発売以降の73週間で最小となりました。これまでの最小差は10月11日の10,509台で、1万台を下回ったのも初めてです。週間順位は変わらず、PS5は6週連続の2位です。

    Switchは前週から59台増えたものの、2週続けて5,000台未満で、直近4週平均も5,821台へ低下しました。Xbox Series X|Sは2週続いた減少から増加へ転じています。上位ではPS5の線が上向き、Switch2は横ばいに近づいています。次週は本体モデル発売によって、この傾きが変わるかに注目です。
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
        y2=667000,
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
    PS5の2026年累計は10月25日時点で489,987台です。前年同時期の702,661台を30.3%、2024年同時期の1,140,900台を57.1%下回っています。年初来の前年割れ幅は前週の31.5%から縮小しました。PS3の2014年同時期398,233台より23.0%多い一方、PS4の2018年同時期1,295,936台には62.2%届きません。

    52週平均は12,818台で、52倍した年換算値は約667,000台です。これとは別に、今年の実績へ残り9週を同じ平均で加えると、年末の年間販売は約605,000台となります。この条件付きの予測では2025年通年の879,204台を31.1%下回ります。残る期間には11月19日の「GTAVI」発売が含まれるため、新作需要が週販を引き上げれば試算を上回る余地があります。

    発売からの累計は7,788,197台となり、800万台まで残り211,803台です。52週平均なら約17週後の2027年2月に到達する計算です。年内到達には残り9週で週平均約23,530台が必要で、今回の回復後の水準からも上積みが求められます。
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
        y2=886000,
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
    10月25日までのSwitchの年内販売は593,982台となりました。前年同時期の1,228,747台から51.7%減、2024年同時期の2,401,492台から75.3%減となり、年間の縮小が続いています。52週平均は17,031台で、年換算では約886,000台ですが、今年の実績に残る9週分を加える年末試算は約747,000台です。2025年通年の1,520,384台から約半減する計算となります。

    発売からの累計は37,010,143台となりました。直近4週平均は5,821台と52週平均より低く、年末試算は過去1年の比較的高い販売が続く場合の水準です。3,800万台までは残り989,857台あり、足元の平均を維持しても3年以上かかります。供給の継続期間も条件になるため、次の大台は長期販売が続いた場合の上振れとして捉えたいところです。
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
        y2=3985000,
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
    2026年のSwitch2販売は10月25日までに2,668,552台となりました。前年同時期の2,468,021台を8.1%上回りますが、前年超過分は前週の244,173台から200,531台へ減少しました。前年は6月発売のため販売期間が異なる一方、今年は年初から販売しており、その差を含めても前年比の伸びは鈍っています。

    52週平均の76,627台を年換算すると約3,985,000台です。ただし今年の実績へ残り9週を同じ平均で加える年末予測は約3,358,000台となり、2025年通年の3,784,067台を11.3%下回ります。

    累計700万台までは残り547,381台です。52週平均なら約8週後の12月20日集計、発売81週で到達し、Switchの97週、PS5の252週を上回る普及速度となります。一方、直近4週平均では2027年4月までかかる計算です。年内到達に必要な残り9週の平均は約60,820台で、11月以降に販売がどこまで戻るかが到達時期を左右します。
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
    Switch2の10月販売は4週間で92,266台と確定しました。9月の119,161台から22.6%減、前年10月の358,399台から74.3%減です。これまで最も少なかった今年6月の100,166台も下回り、発売以来初めて月間10万台を割りました。9月、前年10月とも4週間の集計なので、週数の違いによる減少ではありません。

    10月は4週すべて3万台未満で、月後半は2万台前半に落ち着きました。有力ソフトの発売が続いても本体販売の加速にはつながらず、モデルやセットを待つ動きが販売を抑えた可能性があります。11月12日の「選べるソフトセット発売」は、ソフト同梱で最大4,980円お得な構成となるため、発売前の11月8日集計までは先送りの要因として残ると見ています。

    ゼルダ記念モデルの発売分は11月1日集計から入ります。10月は発売前の購入待ちを含む月だったため、この低い販売水準を11月全体へそのまま延ばすことはせず、発売後にどこまで取り戻すかを確認したいところです。
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
    Switchの10月販売は23,283台で確定しました。前年10月の96,080台に対しては75.8%減となり、前月9月の31,161台と比べても25.3%少ない水準です。これまで最低だった今年6月の25,319台を2,036台下回り、本データの全期間で月間販売の最低値を更新しました。比較した各月はいずれも4週間です。

    初週は7,704台でしたが、中盤から5,000台前後へ下がり、最終週の小幅な反発でも月間の落ち込みは埋まりませんでした。前月比で伸びたPS5やXbox Series X|Sとは異なり、Switchは前年比・前月比とも大幅な減少が続いた月となっています。
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
    PS5の10月販売は51,354台で確定し、9月の32,831台から56.4%増加しました。前年10月の64,732台には20.7%届きませんが、最終週の反発により前月からの回復が進みました。10月の主要4機種の販売に占めるPS5の比率は30.5%で、9月の17.8%から大きく上昇しています。

    今回の回復では、ソフト発売に加えて未開封新品の買取相場にも注目したいところです。[買取Xの価格履歴](https://kaitorix.app/dp/4948872417419)では、日本語専用DE（CFI-2200B01）の最高買取額が9月29日の50,600円から10月29日の54,300円へ3,700円上昇しました。10月30日確認時点の[買取ルデヤ](https://kaitori-rudeya.com/search/index/4948872417419/)も53,800円で、希望小売価格55,000円に近い水準です。ポイント還元などの購入条件次第では、未開封のまま売却するための購入が増えやすい価格帯と考えられます。

    買取Xの日別最高額を月曜から日曜までの週平均にして本レポートの国内週販と照合すると、5月4日～10月25日の25週では相関係数が0.67、9～10月の8週では0.94となりました。前週の買取価格水準と翌週の販売台数水準にも0.65（24組）の正の相関があります。

    相場上昇の背景としては、9月末以降の[脱獄対応の拡大](https://github.com/ntfargo/Relapse-Exploit)や、10月の[表示言語変更ツールの改善](https://github.com/owendswang/ps5-syslang/releases)により、安価な日本語専用機の旧バージョン搭載在庫を求める海外需要が強まった可能性があります。[日本で購入して海外で使用したという投稿](https://www.reddit.com/r/PS5_Jailbreak/comments/1xcf9ii/can_i_buy_this_in_japan_for_play_with_magic_and/)も見られますが、これは匿名の利用報告であり、買取店の販売先や輸出台数まで確認できたものではありません。

    11月19日発売の「PS5DE日本語版ミッドナイトブラック」を待つ動きがあっても、買取価格が高水準を保つ間は、購入・売却を目的とした需要が週販を支える可能性があります。相場と販売の連動が続くなら、11月前半もしばらくは足元の高い販売水準を維持する余地があります。高水準の持続を期待する材料はありますが、今後の販売台数の予測精度を検証したものではなく、新作需要や供給量とあわせて回復の持続性を見極めたいところです。

    仮に国内向けの安価な本体が海外や改造用途へ流れ、国内のソフト購入やサービス利用につながらない販売が増えているのであれば、SIEにとっても不本意な状況と考えられます。本体ソフトウェアの脆弱性修正や新規出荷分の対策強化、販売条件の見直しなどが行われる可能性もあります。具体的な追加対策を確認できたわけではありませんが、その内容によっては買取相場と週販の関係が変わるため、現在の高水準をそのまま先へ延ばす見通しには注意が必要です。
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
    Xbox Series X|Sの10月販売は1,712台で確定しました。9月の918台から86.5%増えた一方、前年10月の2,253台からは24.0%減です。前月比では改善しましたが、前年の販売規模には届きませんでした。

    初週の612台に続き、最終週も581台を販売したことが月間の増加を支えています。中盤の2週は290台、229台にとどまっており、月を通じて一貫して伸びたというより、月初と月末に販売が集中した形です。
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
    10月25日時点の累計はPS5が7,788,197台、Switch2が6,452,619台で、差は1,335,578台です。今週の差の縮小は5,784台にとどまり、前週の11,187台からほぼ半減しました。PS5の販売増加により、Switch2が差を詰める速度は鈍っています。

    52週平均の差は週63,809台で、これが続く場合の逆転は約21週後の2027年3月です。直近4週平均の差は週10,228台まで縮まり、この条件では約131週後の2029年4月となります。短期平均の差は前週の14,399台からさらに小さくなっており、直近の動きを使った試算は大きく後ろへ動きました。

    いずれも平均差を長期間固定した機械的な比較です。今後のモデル発売や年末商戦によって両機種の販売ペースが変わるため、特定の逆転時期を確定的に示すものではありません。
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
    発売73週時点のSwitch2累計は6,452,619台で、3週連続の歴代3位です。2位の3DSは6,515,416台となり、差は前週の37,956台から62,797台へ広がりました。首位DSは7,340,735台で、Switch2を888,116台上回っています。

    次の74週で3DSを上回るには、次週に107,000台以上が必要です。今週の約4.9倍で、本体モデルの発売による上積みがあっても、2位復帰の条件は高くなっています。またDSは74週で7,569,546台まで伸びるため、首位との差を縮めるにはさらに大きな販売が求められます。

    同じ73週のGBAは5,782,736台、Switchは4,719,324台です。Switch2はそれぞれ約67万台、約173万台上回り、前世代機より早い普及は保っていますが、上位2機種との差は拡大が続いています。
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
    2026年第4四半期は4週累計で168,615台となりました。前年同期の最初の4週521,538台を67.7%、2024年の299,648台を43.7%下回っています。今週は市場全体が増加しましたが、四半期の週平均は約42,154台で、出足の弱さを大きく変えるまでには至っていません。

    2024年第4四半期の1,345,463台に並ぶには、残る9週で1,176,848台、週平均約130,761台が必要です。今期最初の4週平均の約3.1倍に当たります。前年の第4四半期は2,308,689台、直前の2026年第3四半期は617,823台であり、今期がどこまで持ち直すかは、11月以降の販売拡大の大きさにかかっています。
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
    2026年の主要4機種の販売は10月25日時点で合計3,771,141台です。前年同時期の4,427,869台を14.8%下回り、差は656,728台となりました。一方、2024年同時期の3,636,066台は3.7%上回っています。表の全機種合計はPS4の275台を含む3,771,416台です。

    前年比の内訳はSwitch2が200,531台増、Switchが634,765台減、PS5が212,674台減、Xbox Series X|Sが9,820台減です。Switch2の増加で補えているのは旧Switchの減少の約3割にとどまり、世代交代後の市場全体は前年より縮小しています。2024年通年の全機種販売4,695,363台までは、残り923,947台の差があります。
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
    2026年のメーカー別シェアは10月25日時点で任天堂が86.5%、ソニーが13.0%、マイクロソフトが0.5%です。前週の86.8%、12.7%、0.5%に対し、ソニーの比率が上がりました。任天堂はやや低下したものの、2025年通年の85.3%、2024年の66.2%より高い比率を維持しています。

    今週のPS5の週間シェアは37.0%で、前週の28.4%から上昇しました。今回は週間と年初来の両方でソニーが比率を上げており、本体販売の反発が構成比にも表れています。

    主要4機種について、今年の実績へ残る9週の52週平均を加えた年末シェアを試算すると、任天堂が約86.7%、ソニーが約12.8%、マイクロソフトが約0.5%です。任天堂中心の構成は続くと見ていますが、PS5が今週の高い販売を継続する場合は、ソニーの比率がこの試算を上回る可能性があります。
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
