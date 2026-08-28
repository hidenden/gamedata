# /// script
# [tool.marimo.display]
# theme = "system"
# ///

import marimo

__generated_with = "0.23.15"
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
def load_sales():
    hard_sales = g.load_hard_sales()
    hard_sales
    return (hard_sales,)


@app.cell
def late_august_analysis(hard_sales):
    # XSXは推計誤差の影響が大きいため分析対象から除外
    weekly_sales = (
        hard_sales
        .filter(pl.col("hw") != "XSX")
        .group_by("report_date")
        .agg(pl.col("units").sum().alias("units"))
        .sort("report_date")
        .with_columns(
            pl.col("units").shift(1).alias("previous_units"),
            pl.col("report_date").shift(1).alias("previous_date"),
        )
        .with_columns(
            ((pl.col("units") / pl.col("previous_units") - 1) * 100).alias("wow_pct"),
            (pl.col("report_date") - pl.col("previous_date")).dt.total_days().alias("gap_days"),
            pl.col("report_date").dt.year().alias("year"),
            pl.col("report_date").dt.month().alias("month"),
            pl.col("report_date").dt.day().alias("day"),
        )
        .filter(pl.col("gap_days") == 7)
    )

    # 各年の「週末日が8月19〜25日」の週を8月後半の比較対象とする
    late_august_sales = (
        weekly_sales
        .filter(
            (pl.col("month") == 8)
            & pl.col("day").is_between(19, 25)
        )
        .select(
            "year",
            "report_date",
            "previous_date",
            "units",
            "previous_units",
            pl.col("wow_pct").round(1),
        )
    )

    ordinary_weeks = weekly_sales.filter(
        ~(
            (pl.col("month") == 8)
            & pl.col("day").is_between(19, 25)
        )
    )

    # 前週比が低下する確率を50%とした片側二項検定
    # （ゼロ変化は低下に含めない）
    def _binomial_tail(successes: int, trials: int) -> float:
        from math import comb
        return sum(comb(trials, i) for i in range(successes, trials + 1)) / 2**trials

    _late_count = late_august_sales.height
    _late_declines = late_august_sales.filter(pl.col("wow_pct") < 0).height
    _recent = late_august_sales.filter(pl.col("year") >= 2015)
    _modern = late_august_sales.filter(pl.col("year") >= 2020)

    seasonality_metrics = {
        "years": _late_count,
        "declines": _late_declines,
        "decline_rate": _late_declines / _late_count,
        "mean_pct": late_august_sales["wow_pct"].mean(),
        "median_pct": late_august_sales["wow_pct"].median(),
        "ordinary_decline_rate": ordinary_weeks.filter(pl.col("wow_pct") < 0).height / ordinary_weeks.height,
        "ordinary_median_pct": ordinary_weeks["wow_pct"].median(),
        "sign_test_p": _binomial_tail(_late_declines, _late_count),
        "since_2015_declines": _recent.filter(pl.col("wow_pct") < 0).height,
        "since_2015_years": _recent.height,
        "since_2020_declines": _modern.filter(pl.col("wow_pct") < 0).height,
        "since_2020_years": _modern.height,
        "latest_pct": late_august_sales.tail(1)["wow_pct"].item(),
    }

    late_august_sales
    return late_august_sales, seasonality_metrics


@app.cell
def seasonality_report(late_august_sales, seasonality_metrics):
    seasonality_chart = (
        alt.Chart(late_august_sales)
        .mark_bar()
        .encode(
            x=alt.X("year:O", title="年", axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("wow_pct:Q", title="前週比（%）"),
            color=alt.condition(
                alt.datum.wow_pct < 0,
                alt.value("#d95f02"),
                alt.value("#1b9e77"),
            ),
            tooltip=[
                alt.Tooltip("year:O", title="年"),
                alt.Tooltip("report_date:T", title="対象週"),
                alt.Tooltip("wow_pct:Q", title="前週比", format=".1f"),
                alt.Tooltip("units:Q", title="販売台数", format=","),
            ],
        )
        .properties(
            width=700,
            height=320,
            title="8月後半（週末日19〜25日）のハード販売台数・前週比",
        )
    )

    _zero_rule = alt.Chart(pl.DataFrame({"y": [0]})).mark_rule(
        color="#666666",
        strokeDash=[4, 4],
    ).encode(y="y:Q")

    seasonality_report = mo.vstack([
        mo.md(f"""
    # 8月後半のハード販売は季節的に低下するか

    ## 結論

    **8月後半には、ハード販売台数が季節的に低下する傾向が確認できる。**  
    XSXを除外した過去{seasonality_metrics['years']}年分の記録では、週末日が8月19〜25日の週に
    **{seasonality_metrics['declines']}回（{seasonality_metrics['decline_rate']:.1%}）**の低下が発生した。
    前週比の平均は**{seasonality_metrics['mean_pct']:.1f}%**、中央値は**{seasonality_metrics['median_pct']:.1f}%**だった。

    通常週では低下した週の比率が{seasonality_metrics['ordinary_decline_rate']:.1%}、前週比中央値が
    {seasonality_metrics['ordinary_median_pct']:.1f}%であるため、8月後半の低下は通常の週次変動より明瞭である。
    低下確率を50%と仮定した片側二項検定は **p = {seasonality_metrics['sign_test_p']:.4f}** となる。

    - 2015年以降：{seasonality_metrics['since_2015_years']}年中{seasonality_metrics['since_2015_declines']}年で低下
    - 2020年以降：{seasonality_metrics['since_2020_years']}年中{seasonality_metrics['since_2020_declines']}年で低下
    - 最新年：前週比 **{seasonality_metrics['latest_pct']:.1f}%**

    ## 解釈上の注意

    この結果は反復する季節パターンを示すが、季節性だけで因果関係を確定するものではない。
    お盆商戦の反動、販促、在庫、新機種・新作発売、価格改定なども各年の変動幅に影響する。
    また、一部年度には複数週集計を配分したと考えられるほぼ同値の週が含まれる。
    """),
        seasonality_chart + _zero_rule,
        mo.md("## 年別の検証データ"),
        mo.ui.table(late_august_sales, pagination=True, page_size=10),
    ])

    seasonality_report
    return


if __name__ == "__main__":
    app.run()
