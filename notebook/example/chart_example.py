import marimo

__generated_with = "0.23.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    # 標準ライブラリ
    from datetime import datetime, timedelta, date
    # サードパーティライブラリ
    import polars as pl
    # import polars.selectors as cs
    # プロジェクト内モジュール
    import gamedata as g

    return date, g


@app.cell
def _(g):
    base_df = g.load_hard_sales()
    hw_list = g.get_hw(base_df)
    return base_df, hw_list


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # chart_hard.py
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## chart_units_by_date_hw
    """)
    return


@app.cell
def _(date, mo):
    # UI要素の追加｡日付でbeginとend
    units_begin_date = mo.ui.date(start=date(2001,1,1), value=date(2026,3,1), label="Begin Date")
    units_end_date = mo.ui.date(start=date(2001,1,1), value=date(2026,4,1), label="End Date")
    mo.hstack([units_begin_date, units_end_date], justify="start")
    return units_begin_date, units_end_date


@app.cell
def _(base_df, g, units_begin_date, units_end_date):
    g.chart_units_by_date_hw(base_df, begin=units_begin_date.value, end=units_end_date.value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## chart_weekly_ranking
    """)
    return


@app.cell
def _(base_df, date, g, hw_list, mo):
    # UI要素の追加｡日付でbeginとend
    ranking_begin_date = mo.ui.date(start=date(2001,1,1), value=date(2017,3,1), label="Ranking Begin")
    ranking_end_date = mo.ui.date(start=date(2001,1,1), value=date(2026,4,1), label="Ranking End")
    ranking_num = mo.ui.number(start=-10, stop=20, value=10, label="ランキング数")
    hws = mo.ui.multiselect(options=hw_list, value=["NS2"], label="ハード")
    maker_mode = mo.ui.checkbox(label="メーカーモード")
    makers = mo.ui.multiselect(options=g.get_maker(base_df), value=["Nintendo"], label="メーカー")
    mo.vstack([ranking_begin_date, ranking_end_date, ranking_num, hws, maker_mode, makers], justify="start")
    return (
        hws,
        maker_mode,
        makers,
        ranking_begin_date,
        ranking_end_date,
        ranking_num,
    )


@app.cell
def _(hws, maker_mode, makers):
    ranking_hw = hws.value
    ranking_maker = makers.value
    if maker_mode.value:
        ranking_hw = None
    else:
        ranking_maker = None

    return ranking_hw, ranking_maker


@app.cell
def _(
    g,
    ranking_begin_date,
    ranking_end_date,
    ranking_hw,
    ranking_maker,
    ranking_num,
):
    _cwr_df = g.chart_weekly_ranking(rank_n=ranking_num.value, 
        begin=ranking_begin_date.value,
        end=ranking_end_date.value,
        hw=ranking_hw,
        maker=ranking_maker,)
    g.style(_cwr_df, highlight=True)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## chart_monthly_ranking
    """)
    return


@app.cell
def _(
    g,
    ranking_begin_date,
    ranking_end_date,
    ranking_hw,
    ranking_maker,
    ranking_num,
):
    _cmr_df = g.chart_monthly_ranking(
        rank_n=ranking_num.value, 
        begin=ranking_begin_date.value,
        end=ranking_end_date.value,
        hw=ranking_hw,
        maker=ranking_maker,
    )
    g.style(_cmr_df, bar=True)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## chart_yearly_ranking
    """)
    return


@app.cell
def _(
    g,
    ranking_begin_date,
    ranking_end_date,
    ranking_hw,
    ranking_maker,
    ranking_num,
):
    _cyr_df = g.chart_yearly_ranking(
        rank_n=ranking_num.value,
        begin=ranking_begin_date.value,
        end=ranking_end_date.value,
        hw=ranking_hw,
        maker=ranking_maker,
    )
    g.style(_cyr_df, gradient=True)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## chart_delta_week_ranking
    """)
    return


@app.cell
def _(mo):
    delta_week_num = mo.ui.number(start=1, stop=600, value=20, label="ランキング対象経過週")
    delta_week_num
    return (delta_week_num,)


@app.cell
def _(delta_week_num, g):
    _cdw_df = g.chart_delta_week_ranking(delta_week_num.value)
    _cdw_df10 = _cdw_df.head(10)
    g.style(_cdw_df10, bar=True)
    return


if __name__ == "__main__":
    app.run()
