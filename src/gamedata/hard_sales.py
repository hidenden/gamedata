# GameData分析用のユーティリティ関数群

import sqlite3
from datetime import datetime, timedelta
import polars as pl
from typing import List

from . import hard_info as hi

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

DB_PATH = "/Users/hide/Documents/sqlite3/gamehard.db"
_hard_sales_cache: pl.DataFrame | None = None
_all_hw_list = None
_all_maker_list = None


def _with_derived_columns(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df.with_columns(
            pl.col("begin_date").cast(pl.Utf8).str.to_date(),
            pl.col("report_date").cast(pl.Utf8).str.to_date(),
            pl.col("end_date").cast(pl.Utf8).str.to_date(),
            pl.col("launch_date").cast(pl.Utf8).str.to_date(),
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
        )
    )


def load_hard_sales(no_cache: bool = False) -> pl.DataFrame:
    """
    sqlite3を使用してデータベースからハードウェア販売データを読み込む関数。
    日付関係のカラムをdate型に変換し、整数カラムを適切なサイズにキャストして返す。

    Args:
        no_cache: Trueの場合はグローバルキャッシュを破棄し、DBから再読み込みする。

    Returns:
        pl.DataFrame: ハードウェア販売データのDataFrame。
                      日付カラムはDate型、整数カラムは最適なサイズに変換済み。

        DataFrameのカラム詳細:
        - weekly_id (String): 週次データのID（gamehard_weekly.id）
        - begin_date (Date): 集計開始日（週の初日）、月曜日である
        - end_date (Date): 集計終了日（週の末日、=report_date）
        - report_date (Date): 集計期間の末日、日曜日である
        - quarter (String): report_dateの四半期（例: "2024Q1"）
        - period_date (Int16): 集計日数(通常は7, 稀に14)
        - hw (String): ゲームハードの識別子
        - units (Int64): 週次販売台数
        - adjust_units (Int64): 週次販売台数の補正値(unitsは補正済みの値である)
        - year (Int16): report_dateの年
        - month (Int16): report_dateの月
        - mday (Int16): report_dateの日
        - week (Int16): report_dateがその月の何番目の日曜日か
        - delta_day (Int32): 発売日から何日後か
        - delta_week (Int32): 発売日から何週間後か
        - delta_month (Int16): 発売日から何ヶ月後か
        - delta_year (Int16): 発売年から何年後か(同じ年なら0)
        - index_week (Int32): 発売から何週目か（1始まり）
        - index_month (Int16): 発売から何ヶ月目か（1始まり）
        - index_year (Int16): 発売から何年目か（1始まり）
        - fiscal_year (Int16): 4月始まりの会計年度（期末年、例：2026年4月〜2027年3月 => 2027）
        - fiscal_month (Int8): 4月を1とする会計月
        - q_num (Int8): report_dateの四半期番号（1-4）
        - fq_num (Int8): fiscal_year内の四半期番号（1-4）
        - fiscal_quarter (String): report_dateの会計四半期（例: "2025FQ4"）
        - units_diff (Int64): 同一ハードの前週比販売台数差分
        - ma4w (Int64): 4週移動平均（直近4週の平均を四捨五入した整数）
        - ma13w (Int64): 13週移動平均（直近13週の平均を四捨五入した整数）
        - ma52w (Int64): 52週移動平均（直近52週の平均を四捨五入した整数）
        - avg_units (Int64): 1日あたりの販売台数 (units / period_date)
        - sum_units (Int64): report_date時点での累計販売台数
        - launch_date (Date): 発売日
        - maker_name (String): メーカー名
        - full_name (String): ゲームハードの正式名称
    """
    global _hard_sales_cache, _all_hw_list, _all_maker_list

    if no_cache:
        _hard_sales_cache = None
        _all_hw_list = None
        _all_maker_list = None
    elif _hard_sales_cache is not None:
        return _hard_sales_cache.clone()

    # SQLite3データベースに接続
    conn = sqlite3.connect(DB_PATH)
    # SQLクエリを実行してデータをDataFrameに読み込む
    query = "SELECT * FROM hard_sales ORDER BY weekly_id;"
    df = pl.read_database(query, conn)

    # 接続を閉じる
    conn.close()

    df = _with_derived_columns(df)
    _hard_sales_cache = df
    return df.clone()


def current_report_date(df: pl.DataFrame) -> datetime:
    """
    DataFrameから最新の報告日を取得する関数。

    Args:
        df: load_hard_sales()の戻り値のDataFrame

    Returns:
        datetime: 最新の報告日
    """
    return df.select(pl.col("report_date").max()).item()


def get_hw(df: pl.DataFrame) -> List[str]:
    """
    DataFrameからハードウェア名のユニークなリストを取得する。

    Args:
        df: load_hard_sales()の戻り値のDataFrame

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
    base_df = load_hard_sales()
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

    base_df = load_hard_sales()
    _all_hw_list = get_hw(base_df)
    remove_hw_list = ["PKS", "PS", "NeoGeoP", "SATURN", "GB"]
    if not true_all:
        # _all_hw_listから remove_hw_listの各要素に一致するものを取り除く
        _all_hw_list = [hw for hw in _all_hw_list if hw not in remove_hw_list]

    return _all_hw_list


def get_maker(df: pl.DataFrame) -> List[str]:
    """
    DataFrameからメーカー名のユニークなリストを取得する。

    Args:
        df: load_hard_sales()の戻り値のDataFrame

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
    base_df = load_hard_sales()
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

    base_df = load_hard_sales()
    _all_maker_list = get_maker(base_df)
    return _all_maker_list
