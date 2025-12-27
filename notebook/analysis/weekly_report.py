import marimo

__generated_with = "0.18.4"
app = marimo.App()


@app.cell
def _():
    ### 週販レポート
    # 標準ライブラリ
    import os
    import sys
    from pathlib import Path
    from datetime import datetime, timedelta

    # サードパーティライブラリ
    import pandas as pd
    from pandas import Timedelta
    import matplotlib.pyplot as plt
    from matplotlib.ticker import ScalarFormatter
    from IPython.display import Markdown, display

    # プロジェクト内モジュール
    from gamedata import hard_sales as hs
    from gamedata import plot_hard as ph
    from gamedata import hard_info as hi
    from gamedata import hard_event as he
    from gamedata import chart_hard as ch
    from gamedata import util as gu

    # レポート日付
    from report_config import get_config

    config = get_config()
    report_date = config["date"]
    report_event_mask = he.EventMasks(hard=1.5, price=3, sale=2, soft=1.5, event=1)

    def show_title(d:datetime) -> None:
        last_updated_str = d.strftime("%Y-%m-%d")
        display(Markdown(f"# 国内ゲームハード週販レポート ({last_updated_str})"))

    show_title(report_date)
    return ch, datetime, gu, he, hs, ph, report_date, report_event_mask


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    * ハードウェアの販売データはファミ通の調査結果を基にしています。
    * 一部のデータは処理上の都合により、週次値に調整しています。
    * 2025年の集計期間はあと1週間分ありますが､次回の更新は年明け､2026年1月7日以降になります｡
    * [過去の週販レポート](index.html)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 直近4週間のハード売り上げ／累計推移

    Switch2の販売台数は先々週の20万台を超える22万台でした｡
    これはロンチ週に続くSwitch2歴代2位の販売台数です｡
    任天堂の連続大量出荷は継続しています｡このまま年末年始も突き進むのでしょうか｡

    Switchはやや回復して3.8万台｡先週よりマシですが先々週は5万台ですから､
    世代交代による落ち込みが顕著です｡

    PS5は先週とほぼ変わらずの1万9千台｡
    クリスマスセール中のはずなのですが､セール効果は400台分だったようです｡
    """)
    return


@app.cell
def _(ch, gu, hs, report_date):
    df1 = hs.load_hard_sales()
    (out1, style1) = ch.chart_units_by_date_hw(df1, begin=gu.weeks_before(report_date, 3), end=report_date)
    style1
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 週販推移
    """)
    return


@app.cell
def _(gu, ph, report_date, report_event_mask):
    (fig, df) = ph.plot_sales(begin=gu.report_begin(report_date), end=report_date, event_mask=report_event_mask)
    fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 週販推移(拡大）

    Switch2の20万台超の出荷が3週間継続中です｡
    これが年末年始､あと2週間継続する可能性は高そうです｡

    年末年始明けでSwitchは本格的に減少するでしょう｡
    今までのSwitch週販最低記録は 2025/7/25の11,766台です｡2月あたりには4桁が見えてきそうです｡

    PS5は19日からのクリスマスセールの効果は出ていません｡予想通りではあります｡
    今年1年間､セールを何度も何度も何度も何度も繰り返し､ついには日本語版値下げという特大技まで繰り広げましたが､
    流れを変える力には足りていません｡
    来年出る(はず)のGTA6までの約1年間をどうやって日本市場でPlayStationのプレゼンスを維持するのか､
    難しい舵取りが続きそうです｡
    """)
    return


@app.cell
def _(gu, ph, report_date, report_event_mask):
    fig_1, df_1 = ph.plot_sales(begin=gu.report_begin(report_date), end=report_date, ymax=230000, event_mask=report_event_mask)
    fig_1
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 月間販売推移
    """)
    return


