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
    11月1日の主要4機種の販売は合計91,704台となり、前週の43,297台から111.8%増加しました。Switch2は68,733台で215.4%増、PS5は16,226台で1.4%増、Switchは5,853台で19.1%増、Xbox Series X|Sは892台で53.5%増です。4機種すべてが増加したのは8月30日以来で、市場の増加48,407台の約97%をSwitch2が占めました。

    [今週のファミ通集計](https://www.famitsu.com/article/202611/93151)では、「Nintendo Switch Sports Resort」が23,466本で首位を保ち、Switch2向けの新作も上位に加わりました。
    Switch2の急反発は10月29日の「ゼルダの伝説40周年記念モデル」発売の効果が強く出ています｡新ハードや改訂版の発売はハードセールス向上の鉄板であることを示してます｡
    PS5も前回の急増後に水準を保ち、今回はSwitch2の回復とPS5の堅調さが重なった週となりました。

    次回11月8日集計には「ゼルダの伝説 時のオカリナ」と「Steller Blade Complete Edition」が入ります。
    次々回11月15日集計には11月12日のSwitch2の「選べるソフトセット発売」が含まれます。記念モデルの初動に続き、
    ソフトやセットを待っていた需要がSwitch2の販売にどこまで影響を与えるかが11月前半の焦点です。
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
        ymax=75000,
        padding_end=1,
        value_label=True,
    )
    weekly_big_chart = mo.ui.altair_chart(_chart)
    mo.vstack(items=[weekly_big_chart], justify="start")

    return


