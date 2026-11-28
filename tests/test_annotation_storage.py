"""CSVの注釈補足情報をSQLiteとDataFrameに通すテスト。"""

import importlib.util
from pathlib import Path
import sqlite3

import polars as pl
import pytest

import gamedata.hard_annotation as ha
from gamedata import data_source


@pytest.mark.parametrize(
    ("mode", "period_columns"),
    [
        ("week", ["delta_week"]),
        ("month", ["year", "month"]),
        ("quarter", ["year", "q_num"]),
        ("fq", ["fiscal_year", "fq_num"]),
        ("year", ["year"]),
        ("fy", ["fiscal_year"]),
    ],
)
def test_summarize_keeps_first_most_important_annotation(mode, period_columns):
    annotations = pl.DataFrame(
        {
            "hw": ["A", "A", "A", "B", "A"],
            "level": [30, 10, 10, 20, 30],
            "note": ["lower priority", "first", "tie", "another machine", "later"],
            **{column: [1, 1, 1, 1, 2] for column in period_columns},
        }
    )

    summary = ha.summarize_annotation(annotations, mode)

    assert set(summary["note"]) == {"first", "another machine", "later"}
    assert summary[period_columns[0]].to_list() == [1, 1, 2]


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
        conn.execute(
            "CREATE TABLE gamehard_info (id TEXT PRIMARY KEY, launch_date TEXT, "
            "maker_name TEXT, full_name TEXT)"
        )
        conn.executemany("INSERT INTO gamehard_info VALUES (?, ?, ?, ?)", sample_info_df.rows())
    assert rows == [("発売", "発売日に関する記事用の補足"), ("年始", None)]

    monkeypatch.setattr(data_source, "_get_source", lambda: data_source.SQLiteSource(db_path))
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
    without_events = ha.join_annotation(sales_df, level=0)
    assert without_events.height == sales_df.height
    assert without_events["note"].null_count() == sales_df.height


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
