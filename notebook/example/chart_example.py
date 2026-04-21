import marimo

__generated_with = "0.23.1"
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
    return (base_df,)


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
    mo.vstack([units_begin_date, units_end_date])
    return units_begin_date, units_end_date


@app.cell
def _(base_df, g, units_begin_date, units_end_date):
    current_df = g.date_filter(base_df, begin=units_begin_date.value, end=units_end_date.value)
    cudh_style = g.chart_units_by_date_hw(current_df)
    cudh_style              
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## chart_weekly_ranking
    """)
    return


@app.cell
def _(date, mo):
    # UI要素の追加｡日付でbeginとend
    ranking_begin_date = mo.ui.date(start=date(2001,1,1), value=date(2017,3,1), label="Ranking Begin")
    ranking_end_date = mo.ui.date(start=date(2001,1,1), value=date(2026,4,1), label="Ranking End")
    ranking_num = mo.ui.number(start=1, stop=20, value=10, label="ランキング数")
    mo.vstack([ranking_begin_date, ranking_end_date, ranking_num])
    return ranking_begin_date, ranking_end_date, ranking_num


@app.cell
def _(g, ranking_begin_date, ranking_end_date, ranking_num):
    cwr_df = g.chart_weekly_ranking(rank_n=ranking_num.value, begin=ranking_begin_date.value, end=ranking_end_date.value)
    g.style(cwr_df, highlight=True)

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## chart_monthly_ranking
    """)
    return


@app.cell
def _(g, ranking_begin_date, ranking_end_date, ranking_num):
    cmr_df = g.chart_monthly_ranking(rank_n=ranking_num.value, 
        begin=ranking_begin_date.value, end=ranking_end_date.value)
    g.style_sales(cmr_df, columns=['月間販売台数'], bars=['月間販売台数'])
    return (cmr_df,)


@app.cell
def _(cmr_df, g):
    # Auto styling
    g.style(cmr_df, bar=True)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## chart_yearly_ranking
    """)
    return


@app.cell
def _(g, ranking_num):
    cyr_df = g.chart_yearly_ranking(rank_n=ranking_num.value)
    g.style(cyr_df, gradient=True)

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
    cdw_df = g.chart_delta_week_ranking(delta_week_num.value)
    cdw_df10 = cdw_df.head(10)
    g.style(cdw_df10, bar=True)
    return


if __name__ == "__main__":
    app.run()
