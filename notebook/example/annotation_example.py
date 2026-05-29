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
    # hard_annotation.py
    """)
    return


@app.cell
def _():
    ui_hws = g.HwSelect(default_list=["NSW", "PS5", "NS2"], force_any=True)
    ui_begin_date = mo.ui.date(label="開始日", value=date(2025, 1, 1))
    ui_end_date = mo.ui.date(label="終了日", value=date(2026, 12, 31))
    ui_mode = mo.ui.dropdown(
        options=["week", "month", "quarter", "year"], value="week", label="集計単位"
    )
    ui_level = mo.ui.number(start=1, stop=50, value=20, label="最大レベル")
    mo.vstack(
        [
            ui_hws,
            mo.hstack([ui_begin_date, ui_end_date, ui_mode, ui_level], justify="start"),
        ]
    )
    return ui_begin_date, ui_end_date, ui_hws, ui_level, ui_mode


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## load_hard_annotation
    """)
    return


@app.cell
def _(ui_hws, ui_level):
    # アノテーションの実データを読み込み、選択HWとレベルで絞り込む
    annotation_df = (
        g.load_hard_annotation()
        .filter(pl.col("hw").is_in(ui_hws.value))
        .filter(pl.col("level") <= ui_level.value)
        .sort(["report_date", "level"])
    )
    annotation_df
    return (annotation_df,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## summarize_annotation
    """)
    return


@app.cell
def _(annotation_df, ui_mode):
    # 月次・四半期・年次では同一期間の代表アノテーションに要約する
    g.summarize_annotation(annotation_df, mode=ui_mode.value)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## join_annotation
    """)
    return


@app.cell
def _(ui_begin_date, ui_end_date, ui_hws, ui_level, ui_mode):
    # 販売データにアノテーションを結合し、note列をチャート表示に利用する
    df_all = g.load_hard_sales()
    mode = ui_mode.value
    if mode == "week":
        sales_df = g.sales_long(
            df_all, hw=ui_hws.value, begin=ui_begin_date.value, end=ui_end_date.value
        )
    elif mode == "month":
        sales_df = g.monthly_sales_long(
            df_all, hw=ui_hws.value, begin=ui_begin_date.value, end=ui_end_date.value
        )
    elif mode == "quarter":
        sales_df = g.quarterly_sales_long(
            df_all, hw=ui_hws.value, begin=ui_begin_date.value, end=ui_end_date.value
        )
    else:
        sales_df = g.yearly_sales_long(
            df_all, hw=ui_hws.value, begin=ui_begin_date.value, end=ui_end_date.value
        )

    g.join_annotation(sales_df, mode=mode, level=ui_level.value)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## chart_line_sales annotation_level
    """)
    return


@app.cell
def _(ui_begin_date, ui_end_date, ui_hws, ui_level, ui_mode):
    # join_annotationを内部利用するチャート関数で注釈表示を確認する
    g.chart_line_sales(
        hw=ui_hws.value,
        mode=ui_mode.value,
        begin=ui_begin_date.value,
        end=ui_end_date.value,
        annotation_level=ui_level.value,
        multi_line=True,
    )
    return


if __name__ == "__main__":
    app.run()
