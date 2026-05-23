#!/usr/bin/env python3
# /// script
# [tool.marimo.display]
# theme = "system"
# ///

from datetime import date, datetime
import sqlite3
import polars as pl
import os


DB_PATH = "/Users/hide/Documents/sqlite3/gamehard.db"
ANNOTATION_CSV = "./game_annotation.csv"
# ISO 8601形式の曜日定数
ISO_MONDAY = 1
ISO_SUNDAY = 7


def initialize_table(_conn: sqlite3.Connection, _debug: bool = False):
    # table:gamehard_annotationが存在する場合は削除
    _conn.execute("DROP TABLE IF EXISTS gamehard_annotation")
    _conn.commit()

    # gamehard_annotationテーブルを作成
    _conn.execute("""
    CREATE TABLE gamehard_annotation (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL CHECK(date GLOB '????-??-??'),
        report_date TEXT NOT NULL CHECK(report_date GLOB '????-??-??'),
        hw TEXT NOT NULL,
        note TEXT NOT NULL,
        level INTEGER NOT NULL CHECK(level >= 1 AND level <= 50))
    """)
    _conn.commit()

    if _debug:
        # 確認のためのgamehard_annotationテーブルのスキーマを表示
        _cursor = _conn.execute("PRAGMA table_info(gamehard_annotation)")
        _columns = _cursor.fetchall()
        print("gamehard_annotation table schema:")
        for _column in _columns:
            print(_column)

    return


def load_annotation_csv(
    _conn: sqlite3.Connection, _csv_path: str, _debug: bool = False
):
    # CSVファイルを読み込む
    _df = pl.read_csv(_csv_path, encoding="utf-8", has_header=True)

    # 日付カラムをdatetime型に変換し､カラム:annotation_dateを作成する
    _df = _df.with_columns(
        pl.col("date").str.strptime(pl.Date, format="%Y-%m-%d").alias("annotation_date")
    )
    # report_dateカラムを作成する。annotation_dateが日曜日ならそのまま、そうでなければ直近の日曜日を設定
    _df = _df.with_columns(
        pl.when(pl.col("annotation_date").dt.weekday() == ISO_SUNDAY)
        .then(pl.col("annotation_date"))
        .otherwise(
            pl.col("annotation_date")
            + pl.duration(days=(ISO_SUNDAY - pl.col("annotation_date").dt.weekday()))
        )
        .alias("report_date")
    )
    # report_dateカラムを文字列型に変換する
    _df = _df.with_columns(
        pl.col("report_date").dt.strftime(format="%Y-%m-%d").alias("report_date_str")
    )

    # データベースに挿入
    id = 0
    for row in _df.iter_rows(named=True):
        id += 1
        _conn.execute(
            "INSERT INTO gamehard_annotation (id, date, report_date, hw, note, level) VALUES (?, ?, ?, ?, ?, ?)",
            (
                id,
                row["date"],
                row["report_date_str"],
                row["hw"],
                row["note"],
                row["level"],
            ),
        )
    _conn.commit()

    # デバッグ用に挿入したデータを表示
    if _debug:
        _cursor = _conn.execute("SELECT * FROM gamehard_annotation")
        _rows = _cursor.fetchall()
        print("Inserted data into gamehard_annotation:")
        for _row in _rows:
            print(_row)

    return


def refresh_annotation(_default_db_path, _annotation_csv, _debug: bool = False):
    # 環境変数GAMEHARD_DBからデータベースのパスを取得. 環境変数が設定されていない場合は、デフォルトのパスを使用
    _db_path = os.getenv("GAMEHARD_DB", _default_db_path)
    # SQLite3データベースに接続
    _conn = sqlite3.connect(_db_path)

    # gamehard_annotationテーブルを初期化
    initialize_table(_conn, _debug=_debug)

    # CSVファイルからデータを読み込み、gamehard_annotationテーブルに挿入
    load_annotation_csv(_conn, _annotation_csv, _debug=_debug)

    # データベース接続を閉じる
    _conn.close()
    return


if __name__ == "__main__":
    refresh_annotation(DB_PATH, ANNOTATION_CSV, _debug=True)
