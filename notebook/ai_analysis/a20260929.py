# /// script
# requires-python = ">=3.11"
# [tool.marimo.display]
# theme = "system"
# ///

import marimo

__generated_with = "0.25.0"
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
    hard_sales_all_df: pl.DataFrame = g.load_hard_sales(True)
    annotation_all_df: pl.DataFrame = g.load_hard_annotation(no_cache=True)
    return annotation_all_df, hard_sales_all_df


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


@app.cell
def forecast_2026_09_27_calculation(hard_sales_all_df: pl.DataFrame):
    forecast_target_date = date(2026, 9, 27)
    forecast_source_date = hard_sales_all_df.select(pl.col("report_date").max()).item()

    _forecast_latest_df = (
        hard_sales_all_df
        .filter(pl.col("report_date") == forecast_source_date)
        .select(
            "hw",
            "full_name",
            pl.col("ma4w").alias("four_week_avg"),
        )
    )

    _forecast_sep_actual_df = (
        hard_sales_all_df
        .filter(
            (pl.col("report_date") >= date(2026, 9, 1))
            & (pl.col("report_date") <= forecast_source_date)
        )
        .group_by("hw")
        .agg(pl.col("units").sum().alias("sep_actual"))
    )

    _forecast_q3_actual_df = (
        hard_sales_all_df
        .filter(
            (pl.col("report_date") >= date(2026, 7, 1))
            & (pl.col("report_date") <= forecast_source_date)
        )
        .group_by("hw")
        .agg(pl.col("units").sum().alias("q3_actual"))
    )

    hardware_forecast_df = (
        _forecast_latest_df
        .join(_forecast_sep_actual_df, on="hw", how="left")
        .join(_forecast_q3_actual_df, on="hw", how="left")
        .with_columns(
            pl.col("four_week_avg").alias("forecast_09_27"),
            (pl.col("sep_actual") + pl.col("four_week_avg")).alias("sep_forecast"),
            (pl.col("q3_actual") + pl.col("four_week_avg")).alias("q3_forecast"),
        )
        .sort("hw")
    )

    _hardware_forecast_display_df = hardware_forecast_df.select(
        pl.col("hw").alias("ハード"),
        pl.col("full_name").alias("名称"),
        pl.col("four_week_avg").alias("直近4週平均"),
        pl.col("sep_actual").alias("9月20日まで実績"),
        pl.col("forecast_09_27").alias("9月27日予測"),
        pl.col("sep_forecast").alias("2026年9月予測"),
        pl.col("q3_actual").alias("第3四半期9月20日まで実績"),
        pl.col("q3_forecast").alias("2026年第3四半期予測"),
    )

    _hardware_forecast_total_df = hardware_forecast_df.select(
        pl.lit("TOTAL").alias("ハード"),
        pl.lit("合計").alias("名称"),
        pl.col("four_week_avg").sum().alias("直近4週平均"),
        pl.col("sep_actual").sum().alias("9月20日まで実績"),
        pl.col("forecast_09_27").sum().alias("9月27日予測"),
        pl.col("sep_forecast").sum().alias("2026年9月予測"),
        pl.col("q3_actual").sum().alias("第3四半期9月20日まで実績"),
        pl.col("q3_forecast").sum().alias("2026年第3四半期予測"),
    )

    hardware_forecast_summary_df = pl.concat(
        [_hardware_forecast_display_df, _hardware_forecast_total_df],
        how="vertical",
    )

    return (
        forecast_source_date,
        forecast_target_date,
        hardware_forecast_df,
        hardware_forecast_summary_df,
    )


@app.cell
def forecast_2026_09_27_output(
    forecast_source_date,
    forecast_target_date,
    hardware_forecast_summary_df,
):
    mo.vstack([
        mo.md(f"""
    ## 2026年9月27日・9月・第3四半期の販売予測

    - 最新実績日は **{forecast_source_date:%Y年%m月%d日}**。
    - **{forecast_target_date:%Y年%m月%d日}** の販売台数は、各ハードの直近4週平均（`ma4w`、1台単位に丸め済み）とする。
    - 9月予測は9月6日・13日・20日の実績に9月27日予測を加算する。
    - 第3四半期予測は7月から9月20日までの実績に9月27日予測を加算する。
    """),
        hardware_forecast_summary_df,
    ])
    return


