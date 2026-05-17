# /// script
# [tool.marimo.display]
# theme = "system"
# ///

import marimo

__generated_with = "0.23.6"
app = marimo.App(width="medium")

with app.setup:
    # 標準ライブラリ
    from datetime import date, datetime

    import marimo as mo
    import altair as alt

    # サードパーティライブラリ
    import polars as pl

    # import polars.selectors as cs
    # プロジェクト内モジュール
    import gamedata as g


@app.cell
def _():
    df_all = g.load_hard_sales()
    return (df_all,)


@app.cell
def _(df_all):
    _cmplist = [("PS5", "PS4"), ("PS5", "PS3")]

    pase_df = g.sales_pase_diffs_long(df_all, cmplist=_cmplist)
    pase_df
    return


@app.cell
def _():
    _cmplist = [("PS5", "PS4"), ("PS5", "PS3"), ("NS2", "NSW")]
    _chart = g.chart_line_pase_diffs(cmplist=_cmplist)
    _mo_chart = mo.ui.altair_chart(_chart)
    mo.vstack([_mo_chart], justify="start")
    return


@app.cell
def _(df_all):
    _cmplist = [("NSW", "PS4"), ("NS2", "PS5")]

    difflib_df = g.cumsum_diffs_long(df_all, cmplist=_cmplist)
    difflib_df
    return


@app.cell
def _():
    from tomlkit.parser import CTRL_CHAR_LIMIT
    _cmplist = [("NSW", "PS4"), ("NS2", "PS5")]
    _chart = g.chart_line_cumsum_diffs(cmplist=_cmplist)
    mo_chart = mo.ui.altair_chart(_chart)
    mo.vstack([mo_chart], justify="start")
    return


@app.cell
def _():
    _chart = g.chart_bar_sales_by_hard_year(hwy=[("NSW", 2017), ("NSW", 2020), ("NS2", 2025)], mode="month")
    _mo_chart = mo.ui.altair_chart(_chart)
    mo.vstack([_mo_chart], justify="start")
    return


@app.cell
def _():
    _chart = g.chart_bar_sales_by_hard_year(hwy=[("PS4", 2020), ("PS5", 2025)] , mode="q")
    _mo_chart = mo.ui.altair_chart(_chart)
    mo.vstack([_mo_chart], justify="start")
    return


@app.cell
def _(df_all):
    dx = g.delta_yearly_sales(df_all)
    dx
    return


@app.cell
def _():
    return


@app.cell
def _():
    _chart = g.chart_bar_yearly_delta(hw=["PS3", "PS4", "PS5"])
    _mo_chart = mo.ui.altair_chart(_chart)
    mo.vstack([_mo_chart], justify="start")
    return


@app.cell
def _():
    _chart = g.chart_bar_month_year(5, begin_year=2016, end_year=2026, stacked=False)
    _mo_chart = mo.ui.altair_chart(_chart)
    mo.vstack([_mo_chart], justify="start")
    return


@app.cell
def _(df_all):

    mdf = g.maker_long(df_all, begin_year=2025, end_year=2026)
    mdf
    return (mdf,)


@app.cell
def _(mdf):

    # maker_listを逆向きにする｡
    maker_list = g.get_maker(mdf)[::-1]
    maker_color = g.get_maker_colors(maker_list)

    base = alt.Chart(mdf).encode(
        theta=alt.Theta(field="yearly_pct", type="quantitative").stack(True),
        color=alt.Color(field="maker_name", type="nominal", title="メーカー",
                        scale=alt.Scale(domain=maker_list, range=maker_color)),
                        column=alt.Row("year:O", 
                                    header=alt.Header(labelAngle=0, 
                                                    labelAlign="left", labelFontSize=14, title=None))
        ).properties(width=140, height=150)
    pie = base.mark_arc(outerRadius=110)
    text = base.mark_text(radius=130, size=12).encode(
        text=alt.Text("yearly_ratio:Q", format=".1%"),
    )
    _chart = (pie + text).properties(width=150, height=180)
    _mo_chart = mo.ui.altair_chart(_chart)
    mo.vstack([_mo_chart], justify="start")

    return


@app.cell
def _():
    _c = g.chart_pie_yearly_share_by_maker(begin_year=2024, end_year=2026)
    mo.ui.altair_chart(_c)
    return


@app.cell
def _():
    _a = [1, 2, 3, 4, 5]
    _a.reverse()
    _a
    return


if __name__ == "__main__":
    app.run()
