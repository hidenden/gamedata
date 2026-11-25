"""元テーブルのデータから週次販売データを組み立てるローダー。"""

import sqlite3
from contextlib import closing
from pathlib import Path

import polars as pl

from ._hard_sales_columns import with_sales_columns
from .hard_info import DB_PATH

_hard_sales_cache: pl.DataFrame | None = None
_all_hw_list: list[str] | None = None
_all_maker_list: list[str] | None = None


def read_data() -> tuple[pl.DataFrame, pl.DataFrame]:
    """同じ時点の gamehard_info と gamehard_weekly を、この順に返す。

    読み込み元を差し替える場合も列名は元テーブルに合わせる。
    launch_date と report_date は Date 型、台数と集計日数は Int64 型。
    """
    uri = Path(DB_PATH).resolve().as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as conn:
        conn.execute("BEGIN")
        info = pl.read_database(
            "SELECT id, launch_date, maker_name, full_name FROM gamehard_info",
            conn,
            schema_overrides=dict.fromkeys(
                ("id", "launch_date", "maker_name", "full_name"), pl.String
            ),
        )
        weekly = pl.read_database(
            "SELECT id, report_date, period_date, hw, units, adjust_units FROM gamehard_weekly",
            conn,
            schema_overrides={
                "id": pl.String,
                "report_date": pl.String,
                "period_date": pl.Int64,
                "hw": pl.String,
                "units": pl.Int64,
                "adjust_units": pl.Int64,
            },
        )
    return (
        info.with_columns(pl.col("launch_date").str.to_date("%Y-%m-%d")),
        weekly.with_columns(pl.col("report_date").str.to_date("%Y-%m-%d")),
    )


def _normalize_weekly(weekly: pl.DataFrame) -> pl.DataFrame:
    fortnight = pl.col("period_date") == 14
    split = weekly.filter(fortnight)
    if split.is_empty():
        return weekly

    # 前週には元の台数の半分（切り捨て）、報告週には残りと補正値を割り当てる。
    units = pl.col("units")
    previous = split.with_columns(
        report_date=pl.col("report_date") - pl.duration(days=7),
        units=units // 2,
        adjust_units=pl.lit(0, dtype=pl.Int64),
        period_date=pl.lit(7, dtype=pl.Int64),
    ).with_columns(id=pl.concat_str("report_date", "hw", separator="_"))
    if previous["id"].is_duplicated().any() or not previous.join(
        weekly.select("id"), on="id", how="semi"
    ).is_empty():
        raise ValueError("14日集計の分割先に同じ週次IDが存在します")
    reported = weekly.with_columns(
        units=pl.when(fortnight).then(units - units // 2).otherwise(units),
        period_date=pl.when(fortnight).then(7).otherwise(pl.col("period_date")),
    )
    return pl.concat([reported, previous])


def load_hard_sales2(no_cache: bool = False) -> pl.DataFrame:
    """元テーブルから load_hard_sales() と同じ列・型・順序の販売データを返す。

    no_cache=True で入力を再読み込みし、キャッシュを更新する。
    """
    global _hard_sales_cache, _all_hw_list, _all_maker_list
    if _hard_sales_cache is not None and not no_cache:
        return _hard_sales_cache.clone()

    info, weekly = read_data()
    report = pl.col("report_date")
    launch = pl.col("launch_date")
    period = pl.col("period_date")
    units = pl.col("units")
    delta_day = (report - launch).dt.total_days()
    delta_year = report.dt.year() - launch.dt.year()
    sales = (
        _normalize_weekly(weekly)
        .join(info, left_on="hw", right_on="id")
        .with_columns(units=units + pl.col("adjust_units").fill_null(0))
        .select(
            weekly_id=pl.col("id"),
            begin_date=report - pl.duration(days=period - 1),
            end_date=report,
            report_date=report,
            period_date=period,
            hw=pl.col("hw"),
            units=units,
            adjust_units=pl.col("adjust_units"),
            year=report.dt.year(),
            month=report.dt.month(),
            mday=report.dt.day(),
            week=(report.dt.day() - 1) // 7 + 1,
            delta_day=delta_day,
            delta_week=delta_day // 7,
            delta_month=delta_year * 12 + report.dt.month() - launch.dt.month(),
            delta_year=delta_year,
            avg_units=pl.when(period > 0).then(units // period).otherwise(0),
            sum_units=units.cum_sum().over("hw", order_by="report_date"),
            launch_date=launch,
            maker_name=pl.col("maker_name"),
            full_name=pl.col("full_name"),
        )
    )
    _hard_sales_cache = with_sales_columns(sales)
    _all_hw_list = None
    _all_maker_list = None
    return _hard_sales_cache.clone()