@app.cell
def q3_history_comparison_calculation(
    hard_sales_all_df: pl.DataFrame,
    hardware_forecast_df,
):
    q3_forecast_total = hardware_forecast_df.select(
        pl.col("q3_forecast").sum()
    ).item()
    q3_forecast_weeks = (
        hard_sales_all_df
        .filter((pl.col("year") == 2026) & (pl.col("q_num") == 3))
        .select(pl.col("report_date").n_unique())
        .item()
        + 1
    )

    q3_historical_df = (
        hard_sales_all_df
        .filter(
            (pl.col("year") >= 2006)
            & (pl.col("year") <= 2025)
            & (pl.col("q_num") == 3)
        )
        .group_by("year")
        .agg(
            pl.col("units").sum().alias("q3_units"),
            pl.col("report_date").n_unique().alias("q3_weeks"),
        )
        .with_columns(
            (pl.col("q3_units") / pl.col("q3_weeks"))
            .round(0)
            .cast(pl.Int64)
            .alias("weekly_units")
        )
        .sort("year")
    )

    q3_history_comparison_df = (
        q3_historical_df
        .with_columns(pl.lit("実績").alias("区分"))
        .vstack(
            pl.DataFrame(
                {
                    "year": [2026],
                    "q3_units": [q3_forecast_total],
                    "q3_weeks": [q3_forecast_weeks],
                    "weekly_units": [round(q3_forecast_total / q3_forecast_weeks)],
                    "区分": ["予測"],
                },
                schema={
                    "year": pl.Int16,
                    "q3_units": pl.Int64,
                    "q3_weeks": pl.UInt32,
                    "weekly_units": pl.Int64,
                    "区分": pl.String,
                },
            )
        )
        .sort("year")
    )

    _q3_ranked_df = q3_history_comparison_df.with_columns(
        pl.col("q3_units").rank("ordinal", descending=True).alias("rank_desc")
    )
    q3_forecast_rank = (
        _q3_ranked_df
        .filter(pl.col("year") == 2026)
        .select("rank_desc")
        .item()
    )

    _q3_2025_total = (
        q3_historical_df.filter(pl.col("year") == 2025).select("q3_units").item()
    )
    _q3_min_row = q3_historical_df.sort("q3_units").row(0, named=True)
    _q3_weekly_min_row = q3_historical_df.sort("weekly_units").row(0, named=True)
    _q3_historical_median = round(
        q3_historical_df.select(pl.col("q3_units").median()).item()
    )

    q3_evaluation_metrics = {
        "forecast_total": q3_forecast_total,
        "forecast_weeks": q3_forecast_weeks,
        "rank": q3_forecast_rank,
        "rank_total": q3_history_comparison_df.height,
        "prior_year_total": _q3_2025_total,
        "prior_year_delta": q3_forecast_total - _q3_2025_total,
        "prior_year_pct": round((q3_forecast_total / _q3_2025_total - 1) * 100, 1),
        "historical_min_year": _q3_min_row["year"],
        "historical_min_total": _q3_min_row["q3_units"],
        "historical_min_delta": q3_forecast_total - _q3_min_row["q3_units"],
        "historical_min_pct": round(
            (q3_forecast_total / _q3_min_row["q3_units"] - 1) * 100,
            1,
        ),
        "historical_median": _q3_historical_median,
        "median_pct": round((q3_forecast_total / _q3_historical_median - 1) * 100, 1),
        "weekly_forecast": round(q3_forecast_total / q3_forecast_weeks),
        "weekly_min_year": _q3_weekly_min_row["year"],
        "weekly_min": _q3_weekly_min_row["weekly_units"],
        "weekly_min_pct": round(
            (q3_forecast_total / q3_forecast_weeks / _q3_weekly_min_row["weekly_units"] - 1)
            * 100,
            1,
        ),
    }

    q3_evaluation_df = pl.DataFrame(
        {
            "比較基準": [
                "2026年第3四半期予測",
                "2025年第3四半期実績",
                f"過去最低（{_q3_min_row['year']}年）",
                "2006〜2025年の中央値",
            ],
            "販売台数": [
                q3_forecast_total,
                _q3_2025_total,
                _q3_min_row["q3_units"],
                _q3_historical_median,
            ],
            "2026年予測との差": [
                0,
                q3_forecast_total - _q3_2025_total,
                q3_forecast_total - _q3_min_row["q3_units"],
                q3_forecast_total - _q3_historical_median,
            ],
            "差率（%）": [
                0.0,
                q3_evaluation_metrics["prior_year_pct"],
                q3_evaluation_metrics["historical_min_pct"],
                q3_evaluation_metrics["median_pct"],
            ],
        }
    )

    return (
        q3_evaluation_df,
        q3_evaluation_metrics,
        q3_forecast_total,
        q3_forecast_weeks,
        q3_history_comparison_df,
    )


@app.cell
def q3_history_comparison_output(
    q3_evaluation_df,
    q3_evaluation_metrics,
    q3_history_comparison_df,
):
    _metrics = q3_evaluation_metrics
    _q3_chart = (
        alt.Chart(q3_history_comparison_df)
        .mark_bar()
        .encode(
            x=alt.X("year:O", title="年"),
            y=alt.Y("q3_units:Q", title="第3四半期販売台数"),
            color=alt.condition(
                alt.datum.区分 == "予測",
                alt.value("#e45756"),
                alt.value("#4c78a8"),
            ),
            tooltip=[
                alt.Tooltip("year:O", title="年"),
                alt.Tooltip("区分:N", title="区分"),
                alt.Tooltip("q3_units:Q", title="販売台数", format=","),
                alt.Tooltip("q3_weeks:Q", title="週数"),
                alt.Tooltip("weekly_units:Q", title="週平均", format=","),
            ],
        )
        .properties(width=720, height=320, title="第3四半期のハード販売台数（2006年以降）")
    )

    mo.vstack([
        mo.md(f"""
    ## 2026年第3四半期予測の歴史比較と評価

    2026年第3四半期の予測値は **{_metrics['forecast_total']:,}台**。2006年以降の21年比較では **{_metrics['rank_total']}年中{_metrics['rank']}位（最下位）** です。

    - 前年（2025年）の{_metrics['prior_year_total']:,}台から **{_metrics['prior_year_delta']:,}台（{_metrics['prior_year_pct']:+.1f}%）**。
    - これまでの最低値である{_metrics['historical_min_year']}年の{_metrics['historical_min_total']:,}台を **{abs(_metrics['historical_min_delta']):,}台（{_metrics['historical_min_pct']:+.1f}%）**下回る。
    - 2006〜2025年の中央値{_metrics['historical_median']:,}台に対して **{_metrics['median_pct']:+.1f}%**。
    - 2026年は13週換算で週平均{_metrics['weekly_forecast']:,}台。従来の週平均最低である{_metrics['weekly_min_year']}年の{_metrics['weekly_min']:,}台も **{_metrics['weekly_min_pct']:+.1f}%**下回る。

    **評価：** 週数をそろえても過去最低であり、2026年第3四半期は2006年以降で最も低い販売水準と評価できる。前年からの落ち込みも大きく、市場全体として非常に弱い四半期である。
    """),
        q3_evaluation_df,
        _q3_chart,
    ])
    return