@app.cell(hide_code=True)
def md_weekly_chart():
    mo.md(r"""
    Switch2は5週続いた減少が止まり、6週ぶりに増加しました。今回の水準は5月24日以来、23週ぶりです。直近4週平均は23,066台から33,700台へ上昇し、13週平均の29,901台も上回りました。ただし、4週平均には発売週の大きな販売が入ったため、次の数週でその上積みがどの程度残るかを確認する必要があります。

    PS5は2週続けて1.6万台を超え、3月29日以来31週ぶりの高水準となりました。4週平均は12,838台から13,703台へ伸び、13週平均の10,316台を上回っています。一方、Switch2との差は前週の5,784台から52,507台へ広がりました。順位は変わらず、Switch2が首位、PS5が2位、Switchが3位、Xbox Series X|Sが4位です。

    Switchは3週ぶりに5,000台を超えましたが、4週平均は5,821台から5,358台へ下がっています。月初の高い週が平均から外れたためで、今回の反発だけで基調の改善まで示したとは言えません。Xbox Series X|Sも2週連続で増え、4月5日以来30週ぶりの販売となり、4週平均は498台まで戻りました。
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
        y2=675000,
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
    PS5の2026年累計は11月1日時点で506,213台となり、年内50万台を超えました。前年同時期の710,198台を28.7%、2024年同時期の1,154,865台を56.2%下回りますが、前年割れ幅は先週の30.3%から縮小しています。PS3の2014年同時期402,878台より25.6%多い一方、PS4の2018年同時期1,313,719台には61.5%届きません。

    52週平均は12,985台で、52倍した年換算値は約675,000台です。今年の実績に残る8週分を同じ平均で加える年末試算は約610,000台となり、2025年通年の879,204台を30.6%下回ります。11月19日の「GTAVI」発売に合わせた購入が増えれば上振れする余地はありますが、足元の回復で年間の前年割れを埋めるには、さらに大きな販売が必要です。

    発売からの累計は7,804,423台で、800万台まで残り195,577台です。52週平均を続ける条件では約16週後の2027年2月となります。年内到達には残り8週で平均約24,447台が必要で、今週の販売水準を維持するだけでは届かない計算です。
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
        y2=733000,
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
    Switchの2026年販売は11月1日までに599,835台となりました。前年同時期の1,255,455台から52.2%減、2024年同時期の2,461,588台から75.6%減です。52週平均は16,630台で、今年の実績に残る8週分を加える年末試算は約733,000台となります。直近4週平均の5,358台より高い過去1年の平均を使っているため、年末商戦での持ち直しを含む目安と捉えたいところです。

    [任天堂の2027年3月期第2四半期決算説明資料](https://www.nintendo.co.jp/ir/pdf/2026/261105_3.pdf#page=11)では、世界通期計画は200万台、上期実績は127万台で、下期に必要な販売は73万台です。前年下期の世界販売で10～12月が占めた比率70.8%と、今上期の日本比率26.0%で配分すると、国内10～12月の参考目標は約13.4万台となります。国内四半期目標が公表されているわけではなく、地域配分と季節性を固定した当レポートの概算です。

    本レポートの第4四半期実売は11月1日までの5週で29,136台となり、この参考値の約22%です。残る8週では週平均約13,200台、今週の約2.2倍が必要です。一方、前年の残り8週は平均約33,100台だったため、その約4割の販売でも参考値には届きます。セルインである任天堂の販売数量とファミ通の実売は流通在庫などにより一致しませんが、足元の5,000台から年末需要がどこまで戻るかを測る目安にはなります。

    累計は37,015,996台です。3,800万台まではなお984,004台を残しており、目前の年末商戦で重視したいのは大台への接近より、旧世代機としての販売をどの規模で維持できるかです。
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
        y2=3348000,
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
    Switch2の2026年累計は11月1日までに2,737,285台となり、前年同時期の2,551,846台を7.3%上回りました。ただし前年超過分は先週の200,531台から185,439台へ減っています。今年の販売期間は前年より長く、今週の反発だけで年初来の伸びの鈍化が解消したとは言えません。52週平均76,337台を残る8週に当てはめる年末試算は約3,348,000台で、2025年通年の3,784,067台を11.5%下回ります。

    Switch2では、[決算資料](https://www.nintendo.co.jp/ir/pdf/2026/261105_3.pdf#page=15)の通期1,650万台から上期649万台を引いた1,001万台が、世界で下期に積み上げる数量です。前年下期の950万台に対して5.4%多く、通期計画が前年の1,986万台を下回っていても、下期には前年以上の販売が求められます。前節の配分式で、前年の10～12月比率を73.8%、今上期の日本比率を21.9%に置き換えた国内の参考規模は約161.6万台です。地域構成が変わらないという仮定による配分値で、任天堂が示した国内目標ではありません。

    これに対して、国内実売は第4四半期の最初の5週で160,999台、参考規模の約10%です。残る8週には平均約18.2万台が必要で、今回の68,733台の約2.6倍、前年の同じ残り8週の平均約15.4万台も約18%上回ります。セルインと実売の差を含む参考比較ではあるものの、記念モデル発売による反発の後にも、年末商戦で相当の上積みが必要な水準です。国内実売の前年の季節配分で計算し直すと約129万台まで下がるため、この参考値を唯一の達成基準とせず、配分の仮定による幅も見ておきたいところです。

    累計700万台までは残り478,648台となりました。52週平均なら約7週後の12月20日集計、発売81週で到達する計算で、Switchの97週、PS5の252週より早い普及となります。年内到達に必要な残り8週の平均は59,831台で、今週はそれを上回りました。節目の達成は見えやすくなりましたが、会社計画から配分した参考規模に近づくには、さらに高い販売が継続する必要があります。
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
    Switch2の11月は最初の1週で68,733台となりました。前年11月の初週83,825台には18.0%届きませんが、10月の週平均23,067台に対しては約3倍です。先月の4週合計92,266台に対しても、1週で約4分の3まで販売が戻りました。

    11月は5週集計となるため、今週と同じ台数が続く場合の単純な月末目安は343,665台です。前年11月の500,414台に並ぶには、残る4週で平均約107,900台が必要で、月初の反発だけでは前年規模の回復を示したことにはなりません。

    記念モデルを待っていた層の購入が進んだ一方、ソフト同梱セットを待つ動きはなお残っていると考えられます。発売週の集中を5週全体へ引き延ばすより、その後の通常販売とセット発売による上積みがつながるかを見る月になりそうです。
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
    Switchの11月初週は5,853台となりました。前年11月の初週26,708台から78.1%減で、10月の週平均5,821台とほぼ同じ水準です。先週より増えてはいますが、月をまたいで販売の勢いが大きく変わった状況ではありません。

    今月は5週集計で、現状のペースを単純に延ばすと29,265台となります。10月の23,283台より月間台数は増えますが、主に集計週数が1週多いことによる差です。前年11月の138,018台との隔たりは大きく、月末に向けて通常週を超える需要がどの程度加わるかが課題です。
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
    PS5の11月初週は16,226台となり、前年11月初週の7,537台を115.3%上回りました。10月の週平均12,839台に対しても26.4%多い出足です。5週を今週と同じペースで進む単純計算では月間81,130台で、前年11月の93,852台には13.6%届きません。内訳ではDEが15,988台で全体の98.5%を占め、Proは前週の277台から149台へ減少しました。増加は引き続きDEに偏っており、Proへの買い替えだけでは今回の販売を説明できません。

    [買取Xの未開封新品価格履歴](https://kaitorix.app/dp/4948872417419)と週販を再集計すると、日本語専用DE（CFI-2200B01）の日別最高額を月曜～日曜で平均した価格は、前週の約52,829円から約53,129円へ0.6%上昇し、販売台数も1.4%増えました。先週述べた高水準の持続は、今回の集計では確認できた形です。ただし日次相場は10月29日の54,300円をピークに下がり、11月1日は51,500円、11月5日確認時点の最高額も51,500円です。週平均の上昇と、直近の相場下落を分けて見る必要があります。

    相関係数は、9月以降の期間を同じ起点で比較すると、先週までの8週の0.94から、今週を加えた9週では0.96となりました。履歴の取得範囲に合わせて全期間の起点を5月11日にそろえると、先週まで24週の0.71に対し、今週まで25週は0.79です。価格を1週先行させた水準同士の相関も0.76となり、先週の約0.65より高くなりました。ただし短期間の観測であり、価格は日本語専用DE単品、台数はPS5全機種合計との比較です。相関の上昇が将来の予測精度の改善を意味するわけではありません。

    前回指摘した[脱獄対応の拡大](https://github.com/ntfargo/Relapse-Exploit)や[表示言語変更ツールの改善](https://github.com/owendswang/ps5-syslang/releases)により、安価な日本語専用機の旧バージョン搭載在庫を求める海外需要が強まった可能性は引き続きあります。ポイント還元を利用した売却目的の購入も考えられますが、輸出量や購入目的を直接観測した結果ではなく、ソフト需要や供給量の影響も取り除けていません。11月19日の「PS5DE日本語版ミッドナイトブラック」を待つ動きがあっても販売は維持されましたが、直近の買取価格が下がるなら、売却を前提とした購入の採算は先週より厳しくなります。

    国内向けの安価な本体がソフト購入やサービス利用につながらない用途へ流れているのであれば、SIEにとって望ましい販売増とは限りません。[公式の最新システム更新](https://www.playstation.com/ja-jp/support/hardware/ps5/system-software-info/)でもセキュリティ修正は告知されていますが、今回の価格下落がその効果だと示す情報は確認できていません。追加のソフトウェア対策や販売条件の見直しの可能性も含め、相場の変化には注意が必要です。過去の正の相関だけを根拠に、11月中も1.6万台が続くと決めつけず、次週以降は下落後の相場に週販がどう反応するかを確かめたいところです。
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
    Xbox Series X|Sの11月初週は892台で、前年11月初週の309台を188.7%上回りました。10月の週平均428台からも約2.1倍に増えています。今週は通常のSeries Xが616台で、前週からの増加304台がシリーズ全体の増加311台のほとんどを占めました。

    5週ある11月を同じペースで進む場合、月間では4,460台となり、前年11月の1,891台を上回る計算です。ただし週ごとの振れが大きい機種であり、月初の販売がそのまま続くとみなすことはできません。Series Xを中心とする増加が複数週続くかを見て、月間の回復を判断したいところです。
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
    11月1日時点の累計はPS5が7,804,423台、Switch2が6,521,352台で、差は1,283,071台です。今週の縮小幅は52,507台となり、前週の5,784台から大きく広がりました。差はなお約128万台ありますが、Switch2が追い上げる速度は今回の反発で上がっています。

    52週平均の販売差は週63,352台で、この差を固定した試算では約21週後の2027年3月末に逆転します。直近4週平均の差は前週の10,228台から19,997台へ拡大し、こちらを使う試算は約65週後の2028年1月末となりました。先週の約131週後から大きく前進していますが、短期平均は1週の急増で変わりやすい指標です。年末商戦での両機種の販売を加えながら、見通しの振れを確認する必要があります。
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
        y2=7300000,
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
    発売74週時点のSwitch2累計は6,521,352台で、4週連続の歴代3位です。2位3DSの6,559,618台との差は、前週の62,797台から38,266台へ縮まりました。一方、首位DSは7,569,546台となり、差は1,048,194台へ拡大して100万台を超えています。

    次の75週では、3DSは「3DSLL」の発売週に当たり、235,974台を販売しています。この累計を上回って2位へ戻るには、Switch2は次週274,241台以上、今週の約4倍が必要です。直近の差は縮まったものの、比較対象側の大きな発売週が控えているため、順位の回復は容易ではありません。

    同じ74週のGBAは5,834,383台、Switchは4,766,770台です。Switch2はそれぞれ686,969台、1,754,582台上回っており、前世代のSwitchに対する普及の先行は維持しています。
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
    2026年第4四半期は5週累計で260,319台となりました。前年同期の最初の5週639,935台から59.3%減、2024年の376,372台から30.8%減です。今週の反発で四半期の週平均は約52,064台へ上がりましたが、前年までの同じ進捗には届いていません。

    2024年第4四半期の1,345,463台に並ぶには、残り8週で1,085,144台、週平均135,643台が必要です。最初の5週平均の約2.6倍に当たります。年末に販売が集中する季節性はあるものの、記念モデルの発売週だけで四半期全体の不足を埋めたとは言えず、11月後半から12月にかけて市場の拡大が続くかが重要になります。
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
    2026年の主要4機種の販売は11月1日時点で合計3,862,845台です。前年同時期の4,546,248台を15.0%下回り、差は先週の656,728台から683,403台へ広がりました。2024年同時期の3,712,737台は4.0%上回っています。表の全機種合計はPS4の275台を含む3,863,120台です。

    前年との差はSwitch2が185,439台増、Switchが655,620台減、PS5が203,985台減、Xbox Series X|Sが9,237台減です。Switch2の増加で補えているのは旧Switchの減少の約28%で、世代交代後の市場規模はなお前年より小さいままです。2024年通年の全機種販売4,695,363台までは残り832,243台となりました。
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
    2026年のメーカー別シェアは11月1日時点で任天堂86.4%、ソニー13.1%、マイクロソフト0.5%です。前週の86.5%、13.0%、0.5%から小幅な変化にとどまり、任天堂の比率は2025年通年の85.3%、2024年の66.2%より高い水準を保っています。

    週間では任天堂の比率が61.7%から81.3%へ戻り、ソニーは37.0%から17.7%へ下がりました。ただし、今週の任天堂比率は年初来の比率より低く、ソニーは逆に年初来を上回っています。そのため、Switch2が大きく回復した週でも、年間累計では任天堂の比率がわずかに下がり、ソニーが上がる結果となりました。

    主要4機種について、今年の実績に残る8週の52週平均を加えた年末シェアは、任天堂約86.6%、ソニー約12.9%、マイクロソフト約0.5%です。任天堂の年末販売が決算計画から配分した参考規模へ近づく場合は、この平均ベースの試算より任天堂の比率が高まる余地があります。
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
