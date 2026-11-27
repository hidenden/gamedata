"""販売・機種・注釈の元テーブルを共通のスキーマで読み込む。"""

import io
import json
import os
import sys
from contextlib import closing
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from typing import TYPE_CHECKING

import polars as pl

if TYPE_CHECKING:
    import sqlite3

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

    def read_tables(
        self, *tables: str, all_columns: bool = False
    ) -> tuple[pl.DataFrame, ...]:
        """同じトランザクションで読み込む。公開用の書き出しでは管理列も含める。"""
        import sqlite3

        with closing(sqlite3.connect(self.uri, uri=True)) as conn:
            conn.execute("BEGIN")
            return tuple(self._read_table(conn, table, all_columns) for table in tables)

    @staticmethod
    def _read_table(
        conn: "sqlite3.Connection", table: str, all_columns: bool
    ) -> pl.DataFrame:
        schema = TABLE_SCHEMAS[table]
        columns = ", ".join(f'"{name}"' for name in schema)
        if all_columns:
            columns = "*"
            if table == "gamehard_weekly":
                schema = {**schema, "flag": pl.Int64, "update_at": pl.String}
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


class HTTPParquetSource:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def _get(self, filename: str) -> bytes:
        # marimo runs Python in a Web Worker, so synchronous binary GET is available.
        from js import XMLHttpRequest

        url = f"{self.base_url}/{filename}"
        request = XMLHttpRequest.new()
        request.open("GET", url, False)
        request.responseType = "arraybuffer"
        request.send()
        if not 200 <= request.status < 300:
            raise OSError(f"HTTP {request.status}: {url}")
        return request.response.to_bytes()

    def read_tables(self, *tables: str) -> tuple[pl.DataFrame, ...]:
        manifest = json.loads(self._get("manifest.json"))
        if manifest["schema_version"] != SCHEMA_VERSION:
            raise ValueError("公開データのスキーマバージョンが一致しません")
        frames = []
        for table in tables:
            schema = TABLE_SCHEMAS[table]
            content = self._get(f"{table}.parquet")
            if sha256(content).hexdigest() != manifest["sha256"][table]:
                raise ValueError(f"公開データのチェックサムが一致しません: {table}")
            frame = pl.read_parquet(
                io.BytesIO(content), columns=list(schema), use_pyarrow=True
            )
            if list(frame.schema.items()) != list(schema.items()):
                raise ValueError(f"公開データの列または型が一致しません: {table}")
            frames.append(frame)
        return tuple(frames)


@lru_cache(maxsize=1)
def _get_source() -> SQLiteSource | HTTPParquetSource:
    if sys.platform == "emscripten":
        from js import location

        return HTTPParquetSource(f"{location.origin}/dashboard/data")
    return SQLiteSource(os.environ.get("GAMEHARD_DB") or DEFAULT_DB_PATH)


def read_tables(*tables: str) -> tuple[pl.DataFrame, ...]:
    """同一の読み取り時点のテーブルを指定順で返す。"""
    return _get_source().read_tables(*tables)