@app.cell
def q1_q3_history_comparison_calculation(
    hard_sales_all_df: pl.DataFrame,
    q3_forecast_total,
):
    q1_q3_historical_wide_df = (
        hard_sales_all_df
        .filter(
            (pl.col("year") >= 2006)
            & (pl.col("year") <= 2025)
            & pl.col("q_num").is_in([1, 2, 3])
        )
        .group_by(["year", "q_num"])
        .agg(pl.col("units").sum().alias("units"))
        .pivot(on="q_num", index="year", values="units", aggregate_function="first")
        .rename({"1": "q1_units", "2": "q2_units", "3": "q3_units"})
        .with_columns(
            (pl.col("q1_units") + pl.col("q2_units")).alias("h1_units"),
            (
                pl.col("q1_units")
                + pl.col("q2_units")
                + pl.col("q3_units")
            ).alias("q1_q3_units"),
        )
        .select("year", "q1_units", "q2_units", "q3_units", "h1_units", "q1_q3_units")
        .sort("year")
    )

    _q1_2026_units = (
        hard_sales_all_df
        .filter((pl.col("year") == 2026) & (pl.col("q_num") == 1))
        .select(pl.col("units").sum())
        .item()
    )
    _q2_2026_units = (
        hard_sales_all_df
        .filter((pl.col("year") == 2026) & (pl.col("q_num") == 2))
        .select(pl.col("units").sum())
        .item()
    )

    q1_q3_2026_df = pl.DataFrame(
        {
            "year": [2026],
            "q1_units": [_q1_2026_units],
            "q2_units": [_q2_2026_units],
            "q3_units": [q3_forecast_total],
            "h1_units": [_q1_2026_units + _q2_2026_units],
            "q1_q3_units": [_q1_2026_units + _q2_2026_units + q3_forecast_total],
        },
        schema={
            "year": pl.Int16,
            "q1_units": pl.Int64,
            "q2_units": pl.Int64,
            "q3_units": pl.Int64,
            "h1_units": pl.Int64,
            "q1_q3_units": pl.Int64,
        },
    )

    q1_q3_all_years_df = q1_q3_historical_wide_df.vstack(q1_q3_2026_df)

    def _q1_q3_metric(_column):
        _value = q1_q3_2026_df.select(_column).item()
        _median = round(q1_q3_historical_wide_df.select(pl.col(_column).median()).item())
        _rank_desc = (
            q1_q3_all_years_df
            .with_columns(pl.col(_column).rank("ordinal", descending=True).alias("rank"))
            .filter(pl.col("year") == 2026)
            .select("rank")
            .item()
        )
        _prior_year_value = (
            q1_q3_historical_wide_df
            .filter(pl.col("year") == 2025)
            .select(_column)
            .item()
        )
        return {
            "value": _value,
            "median": _median,
            "median_pct": round((_value / _median - 1) * 100, 1),
            "low_rank": q1_q3_all_years_df.height - _rank_desc + 1,
            "rank_total": q1_q3_all_years_df.height,
            "yoy_delta": _value - _prior_year_value,
            "yoy_pct": round((_value / _prior_year_value - 1) * 100, 1),
        }

    q1_q3_evaluation_metrics = {
        "1Q": _q1_q3_metric("q1_units"),
        "2Q": _q1_q3_metric("q2_units"),
        "3Q": _q1_q3_metric("q3_units"),
        "上期": _q1_q3_metric("h1_units"),
        "1〜3Q累計": _q1_q3_metric("q1_q3_units"),
    }

    q1_q3_evaluation_df = pl.DataFrame(
        {
            "期間": ["1Q", "2Q", "3Q（予測）", "1〜3Q累計（予測）"],
            "2026年販売台数": [
                q1_q3_evaluation_metrics["1Q"]["value"],
                q1_q3_evaluation_metrics["2Q"]["value"],
                q1_q3_evaluation_metrics["3Q"]["value"],
                q1_q3_evaluation_metrics["1〜3Q累計"]["value"],
            ],
            "2006〜2025年中央値": [
                q1_q3_evaluation_metrics["1Q"]["median"],
                q1_q3_evaluation_metrics["2Q"]["median"],
                q1_q3_evaluation_metrics["3Q"]["median"],
                q1_q3_evaluation_metrics["1〜3Q累計"]["median"],
            ],
            "中央値との差率（%）": [
                q1_q3_evaluation_metrics["1Q"]["median_pct"],
                q1_q3_evaluation_metrics["2Q"]["median_pct"],
                q1_q3_evaluation_metrics["3Q"]["median_pct"],
                q1_q3_evaluation_metrics["1〜3Q累計"]["median_pct"],
            ],
            "低い方からの順位（21年中）": [
                q1_q3_evaluation_metrics["1Q"]["low_rank"],
                q1_q3_evaluation_metrics["2Q"]["low_rank"],
                q1_q3_evaluation_metrics["3Q"]["low_rank"],
                q1_q3_evaluation_metrics["1〜3Q累計"]["low_rank"],
            ],
            "前年比（%）": [
                q1_q3_evaluation_metrics["1Q"]["yoy_pct"],
                q1_q3_evaluation_metrics["2Q"]["yoy_pct"],
                q1_q3_evaluation_metrics["3Q"]["yoy_pct"],
                q1_q3_evaluation_metrics["1〜3Q累計"]["yoy_pct"],
            ],
        }
    )

    q1_q3_history_long_df = (
        q1_q3_all_years_df
        .select("year", "q1_units", "q2_units", "q3_units")
        .unpivot(index="year", variable_name="quarter", value_name="units")
        .with_columns(
            pl.col("quarter").replace(
                {"q1_units": "1Q", "q2_units": "2Q", "q3_units": "3Q"}
            ),
            pl.when((pl.col("year") == 2026) & (pl.col("quarter") == "q3_units"))
            .then(pl.lit("予測"))
            .otherwise(pl.lit("実績"))
            .alias("区分"),
        )
    )

    return q1_q3_evaluation_df, q1_q3_evaluation_metrics, q1_q3_history_long_df


