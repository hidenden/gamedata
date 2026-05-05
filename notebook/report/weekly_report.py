# /// script
# [tool.marimo.display]
# theme = "system"
# ///

import marimo

__generated_with = "0.23.3"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import altair as alt
    # 標準ライブラリ
    from datetime import datetime, timedelta, date

    # サードパーティライブラリ
    import polars as pl
    # import polars.selectors as cs

    # プロジェクト内モジュール
    import gamedata as g

    return alt, datetime, g, mo, pl


@app.cell
def _(g, mo):
    _args = mo.cli_args()
    is_publish = True if _args.get("publish") else False
    if not is_publish:
        g.disable_styler()
    return (is_publish,)


@app.cell
def _(datetime, g, is_publish, mo):
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
def _(mo):
    mo.md(r"""
    * ハードウェアの販売データはファミ通の調査結果を基にしています。
    * 一部のデータは処理上の都合により、週次値に調整しています｡
    * [過去の週販レポート](../index.html)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 直近4週間のハード売り上げ／累計推移
    """)
    return


@app.cell
def _(df_all, g, report_date):
    g.units_by_date_hw_table(df_all, begin=g.weeks_before(report_date, 3), end=report_date)
    return


@app.cell(hide_code=True)
def _(mo):
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
def _(mo):
    mo.md(r"""
    ## 週販推移
    """)
    return


@app.cell
def _(g, mo, report_date, report_event_mask):
    _begin = g.report_begin(report_date)
    _end = report_date
    _chart = g.chart_sales(begin=_begin, end=_end, event_mask=report_event_mask)
    weekly_chart = mo.ui.altair_chart(_chart)
    weekly_chart
    return (weekly_chart,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 週販推移(拡大)
    """)
    return


@app.cell
def _(alt, mo, weekly_chart):
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
def _(mo):
    mo.md(r"""
    ## 過去年の週販比較
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### PlayStation 5:2023年から2026年の3月1日以降
    """)
    return


@app.cell
def _(datetime, g, mo):
    _offset_chart = g.chart_sales_with_offset(
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
def _(mo):
    mo.md(r"""
    ### Nintendo Switch2: 2026年と, Switch 2018,2019年 3月1日以降
    """)
    return


@app.cell
def _(datetime, g, mo):
    _offset_chart = g.chart_sales_with_offset(
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
def _(mo):
    mo.md(r"""
    ## 月間販売推移
    """)
    return


@app.cell
def _(alt, datetime, df_all, g, mo, report_date):
    _msl_df = g.monthly_sales_long(df_all, begin=datetime(2025,3,1), end=report_date,
        hw=["NS2", "NSW", "PS5"])
    _base = alt.Chart(_msl_df).encode(
            x='year_month:T',
            y='monthly_units:Q',
            color='hw:N',
        )
    _msl_chart = mo.ui.altair_chart(
        _base.mark_bar().properties(
            width=800,
            height=400,
            title='月間販売推移'
        )
    )
    mo.vstack(items=[_msl_chart, _msl_df.pivot(index="year_month", on="hw", values="monthly_units")])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Nintendo Switch:月間販売台数
    """)
    return


@app.cell
def _(alt, df_all, g, mo, report_date):
    _begin = g.years_ago(report_date)
    _df = g.monthly_sales_long(df_all, begin=_begin, end=report_date,   hw=["NSW"])
    _chart = mo.ui.altair_chart(
        alt.Chart(_df).mark_bar().encode(
                x=alt.X('month:O', title='月'),
                y=alt.Y('monthly_units:Q', title='販売台数'),
                color=alt.Color('year:N', title='年'),
                xOffset='year:N',
            ).properties(
                width=800,
                height=400,
                title='月間販売推移'
        )
    )
    mo.vstack(items=[_chart, g.style_df(_df.pivot(index="month", on="year", values="monthly_units"))])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 累計販売推移
    """)
    return


@app.cell
def _(datetime, g, pl):
    begin_nsw = datetime(2017,3,3)
    event_df = (g.load_hard_event()
                            .filter(pl.col("report_date") >= begin_nsw)
                            .filter(pl.col("priority") < 2))
    event_df
    return


@app.cell
def _(datetime, g, mo, report_date, report_event_mask):
    _chart = g.chart_cumulative_sales(hw=["NSW", "NS2", "PS5", "XSX"],
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
def _(mo):
    mo.md(r"""
    ### Switch2: 47週目の状況
    """)
    return


@app.cell
def _(g, mo, report_event_mask):
    _chart = g.chart_cumulative_sales_by_delta(
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
def _(mo):
    mo.md(r"""
    ## 年単位の状況
    """)
    return


@app.cell
def _(alt, df_all, g, mo, report_date):
    _df = g.yearly_sales_long(df_all, 
        hw=['3DS', 'WiiU','NS2', 'NSW',  'PS4', 'PS5', 'Vita', 'XSX', 'XBOne'],
        begin=g.years_ago(report_date, 10),
        end = report_date,)

    _base = alt.Chart(_df).encode(
            x='year:O',
            y='yearly_units:Q',
            color='hw:N',
        )
    _chart = mo.ui.altair_chart(
        _base.mark_bar().properties(
            width=800,
            height=400,
            title='年間販売推移'
        )
    )
    _df2 = _df.pivot(index="year", on="hw", values="yearly_units").fill_null(0)
    mo.vstack(items=[_chart, g.style_df(_df2)])
    return


@app.cell
def _(alt, df_all, g, mo, pl):

    _df = g.maker_long(df_all, begin_year=2016)

    _MAKERS = ['Nintendo', 'SONY', 'Microsoft']
    _COLORS = ['red', 'mediumblue', 'green']

    _chart_df = (
        _df
        .sort(['year', pl.col('maker_name').cast(pl.Enum(_MAKERS))])
        .with_columns(
            ((pl.col('yearly_percentage').cum_sum().over('year') - pl.col('yearly_percentage') / 2) / 100)
            .alias('mid_point'),
            (pl.col('yearly_percentage').round(1).cast(pl.String) + '%')
            .alias('pct_label'),
        )
    )

    _base = alt.Chart(_chart_df).encode(
        y=alt.Y('year:O', sort='descending', title='年'),
        x=alt.X('yearly_units:Q', stack='normalize', title='メーカーシェア'),
        color=alt.Color('maker_name:N',
            sort=_MAKERS,
            scale=alt.Scale(domain=_MAKERS, range=_COLORS),
        ),
        order=alt.Order('mid_point:Q'),
    )

    _bars = _base.mark_bar()
    _text = _base.mark_text(size=12, baseline='middle').encode(
        detail='maker_name:N',
        color=alt.value('white'),
        text=alt.Text('pct_label:N'),
        x=alt.X('mid_point:Q'),
    )

    _chart = mo.ui.altair_chart((_bars + _text).properties(width=800, height=400, title='年間シェア推移'))
    mo.vstack(items=[_chart, _df])
    return


if __name__ == "__main__":
    app.run()
