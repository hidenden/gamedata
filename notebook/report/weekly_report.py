# /// script
# [tool.marimo.display]
# theme = "system"
# ///

import marimo

__generated_with = "0.23.5"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    import altair as alt
    # 標準ライブラリ
    from datetime import datetime, timedelta, date

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
    return (is_publish,)


@app.cell
def _(is_publish):
    # レポート日付
    from report_config import get_config

    config = get_config()
    report_date = config["date"]
    report_event_mask = g.EventMasks(hard=1.5, price=3, sale=2, soft=1.5, event=1)

    def show_title(d:datetime) :
        last_updated_str = d.strftime("%Y-%m-%d")
        mode: str = "analyze mode" if not is_publish else ""
        return mo.md(f"# 国内ゲームハード週販レポート ({last_updated_str}) {mode}")

    df_all = g.load_hard_sales()
    return df_all, report_date, report_event_mask, show_title


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
    g.units_by_date_hw_table(df_all, begin=g.weeks_before(report_date, 3), end=report_date)
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
def _(report_date, report_event_mask):
    _begin = g.report_begin(report_date)
    _end = report_date
    _chart = g.chart_line_sales(begin=_begin, end=_end, event_mask=report_event_mask)
    weekly_chart = mo.ui.altair_chart(_chart)
    weekly_chart
    return (weekly_chart,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### 週販推移(拡大)
    """)
    return


@app.cell
def _(weekly_chart):
    _zoom_df = weekly_chart.value
    _zoom_base = alt.Chart(_zoom_df).encode(
            x='report_date:T',
            y='units:Q',
            color='hw:N',
        )
    _zoom_text = _zoom_base.transform_filter(alt.datum.event_name != None).mark_text(
        dy=-10, dx=10, align='center', limit=80).encode(
            text='event_name:N',
        )
    _zoom_chart = mo.ui.altair_chart(
        ((_zoom_base.mark_point() + _zoom_base.mark_line() + _zoom_text)).properties(
            width=800,
            height=400,
            title='販売台数(週単位)[拡大]',
        )
    )
    _zoom_chart
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
          {'hw': 'PS5', 'begin': datetime(2023,3,1)},
          {'hw': 'PS5', 'begin': datetime(2024,3,1)},
          {'hw': 'PS5', 'begin': datetime(2025,3,1)},
          {'hw': 'PS5', 'begin': datetime(2026,3,1)},
          ],
      end = 20)

    _ps5_offset_chart = mo.ui.altair_chart(_offset_chart)
    _ps5_offset_chart
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
          {'hw': 'NSW', 'begin': datetime(2018,3,1)},
          {'hw': 'NSW', 'begin': datetime(2019,3,1)},
          {'hw': 'NS2', 'begin': datetime(2026,3,1)},
          ],
      end = 20)

    _ns2_offset_chart = mo.ui.altair_chart(_offset_chart)
    _ns2_offset_chart
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 月間販売推移
    """)
    return


@app.cell
def _(report_date):
    _bar = g.chart_bar_sales(begin=datetime(2025,3,1), end=report_date, stacked=True)
    bar_chart = mo.ui.altair_chart(_bar)
    return (bar_chart,)


@app.cell
def _(bar_chart):
    mo.vstack(items=[bar_chart, bar_chart.dataframe.pivot(index="year_month", on="hw", values="monthly_units")])
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
    _chart_bar = mo.ui.altair_chart(g.chart_bar_hwsales_by_year(begin=_begin, end=_end, hw="NSW"))
    mo.vstack(items=[_chart_bar, _chart_bar.dataframe.pivot(index="month", on="year", values="monthly_units")])
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 累計販売推移
    """)
    return


@app.cell
def _():
    begin_nsw = datetime(2017,3,3)
    event_df = (g.load_hard_event()
                            .filter(pl.col("report_date") >= begin_nsw)
                            .filter(pl.col("priority") < 2))
    event_df
    return


@app.cell
def _(report_date, report_event_mask):
    _chart = g.chart_line_cumulative(hw=["NSW", "NS2", "PS5", "XSX"],
        begin=datetime(2017,3,1), end=report_date,
        event_mask=report_event_mask)
    chart_cumulative = mo.ui.altair_chart(_chart)
    chart_cumulative
    return (chart_cumulative,)


@app.cell
def _(chart_cumulative):
    chart_cumulative.value
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Switch2: 47週目の状況
    """)
    return


@app.cell
def _(report_event_mask):
    _chart = g.chart_line_cumulative_delta(
        hw=["NS2", "NSW", "PS5", "3DS", "DS", "GBA", "PS2", "Wii"], 
        end=60,
        event_mask=report_event_mask
    )
    cd_chart = mo.ui.altair_chart(_chart)
    cd_chart
    return (cd_chart,)


@app.cell
def _(cd_chart):
    cd_chart.dataframe.pivot(index="delta_week", on="hw", values="sum_units")
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 年単位の状況
    """)
    return


@app.cell
def _(report_date):
    _year_bar = mo.ui.altair_chart(g.chart_bar_sales(
            mode="year", stacked=True,
            begin=g.years_ago(report_date, 10), \
            end = report_date))

    mo.vstack(items=[_year_bar, 
            g.style_df(_year_bar.dataframe.pivot(index="year", on="hw", values="yearly_units"))])
    return


@app.cell
def _():
    _chart = g.chart_hbar_yearly_share_by_maker(2016, 2026)
    share_chart = mo.ui.altair_chart(_chart)

    return (share_chart,)


@app.cell
def _(share_chart):
    mo.vstack(items=[share_chart, 
        g.style_df(share_chart.dataframe.pivot(index="year", on="maker_name", values="yearly_units").sort(by="year", 
        descending=True))])
    return


if __name__ == "__main__":
    app.run()
