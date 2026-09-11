"""Observe only the supplied eager DataFrame; never reload or mutate it."""

import polars as pl

from .datasets import DATASETS
from .models import SCHEMA_VERSION
from .registry import describe
from .rendering import json_value


def inspect_frame(df, *, dataset=None, profile="basic", sample_rows=0):
    """Inspect schema and coverage, optionally testing keys/nulls/weekly gaps.

    dataset is an explicitly supplied contract, not a provenance assertion.
    basic scans date and dimension columns; full can scan the entire frame.
    Samples are opt-in (0..20). Dimension and group listings are capped at 20.
    LazyFrame is rejected to avoid implicit query execution.
    """
    if not isinstance(df, pl.DataFrame):
        raise TypeError(
            "df must be a polars.DataFrame; LazyFrame is not collected implicitly"
        )
    if profile not in ("basic", "full"):
        raise ValueError("profile must be basic or full")
    if type(sample_rows) is not int or not 0 <= sample_rows <= 20:
        raise ValueError("sample_rows must be between 0 and 20")
    if dataset is not None:
        if not isinstance(dataset, str):
            raise TypeError("dataset must be str or None")
        dataset = dataset.removeprefix("dataset:")
        definition = describe(f"dataset:{dataset}")
    else:
        definition = None
    observed = {
        "rows": df.height,
        "columns": {k: str(v) for k, v in df.schema.items()},
        "date_ranges": {},
        "dimensions": {},
    }
    for name, dtype in df.schema.items():
        if dtype == pl.Date or isinstance(dtype, pl.Datetime):
            observed["date_ranges"][name] = {
                "min": df[name].min(),
                "max": df[name].max(),
            }
    for name in ("hw", "maker_name"):
        if name in df.columns and (
            df.schema[name] in (pl.String, pl.Categorical)
            or isinstance(df.schema[name], pl.Enum)
        ):
            values = df[name].drop_nulls().cast(pl.String).unique().sort()
            observed["dimensions"][name] = {
                "count": len(values),
                "values": values.head(20).to_list(),
                "truncated": len(values) > 20,
            }
    validation = {
        "status": "unmatched",
        "missing_columns": [],
        "extra_columns": [],
        "dtype_mismatches": [],
        "checks_not_run": [],
    }
    candidates = []
    if definition:
        expected = definition["columns"]
        validation["missing_columns"] = sorted(set(expected) - set(df.columns))
        validation["extra_columns"] = sorted(set(df.columns) - set(expected))
        validation["dtype_mismatches"] = [
            {
                "column": name,
                "expected": spec["dtype"],
                "observed": str(df.schema[name]),
            }
            for name, spec in expected.items()
            if name in df.columns and str(df.schema[name]) != spec["dtype"]
        ]
        validation["status"] = (
            "schema_mismatch"
            if any(
                validation[k]
                for k in ("missing_columns", "extra_columns", "dtype_mismatches")
            )
            else "schema_match"
        )
    else:
        for name, spec in DATASETS.items():
            overlap = set(df.columns) & set(spec["columns"])
            if overlap:
                candidates.append(
                    {
                        "dataset": name,
                        "matched_columns": len(overlap),
                        "expected_columns": len(spec["columns"]),
                        "score": len(overlap)
                        / len(set(df.columns) | set(spec["columns"])),
                    }
                )
        candidates.sort(key=lambda item: (-item["score"], item["dataset"]))
    if profile == "full":
        observed["null_counts"] = dict(zip(df.columns, df.null_count().row(0)))
        key = definition["key"] if definition else []
        if key and set(key) <= set(df.columns):
            keys = df.select(key)
            validation["key"] = {
                "columns": key,
                "duplicate_rows": keys.height - keys.unique().height,
                "null_rows": keys.filter(pl.any_horizontal(pl.all().is_null())).height,
            }
        else:
            validation["checks_not_run"].append("key: 定義またはキー列がない")
        if (
            "hw" in df.columns
            and df.schema["hw"] == pl.String
            and "report_date" in df.columns
            and df.schema["report_date"] == pl.Date
        ):
            coverage = (
                df.group_by("hw")
                .agg(
                    pl.len().alias("rows"),
                    pl.col("report_date").min().alias("begin"),
                    pl.col("report_date").max().alias("end"),
                )
                .sort("hw", nulls_last=True)
            )
            observed["coverage_by_hw"] = {
                "count": coverage.height,
                "items": coverage.head(20).to_dicts(),
                "truncated": coverage.height > 20,
            }
            if dataset == "hard_sales":
                dates = (
                    df.select("hw", "report_date")
                    .drop_nulls()
                    .unique()
                    .sort(["hw", "report_date"])
                )
                gaps = dates.with_columns(
                    pl.col("report_date")
                    .diff()
                    .over("hw")
                    .dt.total_days()
                    .alias("days_since_previous")
                ).filter(pl.col("days_since_previous") > 7)
                observed["weekly_gap_candidates"] = {
                    "count": gaps.height,
                    "items": gaps.head(20).to_dicts(),
                    "truncated": gaps.height > 20,
                    "meaning": "7日超の間隔。抽出や14日集計でも生じるため欠測とは断定しない",
                }
    else:
        validation["checks_not_run"] = [
            "null_counts",
            "key",
            "coverage_by_hw",
            "weekly_gap_candidates",
        ]
    if sample_rows:
        observed["sample"] = {
            "items": df.head(sample_rows).to_dicts(),
            "truncated": df.height > sample_rows,
        }
    return json_value(
        {
            "schema_version": SCHEMA_VERSION,
            "dataset": dataset,
            "profile": profile,
            "definition": definition,
            "observed": observed,
            "validation": validation,
            "candidates": candidates[:5],
            "candidates_truncated": len(candidates) > 5,
            "unknown": [
                "データの由来・抽出履歴・DB更新日時はDataFrameから確定できない",
                "日付の最大値はこのDataFrame内の最新日であり、DBの最新日とは限らない",
                "列名と型の一致は、列の意味や累計の起点の一致を保証しない",
            ],
        }
    )