@app.cell
def _(gu, ph, report_date):
    fig_2, df_2 = ph.plot_monthly_bar_by_hard(hw=['NS2', 'PS5', 'NSW', 'XSX'], 
                        begin=gu.report_begin(report_date), end=report_date, stacked=False)
    fig_2
    return (df_2,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    12月のSwitch2が60万台を突破｡残り1週間で合計80万台に到達するでしょう｡
    その場合､任天堂は10月､11月､12月の2025Q3に166万台を出荷したことになります｡
    """)
    return


@app.cell
def _(df_2):
    df_3 = df_2.style.format({'NS2': '{:,.0f}', 'NSW': '{:,.0f}', 'PS5': '{:,.0f}', 'XSX': '{:,.0f}'})
    df_3
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Nintendo Switchの月間販売台数： 2023,2024年との比較

    Switch2の大量出荷によりSwitch→Switch2への切り替えスピードが早まっています｡
    12月の前年比は33%程度になりそうです｡
    """)
    return


@app.cell
def _(gu, ph, report_date):
    fig_3, df_4 = ph.plot_monthly_bar_by_year(hw='NSW', ymax=480000, begin=gu.years_ago(report_date), end=report_date)
    fig_3
    return (df_4,)


@app.cell
def _(df_4, report_date):
    this_year = report_date.year
    df_5 = df_4.drop(columns=[2023])
    df_5.loc[:, 'YoY'] = df_5.loc[:, this_year] / df_5.loc[:, this_year - 1]
    style_df5 = df_5.style.format({'YoY': '{:.1%}'})
    style_df5
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### PlayStation 5の月間販売台数： 2023, 2024年との比較

    PS5にクリスマスは訪れませんでした｡
    セールの効果なく､12月は8万程度になりそうです｡9万台は無理なので11月を下回ります｡
    昨年同月比はギリギリ50%いくかどうか｡
    """)
    return


@app.cell
def _(gu, ph, report_date):
    fig_4, df_6 = ph.plot_monthly_bar_by_year(hw='PS5', ymax=480000, begin=gu.years_ago(report_date), end=report_date)
    fig_4
    return (df_6,)


@app.cell
def _(df_6, report_date):
    this_year_1 = report_date.year
    df_7 = df_6.drop(columns=[2023])
    df_7.loc[:, 'YoY'] = df_7.loc[:, this_year_1] / df_7.loc[:, this_year_1 - 1]
    style_df7 = df_7.style.format({'YoY': '{:.1%}'})
    style_df7
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 累計販売推移
    """)
    return


@app.cell
def _(datetime, he, ph):
    long_range_event_mask = he.EventMasks(hard=0.5, soft=0, event=0, price=0, sale=0)
    fig_5, df_8 = ph.plot_cumulative_sales(hw=['PS4', 'NS2', 'PS5', 'NSW', 'XSX'], 
                    begin=datetime(2017, 3, 1), event_mask=long_range_event_mask)
    fig_5
    return


@app.cell
def _(ph, report_event_mask):
    fig_6, df_9 = ph.plot_cumulative_sales_by_delta(hw=['PS4', 'NS2', 'PS5', 'NSW', 'XSX'], end=40, event_mask=report_event_mask)
    fig_6
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Switch2/PS5差分

    Switch2の累計は358万台に到達｡次週には370万を超えるでしょう｡これはPS5の国内累計727万台の半分､363万台を超えます｡
    Switch2は半年強でPS5累計の半分まで迫りました｡
    """)
    return


@app.cell
def _(ph):
    (fig4, d4) = ph.plot_cumsum_diffs(cmplist = [('NS2', 'PS5'), ('NSW', 'PS4')], xgrid=10)
    fig4
    return


@app.cell
def _():
    # d4.head(35)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### PS5/PS4差分

    PS4とPS5の推移差は日本版の値下げによっても縮まっていませんが､
    これ以上差が広がるのを防ぐ効果はあったようです｡
    ただ､年末年始を過ぎた後にどうなるかは分かりません｡
    """)
    return


