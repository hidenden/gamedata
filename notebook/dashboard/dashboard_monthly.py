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

    return date, g, mo


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


if __name__ == "__main__":
    app.run()