@app.cell
def q1_q3_history_comparison_output(
    q1_q3_evaluation_df,
    q1_q3_evaluation_metrics,
    q1_q3_history_long_df,
):
    _q1 = q1_q3_evaluation_metrics["1Q"]
    _q2 = q1_q3_evaluation_metrics["2Q"]
    _q3 = q1_q3_evaluation_metrics["3Q"]
    _h1 = q1_q3_evaluation_metrics["上期"]
    _ytd = q1_q3_evaluation_metrics["1〜3Q累計"]

    _quarter_chart_base = alt.Chart(q1_q3_history_long_df)
    _quarter_history_chart = (
        _quarter_chart_base
        .transform_filter(alt.datum.year < 2026)
        .mark_line(point=True)
        .encode(
            x=alt.X("year:O", title="年"),
            y=alt.Y("units:Q", title="販売台数"),
            color=alt.Color("quarter:N", title="四半期"),
            tooltip=[
                alt.Tooltip("year:O", title="年"),
                alt.Tooltip("quarter:N", title="四半期"),
                alt.Tooltip("units:Q", title="販売台数", format=","),
            ],
        )
    )
    _quarter_2026_points = (
        _quarter_chart_base
        .transform_filter(alt.datum.year == 2026)
        .mark_point(filled=True, size=110)
        .encode(
            x=alt.X("year:O", title="年"),
            y=alt.Y("units:Q", title="販売台数"),
            color=alt.Color("quarter:N", title="四半期"),
            shape=alt.Shape("区分:N", title="区分"),
            tooltip=[
                alt.Tooltip("year:O", title="年"),
                alt.Tooltip("quarter:N", title="四半期"),
                alt.Tooltip("区分:N", title="区分"),
                alt.Tooltip("units:Q", title="販売台数", format=","),
            ],
        )
    )

    mo.vstack([
        mo.md(f"""
    ## 2026年1〜3Qの歴史比較

    **結論：3Qが特異的に弱い。** 年初から弱含みではあるものの、歴史的な低水準に落ち込んだのは3Qである。

    - **1Q** は{_q1['value']:,}台。中央値比{_q1['median_pct']:+.1f}%で、低い方から{_q1['low_rank']}位。やや低めだが過去最低圏ではない。
    - **2Q** は{_q2['value']:,}台。中央値比{_q2['median_pct']:+.1f}%で、低い方から{_q2['low_rank']}位。おおむね歴史的な中央値の水準。
    - **上期累計** は{_h1['value']:,}台。中央値比{_h1['median_pct']:+.1f}%だが、前年上期比では{_h1['yoy_pct']:+.1f}%。
    - **3Q予測** は{_q3['value']:,}台。中央値比{_q3['median_pct']:+.1f}%で、低い方から{_q3['low_rank']}位（最下位）。前年同期比も{_q3['yoy_pct']:+.1f}%。
    - **1〜3Q累計予測** は{_ytd['value']:,}台で、中央値比{_ytd['median_pct']:+.1f}%、低い方から{_ytd['low_rank']}位。上期の弱さよりも、3Qの急落が累計を大きく押し下げている。
    """),
        q1_q3_evaluation_df,
        (_quarter_history_chart + _quarter_2026_points).properties(
            width=720,
            height=340,
            title="1〜3Qのハード販売台数推移（2006年以降）",
        ),
    ])
    return