@app.cell
def _(he, ph):
    middle_range_event_mask = he.EventMasks(hard=1.5, soft=0, event=1, price=1, sale=0)
    fig_7, df_10 = ph.plot_cumulative_sales_by_delta(hw=['PS4', 'PS5'], end=280, event_mask=middle_range_event_mask)
    fig_7
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Switch2初動状況
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Switch2は今週も歴代初動1位の座をキープしています｡20万台出荷が続くうちは盤石の首位でしょう｡
    """)
    return


@app.cell
def _(ph, report_event_mask):
    fig_8, df_11 = ph.plot_cumulative_sales_by_delta(hw=['GBA', 'NS2', 'DS', 'PS2', 'Wii', '3DS', 'NSW', 'PS5'], 
                        mode='week', xgrid=2, end=39, event_mask=report_event_mask)
    fig_8
    return (df_11,)


@app.cell
def _(df_11):
    df12 = df_11.iloc[df_11.index == 28]
    # df12をunpivotして、列名を"ハード"、"販売数"にする
    df12_unpivot = df12.unstack().reset_index()
    df12_unpivot.columns = ['ハード', '週数', '販売数']
    df12_unpivot.sort_values(by='販売数', ascending=False, inplace=True)
    df12_unpivot.set_index('ハード', inplace=True)
    style_df12 = df12_unpivot.style.format({'販売数': '{:,.0f}'})
    style_df12
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 年単位の状況

    2025年の販売台数が596万台に達しました｡2025年は620万台で着地しそうです｡
    2022年の626万台にはギリ届かないものの､2018,2019年を超える､景気の良い水準になりました｡

    2017年､最初の年のSwitchは10ヶ月で340万台売りましたが､
    Switch2は7ヶ月で約380万台販売できそうです｡
    """)
    return


@app.cell
def _(gu, ph, report_date):
    fig_9, df_12 = ph.plot_yearly_bar_by_hard(hw=['PS4', 'PS5', 'NSW', 'NS2', '3DS', 'WiiU', 'Vita', 'XSX', 'XBOne'],
             begin=gu.years_ago(report_date, 10), end=report_date, stacked=True)
    fig_9
    return


@app.cell
def _():
    # df["sum"] = df.sum(axis=1)
    # df
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### PS5の年間販売台数推移
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    集計期間はあと1週残っていますが､PS5については2025年は90万台に届かないと言い切っていいでしょう｡
    100万台はもちろん､2021年の水準にも届かず､今年のPS5は急速な減少に見舞われた年でした｡
    """)
    return


@app.cell
def _(gu, ph, report_date):
    fig_10, df_13 = ph.plot_yearly_bar_by_hard(hw=['PS5'], begin=gu.years_ago(report_date, 10), end=report_date, stacked=True)
    fig_10
    return (df_13,)


@app.cell
def _(df_13):
    df_13
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### PS4, PS3の落ち込み方

    PS3,PS4の末期の落ち込み方を見るとわかりますが､100万台を下回るのは非常に危険です｡
    ここから先は急激な下り坂です｡
    """)
    return


@app.cell
def _(datetime, ph):
    fig_11, df_14 = ph.plot_yearly_bar_by_hard(hw=['PS4'], begin=datetime(2005, 1, 1), stacked=True, ticklabelsize=8)
    fig_11
    return


@app.cell
def _(datetime, ph):
    fig_12, df_15 = ph.plot_yearly_bar_by_hard(hw=['PS3'], begin=datetime(2005, 1, 1), stacked=True, ticklabelsize=8)
    fig_12
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ただ､この下り坂には明確な理由がありまして､
    PS3もPS4も急激な落ち込みは「次世代機」が見えているからこそ発生しています｡
    PS4が100万台を切った年はPS5の発売年ですし､
    PS3が100万台を切った年は翌年2月にPS4の発売を控えていました｡

    一方､PS5は次世代機が2年以上先の状況で100万台を切った初めてのケースです｡
    この場合に翌年がどうなるのか､従来の推移を単純に当て嵌めることは出来ません｡
    我々は未知の領域にいます｡
    """)
    return


@app.cell
def _(datetime, ph):
    fig_13, df_16 = ph.plot_yearly_bar_by_hard(hw=['PS3', 'PS4', 'PS5'], begin=datetime(2005, 1, 1), stacked=True, ticklabelsize=8)
    fig_13
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 年単位のメーカーシェア

    ここまで来たら数字変化しないだろうと思ってたら､任天堂のシェアが85%に達してしまいました｡
    """)
    return


@app.cell
def _(gu, ph, report_date):
    fig_14, df_17 = ph.plot_maker_share_pie(begin_year=gu.years_ago(report_date, 2).year, end_year=report_date.year)
    fig_14
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    2020年の87.8%に次ぐ高さです｡
    """)
    return


@app.cell
def _(ph):
    fig_15, df_18 = ph.plot_maker_share_pie(begin_year=2020, end_year=2020)
    fig_15
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
