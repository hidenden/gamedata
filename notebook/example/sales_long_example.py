# /// script
# [tool.marimo.display]
# theme = "system"
# ///

import marimo

__generated_with = "0.23.6"
app = marimo.App(width="medium")

with app.setup:
    # 標準ライブラリ
    from datetime import date

    import marimo as mo

    # サードパーティライブラリ
    import polars as pl

    # プロジェクト内モジュール
    import gamedata as g


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # hard_sales_long.py
    """)
    return


@app.cell
def _():
    # long形式変換の入力として実データを使う
    df_all: pl.DataFrame = g.load_hard_sales()
    latest_date = g.current_report_date(df_all)
    return df_all, latest_date


@app.cell
def _(latest_date):
    ui_hws = g.HwSelect(default_list=["NSW", "PS5", "NS2"], force_any=True)
    ui_makers = g.MakerSelect(default_list=["任天堂", "ソニー"], force_any=True)
    ui_begin_date = mo.ui.date(label="開始日", value=date(2025, 1, 1))
    ui_end_date = mo.ui.date(label="終了日", value=latest_date)
    ui_mode = mo.ui.dropdown(
        options=["week", "month", "quarter", "year"], value="week", label="集計単位"
    )
    mo.vstack(
        [
            ui_hws,
            ui_makers,
            mo.hstack([ui_begin_date, ui_end_date, ui_mode], justify="start"),
        ]
    )
    return ui_begin_date, ui_end_date, ui_hws, ui_makers, ui_mode


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## sales_long
    """)
    return


@app.cell
def _(df_all: pl.DataFrame, ui_begin_date, ui_end_date, ui_hws):
    # 週次販売台数をlong形式で取得する
    g.sales_long(
        df_all,
        hw=ui_hws.value,
        begin=ui_begin_date.value,
        end=ui_end_date.value,
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## monthly_sales_long
    """)
    return


@app.cell
def _(df_all: pl.DataFrame, ui_begin_date, ui_end_date, ui_hws):
    # 月次販売台数をlong形式で取得する
    g.monthly_sales_long(
        df_all,
        hw=ui_hws.value,
        begin=ui_begin_date.value,
        end=ui_end_date.value,
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## quarterly_sales_long
    """)
    return


@app.cell
def _(df_all: pl.DataFrame, ui_begin_date, ui_end_date, ui_hws):
    # 四半期販売台数をlong形式で取得する
    g.quarterly_sales_long(
        df_all,
        hw=ui_hws.value,
        begin=ui_begin_date.value,
        end=ui_end_date.value,
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## yearly_sales_long
    """)
    return


@app.cell
def _(df_all: pl.DataFrame, ui_begin_date, ui_end_date, ui_hws):
    # 年次販売台数をlong形式で取得する
    g.yearly_sales_long(
        df_all,
        hw=ui_hws.value,
        begin=ui_begin_date.value,
        end=ui_end_date.value,
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## cumulative_sales_long
    """)
    return


@app.cell
def _(df_all: pl.DataFrame, ui_begin_date, ui_end_date, ui_hws, ui_mode):
    # カレンダー日付ベースの累計販売台数をlong形式で取得する
    _mode = ui_mode.value if ui_mode.value in ["week", "month", "year"] else "month"
    g.cumulative_sales_long(
        df_all,
        hw=ui_hws.value,
        begin=ui_begin_date.value,
        end=ui_end_date.value,
        mode=_mode,
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## sales_by_delta_long
    """)
    return


@app.cell
def _():
    ui_delta_begin = mo.ui.number(start=0, value=0, label="経過期間 開始")
    ui_delta_end = mo.ui.number(start=1, value=52, label="経過期間 終了")
    mo.hstack([ui_delta_begin, ui_delta_end], justify="start")
    return ui_delta_begin, ui_delta_end


@app.cell
def _(df_all: pl.DataFrame, ui_delta_begin, ui_delta_end, ui_hws, ui_mode):
    # 発売日からの経過期間をインデックスにして販売台数を集計する
    _mode = ui_mode.value if ui_mode.value in ["week", "month", "year"] else "week"
    g.sales_by_delta_long(
        df_all,
        mode=_mode,
        begin=ui_delta_begin.value,
        end=ui_delta_end.value,
        hw=ui_hws.value,
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## cumulative_sales_by_delta_long
    """)
    return


@app.cell
def _(df_all: pl.DataFrame, ui_delta_begin, ui_delta_end, ui_hws, ui_mode):
    # 発売日からの経過期間を揃えた累計販売台数を取得する
    _mode = ui_mode.value if ui_mode.value in ["week", "month", "year"] else "week"
    g.cumulative_sales_by_delta_long(
        df_all,
        mode=_mode,
        begin=ui_delta_begin.value,
        end=ui_delta_end.value,
        hw=ui_hws.value,
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## sales_with_offset_long
    """)
    return


@app.cell
def _(df_all: pl.DataFrame):
    # 任意の開始日からの週数に変換し、異なる期間を比較しやすくする
    hw_periods = [
        {"hw": "NSW", "begin": date(2017, 3, 3), "label": "NSW launch"},
        {"hw": "PS5", "begin": date(2020, 11, 15), "label": "PS5 launch"},
        {"hw": "NS2", "begin": date(2025, 6, 5), "label": "NS2 launch"},
    ]
    g.sales_with_offset_long(df_all, hw_periods=hw_periods, end=52)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## yearly_cumulative_long
    """)
    return


@app.cell
def _(df_all: pl.DataFrame, ui_hws):
    # 同一年内の年次累計販売台数をlong形式で取得する
    g.yearly_cumulative_long(df_all, year=2026, hw=ui_hws.value, begin=1, end=366)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## yearly_cumulative_by_hwy_long
    """)
    return


@app.cell
def _(df_all: pl.DataFrame):
    # ハードと年の組み合わせごとに、年間通算日を揃えた累計を作る
    g.yearly_cumulative_by_hwy_long(
        df_all,
        hw_years=[("NSW", 2025), ("PS5", 2025), ("NS2", 2026)],
        begin=1,
        end=366,
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## maker_long
    """)
    return


@app.cell
def _(df_all: pl.DataFrame, ui_makers):
    # メーカー別年次販売台数とシェアをlong形式で取得する
    g.maker_long(df_all, begin_year=2021, end_year=2026).filter(
        pl.col("maker_name").is_in(ui_makers.value)
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## cumsum_diffs_long / sales_pase_diffs_long
    """)
    return


@app.cell
def _(df_all: pl.DataFrame):
    # 累計差分と販売ペース差分のデータを作成する
    _cumsum = g.cumsum_diffs_long(df_all, cmplist=[("NS2", "PS5"), ("NSW", "PS4")])
    _pase = g.sales_pase_diffs_long(df_all, cmplist=[("PS5", "PS4"), ("NS2", "PS5")])
    mo.vstack([_cumsum, _pase])
    return


if __name__ == "__main__":
    app.run()
