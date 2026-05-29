# /// script
# [tool.marimo.display]
# theme = "system"
# ///

import marimo

__generated_with = "0.23.6"
app = marimo.App(width="medium")

with app.setup:
    # 標準ライブラリ
    from datetime import timedelta

    import marimo as mo

    # サードパーティライブラリ
    import polars as pl

    # プロジェクト内モジュール
    import gamedata as g


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # hard_sales_report.py
    """)
    return


@app.cell
def _():
    # レポート系関数も実データを読み込んで表示例を作る
    df_all = g.load_hard_sales()
    latest_date = g.current_report_date(df_all)
    return df_all, latest_date


@app.cell
def _(latest_date):
    ui_hws = g.HwSelect(default_list=["NSW", "PS5", "NS2"], force_any=True)
    ui_makers = g.MakerSelect(default_list=["任天堂", "ソニー"], force_any=True)
    ui_begin_date = mo.ui.date(label="開始日", value=latest_date - timedelta(weeks=12))
    ui_end_date = mo.ui.date(label="終了日", value=latest_date)
    ui_rank_n = mo.ui.number(start=-20, stop=20, value=10, label="ランキング件数")
    mo.vstack(
        [
            ui_hws,
            ui_makers,
            mo.hstack([ui_begin_date, ui_end_date, ui_rank_n], justify="start"),
        ]
    )
    return ui_begin_date, ui_end_date, ui_hws, ui_makers, ui_rank_n


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## units_by_date_hw_table
    """)
    return


@app.cell
def _(df_all, ui_begin_date, ui_end_date):
    # 指定期間の日付・ハード別販売台数テーブルをStylerで表示する
    g.units_by_date_hw_table(
        df_all,
        begin=ui_begin_date.value,
        end=ui_end_date.value,
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## weekly_sales_ranking
    """)
    return


@app.cell
def _(ui_begin_date, ui_end_date, ui_hws, ui_rank_n):
    # 週次販売台数のランキングを作成する
    g.weekly_sales_ranking(
        rank_n=ui_rank_n.value,
        begin=ui_begin_date.value,
        end=ui_end_date.value,
        hw=ui_hws.value,
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## monthly_sales_ranking
    """)
    return


@app.cell
def _(ui_begin_date, ui_end_date, ui_hws, ui_rank_n):
    # 月次販売台数のランキングを作成する
    g.monthly_sales_ranking(
        rank_n=ui_rank_n.value,
        begin=ui_begin_date.value,
        end=ui_end_date.value,
        hw=ui_hws.value,
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## yearly_sales_ranking
    """)
    return


@app.cell
def _(ui_begin_date, ui_end_date, ui_hws, ui_rank_n):
    # 年次販売台数のランキングを作成する
    g.yearly_sales_ranking(
        rank_n=ui_rank_n.value,
        begin=ui_begin_date.value,
        end=ui_end_date.value,
        hw=ui_hws.value,
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## maker ranking
    """)
    return


@app.cell
def _(ui_begin_date, ui_end_date, ui_makers, ui_rank_n):
    # メーカー名をMakerSelectで選択してランキングを作成する
    g.monthly_sales_ranking(
        rank_n=ui_rank_n.value,
        begin=ui_begin_date.value,
        end=ui_end_date.value,
        maker=ui_makers.value,
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## delta_week_ranking
    """)
    return


@app.cell
def _():
    ui_delta_week = mo.ui.number(start=0, value=52, label="経過週")
    ui_reached_units = mo.ui.number(
        start=100000, step=100000, value=1000000, label="到達台数"
    )
    mo.hstack([ui_delta_week, ui_reached_units], justify="start")
    return ui_delta_week, ui_reached_units


@app.cell
def _(ui_delta_week):
    # 発売後の指定週時点における累計販売台数ランキングを表示する
    g.delta_week_ranking(delta_week=ui_delta_week.value)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## reached_unit_summary
    """)
    return


@app.cell
def _(ui_reached_units):
    # 指定台数に到達した週と集計日を確認する
    g.reached_unit_summary(n=ui_reached_units.value, all=False)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## rename_columns / rename_hw / style_df
    """)
    return


@app.cell
def _(df_all, ui_begin_date, ui_end_date, ui_hws):
    # 表示用にハード名と列名を整え、数値列に簡単なスタイルを付ける
    sample_df = (
        g.sales_long(
            df_all,
            hw=ui_hws.value,
            begin=ui_begin_date.value,
            end=ui_end_date.value,
        )
        .sort(["report_date", "units"], descending=[False, True])
        .head(20)
    )
    sample_df = g.rename_columns(g.rename_hw(sample_df))
    g.style_df(sample_df, bar=True)
    return


if __name__ == "__main__":
    app.run()