@app.cell
def q3_cause_analysis_calculation(
    annotation_all_df: pl.DataFrame,
    forecast_source_date,
    forecast_target_date,
    hard_sales_all_df: pl.DataFrame,
    hardware_forecast_df,
):
    _q3_2025_hardware_long_df = (
        hard_sales_all_df
        .filter((pl.col("year") == 2025) & (pl.col("q_num") == 3))
        .group_by(["hw", "full_name"])
        .agg(pl.col("units").sum().alias("units"))
        .with_columns(pl.lit("2025年3Q実績").alias("period"))
    )
    _q3_2026_hardware_long_df = hardware_forecast_df.select(
        "hw",
        "full_name",
        pl.col("q3_forecast").alias("units"),
    ).with_columns(pl.lit("2026年3Q予測").alias("period"))

    _q3_cause_yoy_base_df = (
        pl.concat([_q3_2025_hardware_long_df, _q3_2026_hardware_long_df])
        .pivot(
            on="period",
            index=["hw", "full_name"],
            values="units",
            aggregate_function="first",
        )
        .fill_null(0)
        .with_columns(
            (
                pl.col("2026年3Q予測") - pl.col("2025年3Q実績")
            ).alias("前年比差")
        )
    )
    _q3_yoy_total_decline = -_q3_cause_yoy_base_df.select(
        pl.col("前年比差").sum()
    ).item()
    q3_cause_yoy_hardware_df = (
        _q3_cause_yoy_base_df
        .with_columns(
            ((-pl.col("前年比差") / _q3_yoy_total_decline) * 100)
            .round(1)
            .alias("減少寄与率（%）")
        )
        .sort("前年比差")
    )

    _q2_2026_hardware_long_df = (
        hard_sales_all_df
        .filter((pl.col("year") == 2026) & (pl.col("q_num") == 2))
        .group_by(["hw", "full_name"])
        .agg(pl.col("units").sum().alias("units"))
        .with_columns(pl.lit("2026年2Q実績").alias("period"))
    )
    _q3_cause_q2q3_base_df = (
        pl.concat([_q2_2026_hardware_long_df, _q3_2026_hardware_long_df])
        .pivot(
            on="period",
            index=["hw", "full_name"],
            values="units",
            aggregate_function="first",
        )
        .fill_null(0)
        .with_columns(
            (
                pl.col("2026年3Q予測") - pl.col("2026年2Q実績")
            ).alias("前期差")
        )
    )
    _q3_qoq_total_decline = -_q3_cause_q2q3_base_df.select(
        pl.col("前期差").sum()
    ).item()
    q3_cause_q2q3_hardware_df = (
        _q3_cause_q2q3_base_df
        .with_columns(
            ((-pl.col("前期差") / _q3_qoq_total_decline) * 100)
            .round(1)
            .alias("減少寄与率（%）")
        )
        .sort("前期差")
    )

    _ns2_2026_weekly_df = (
        hard_sales_all_df
        .filter((pl.col("year") == 2026) & (pl.col("hw") == "NS2"))
        .select("report_date", "units")
    )
    _ns2_price_before_df = _ns2_2026_weekly_df.filter(
        (pl.col("report_date") >= date(2026, 5, 3))
        & (pl.col("report_date") <= date(2026, 5, 24))
    )
    _ns2_price_after_df = _ns2_2026_weekly_df.filter(
        (pl.col("report_date") >= date(2026, 5, 31))
        & (pl.col("report_date") <= date(2026, 6, 28))
    )
    _ns2_q3_actual_df = _ns2_2026_weekly_df.filter(
        (pl.col("report_date") >= date(2026, 7, 5))
        & (pl.col("report_date") <= forecast_source_date)
    )
    _ns2_q3_forecast = hardware_forecast_df.filter(pl.col("hw") == "NS2").select(
        "q3_forecast"
    ).item()
    q3_cause_price_period_df = pl.DataFrame(
        {
            "期間": [
                "値上げ前4週（5/3〜5/24）",
                "値上げ実施後5週（5/31〜6/28）",
                "3Q実績12週（7/5〜9/20）",
                "3Q予測13週（7/5〜9/27）",
            ],
            "注釈上の主な出来事": [
                "5/8 NS2値上げ発表の前後",
                "5/25 NS2値上げ実施後",
                "3Qの実績",
                "3Q実績 + 9/27予測",
            ],
            "販売台数": [
                _ns2_price_before_df.select(pl.col("units").sum()).item(),
                _ns2_price_after_df.select(pl.col("units").sum()).item(),
                _ns2_q3_actual_df.select(pl.col("units").sum()).item(),
                _ns2_q3_forecast,
            ],
            "週数": [
                _ns2_price_before_df.height,
                _ns2_price_after_df.height,
                _ns2_q3_actual_df.height,
                13,
            ],
            "週平均": [
                round(_ns2_price_before_df.select(pl.col("units").mean()).item()),
                round(_ns2_price_after_df.select(pl.col("units").mean()).item()),
                round(_ns2_q3_actual_df.select(pl.col("units").mean()).item()),
                round(_ns2_q3_forecast / 13),
            ],
        }
    )

    _q3_cause_weekly_hardware_df = (
        hard_sales_all_df
        .filter(
            (pl.col("year") == 2026)
            & pl.col("hw").is_in(["NS2", "NSW", "PS5", "XSX"])
        )
        .sort(["hw", "report_date"])
        .with_columns(pl.col("units").shift(1).over("hw").alias("_prior_units"))
        .with_columns(
            pl.col("_prior_units")
            .rolling_mean(window_size=4)
            .over("hw")
            .alias("prior_4w_avg")
        )
    )
    _q3_cause_annotations_df = (
        annotation_all_df
        .filter(
            (pl.col("report_date") >= date(2026, 7, 5))
            & (pl.col("report_date") <= forecast_source_date)
        )
        .group_by(["report_date", "hw"])
        .agg(
            pl.col("note").alias("注釈"),
            pl.col("level").max().alias("注釈レベル"),
        )
    )
    q3_cause_event_week_df = (
        _q3_cause_annotations_df
        .join(
            _q3_cause_weekly_hardware_df.select(
                "report_date", "hw", "units", "prior_4w_avg"
            ),
            on=["report_date", "hw"],
            how="left",
        )
        .with_columns(
            (pl.col("units") / pl.col("prior_4w_avg") - 1)
            .mul(100)
            .round(1)
            .alias("直前4週平均との差（%）")
        )
        .select(
            pl.col("report_date").alias("週"),
            pl.col("hw").alias("ハード"),
            pl.col("注釈"),
            pl.col("units").alias("週販"),
            pl.col("prior_4w_avg").round(0).cast(pl.Int64).alias("直前4週平均"),
            pl.col("直前4週平均との差（%）"),
        )
        .sort("週")
    )

    _q3_weekly_actual_total_df = (
        hard_sales_all_df
        .filter((pl.col("year") == 2026) & (pl.col("q_num") == 3))
        .group_by("report_date")
        .agg(pl.col("units").sum().alias("total_units"))
        .with_columns(pl.lit("実績").alias("区分"))
    )
    q3_cause_weekly_total_df = (
        _q3_weekly_actual_total_df
        .vstack(
            pl.DataFrame(
                {
                    "report_date": [forecast_target_date],
                    "total_units": [
                        hardware_forecast_df.select(pl.col("forecast_09_27").sum()).item()
                    ],
                    "区分": ["予測"],
                },
                schema={
                    "report_date": pl.Date,
                    "total_units": pl.Int64,
                    "区分": pl.String,
                },
            )
        )
        .sort("report_date")
    )

    q3_cause_metrics = {
        "total_yoy_decline": _q3_yoy_total_decline,
        "ns2_yoy_decline": -q3_cause_yoy_hardware_df.filter(pl.col("hw") == "NS2").select("前年比差").item(),
        "ns2_yoy_share": q3_cause_yoy_hardware_df.filter(pl.col("hw") == "NS2").select("減少寄与率（%）").item(),
        "ns2_qoq_decline": -q3_cause_q2q3_hardware_df.filter(pl.col("hw") == "NS2").select("前期差").item(),
        "ns2_qoq_share": q3_cause_q2q3_hardware_df.filter(pl.col("hw") == "NS2").select("減少寄与率（%）").item(),
        "price_before_weekly": q3_cause_price_period_df.row(0, named=True)["週平均"],
        "price_after_weekly": q3_cause_price_period_df.row(1, named=True)["週平均"],
        "q3_ns2_weekly": q3_cause_price_period_df.row(3, named=True)["週平均"],
    }

    return (
        q3_cause_event_week_df,
        q3_cause_metrics,
        q3_cause_price_period_df,
        q3_cause_weekly_total_df,
        q3_cause_yoy_hardware_df,
    )


