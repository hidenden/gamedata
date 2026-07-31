# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "altair==6.2.2",
#     "marimo>=0.23.14",
#     "pandas>=2.3.3",
#     "polars==1.42.1",
#     "pyarrow>=23.0.1",
# ]
# [tool.marimo.display]
# theme = "system"
# ///

import marimo

__generated_with = "0.23.14"
app = marimo.App(width="medium")

with app.setup:
    # 標準ライブラリ
    from datetime import date, datetime
    from pathlib import Path
    import sys

    import marimo as mo
    import altair as alt

    # サードパーティライブラリ
    import polars as pl

    # import polars.selectors as cs
    # プロジェクト内モジュール
    # _src_dir = Path.cwd() / "src"
    # if str(_src_dir) not in sys.path:
    #    sys.path.insert(0, str(_src_dir))
    import gamedata as g


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # PS5, Switchを連続で超える
    """)
    return


@app.cell
def _():
    df_all = g.load_hard_sales()
    return (df_all,)


@app.cell
def _(df_all):
    _df_latest = g.extract_latest(df_all, 1)
    switch2_latest = _df_latest.filter(pl.col("hw") == "NS2").row(0, named=True)
    switch_latest = _df_latest.filter(pl.col("hw") == "NSW").row(0, named=True)
    ps5_latest = _df_latest.filter(pl.col("hw") == "PS5").row(0, named=True)
    return


@app.cell
def ps5_switch_sales_streak(df_all):
    # PS5とSwitchの週次販売台数を同じ集計日で比較する
    def _calculate_ps5_switch_streaks(sales_df: pl.DataFrame):
        comparison = (
            sales_df.filter(pl.col("hw").is_in(["PS5", "NSW"]))
            .select("report_date", "hw", "units")
            .pivot(
                index="report_date",
                on="hw",
                values="units",
                aggregate_function="last",
            )
            # 片方のデータがない週は、公平に比較できないため除外する
            .drop_nulls(["PS5", "NSW"])
            .sort("report_date")
            .with_columns((pl.col("PS5") > pl.col("NSW")).alias("ps5_above_switch"))
        )

        # PS5 > Switchが真で、集計日が7日間隔の行を連続区間にまとめる
        runs = []
        current_run = []
        for row in comparison.to_dicts():
            is_next_week = (
                not current_run
                or (row["report_date"] - current_run[-1]["report_date"]).days == 7
            )
            if row["ps5_above_switch"] and is_next_week:
                current_run.append(row)
            else:
                if current_run:
                    runs.append(current_run)
                current_run = [row] if row["ps5_above_switch"] else []
        if current_run:
            runs.append(current_run)

        latest_date = comparison["report_date"].max()
        run_records = [
            {
                "start_date": run[0]["report_date"],
                "end_date": run[-1]["report_date"],
                "weeks": len(run),
                "ps5_units": sum(row["PS5"] for row in run),
                "switch_units": sum(row["NSW"] for row in run),
                "units_diff": sum(row["PS5"] - row["NSW"] for row in run),
                "is_current": run[-1]["report_date"] == latest_date,
            }
            for run in runs
        ]

        # 継続週数の長い順に並べ、同じ週数には同じ順位を付ける
        streaks = (
            pl.DataFrame(run_records)
            .with_columns(
                pl.col("weeks")
                .rank(method="dense", descending=True)
                .cast(pl.Int16)
                .alias("rank")
            )
            .select(
                "rank",
                "weeks",
                "start_date",
                "end_date",
                "ps5_units",
                "switch_units",
                "units_diff",
                "is_current",
            )
            .sort(["weeks", "start_date"], descending=[True, False])
        )
        return comparison.sort("report_date", descending=True), streaks

    ps5_switch_comparison, ps5_switch_streaks = _calculate_ps5_switch_streaks(df_all)
    ps5_switch_streak = int(
        ps5_switch_streaks.filter(pl.col("is_current"))["weeks"].item()
    )

    # 全連続区間を長い順に表示し、現在進行中の区間を識別できるようにする
    mo.vstack(
        [
            mo.md(
                f"**現在は{ps5_switch_streak}週連続。"
                "全期間の最長記録と比較した一覧です。**"
            ),
            mo.ui.table(ps5_switch_streaks, pagination=True, page_size=15),
        ]
    )
    return


if __name__ == "__main__":
    app.run()
