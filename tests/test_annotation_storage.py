"""CSVの注釈補足情報をSQLiteとDataFrameに通すテスト。"""

import importlib.util
from pathlib import Path
import sqlite3

import polars as pl

import gamedata.hard_annotation as ha


_REFRESH_PATH = (
    Path(__file__).parents[1] / "database" / "annotation" / "refresh_annotation.py"
)


def _refresh_module():
    spec = importlib.util.spec_from_file_location("refresh_annotation_test", _REFRESH_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_desc_is_stored_loaded_and_joined(tmp_path, monkeypatch, sample_info_df, sample_sales_df):
    monkeypatch.delenv("GAMEHARD_DB", raising=False)
    csv_path = tmp_path / "annotation.csv"
    csv_path.write_text(
        "date,hw,note,level,desc\n"
        "2020-11-12,PS5,発売,5,発売日に関する記事用の補足\n"
        "2021-01-01,PS5,年始,30,   \n",
        encoding="utf-8",
    )
    db_path = tmp_path / "annotation.db"
    refresh = _refresh_module()
    refresh.refresh_annotation(str(db_path), str(csv_path))

    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            'SELECT note, "desc" FROM gamehard_annotation ORDER BY id'
        ).fetchall()
    assert rows == [("発売", "発売日に関する記事用の補足"), ("年始", None)]

    monkeypatch.setattr(ha, "DB_PATH", str(db_path))
    monkeypatch.setattr(ha.hi, "load_hard_info", lambda: sample_info_df)
    monkeypatch.setattr(ha, "_annotation_dataframe", None)
    annotation_df = ha.load_hard_annotation(no_cache=True)
    assert annotation_df["desc"].to_list() == ["発売日に関する記事用の補足", None]

    monkeypatch.setattr(ha, "load_hard_annotation", lambda: annotation_df)
    sales_df = sample_sales_df.filter(pl.col("report_date").eq(annotation_df["report_date"][0]))
    joined = ha.join_annotation(sales_df, level=50)
    assert "desc" in joined.columns
    assert joined.filter(pl.col("hw") == "PS5")["desc"].to_list() == [
        "発売日に関する記事用の補足"
    ]


def test_refresh_accepts_legacy_csv_without_desc(tmp_path, monkeypatch):
    monkeypatch.delenv("GAMEHARD_DB", raising=False)
    csv_path = tmp_path / "legacy_annotation.csv"
    csv_path.write_text(
        "date,hw,note,level\n2020-11-12,PS5,発売,5\n", encoding="utf-8"
    )
    db_path = tmp_path / "annotation.db"
    refresh = _refresh_module()
    refresh.refresh_annotation(str(db_path), str(csv_path))

    with sqlite3.connect(db_path) as conn:
        assert conn.execute('SELECT "desc" FROM gamehard_annotation').fetchone() == (
            None,
        )
