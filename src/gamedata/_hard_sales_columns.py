"""販売データのローダーが共有する派生列。"""

import polars as pl


def with_sales_columns(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df.with_columns(
            pl.col("period_date").cast(pl.Int16),
            pl.col("year").cast(pl.Int16),
            pl.col("month").cast(pl.Int16),
            pl.col("mday").cast(pl.Int16),
            pl.col("week").cast(pl.Int16),
            pl.col("delta_day").cast(pl.Int32),
            pl.col("delta_week").cast(pl.Int32),
            pl.col("delta_month").cast(pl.Int16),
            pl.col("delta_year").cast(pl.Int16),
        )
        .with_columns(
            q_num=pl.col("report_date").dt.quarter().cast(pl.Int8),
            fiscal_year=pl.when(pl.col("month") <= 3)
            .then(pl.col("year"))
            .otherwise(pl.col("year") + 1)
            .cast(pl.Int16),
            fiscal_month=(((pl.col("month") + 8) % 12) + 1).cast(pl.Int8),
            index_week=(pl.col("delta_week") + 1).cast(pl.Int32),
            index_month=(pl.col("delta_month") + 1).cast(pl.Int16),
            index_year=(pl.col("delta_year") + 1).cast(pl.Int16),
        )
        .with_columns(
            fq_num=((pl.col("fiscal_month") - 1) // 3 + 1).cast(pl.Int8),
            quarter=(
                pl.col("year").cast(pl.Utf8) + "Q" + pl.col("q_num").cast(pl.Utf8)
            ),
        )
        .with_columns(
            fiscal_quarter=(
                pl.col("fiscal_year").cast(pl.Utf8)
                + "FQ"
                + pl.col("fq_num").cast(pl.Utf8)
            ),
        )
        .sort("weekly_id")
        .with_columns(
            pl.col("units").diff().over("hw").alias("units_diff"),
            pl.col("units")
            .rolling_mean(window_size=4)
            .round(0)
            .cast(pl.Int64)
            .over("hw")
            .alias("ma4w"),
            pl.col("units")
            .rolling_mean(window_size=13)
            .round(0)
            .cast(pl.Int64)
            .over("hw")
            .alias("ma13w"),
            pl.col("units")
            .rolling_mean(window_size=52)
            .round(0)
            .cast(pl.Int64)
            .over("hw")
            .alias("ma52w"),
            pl.col("units")
            .cum_sum()
            .over(pl.col("hw"), pl.col("year"))
            .alias("yearly_sum_units"),
        )
        .with_columns(
            pl.col("report_date").dt.ordinal_day().alias("yday").cast(pl.Int16),
            (pl.col("report_date").dt.strftime("%U").cast(pl.Int16) + 1).alias("yweek"),
        )
    )
