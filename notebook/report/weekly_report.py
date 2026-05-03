# /// script
# [tool.marimo.display]
# theme = "system"
# ///

import marimo

__generated_with = "0.23.4"
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
    g.set_dispfunc(func=None)
    return alt, datetime, g, mo, pl


@app.cell
def _(mo):
    is_publish = False
    _args = mo.cli_args()
    if _args.get("publish"):
        is_publish = True

    is_publish
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
        mode = "LAB MODE" if not is_publish else ""
        return mo.md(f"# 国内ゲームハード週販レポート ({last_updated_str}) {mode} {is_publish}")

    df_all = g.load_hard_sales()
    return df_all, report_date, show_title


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
    g.chart_units_by_date_hw(df_all, begin=g.weeks_before(report_date, 3), end=report_date)
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
def _(alt, df_all, g, mo, report_date):
    _begin = g.report_begin(report_date)
    _end = report_date
    _weekly_df = g.date_filter(df_all, begin=_begin, end=_end)
    _current_hw = g.get_hw(_weekly_df)
    _hw_colors = g.get_hard_colors(_current_hw)
    _base = alt.Chart(_weekly_df).encode(
            x='report_date:T',
            y='units:Q',
            color=alt.Color('hw:N', scale=alt.Scale(domain=_current_hw, range=_hw_colors)),
        )

    weekly_chart = mo.ui.altair_chart(
        ((_base.mark_point() + _base.mark_line())).properties(
            width=800,
            height=400,
            title='販売台数(週単位)'
        )
    )
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
    _zoom_chart = mo.ui.altair_chart(
        ((_zoom_base.mark_point() + _zoom_base.mark_line())).properties(
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
def _(datetime, df_all, g):
    ps5_offset_df = g.sales_with_offset_long(df_all,
      hw_periods=[
          {'hw': 'PS5', 'begin': datetime(2023,3,1)},
          {'hw': 'PS5', 'begin': datetime(2024,3,1)},
          {'hw': 'PS5', 'begin': datetime(2025,3,1)},
          {'hw': 'PS5', 'begin': datetime(2026,3,1)},
          ],
      end = 20)

    ps5_offset_df
    return (ps5_offset_df,)


@app.cell
def _(alt, mo, ps5_offset_df):
    _base = alt.Chart(ps5_offset_df).encode(
            x='offset_week:T',
            y='units:Q',
            color='label:N',
        )

    _ps5_offset_chart = mo.ui.altair_chart(
        ((_base.mark_point() + _base.mark_line())).properties(
            width=800,
            height=400,
            title='過去週販比較'
        )
    )
    _ps5_offset_chart
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Nintendo Switch2: 2026年と, Switch 2018,2019年 3月1日以降
    """)
    return


@app.cell
def _():
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
    mo.vstack(items=[_chart, _df.pivot(index="month", on="year", values="monthly_units")])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 累計販売推移
    """)
    return


@app.cell
def _(alt, datetime, df_all, g, mo):
    from tomlkit.parser import CTRL_CHAR_LIMIT
    _df = g.cumulative_sales_long(df_all, begin=datetime(2017,3,3),hw=["NSW", "PS5", "NS2", "XSX"])

    _base = alt.Chart(_df).encode(
            x='report_date:T',
            y='sum_units:Q',
            color='hw:N',
        )
    _chart = mo.ui.altair_chart(
        ((_base.mark_line())).properties(
            width=800,
            height=400,
            title='累計販売推移'
        )
    )
    _chart
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Switch2: 47週目の状況
    """)
    return


@app.cell
def _(alt, df_all, g, mo):
    _df = g.cumulative_sales_by_delta_long(
        df_all, 
        hw=["NS2", "NSW", "PS5", "3DS", "DS", "GBA", "PS2", "Wii"], 
        mode="week",
        begin = 0, end=60)

    _base = alt.Chart(_df).encode(
            x='delta_week:Q',
            y='sum_units:Q',
            color='hw:N',
        )
    _chart = mo.ui.altair_chart(
        ((_base.mark_line())).properties(
            width=800,
            height=400,
            title='累計販売推移(発売週からの経過週数で比較)'
        )
    )
    mo.vstack(items=[_chart, _df.pivot(index="delta_week", on="hw", values="sum_units")])
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
    mo.vstack(items=[_chart, g.style(_df2)])
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
