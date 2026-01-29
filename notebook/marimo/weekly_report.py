import marimo

__generated_with = "0.19.6"
app = marimo.App()


@app.cell
def _(mo):
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
    import japanize_matplotlib
    from matplotlib.ticker import ScalarFormatter
    from IPython.display import Markdown, display

    # プロジェクト内モジュール
    from gamedata import hard_sales as hs
    from gamedata import plot_bar as ph
    from gamedata import hard_info as hi
    from gamedata import hard_event as he
    from gamedata import chart_hard as ch
    from gamedata import util as gu

    # レポート日付
    from report_config import get_config

    config = get_config()
    report_date = config["date"]
    report_event_mask = he.EventMasks(hard=1.5, price=3, sale=2, soft=1.5, event=1)

    mo.md(f"# 国内ゲームハード週販レポート ({report_date.strftime('%Y-%m-%d')})")
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
    (fig_weekly, _) = ph.plot_sales(begin=gu.report_begin(report_date), end=report_date, event_mask=report_event_mask)
    fig_weekly
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
    fig_weekly_big, _ = ph.plot_sales(begin=gu.report_begin(report_date), end=report_date, ymax=230000, event_mask=report_event_mask)
    fig_weekly_big
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 月間販売推移
    """)
    return


@app.cell
def _(gu, ph, report_date):
    (fig_monthly, df_monthly) = ph.plot_monthly_bar_by_hard(hw=['NS2', 'PS5', 'NSW', 'XSX'], 
                        begin=gu.report_begin(report_date), end=report_date, stacked=False)
    fig_monthly
    return (df_monthly,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    12月のSwitch2が60万台を突破｡残り1週間で合計80万台に到達するでしょう｡
    その場合､任天堂は10月､11月､12月の2025Q3に166万台を出荷したことになります｡
    """)
    return


@app.cell
def _(df_monthly):
    df_monthly_styled = df_monthly.style.format({'NS2': '{:,.0f}', 'NSW': '{:,.0f}', 'PS5': '{:,.0f}', 'XSX': '{:,.0f}'})
    df_monthly_styled
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
    switch_monthly_bar_by_year, df_switch_monthly_bar_by_year = ph.plot_monthly_bar_by_year(hw='NSW', ymax=480000, begin=gu.years_ago(report_date), end=report_date)
    switch_monthly_bar_by_year
    return (df_switch_monthly_bar_by_year,)


@app.cell
def _(df_switch_monthly_bar_by_year, report_date):
    this_year = report_date.year
    df_switch_2024_2025 = df_switch_monthly_bar_by_year.drop(columns=[2023])
    df_switch_2024_2025.loc[:, 'YoY'] = df_switch_2024_2025.loc[:, this_year] / df_switch_2024_2025.loc[:, this_year - 1]
    style_df_switch_2024_2025 = df_switch_2024_2025.style.format({'YoY': '{:.1%}'})
    style_df_switch_2024_2025
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
    fig_ps5_monthly_bar_by_year, df_ps5_monthly_bar_by_year = ph.plot_monthly_bar_by_year(hw='PS5', ymax=480000, begin=gu.years_ago(report_date), end=report_date)
    fig_ps5_monthly_bar_by_year
    return (df_ps5_monthly_bar_by_year,)


@app.cell
def _(df_ps5_monthly_bar_by_year, report_date):
    this_year_1 = report_date.year
    df_ps5_2024_2025 = df_ps5_monthly_bar_by_year.drop(columns=[2023])
    df_ps5_2024_2025.loc[:, 'YoY'] = df_ps5_2024_2025.loc[:, this_year_1] / df_ps5_2024_2025.loc[:, this_year_1 - 1]
    style_df_ps5_2024_2025 = df_ps5_2024_2025.style.format({'YoY': '{:.1%}'})
    style_df_ps5_2024_2025
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
    fig_cumulative_sales, _ = ph.plot_cumulative_sales(hw=['PS4', 'NS2', 'PS5', 'NSW', 'XSX'], 
                    begin=datetime(2017, 3, 1), event_mask=long_range_event_mask)
    fig_cumulative_sales
    return


