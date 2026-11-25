import runpy
import sqlite3
from contextlib import closing
from datetime import date, timedelta
from pathlib import Path

import pytest
from polars.testing import assert_frame_equal

from gamedata import (
    data_source,
    hard_annotation,
    hard_sales,
    hard_sales2,
    load_hard_info,
    load_hard_sales2,
)


DATABASE = Path(__file__).resolve().parents[1] / "database"


@pytest.fixture
def sales_db(tmp_path, monkeypatch):
    path = tmp_path / "sales.db"
    monkeypatch.setattr(hard_sales, "DB_PATH", path)
    monkeypatch.setattr(data_source, "_get_source", lambda: data_source.SQLiteSource(path))
    for module in (hard_sales, hard_sales2):
        monkeypatch.setattr(module, "_hard_sales_cache", None)
    monkeypatch.setattr(hard_sales2, "_all_hw_list", None)
    monkeypatch.setattr(hard_sales2, "_all_maker_list", None)
    with closing(sqlite3.connect(path)) as conn:
        conn.executescript((DATABASE / "create_tables.sql").read_text())
        conn.executescript((DATABASE / "update_tables.sql").read_text())
        conn.executemany(
            "INSERT INTO gamehard_info VALUES (?, ?, ?, ?)",
            [("A", "2023-12-30", "X", "Alpha"), ("B", "2024-01-01", "Y", "Beta")],
        )
        conn.commit()
    return path


def test_matches_full_legacy_pipeline(sales_db):
    # 年をまたぐ14日集計と、52週移動平均が計算できる長さの履歴。
    start = date(2024, 1, 7)
    rows = [("2024-01-07_A", start.isoformat(), 14, "A", 31, -3)]
    for i in range(1, 54):
        report = (start + timedelta(weeks=i)).isoformat()
        for hw in ("A", "B"):
            rows.append((f"{report}_{hw}", report, 7, hw, i * 3, 2))
    with closing(sqlite3.connect(sales_db)) as conn:
        conn.executemany(
            "INSERT INTO gamehard_weekly (id, report_date, period_date, hw, units, adjust_units)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            reversed(rows),
        )
        conn.commit()

    actual = load_hard_sales2()
    with closing(sqlite3.connect(sales_db)) as conn:
        assert conn.execute(
            "SELECT period_date, units, adjust_units FROM gamehard_weekly WHERE id='2024-01-07_A'"
        ).fetchone() == (14, 31, -3)
    legacy = runpy.run_path(str(DATABASE / "update/refresh_analysis.py"))
    legacy["normalize7_db"](sales_db, debug_mode=False)
    legacy["insert_weekly_analysis"](sales_db, debug_mode=False)
    expected = hard_sales.load_hard_sales()
    assert_frame_equal(actual, expected, check_exact=True)
    assert_frame_equal(load_hard_sales2(no_cache=True), expected, check_exact=True)


def test_reads_base_tables_only_and_refreshes_cache(sales_db):
    with closing(sqlite3.connect(sales_db)) as conn:
        conn.executescript("DROP VIEW hard_sales; DROP TABLE gamehard_weekly_analysis;")
        empty = load_hard_sales2()
        assert hard_sales.get_hw_all() == []
        assert hard_sales.get_maker_all() == []
        conn.execute(
            "INSERT INTO gamehard_weekly (id, report_date, period_date, hw, units)"
            " VALUES ('2024-04-07_A', '2024-04-07', 7, 'A', 123)"
        )
        conn.commit()
    assert empty.is_empty()
    assert load_hard_sales2().is_empty()
    refreshed = load_hard_sales2(no_cache=True)
    assert refreshed.schema == empty.schema
    assert refreshed["units"].to_list() == [123]
    assert hard_sales.get_hw_all() == ["A"]
    assert hard_sales.get_maker_all() == ["X"]
    cached = load_hard_sales2()
    assert cached is not refreshed
    assert_frame_equal(cached, refreshed, check_exact=True)


def test_all_loaders_match_exported_parquet(sales_db, tmp_path, monkeypatch):
    monkeypatch.setattr(hard_annotation, "_annotation_dataframe", None)
    with closing(sqlite3.connect(sales_db)) as conn:
        conn.executescript("""
            DROP VIEW hard_sales;
            DROP TABLE gamehard_weekly_analysis;
            CREATE TABLE gamehard_annotation (
                id INTEGER PRIMARY KEY, date TEXT, report_date TEXT,
                hw TEXT, note TEXT, level INTEGER, "desc" TEXT
            );
            INSERT INTO gamehard_annotation
            VALUES (1, '2024-01-07', '2024-01-07', 'A', '新年', 5, NULL);
            INSERT INTO gamehard_weekly (id, report_date, period_date, hw, units, adjust_units)
            VALUES ('2024-01-07_A', '2024-01-07', 14, 'A', 31, -3);
        """)

    def load_all():
        return (
            load_hard_info(),
            load_hard_sales2(no_cache=True),
            hard_annotation.load_hard_annotation(no_cache=True),
        )

    expected = load_all()
    export = runpy.run_path(str(DATABASE / "export_parquet.py"))["export_snapshot"]
    export(sales_db, tmp_path / "_parquet")
    monkeypatch.setattr(data_source, "files", lambda package: tmp_path)
    source = data_source.EmbeddedParquetSource()
    monkeypatch.setattr(data_source, "_get_source", lambda: source)
    for actual, reference in zip(load_all(), expected, strict=True):
        assert_frame_equal(actual, reference, check_exact=True)