@app.cell
def q3_cause_analysis_output(
    q3_cause_event_week_df,
    q3_cause_metrics,
    q3_cause_price_period_df,
    q3_cause_weekly_total_df,
    q3_cause_yoy_hardware_df,
):
    _cause = q3_cause_metrics
    _q3_total_chart = (
        alt.Chart(q3_cause_weekly_total_df)
        .mark_bar()
        .encode(
            x=alt.X("report_date:T", title="週", axis=alt.Axis(format="%m/%d")),
            y=alt.Y("total_units:Q", title="全ハード週販"),
            color=alt.Color(
                "区分:N",
                title="区分",
                scale=alt.Scale(domain=["実績", "予測"], range=["#4c78a8", "#e45756"]),
            ),
            tooltip=[
                alt.Tooltip("report_date:T", title="週", format="%Y-%m-%d"),
                alt.Tooltip("区分:N", title="区分"),
                alt.Tooltip("total_units:Q", title="販売台数", format=","),
            ],
        )
        .properties(width=720, height=250, title="2026年3Qの全ハード週販")
    )

    mo.vstack([
        mo.md(f"""
    ## 2026年3Qが落ち込んだ要因の推定

    **最も強い説明は、NS2の前年反動と値上げ前の需要前倒しです。** ただし、週販と注釈の時点対応からの推定であり、因果を断定するものではありません。

    1. **NS2が前年比減少の中心** — 全ハードの前年比減少{_cause['total_yoy_decline']:,}台のうち、NS2は{_cause['ns2_yoy_decline']:,}台、**{_cause['ns2_yoy_share']:.1f}%**を占める。注釈では2025年6月にSwitch2発売が記録されており、2025年3Q（939,938台）は発売直後の高い需要を含む。2026年3Q予測の390,083台との比較には大きな発売反動がある。
    2. **5月の値上げ前後でNS2需要が前倒しされた可能性** — 注釈には5/8の値上げ発表、5/25の値上げ実施がある。直前4週の週平均{_cause['price_before_weekly']:,}台が、実施後5週では{_cause['price_after_weekly']:,}台へ急減し、3Q予測の週平均も{_cause['q3_ns2_weekly']:,}台にとどまる。2Qから3Qへの全ハード減少でも、NS2は{_cause['ns2_qoq_decline']:,}台、**{_cause['ns2_qoq_share']:.1f}%**を占める。
    3. **3Qのイベント効果は局所的** — 注釈にあるSplatoon Raiders週はNS2が直前4週平均比+80.2%と大きく伸びた一方、ELDEN RING週は-23.8%、9月のDirect週は+13.3%だった。複数のソフト・配信イベントはあったが、3Q全体の基調を反転させる持続的な上振れは確認できない。
    4. **NSWの縮小とPS5の弱含みは副次要因** — NSWは前年比130,440台減、PS5は31,067台減だが、寄与はNS2より小さい。

    注釈データには供給制約や景気要因を直接示す記録がないため、それらを主因とは評価できない。
    """),
        mo.md("### 前年比のハード別寄与"),
        q3_cause_yoy_hardware_df,
        mo.md("### NS2の値上げ前後と3Qの水準"),
        q3_cause_price_period_df,
        _q3_total_chart,
        mo.md("### 注釈がある週の販売反応"),
        q3_cause_event_week_df,
    ])
    return


