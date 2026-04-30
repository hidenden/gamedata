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
    return date, datetime, g, mo


@app.cell
def _(g, mo):
    target_year = mo.ui.number(start=2005, step=1, value=2026, label="対象年")
    range_year = mo.ui.number(start=1, step=1, value=5, label="対象年の範囲")
    hw_list = g.get_hw_all()
    hw_select = mo.ui.dropdown(options=hw_list, value="NSW")
    return hw_select, range_year, target_year


@app.cell
def _(date, range_year, target_year):
    begin_year= date(target_year.value - range_year.value + 1, 1, 1)
    end_year = date(target_year.value, 12, 31)
    return begin_year, end_year


@app.cell
def _(hw_select, mo, range_year, target_year):
    mo.hstack([hw_select, target_year, range_year], justify="start")
    return


@app.cell
def _(begin_year, end_year, g, hw_select, mo):
    (_fig, _df) = g.plot_monthly_bar_by_year(hw=hw_select.value, begin=begin_year, end=end_year)
    mo.vstack([_fig, _df], justify="start")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 各月のメーカーごとの販売実績
    """)
    return


@app.cell
def _(mo):
    month = mo.ui.number(start=1, stop=12, step=1, value=12, label="対象月")
    begin_year2 = mo.ui.number(start=2001, step=1, value=2021, label="開始年")
    end_year2 = mo.ui.number(start=2005, step=1, value=2026, label="終了年")
    stacked = mo.ui.checkbox(label="積み上げ", value=True)

    return begin_year2, end_year2, month, stacked


@app.cell
def _(begin_year2, datetime, end_year2, g, mo, month, stacked):
    _begin = datetime(begin_year2.value, 1, 1)
    _end = datetime(end_year2.value, 12, 31)
    (_fig, _df) = g.plot_yearly_bar_by_month(month=month.value, stacked=stacked.value,
                                            ticklabelsize=8,
                                            begin=_begin, end=_end)

    mo.vstack([begin_year2, end_year2, stacked, month, _fig, _df], justify="start")

    return


if __name__ == "__main__":
    app.run()
