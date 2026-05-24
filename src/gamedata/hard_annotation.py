# Game Annotation取得用のユーティリティ関数群

import sqlite3
from datetime import datetime, date
import polars as pl
from typing import List, TypedDict, Dict, Any
from . import hard_info as hi
from .mode import Mode, parse_mode

DB_PATH = "/Users/hide/Documents/sqlite3/gamehard.db"
# ISO 8601形式の曜日定数
ISO_MONDAY = 1
ISO_SUNDAY = 7

_annotation_dataframe: pl.DataFrame | None = None


def load_hard_annotation(no_cache: bool = False) -> pl.DataFrame:
    """
    sqlite3を使用してデータベースからハードウェアアノテーションデータを読み込む関数。
    日付関係のカラムをdatetime型に変換して返す。

    Args:
        no_cache (bool): Trueの場合はキャッシュを無視してデータを再読み込みする。

    Returns:
        pl.DataFrame: ハードウェアアノテーションデータのDataFrame。

    """
    global _annotation_dataframe

    if _annotation_dataframe is not None and not no_cache:
        return _annotation_dataframe.clone()
    # データベースに接続
    conn = sqlite3.connect(DB_PATH)
    # データを読み込む
    query = "SELECT * FROM gamehard_annotation"
    df = pl.read_database(query=query, connection=conn)
    # データベース接続を閉じる
    conn.close()

    # カラムdateとカラムreport_dateをdate型に変換
    df = df.with_columns(
        pl.col("date").str.strptime(pl.Date, format="%Y-%m-%d").alias("annotation_date")
    )
    df = df.with_columns(pl.col("report_date").str.strptime(pl.Date, format="%Y-%m-%d"))

    df = _delta_annotation(df, hi.load_hard_info())
    df = _refine_annotation(df)

    _annotation_dataframe = df

    return _annotation_dataframe.clone()