@app.cell
def q3_21st_century_comparison_calculation(
    hard_sales_all_df: pl.DataFrame,
    q3_forecast_total,
    q3_forecast_weeks,
):
    q3_21st_century_historical_df = (
        hard_sales_all_df
        .filter(
            (pl.col("year") >= 2001)
            & (pl.col("year") <= 2025)
            & (pl.col("q_num") == 3)
        )
        .group_by("year")
        .agg(
            pl.col("units").sum().alias("第3四半期販売台数"),
            pl.col("report_date").n_unique().alias("週数"),
        )
        .with_columns(
            (pl.col("第3四半期販売台数") / pl.col("週数"))
            .round(0)
            .cast(pl.Int64)
            .alias("週平均販売台数"),
            pl.lit("実績").alias("区分"),
        )
        .sort("year")
    )

    _q3_2026_21st_century_df = pl.DataFrame(
        {
            "year": [2026],
            "第3四半期販売台数": [q3_forecast_total],
            "週数": [q3_forecast_weeks],
            "週平均販売台数": [round(q3_forecast_total / q3_forecast_weeks)],
            "区分": ["予測"],
        },
        schema={
            "year": pl.Int16,
            "第3四半期販売台数": pl.Int64,
            "週数": pl.UInt32,
            "週平均販売台数": pl.Int64,
            "区分": pl.String,
        },
    )
    q3_21st_century_comparison_df = (
        q3_21st_century_historical_df
        .vstack(_q3_2026_21st_century_df)
        .with_columns(
            pl.col("第3四半期販売台数")
            .rank("ordinal", descending=True)
            .alias("販売台数順位"),
            pl.col("週平均販売台数")
            .rank("ordinal", descending=True)
            .alias("週平均順位"),
        )
        .sort("year")
    )

    _q3_2001_2005_min = (
        q3_21st_century_historical_df
        .filter((pl.col("year") >= 2001) & (pl.col("year") <= 2005))
        .sort("第3四半期販売台数")
        .row(0, named=True)
    )
    _q3_21st_century_previous_min = (
        q3_21st_century_historical_df
        .sort("第3四半期販売台数")
        .row(0, named=True)
    )
    q3_21st_century_metrics = {
        "rank": q3_21st_century_comparison_df
        .filter(pl.col("year") == 2026)
        .select("販売台数順位")
        .item(),
        "weekly_rank": q3_21st_century_comparison_df
        .filter(pl.col("year") == 2026)
        .select("週平均順位")
        .item(),
        "count": q3_21st_century_comparison_df.height,
        "early_min_year": _q3_2001_2005_min["year"],
        "early_min_units": _q3_2001_2005_min["第3四半期販売台数"],
        "early_min_delta": q3_forecast_total - _q3_2001_2005_min["第3四半期販売台数"],
        "early_min_pct": round(
            (q3_forecast_total / _q3_2001_2005_min["第3四半期販売台数"] - 1) * 100,
            1,
        ),
        "previous_min_year": _q3_21st_century_previous_min["year"],
        "previous_min_units": _q3_21st_century_previous_min["第3四半期販売台数"],
        "previous_min_delta": q3_forecast_total
        - _q3_21st_century_previous_min["第3四半期販売台数"],
        "previous_min_pct": round(
            (
                q3_forecast_total
                / _q3_21st_century_previous_min["第3四半期販売台数"]
                - 1
            )
            * 100,
            1,
        ),
    }

    q3_21st_century_reference_df = (
        q3_21st_century_comparison_df
        .filter(
            pl.col("year").is_in([2001, 2002, 2003, 2004, 2005, 2016, 2026])
        )
        .select(
            pl.col("year").alias("年"),
            "区分",
            "第3四半期販売台数",
            "週数",
            "週平均販売台数",
        )
        .sort("年")
    )

    return q3_21st_century_metrics, q3_21st_century_reference_df


@app.cell
def q3_21st_century_comparison_output(
    q3_21st_century_metrics,
    q3_21st_century_reference_df,
    q3_forecast_total,
):
    _q3_21 = q3_21st_century_metrics
    mo.vstack([
        mo.md(f"""
    ## 21世紀における2026年3Qの位置

    **はい。2026年3Q予測の{q3_forecast_total:,}台は、2001〜2026年の{_q3_21['count']}年比較で最下位です。** 13週換算の週平均でも最下位です。

    - 2001〜2005年で最も低いのは{_q3_21['early_min_year']}年の{_q3_21['early_min_units']:,}台で、2026年は**{abs(_q3_21['early_min_delta']):,}台（{_q3_21['early_min_pct']:+.1f}%）**下回る。
    - 21世紀全体の従来最低は{_q3_21['previous_min_year']}年の{_q3_21['previous_min_units']:,}台で、2026年はさらに**{abs(_q3_21['previous_min_delta']):,}台（{_q3_21['previous_min_pct']:+.1f}%）**低い。
    """),
        q3_21st_century_reference_df,
    ])
    return


