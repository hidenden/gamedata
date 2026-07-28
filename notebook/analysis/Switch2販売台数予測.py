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
    # Switch2販売台数予測
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
def nintendo_2026_quarterly_forecast(df_all):
    # 過去の四半期構成比から、任天堂ハードの2026年販売台数を予測する
    def _forecast_nintendo_2026(sales_df: pl.DataFrame):
        # gamedataの既存関数で、2015～2025年のメーカー別・暦年四半期別販売を集計する
        historical = (
            g.quarterly_sales(
                sales_df,
                begin=date(2015, 1, 1),
                end=date(2025, 12, 31),
                maker_mode=True,
            )
            .filter(pl.col("maker_name") == "Nintendo")
            .select("year", "q_num", "quarter", "quarterly_units")
            .with_columns(
                pl.col("quarterly_units").sum().over("year").alias("yearly_units")
            )
            # 各年の年間販売台数に占める四半期販売台数の比率を求める
            .with_columns(
                (pl.col("quarterly_units") / pl.col("yearly_units")).alias(
                    "quarter_ratio"
                )
            )
            .sort(["year", "q_num"])
        )

        # 11年間について、四半期ごとの年間構成比を単純平均する
        average_ratios = (
            historical.group_by("q_num")
            .agg(
                pl.col("quarter_ratio").mean().alias("average_ratio"),
                pl.col("quarterly_units")
                .mean()
                .round()
                .cast(pl.Int64)
                .alias("average_units"),
            )
            .with_columns((pl.col("average_ratio") * 100).round(2).alias("average_pct"))
            .sort("q_num")
        )

        # 2026年は完了済みのQ1・Q2だけを実績値として取得する
        actual_2026_h1 = (
            g.quarterly_sales(
                sales_df,
                begin=date(2026, 1, 1),
                end=date(2026, 6, 30),
                maker_mode=True,
            )
            .filter(pl.col("maker_name") == "Nintendo")
            .select("q_num", "quarter", "quarterly_units")
            .sort("q_num")
        )

        # 上期実績 ÷ 過去平均の上期構成比で、2026年の年間販売を逆算する
        h1_units = int(actual_2026_h1["quarterly_units"].sum())
        h1_ratio = float(
            average_ratios.filter(pl.col("q_num").is_in([1, 2]))["average_ratio"].sum()
        )
        annual_forecast = round(h1_units / h1_ratio)

        # 逆算した年間値を、過去平均のQ3・Q4構成比で配分する
        q3_forecast = round(
            annual_forecast
            * average_ratios.filter(pl.col("q_num") == 3)["average_ratio"].item()
        )
        q4_forecast = round(
            annual_forecast
            * average_ratios.filter(pl.col("q_num") == 4)["average_ratio"].item()
        )
        forecast = pl.DataFrame(
            {
                "period": ["2026Q1", "2026Q2", "2026Q3", "2026Q4", "2026年"],
                "status": ["実績", "実績", "予測", "予測", "予測"],
                "units": [
                    actual_2026_h1["quarterly_units"][0],
                    actual_2026_h1["quarterly_units"][1],
                    q3_forecast,
                    q4_forecast,
                    annual_forecast,
                ],
            }
        )
        return historical, average_ratios, forecast

    (
        nintendo_quarterly_history,
        nintendo_quarterly_average_ratios,
        nintendo_2026_forecast,
    ) = _forecast_nintendo_2026(df_all)

    # 年別実績、季節構成比、2026年予測をまとめて表示する
    mo.vstack(
        [
            mo.md("## 任天堂ハードの暦年四半期販売と2026年予測"),
            mo.md("### 2015～2025年の四半期販売台数と年間構成比"),
            mo.ui.table(nintendo_quarterly_history, pagination=True, page_size=12),
            mo.md("### 四半期構成比の11年間平均"),
            nintendo_quarterly_average_ratios,
            mo.md("### 2026年予測（Q1・Q2実績から逆算）"),
            nintendo_2026_forecast,
        ]
    )
    return nintendo_2026_forecast, nintendo_quarterly_history


@app.cell
def nintendo_yearly_comparison(
    nintendo_2026_forecast,
    nintendo_quarterly_history,
):
    # 2026年予測を、2015～2025年の任天堂ハード年間販売台数と比較する
    nintendo_yearly_comparison = (
        nintendo_quarterly_history.group_by("year")
        .agg(pl.col("quarterly_units").sum().alias("units"))
        .with_columns(pl.lit("実績").alias("status"))
        .vstack(
            pl.DataFrame(
                {
                    "year": [2026],
                    "units": [
                        nintendo_2026_forecast.filter(pl.col("period") == "2026年")[
                            "units"
                        ].item()
                    ],
                    "status": ["予測"],
                },
                schema={"year": pl.Int16, "units": pl.Int64, "status": pl.String},
            )
        )
        .sort("year")
    )

    _nintendo_2026_units = nintendo_yearly_comparison.filter(pl.col("year") == 2026)[
        "units"
    ].item()
    _nintendo_2026_rank = (
        nintendo_yearly_comparison.filter(pl.col("units") > _nintendo_2026_units).height
        + 1
    )
    _nintendo_nearest_year = (
        nintendo_yearly_comparison.filter(pl.col("year") != 2026)
        .with_columns(
            (pl.col("units") - _nintendo_2026_units).abs().alias("absolute_difference")
        )
        .sort("absolute_difference")
        .row(0, named=True)
    )
    _nintendo_difference = _nintendo_2026_units - _nintendo_nearest_year["units"]
    _nintendo_difference_pct = _nintendo_difference / _nintendo_nearest_year["units"]

    nintendo_yearly_comparison_chart = (
        alt.Chart(nintendo_yearly_comparison)
        .mark_bar()
        .encode(
            x=alt.X("year:O", title="年"),
            y=alt.Y("units:Q", title="年間販売台数"),
            color=alt.Color(
                "status:N",
                title="区分",
                scale=alt.Scale(domain=["実績", "予測"], range=["#4C78A8", "#F58518"]),
            ),
            tooltip=[
                alt.Tooltip("year:O", title="年"),
                alt.Tooltip("units:Q", title="販売台数", format=","),
                alt.Tooltip("status:N", title="区分"),
            ],
        )
        .properties(width=650, height=320)
    )

    mo.vstack(
        [
            mo.md("### 任天堂ハード年間販売台数との比較"),
            mo.md(
                f"2026年予測は **{_nintendo_2026_units:,}台**で、"
                f"2015～2026年の12年中 **{_nintendo_2026_rank}位**に相当します。"
                f"最も近い{_nintendo_nearest_year['year']}年"
                f"（{_nintendo_nearest_year['units']:,}台）を"
                f"{_nintendo_difference:,}台（{_nintendo_difference_pct:.1%}）上回る水準です。"
            ),
            mo.ui.altair_chart(nintendo_yearly_comparison_chart),
            mo.ui.table(
                nintendo_yearly_comparison.sort("units", descending=True),
                pagination=False,
            ),
        ]
    )
    return


if __name__ == "__main__":
    app.run()
