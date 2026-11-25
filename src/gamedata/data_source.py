"""販売・機種・注釈の元テーブルを共通のスキーマで読み込む。"""

import io
import json
import os
import sqlite3
from contextlib import closing
from functools import lru_cache
from hashlib import sha256
from importlib.resources import files
from pathlib import Path

import polars as pl

DEFAULT_DB_PATH = "/Users/hide/Documents/sqlite3/gamehard.db"
SCHEMA_VERSION = 1
TABLE_SCHEMAS = {
    "gamehard_info": {
        "id": pl.String,
        "launch_date": pl.Date,
        "maker_name": pl.String,
        "full_name": pl.String,
    },
    "gamehard_weekly": {
        "id": pl.String,
        "report_date": pl.Date,
        "period_date": pl.Int64,
        "hw": pl.String,
        "units": pl.Int64,
        "adjust_units": pl.Int64,
    },
    "gamehard_annotation": {
        "id": pl.Int64,
        "date": pl.Date,
        "report_date": pl.Date,
        "hw": pl.String,
        "note": pl.String,
        "level": pl.Int64,
        "desc": pl.String,
    },
}


class SQLiteSource:
    def __init__(self, path: str | Path):
        self.uri = Path(path).expanduser().resolve().as_uri() + "?mode=ro"

    def read_tables(self, *tables: str) -> tuple[pl.DataFrame, ...]:
        with closing(sqlite3.connect(self.uri, uri=True)) as conn:
            conn.execute("BEGIN")
            return tuple(self._read_table(conn, table) for table in tables)

    @staticmethod
    def _read_table(conn: sqlite3.Connection, table: str) -> pl.DataFrame:
        schema = TABLE_SCHEMAS[table]
        columns = ", ".join(f'"{name}"' for name in schema)
        df = pl.read_database(
            f'SELECT {columns} FROM "{table}" ORDER BY rowid',
            conn,
            schema_overrides={
                name: pl.String if dtype == pl.Date else dtype
                for name, dtype in schema.items()
            },
        )
        return df.with_columns(
            pl.col(name).str.to_date("%Y-%m-%d")
            for name, dtype in schema.items()
            if dtype == pl.Date
        )


class EmbeddedParquetSource:
    def __init__(self):
        self.resources = files("gamedata").joinpath("_parquet")
        manifest = json.loads(
            self.resources.joinpath("manifest.json").read_text(encoding="utf-8")
        )
        if manifest["schema_version"] != SCHEMA_VERSION:
            raise ValueError("埋め込み Parquet のスキーマバージョンが一致しません")
        self.checksums = manifest["sha256"]
        if self.checksums.keys() != TABLE_SCHEMAS.keys():
            raise ValueError("埋め込み Parquet のテーブル一覧が一致しません")

    def read_tables(self, *tables: str) -> tuple[pl.DataFrame, ...]:
        return tuple(self._read_table(table) for table in tables)

    def _read_table(self, table: str) -> pl.DataFrame:
        schema = TABLE_SCHEMAS[table]
        content = self.resources.joinpath(f"{table}.parquet").read_bytes()
        if sha256(content).hexdigest() != self.checksums[table]:
            raise ValueError(f"埋め込み Parquet のチェックサムが一致しません: {table}")
        df = pl.read_parquet(io.BytesIO(content))
        if list(df.schema.items()) != list(schema.items()):
            raise ValueError(f"埋め込み Parquet の列または型が一致しません: {table}")
        return df


@lru_cache(maxsize=1)
def _get_source() -> SQLiteSource | EmbeddedParquetSource:
    source = os.environ.get("GAMEHARD_DATA_SOURCE", "sqlite")
    if source == "sqlite":
        return SQLiteSource(os.environ.get("GAMEHARD_DB") or DEFAULT_DB_PATH)
    if source == "parquet":
        return EmbeddedParquetSource()
    raise ValueError(f"GAMEHARD_DATA_SOURCE は sqlite または parquet を指定してください: {source}")


def read_tables(*tables: str) -> tuple[pl.DataFrame, ...]:
    """同一の読み取り時点のテーブルを指定順で返す。"""
    return _get_source().read_tables(*tables)