@app.cell
def all_quarter_rank_calculation(
    hard_sales_all_df: pl.DataFrame,
    q3_forecast_total,
    q3_forecast_weeks,
):
    _quarter_rank_historical_df = (
        hard_sales_all_df
        .filter((pl.col("year") >= 2001) & (pl.col("year") <= 2025))
        .group_by(["year", "q_num"])
        .agg(
            pl.col("units").sum().alias("販売台数"),
            pl.col("report_date").n_unique().alias("週数"),
        )
        .with_columns(
            (pl.col("販売台数") / pl.col("週数"))
            .round(0)
            .cast(pl.Int64)
            .alias("週平均販売台数"),
            pl.lit("実績").alias("区分"),
        )
    )
    _quarter_rank_2026_q1q2_df = (
        hard_sales_all_df
        .filter((pl.col("year") == 2026) & pl.col("q_num").is_in([1, 2]))
        .group_by(["year", "q_num"])
        .agg(
            pl.col("units").sum().alias("販売台数"),
            pl.col("report_date").n_unique().alias("週数"),
        )
        .with_columns(
            (pl.col("販売台数") / pl.col("週数"))
            .round(0)
            .cast(pl.Int64)
            .alias("週平均販売台数"),
            pl.lit("実績").alias("区分"),
        )
    )
    _quarter_rank_2026_q3_df = pl.DataFrame(
        {
            "year": [2026],
            "q_num": [3],
            "販売台数": [q3_forecast_total],
            "週数": [q3_forecast_weeks],
            "週平均販売台数": [round(q3_forecast_total / q3_forecast_weeks)],
            "区分": ["予測"],
        },
        schema={
            "year": pl.Int16,
            "q_num": pl.Int8,
            "販売台数": pl.Int64,
            "週数": pl.UInt32,
            "週平均販売台数": pl.Int64,
            "区分": pl.String,
        },
    )
    quarterly_rank_all_df = (
        pl.concat(
            [
                _quarter_rank_historical_df,
                _quarter_rank_2026_q1q2_df,
                _quarter_rank_2026_q3_df,
            ]
        )
        .with_columns(
            pl.col("販売台数").rank("ordinal", descending=True).alias("販売台数順位"),
            pl.col("週平均販売台数")
            .rank("ordinal", descending=True)
            .alias("週平均順位"),
        )
        .sort(["year", "q_num"])
    )

    _quarter_rank_current = quarterly_rank_all_df.filter(
        (pl.col("year") == 2026) & (pl.col("q_num") == 3)
    ).row(0, named=True)
    _quarter_rank_previous_min = (
        quarterly_rank_all_df
        .filter(~((pl.col("year") == 2026) & (pl.col("q_num") == 3)))
        .sort("販売台数")
        .row(0, named=True)
    )
    quarterly_rank_metrics = {
        "rank": _quarter_rank_current["販売台数順位"],
        "weekly_rank": _quarter_rank_current["週平均順位"],
        "count": quarterly_rank_all_df.height,
        "previous_min_year": _quarter_rank_previous_min["year"],
        "previous_min_quarter": _quarter_rank_previous_min["q_num"],
        "previous_min_units": _quarter_rank_previous_min["販売台数"],
        "previous_min_delta": _quarter_rank_current["販売台数"]
        - _quarter_rank_previous_min["販売台数"],
        "previous_min_pct": round(
            (
                _quarter_rank_current["販売台数"]
                / _quarter_rank_previous_min["販売台数"]
                - 1
            )
            * 100,
            1,
        ),
    }

    quarterly_rank_lowest_df = (
        quarterly_rank_all_df
        .with_columns(pl.format("{}Q{}", pl.col("year"), pl.col("q_num")).alias("四半期"))
        .select(
            "四半期",
            "区分",
            "販売台数",
            "週数",
            "週平均販売台数",
            "販売台数順位",
            "週平均順位",
        )
        .sort("販売台数")
    )

    return quarterly_rank_lowest_df, quarterly_rank_metrics


@app.cell
def all_quarter_rank_output(
    q3_forecast_total,
    quarterly_rank_lowest_df,
    quarterly_rank_metrics,
):
    _quarter_rank = quarterly_rank_metrics
    mo.vstack([
        mo.md(f"""
    ## 全四半期に対する2026年3Qの順位

    2001年1Q〜2026年3Qの**103四半期**を比較すると、2026年3Q予測の{q3_forecast_total:,}台は **{_quarter_rank['rank']}位 / {_quarter_rank['count']}位（最下位）** です。13週あたりの週平均でも **{_quarter_rank['weekly_rank']}位 / {_quarter_rank['count']}位（最下位）** です。

    従来の最低は{_quarter_rank['previous_min_year']}年{_quarter_rank['previous_min_quarter']}Qの{_quarter_rank['previous_min_units']:,}台で、2026年3Qは **{abs(_quarter_rank['previous_min_delta']):,}台（{_quarter_rank['previous_min_pct']:+.1f}%）**下回ります。
    """),
        mo.md("### 販売台数が低い順の全四半期ランキング"),
        quarterly_rank_lowest_df,
    ])
    return


@app.cell
def all_quarter_worst10_chart(quarterly_rank_lowest_df):
    _quarterly_bottom10 = quarterly_rank_lowest_df.head(10)
    _quarterly_bottom10_bar = (
        alt.Chart(_quarterly_bottom10)
        .mark_bar()
        .encode(
            y=alt.Y(
                "四半期:N",
                sort=alt.SortField(field="販売台数", order="ascending"),
                title=None,
            ),
            x=alt.X("販売台数:Q", title="販売台数"),
            color=alt.condition(
                alt.datum.区分 == "予測",
                alt.value("#e45756"),
                alt.value("#4c78a8"),
            ),
            tooltip=[
                alt.Tooltip("四半期:N", title="四半期"),
                alt.Tooltip("区分:N", title="区分"),
                alt.Tooltip("販売台数:Q", title="販売台数", format=","),
                alt.Tooltip("週数:Q", title="週数"),
                alt.Tooltip("週平均販売台数:Q", title="週平均", format=","),
            ],
        )
    )
    _quarterly_bottom10_text = (
        alt.Chart(_quarterly_bottom10)
        .mark_text(align="left", dx=4)
        .encode(
            y=alt.Y("四半期:N", sort=alt.SortField(field="販売台数", order="ascending")),
            x=alt.X("販売台数:Q"),
            text=alt.Text("販売台数:Q", format=","),
        )
    )

    mo.vstack([
        mo.md("## 四半期集計ワースト10"),
        (_quarterly_bottom10_bar + _quarterly_bottom10_text).properties(
            width=720,
            height=330,
            title="2001年以降の四半期販売台数：ワースト10",
        ),
        mo.md("赤は2026年3Qの予測値、青は実績値。"),
    ])
    return


if __name__ == "__main__":
    app.run()
