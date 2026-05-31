# /// script
# [tool.marimo.display]
# theme = "system"
# ///

import marimo

__generated_with = "0.23.5"
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
    hw_dropdown = mo.ui.dropdown(options=g.get_hw_all(), value="NSW", label="HW")
    start_year_number = mo.ui.number(start=2001, stop=2026, value=2001, label="開始年")
    end_year_number = mo.ui.number(start=2001, stop=2026, value=2026, label="終了年")

    mode_dropdown = mo.ui.dropdown(
        options=["week", "month"], value="month", label="集計単位"
    )
    scale_dropdown = mo.ui.dropdown(
        options=["linear", "log", "sqrt"], value="log", label="カラースケールの種類"
    )
    color_dropdown = mo.ui.dropdown(
        options=[
            "viridis", "magma", "inferno", "plasma", "cividis", "turbo"
        ], value="plasma", label="カラースケール"
    )
    grid_checkbox = mo.ui.checkbox(label="グリッド線を表示")

    # UIの値をこのセルで直接参照し、値変更時にチャート生成を再実行させる
    mo.vstack(
        [
            hw_dropdown,
            mo.hstack([start_year_number, end_year_number], justify="start"),
            mode_dropdown,
            scale_dropdown,
            color_dropdown,
            grid_checkbox,
        ],
    )
    return (
        color_dropdown,
        end_year_number,
        grid_checkbox,
        hw_dropdown,
        mode_dropdown,
        scale_dropdown,
        start_year_number,
    )


@app.cell
def _(
    color_dropdown,
    end_year_number,
    grid_checkbox,
    hw_dropdown,
    mode_dropdown,
    scale_dropdown,
    start_year_number,
):
    _chart = g.chart_heatmap(
        hw=hw_dropdown.value,
        begin=date(start_year_number.value, 1, 1),
        end=date(end_year_number.value, 12, 31),
        mode=mode_dropdown.value,
        scale_scheme=color_dropdown.value,
        scale_type=scale_dropdown.value,
        grid=grid_checkbox.value,
    )
    _chart_ui = mo.ui.altair_chart(_chart)
    _chart_ui
    return


if __name__ == "__main__":
    app.run()
