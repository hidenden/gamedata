import marimo

__generated_with = "0.23.3"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo

    # 標準ライブラリ
    from datetime import date, datetime, timedelta

    # サードパーティライブラリ
    import polars as pl
    # import polars.selectors as cs

    # プロジェクト内モジュール
    import gamedata as g

    g.set_dispfunc(func=None)


@app.cell
def ui_target_year_01():
    target_year = mo.ui.number(start=2005, step=1, value=2026, label="対象年")
    range_year = mo.ui.number(start=1, step=1, value=5, label="対象年の範囲")
    hw_list = g.get_hw_all()
    hw_select = mo.ui.dropdown(options=hw_list, value="NSW")
    return hw_select, range_year, target_year


@app.cell
def range_year(range_year, target_year):
    begin_year = date(target_year.value - range_year.value + 1, 1, 1)
    end_year = date(target_year.value, 12, 31)
    return begin_year, end_year


@app.cell
def hw_select(hw_select, range_year, target_year):
    mo.hstack([hw_select, target_year, range_year], justify="start")
    return


@app.cell
def begin_year(begin_year, end_year, hw_select):
    _chart = g.chart_bar_hwsales_by_year(
        hw=hw_select.value,
        begin=begin_year,
        end=end_year,
        mode="month",
    )
    mo.vstack([_chart], justify="start")
    return


@app.cell(hide_code=True)
def md_cell_01():
    mo.md(r"""
    ## 各月のメーカーごとの販売実績
    """)
    return


@app.cell
def ui_month_02():
    month = mo.ui.number(start=1, stop=12, step=1, value=12, label="対象月")
    begin_year2 = mo.ui.number(start=2001, step=1, value=2021, label="開始年")
    end_year2 = mo.ui.number(start=2005, step=1, value=2026, label="終了年")
    stacked = mo.ui.switch(label="積み上げ", value=True)

    return begin_year2, end_year2, month, stacked


@app.cell
def begin_year2(begin_year2, end_year2, month, stacked):
    _chart = g.chart_bar_month_year(
        month=month.value,
        begin_year=begin_year2.value,
        end_year=end_year2.value,
        stacked=stacked.value,
    )

    mo.vstack([begin_year2, end_year2, stacked, month, _chart], justify="start")

    return


if __name__ == "__main__":
    app.run()
