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


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # 情報取得の関数群の案の検討

    - 引数には必ずhwを指定 (一つだけ)
    - 返り値はint､もしくはintのリスト｡(DataFrameは返さない)
    - 日付を指定したらextract_by_date()で処理する｡
    - 日付が指定されない場合は そのハードの最新データを用いる (extract_by_latest()は使えなさそう)
    - delta weekを指定するモードも必要｡

    ## 絞り込みを引数指定するパターン

    - 日付 report_date: datetime, date
    - 整数 delta_week: int

    ## 戻り値を指定する引数パターン

    - cumulative: bool = False 累積値を返すかどうかのフラグ


    ## 関数名

    - sales_value()
    """)
    return


@app.function
def sales_value(
    hw: str,
    report_date: date | datetime | None = None,
    index_week: int | None = None,
    cumulative: bool = False
) -> int:
    if report_date is not None and index_week is not None:
        raise ValueError("report_date と index_week は同時に指定できません。")

    df_all = g.load_hard_sales()

    if report_date:
        df = g.extract_by_date(df=df_all, hw=[hw], target_date=report_date)

    elif index_week:
        if index_week < 0:
            df = df_all.filter(pl.col("hw") == hw).sort(pl.col("index_week"), descending=
True).head(1)
        else: 
            df = df_all.filter(
                (pl.col("hw") == hw) & (pl.col("index_week") == index_week)
                )   
    else:
        raise ValueError("report_date または index_week のいずれかを指定してください。")

    column_name = "units"
    if cumulative:
        column_name = "sum_units"
    return df.select(pl.col(column_name)).item()  # 単一の値を取得


@app.cell
def _():
    x1 = sales_value(hw="NS2", report_date=date(2025, 12, 29))
    print(x1)
    return


@app.cell
def _():
    x2 = sales_value(hw="NS2", index_week=3)
    print(x2)
    return


@app.cell
def _():
    x3 = sales_value(hw="NS2", index_week=40, cumulative=True)
    print(x3)
    return


@app.cell
def _():
    x4 = sales_value(hw="NS2", index_week=-1, cumulative=True)
    print(x4)
    return


@app.cell
def _():
    _v = sales_value(hw="NS2", report_date=date(2026, 5, 9), cumulative=True)
    print(_v)
    return


@app.cell
def _():
    df_all = g.load_hard_sales()
    dfx = df_all.filter(pl.col("hw") == "NS2").sort(pl.col("index_week"), descending=
    True).head(1)
    dfx
    return


if __name__ == "__main__":
    app.run()
