import marimo

__generated_with = "0.23.6"
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
def _():
    end = mo.ui.number(label="累積グラフ週数", value=52, start=10, stop=1000, step=5)
    annotation_level = mo.ui.number(
        start=1, stop=50, value=20, label="アノテーションレベル"
    )
    # run_button = mo.ui.run_button(label="更新", kind="success")
    return annotation_level, end


@app.cell
def _():
    hwselect = g.HwSelect(default_list=["NS2", "PS5", "NSW"])
    hw_widget = hwselect.widget
    return hw_widget, hwselect


@app.cell
def _(annotation_level, end, hwselect):
    mo.vstack([hwselect, annotation_level, end])
    return


@app.cell
def _(annotation_level, end, hw_widget, hwselect):
    # mo.stop(not run_button.value)
    hw_widget
    _chart1 = g.chart_line_cumulative(
        hw=hwselect.value,
        annotation_level=annotation_level.value,
        multi_line=True,
    )
    _chart2 = g.chart_line_cumulative_delta(
        hw=hwselect.value,
        end=end.value,
        annotation_level=annotation_level.value,
        multi_line=True,
    )
    mo.vstack([_chart1, _chart2])
    return


if __name__ == "__main__":
    app.run()
