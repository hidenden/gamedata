import marimo

__generated_with = "0.23.3"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    # 標準ライブラリ
    from datetime import datetime, timedelta, date

    # サードパーティライブラリ
    import polars as pl
    # import polars.selectors as cs

    # プロジェクト内モジュール
    import gamedata as g
    g.set_dispfunc(func=None)
    return g, mo


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 週販ランキング
    """)
    return


@app.cell
def _(g, mo):
    hwselect = g.HwSelect(force_any=True)
    hw_widget = hwselect.widget
    rank_num = mo.ui.number(start=5, stop=30, step=1, value=10, label="ランキング表示数")
    mo.vstack([hwselect,rank_num], justify="start")
    return hw_widget, hwselect, rank_num


@app.cell
def _(g, hw_widget, hwselect, rank_num):
    hw_widget
    best_week_ranking = g.style(g.chart_weekly_ranking(rank_n=rank_num.value, hw=hwselect.value), bar=True)
    worst_week_ranking = g.style(g.chart_weekly_ranking(rank_n=-rank_num.value, hw=hwselect.value ), bar=True)
    return best_week_ranking, worst_week_ranking


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### ベストランキング
    """)
    return


@app.cell
def _(best_week_ranking):
    best_week_ranking
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### ワーストランキング
    """)
    return


@app.cell
def _(worst_week_ranking):
    worst_week_ranking
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 月間ランキング
    """)
    return


@app.cell
def _(g, hw_widget, hwselect, rank_num):
    hw_widget
    best_month_ranking = g.style(g.chart_monthly_ranking(rank_n=rank_num.value, hw=hwselect.value), bar=True)
    worst_month_ranking = g.style(g.chart_monthly_ranking(rank_n=-rank_num.value, hw=hwselect.value ), bar=True)
    return best_month_ranking, worst_month_ranking


@app.cell
def _(best_month_ranking):
    best_month_ranking
    return


@app.cell
def _(worst_month_ranking):
    worst_month_ranking
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 年間ランキング

    ### 年間機種別ランキング
    """)
    return


@app.cell
def _(g, hw_widget, hwselect, rank_num):
    hw_widget
    best_year_ranking = g.style(g.chart_yearly_ranking(rank_n=rank_num.value, hw=hwselect.value), bar=True)
    worst_year_ranking = g.style(g.chart_yearly_ranking(rank_n=-rank_num.value, hw=hwselect.value ), bar=True)
    return best_year_ranking, worst_year_ranking


@app.cell
def _(best_year_ranking):
    best_year_ranking
    return


@app.cell
def _(worst_year_ranking):
    worst_year_ranking
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 年間メーカーランキング
    """)
    return


@app.cell
def _(g):
    maker_select = g.MakerSelect(force_any=True)
    maker_widget = maker_select.widget
    maker_select
    return maker_select, maker_widget


@app.cell
def _(g, maker_select, maker_widget, rank_num):
    maker_widget
    best_maker_ranking = g.style(g.chart_yearly_ranking(rank_n=rank_num.value, maker=maker_select.value), bar=True)
    worst_maker_ranking = g.style(g.chart_yearly_ranking(rank_n=-rank_num.value, maker=maker_select.value ), bar=True)
    return best_maker_ranking, worst_maker_ranking


@app.cell
def _(best_maker_ranking):
    best_maker_ranking
    return


@app.cell
def _(worst_maker_ranking):
    worst_maker_ranking
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 経過週累計ランキング
    """)
    return


@app.cell
def _(mo):
    weeks = mo.ui.number(start=1, stop=500, step=1, value=40, label="経過週累計ランキングの累計週")
    return (weeks,)


@app.cell
def _(g, mo, weeks):
    _delta_ranking = g.style(g.chart_delta_week_ranking(weeks.value), bar=True)
    mo.vstack([weeks, _delta_ranking], justify="start")
    return


if __name__ == "__main__":
    app.run()
