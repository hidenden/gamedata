"""元テーブルのデータから週次販売データを組み立てるローダー。"""

from datetime import datetime, timedelta
from typing import List

import polars as pl

from . import hard_info as hi
from .data_source import read_tables

# Polars Configuration
(
    pl.Config.set_tbl_rows(30)
    .set_tbl_cols(-1)
    .set_float_precision(2)
    .set_thousands_separator(",")
    .set_trim_decimal_zeros(True)
    .set_tbl_hide_column_data_types(False)
    .set_tbl_hide_dataframe_shape(True)
    # .set_tbl_column_data_type_inline(True)
)

_hard_sales_cache: pl.DataFrame | None = None
_all_hw_list: list[str] | None = None
_all_maker_list: list[str] | None = None


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


def _with_sales_columns(df: pl.DataFrame) -> pl.DataFrame:
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


def load_hard_sales2(no_cache: bool = False) -> pl.DataFrame:
    """週次販売データと機種情報から、補正済みの販売台数と集計指標を返す。

    no_cache=True で入力を再読み込みし、キャッシュを更新する。
    """
    global _hard_sales_cache, _all_hw_list, _all_maker_list
    if _hard_sales_cache is not None and not no_cache:
        return _hard_sales_cache.clone()

    info, weekly = read_tables("gamehard_info", "gamehard_weekly")
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
    _hard_sales_cache = _with_sales_columns(sales)
    _all_hw_list = None
    _all_maker_list = None
    return _hard_sales_cache.clone()


def current_report_date(df: pl.DataFrame) -> datetime:
    """
    DataFrameから最新の報告日を取得する関数。

    Args:
        df: load_hard_sales2()の戻り値のDataFrame

    Returns:
        datetime: 最新の報告日
    """
    return df.select(pl.col("report_date").max()).item()


def get_hw(df: pl.DataFrame) -> List[str]:
    """
    DataFrameからハードウェア名のユニークなリストを取得する。

    Args:
        df: load_hard_sales2()の戻り値のDataFrame

    Returns:
        List[str]: ハードウェア名のユニークなリスト
    """
    return hi.sort_hard(df.select(["hw"]).unique().to_series(0).to_list())


def get_active_hw(days: int = 365) -> List[str]:
    """
    直近1年間のデータを元にアクティブなハードウェア名のリストを取得する。

    Returns:
        List[str]: アクティブなハードウェア名のリスト
    """
    base_df = load_hard_sales2()
    now = datetime.now()
    one_year_ago = now - timedelta(days=days)
    recent_df = base_df.filter(pl.col("report_date") >= one_year_ago)
    active_hw = get_hw(recent_df)
    return active_hw


def get_hw_all(true_all: bool = False) -> List[str]:
    """
    データベースに存在する全てのハードウェア名のリストを取得する。

    Returns:
        List[str]: 全てのハードウェア名のリスト
    """
    global _all_hw_list
    if _all_hw_list is not None:
        return _all_hw_list

    base_df = load_hard_sales2()
    hw_list = get_hw(base_df)
    remove_hw_list = ["PKS", "PS", "NeoGeoP", "SATURN", "GB"]
    if not true_all:
        hw_list = [hw for hw in hw_list if hw not in remove_hw_list]

    _all_hw_list = hw_list
    return hw_list


def get_maker(df: pl.DataFrame) -> List[str]:
    """
    DataFrameからメーカー名のユニークなリストを取得する。

    Args:
        df: load_hard_sales2()の戻り値のDataFrame

    Returns:
        List[str]: メーカー名のユニークなリスト
    """
    return hi.sort_maker(
        df.select(pl.col("maker_name")).unique().to_series(0).to_list()
    )


def get_active_maker(days: int = 365) -> List[str]:
    """
    直近1年間のデータを元にアクティブなメーカー名のリストを取得する。

    Returns:
        List[str]: アクティブなメーカー名のリスト
    """
    base_df = load_hard_sales2()
    now = datetime.now()
    one_year_ago = now - timedelta(days=days)
    recent_df = base_df.filter(pl.col("report_date") >= one_year_ago)
    active_maker = get_maker(recent_df)
    return active_maker


def get_maker_all() -> List[str]:
    """
    データベースに存在する全てのメーカー名のリストを取得する。

    Returns:
        List[str]: 全てのメーカー名のリスト
    """
    global _all_maker_list
    if _all_maker_list is not None:
        return _all_maker_list

    base_df = load_hard_sales2()
    maker_list = get_maker(base_df)
    _all_maker_list = maker_list
    return maker_list