@app.cell
def _(ph, report_event_mask):
    fig_cumulative_sales_by_delta, _ = ph.plot_cumulative_sales_by_delta(hw=['PS4', 'NS2', 'PS5', 'NSW', 'XSX'], end=40, event_mask=report_event_mask)
    fig_cumulative_sales_by_delta
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
    fig_diff_ps5_ns2, df_diff_ps5_ns2 = ph.plot_cumsum_diffs(cmplist = [('NS2', 'PS5'), ('NSW', 'PS4')], xgrid=10)
    fig_diff_ps5_ns2
    return (df_diff_ps5_ns2,)


@app.cell
def _(df_diff_ps5_ns2, mo):
    mo.ui.table(df_diff_ps5_ns2.head(30))
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
    fig_diff_ps4_ps5, _ = ph.plot_cumulative_sales_by_delta(hw=['PS4', 'PS5'], end=280, event_mask=middle_range_event_mask)
    fig_diff_ps4_ps5
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
    fig_ns2_initial, df_ns2_initial = ph.plot_cumulative_sales_by_delta(hw=['GBA', 'NS2', 'DS', 'PS2', 'Wii', '3DS', 'NSW', 'PS5'], 
                        mode='week', xgrid=2, end=39, event_mask=report_event_mask)
    fig_ns2_initial
    return (df_ns2_initial,)


@app.cell
def _(df_ns2_initial):
    df_ns2_initial_h = df_ns2_initial.iloc[df_ns2_initial.index == 28]
    # df12をunpivotして、列名を"ハード"、"販売数"にする
    df_ns2_initial_h_unpivot = df_ns2_initial_h.unstack().reset_index()
    df_ns2_initial_h_unpivot.columns = ['ハード', '週数', '販売数']
    df_ns2_initial_h_unpivot.sort_values(by='販売数', ascending=False, inplace=True)
    df_ns2_initial_h_unpivot.set_index('ハード', inplace=True)
    style_df_ns2_initial_h = df_ns2_initial_h_unpivot.style.format({'販売数': '{:,.0f}'})
    style_df_ns2_initial_h
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
    fig_yearly_bar, df_yearly_bar = ph.plot_yearly_bar_by_hard(hw=['PS4', 'PS5', 'NSW', 'NS2', '3DS', 'WiiU', 'Vita', 'XSX', 'XBOne'],
             begin=gu.years_ago(report_date, 10), end=report_date, stacked=True)
    fig_yearly_bar
    return (df_yearly_bar,)


@app.cell
def _(df_yearly_bar):
    df_yearly_bar["sum"] = df_yearly_bar.sum(axis=1)
    df_yearly_bar
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
    fig_yearly_ps5, df_yearly_ps5 = ph.plot_yearly_bar_by_hard(hw=['PS5'], begin=gu.years_ago(report_date, 10), end=report_date, stacked=True)
    fig_yearly_ps5
    return (df_yearly_ps5,)


@app.cell
def _(df_yearly_ps5):
    df_yearly_ps5
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
    fig_yearly_ps4, _ = ph.plot_yearly_bar_by_hard(hw=['PS4'], begin=datetime(2005, 1, 1), stacked=True, ticklabelsize=8)
    fig_yearly_ps4
    return


@app.cell
def _(datetime, ph):
    fig_yearly_ps3, _ = ph.plot_yearly_bar_by_hard(hw=['PS3'], begin=datetime(2005, 1, 1), stacked=True, ticklabelsize=8)
    fig_yearly_ps3
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
    fig_yearly_ps, _ = ph.plot_yearly_bar_by_hard(hw=['PS3', 'PS4', 'PS5'], begin=datetime(2005, 1, 1), stacked=True, ticklabelsize=8)
    fig_yearly_ps
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
    fig_share, df_share = ph.plot_maker_share_pie(begin_year=gu.years_ago(report_date, 2).year, end_year=report_date.year)
    fig_share
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    2020年の87.8%に次ぐ高さです｡
    """)
    return


@app.cell
def _(ph):
    fig_share_2020, _ = ph.plot_maker_share_pie(begin_year=2020, end_year=2020)
    fig_share_2020
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
