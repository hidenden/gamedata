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
    hw_select = g.HwSelect(hw_list=["GBA", "DS", "3DS", "PSP", "Vita", "NSW", "NS2"])
    hw_widget = hw_select.widget
    annotation_level = mo.ui.number(
        start=1, stop=50, value=20, label="アノテーションレベル"
    )
    mode_select = mo.ui.dropdown(
        options=["week", "month", "quarter", "year"], value="week"
    )
    return annotation_level, hw_select, hw_widget, mode_select


@app.cell
def _(date, mo):
    begin_date = mo.ui.date(start=date(2001, 1, 1), value=date(2011, 12, 1))
    end_date = mo.ui.date(start=date(2001, 1, 1), value=date(2012, 11, 30))
    mo.hstack(items=[begin_date, end_date], justify="start")
    return begin_date, end_date


@app.cell
def _(
    begin_date,
    end_date,
    annotation_level,
    g,
    hw_select,
    hw_widget,
    mo,
    mode_select,
):
    hw_widget
    _chart = g.chart_line_sales(
        hw=hw_select.value,
        mode=mode_select.value,
        begin=begin_date.value,
        end=end_date.value,
        annotation_level=annotation_level.value,
        multi_line=True,
    )
    mo.vstack([hw_select, annotation_level, mode_select, _chart], justify="start")
    return


if __name__ == "__main__":
    app.run()
