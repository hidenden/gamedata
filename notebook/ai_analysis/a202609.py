# /// script
# requires-python = ">=3.11"
# [tool.marimo.display]
# theme = "system"
# ///

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")

with app.setup:
    # 標準ライブラリ
    from datetime import date, datetime
    from pathlib import Path
    import sys

    # サードパーティライブラリ
    import marimo as mo
    import altair as alt
    import polars as pl
    # import polars.selectors as cs

    import scipy as sp
    import statsmodels.api as sm
    import holidays as holidays
    import ruptures as rpt
    import vl_convert as vlc

    # プロジェクト内モジュール
    import gamedata as g



@app.cell
def load_db():
    hard_sales_df: pl.DataFrame = g.load_hard_sales(True)
    annotation_df: pl.DataFrame = g.load_hard_annotation(no_cache=True)

    return (hard_sales_df,)


@app.cell(hide_code=True)
def md_prologue():
    mo.md(r"""
    # ゲームハードウェア分析 notebook

    - このnotebookは日本国内のゲームハードウェア販売状況をデータから分析するものです｡
    - ハードウェアの販売データは hard_sales_all_df に格納されています。これは毎週の各ハードウェアの販売台数が格納されています｡
    - 注釈データは annotation_all_df に格納されています。これはゲーム関係のイベントと日付が格納されています｡売上の変化に影響を与える要因として利用してください｡
    - データ分析時には､出来るだけ import済みの gamedataライブラリを使用して下さい｡
    - gamedataライブラリで不足する場合は､新たな関数を実装して分析と可視化を行って下さい。
    - 新たな関数が将来の分析でも使える汎用性を持つと判断される場合には､出来るだけ汎用な形式で関数化を試み､その旨を報告して下さい｡
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 開発者用メモ

    marimo起動方法

    ```shell
    uv run marimo edit --no-token --no-sandbox <notebook_file_path>
    ```

    marimo-pair接続プロンプト

    ```text
    marimo-pair http://localhost:2718 の既存セッションで､以下に示すnotebookとpairしてください。
    新しいmarimoサーバーは起動しないでください。
    sandbox内から接続できない場合は、接続スクリプトをsandbox外で実行してください。

    notebook名:
    ```
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## AIへの指示

    分析前に `from gamedata import catalog` を実行し、`catalog.overview()` を参照してください。
    販売データは `hard_sales_all_df`、注釈データは `annotation_all_df` にあります。
    `catalog.inspect_frame(hard_sales_all_df, dataset="hard_sales")` で実際の収録範囲を確認し、
    `catalog.search()` と `catalog.describe()` で分析に使う既存関数と列の意味を確認してください。
    """)
    return


@app.cell
def _(hard_sales_df: pl.DataFrame):
    [ns2_info, ps5_info, nsw_info] = g.hard_sales_summary(
        hard_sales_df, hw=["NS2", "PS5", "NSW"]
    )

    return


@app.cell
def _():
    _chart = g.chart_line_cumulative_delta(
        hw=[
            "NS2",
            "NSW",
            "3DS",
            "DS",
            "GBA",
        ],
        end=85,
        annotation_level=23,
        mode="week",
        with_point=False,
        multi_line=False,
        begin=45,
        ymin=3000000,
    )
    cd_chart = mo.ui.altair_chart(_chart)
    mo.vstack(items=[cd_chart], justify="start")

    return


if __name__ == "__main__":
    app.run()
