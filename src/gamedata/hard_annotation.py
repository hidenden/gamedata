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
            "delta_week",
        ]
    )
    return df_event_merged


def get_annotation(
    level: int = 50,
    hw: List[str] = [],
    begin: datetime | date | None = None,
    end: datetime | date | None = None,
    mode: str = "week",
) -> pl.DataFrame:
    """指定された条件に基づいてハードウェアアノテーションをフィルタリングして返す関数。

    Args:
    level (int): 取得するアノテーションの最大レベル。デフォルトは50で、1から50の範囲で指定する必要があります。
    hw (List[str]): 取得するアノテーションの対象となるゲームハードのリスト。デフォルトは空リストで、指定しない場合は全てのゲームハードが対象となります。
    begin (datetime | date | None): 取得するアノテーションの開始日。デフォルトはNoneで、指定しない場合は開始日でのフィルタリングは行われません。
    end (datetime | date | None): 取得するアノテーションの終了日。デフォルトはNoneで、指定しない場合は終了日でのフィルタリングは行われません。
    mode (str): 取得するアノテーションのモード。デフォルトは"week"で、"week"、"month"、"quarter"、"year"、"fiscal_quarter"、"fiscal_year"のいずれかを指定する必要があります。

    Returns:
    pl.DataFrame: フィルタリングされたハードウェアアノテーションのDataFrame。カラムは以下の通りです。
        - id (Int32): アノテーションのID
        - annotation_date (Date): アノテーションの日付
        - hw (String): ゲームハードの識別子
        - note (String): アノテーションの内容
        - level (Int32): アノテーションのレベル
        - report_date (Date): アノテーションのレポート日
        - delta_week (Int32): アノテーションのレポート日とゲームハードの発売日との差分（週単位）
    """
    mode_enum = parse_mode(mode)
    if mode_enum != Mode.WEEK:
        raise NotImplementedError(f"Mode {mode_enum} is not supported yet.")

    df = load_hard_annotation()
    df = df.filter(pl.col("level") <= level)
    if hw:
        df = df.filter(pl.col("hw").is_in(hw))
    if begin:
        df = df.filter(pl.col("annotation_date") >= begin)
    if end:
        df = df.filter(pl.col("annotation_date") <= end)
    return df