def _delta_annotation(
    annotation_df: pl.DataFrame, info_df: pl.DataFrame
) -> pl.DataFrame:
    """
    annotation_dfにinfo_dfのlaunch_dateを結合し、report_dateとlaunch_dateの
    差分からdelta_weekを計算して追加する関数。
    Args:
        annotation_df (pl.DataFrame): ハードウェアアノテーションデータ
        info_df (pl.DataFrame): ハードウェア情報データ
    Returns:
        pl.DataFrame: delta_weekが追加されたハードウェアアノテーションデータ
    """
    df_event_merged = annotation_df.join(
        info_df, left_on="hw", right_on="id", how="left"
    )
    df_event_merged = df_event_merged.with_columns(
        ((pl.col("report_date") - pl.col("launch_date")).dt.total_days() // 7)
        .cast(pl.Int32)
        .alias("delta_week")
    )

    df_event_merged = df_event_merged.select(
        [
            "id",
            "annotation_date",
            "hw",
            "note",
            "level",
            "report_date",
            "launch_date",
            "delta_week",
        ]
    )
    return df_event_merged


def _refine_annotation(annotation_df: pl.DataFrame) -> pl.DataFrame:
    """
    annotation_dfを様々な販売情報と結合できるように､日付関係のカラムを追加する｡
    Args:
        annotation_df (pl.DataFrame): ハードウェアアノテーションデータ
    Returns:
        pl.DataFrame: 日付関係のカラムが追加されたハードウェアアノテーションデータ
    """
    annotation_df = (
        annotation_df.with_columns(
            pl.col("report_date").dt.year().alias("year"),
            pl.col("report_date").dt.month().alias("month"),
            (pl.col("report_date").dt.year() - pl.col("launch_date").dt.year()).alias(
                "delta_year"
            ),
            (
                (pl.col("report_date").dt.year() - pl.col("launch_date").dt.year()) * 12
                + (pl.col("report_date").dt.month() - pl.col("launch_date").dt.month())
            ).alias("delta_month"),
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
        )
    )
    return annotation_df


def _summarize_annotation(annotation_df: pl.DataFrame, mode_enum: Mode) -> pl.DataFrame:
    if mode_enum == Mode.WEEK:
        return annotation_df

    if mode_enum == Mode.MONTH:
        annotation_df = (
            annotation_df.group_by(["hw", "year", "month"])
            .agg([pl.all().gather(pl.col("level").arg_min().first())])
            .explode(pl.all().exclude("hw", "year", "month"))
        )
        return annotation_df.sort(["year", "month"], descending=[False, False])

    if mode_enum == Mode.QUARTER:
        annotation_df = (
            annotation_df.group_by(["hw", "year", "q_num"])
            .agg([pl.all().gather(pl.col("level").arg_min().first())])
            .explode(pl.all().exclude("hw", "year", "q_num"))
        )
        return annotation_df.sort(["year", "q_num"], descending=[False, False])

    if mode_enum == Mode.FISCAL_QUARTER:
        annotation_df = (
            annotation_df.group_by(["hw", "fiscal_year", "fq_num"])
            .agg([pl.all().gather(pl.col("level").arg_min().first())])
            .explode(pl.all().exclude("hw", "fiscal_year", "fq_num"))
        )
        return annotation_df.sort(["fiscal_year", "fq_num"], descending=[False, False])

    if mode_enum == Mode.YEAR:
        annotation_df = (
            annotation_df.group_by(["hw", "year"])
            .agg([pl.all().gather(pl.col("level").arg_min().first())])
            .explode(pl.all().exclude("hw", "year"))
        )
        return annotation_df.sort(["year"], descending=[False])

    if mode_enum == Mode.FISCAL_YEAR:
        annotation_df = (
            annotation_df.group_by(["hw", "fiscal_year"])
            .agg([pl.all().gather(pl.col("level").arg_min().first())])
            .explode(pl.all().exclude("hw", "fiscal_year"))
        )
        return annotation_df.sort(["fiscal_year"], descending=[False])


def summarize_annotation(
    annotation_df: pl.DataFrame, mode: str = "week"
) -> pl.DataFrame:
    mode_enum = parse_mode(mode)
    return _summarize_annotation(annotation_df, mode_enum)


def join_annotation(
    sales_df: pl.DataFrame,
    delta: bool = False,
    mode: str = "week",
    level: int = 50,
    hw_col: str | None = None,
) -> pl.DataFrame:
    """販売データにアノテーション情報を結合して返す関数。

    Args:
    sales_df (pl.DataFrame): 販売データのDataFrame。含まれているカラムを調べ､結合ロジックを判定する｡
    delta (bool): Trueの場合、相対日付カラムを使用して結合する。Falseの場合 絶対日付カラムで結合する。デフォルトはFalse。
    mode (str): 結合に使用するモードを指定する文字列。デフォルトは"week"で、"week", "month", "quarter", "year", "fiscal_quarter", "fiscal_year"のいずれかを指定する必要があります。
    level (int): 取得するアノテーションの最大レベル。デフォルトは50で、1から50の範囲で指定する必要があります。

    Returns:
    pl.DataFrame: フィルタリングされたハードウェアアノテーションのDataFrame。追加されるカラムは以下の通りです。
        - id (Int32): アノテーションのID
        - hw (String): ゲームハードの識別子
        - note (String): アノテーションの内容
        - level (Int32): アノテーションのレベル
    """

    def contains_all(main_list: list[str], required: list[str]) -> bool:
        """main_list が required の全要素を含んでいるか確認"""
        return set(required).issubset(set(main_list))

    mode_enum = parse_mode(mode)
    annotation_df = load_hard_annotation().filter(pl.col("level") <= level)
    annotation_df = _summarize_annotation(annotation_df, mode_enum)
    if hw_col is not None:
        # カラム名 hw_col の内容を hw カラムにコピー (結合のため)
        sales_df = sales_df.with_columns(pl.col(hw_col).alias("hw"))

    if delta:  # Delta mode
        if contains_all(sales_df.columns, ["delta_week"]) and mode_enum == Mode.WEEK:
            # Weekly mode
            sales_df = sales_df.join(
                other=annotation_df, on=["hw", "delta_week"], how="left"
            )
            return sales_df

        if contains_all(sales_df.columns, ["index_week"]) and mode_enum == Mode.WEEK:
            # Weekly mode
            sales_df = sales_df.join(
                other=annotation_df, on=["hw", "index_week"], how="left"
            )
            return sales_df

        if contains_all(sales_df.columns, ["delta_month"]) and mode_enum == Mode.MONTH:
            # Monthly mode
            sales_df = sales_df.join(
                other=annotation_df, on=["hw", "delta_month"], how="left"
            )
            return sales_df

        if contains_all(sales_df.columns, ["index_month"]) and mode_enum == Mode.MONTH:
            # Monthly mode
            sales_df = sales_df.join(
                other=annotation_df, on=["hw", "index_month"], how="left"
            )
            return sales_df

        if contains_all(sales_df.columns, ["delta_year"]) and mode_enum == Mode.YEAR:
            # Yearly mode
            sales_df = sales_df.join(
                other=annotation_df, on=["hw", "delta_year"], how="left"
            )
            return sales_df

        if contains_all(sales_df.columns, ["index_year"]) and mode_enum == Mode.YEAR:
            # Yearly mode
            sales_df = sales_df.join(
                other=annotation_df, on=["hw", "index_year"], how="left"
            )
            return sales_df

    else:  # Absolute date mode
        if contains_all(sales_df.columns, ["report_date"]) and mode_enum == Mode.WEEK:
            # Weekly mode
            sales_df = sales_df.join(
                other=annotation_df, on=["hw", "report_date"], how="left"
            )
            return sales_df

        if (
            contains_all(sales_df.columns, ["year", "month"])
            and mode_enum == Mode.MONTH
        ):
            # Monthly mode
            sales_df = sales_df.join(
                other=annotation_df, on=["hw", "year", "month"], how="left"
            )
            return sales_df

        if (
            contains_all(sales_df.columns, ["year", "q_num"])
            and mode_enum == Mode.QUARTER
        ):
            # Quarterly mode
            sales_df = sales_df.join(
                other=annotation_df, on=["hw", "year", "q_num"], how="left"
            )
            return sales_df

        if (
            contains_all(sales_df.columns, ["year", "fq_num"])
            and mode_enum == Mode.FISCAL_QUARTER
        ):
            # Fiscal Quarterly mode
            sales_df = sales_df.join(
                other=annotation_df, on=["hw", "year", "fq_num"], how="left"
            )
            return sales_df

        if contains_all(sales_df.columns, ["year"]) and mode_enum == Mode.YEAR:
            # Yearly mode
            sales_df = sales_df.join(other=annotation_df, on=["hw", "year"], how="left")
            return sales_df

    raise ValueError("sales_dfのカラムに結合に必要なカラムが見つかりませんでした。")
