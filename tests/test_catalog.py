"""Catalog contracts against actual transformations, without a local database."""

from datetime import date
import json
import sqlite3

import polars as pl
import pytest

import gamedata as g
from gamedata import catalog
from gamedata.catalog.datasets import DATASETS
from gamedata.catalog.functions import FUNCTIONS
from gamedata.catalog.registry import _entries


def test_read_only_and_json(sample_sales_df, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Catalog must not connect to the database")

    monkeypatch.setattr(sqlite3, "connect", forbidden)
    original = sample_sales_df.clone()
    for result in (
        catalog.overview(),
        catalog.search("累計"),
        catalog.inspect_frame(
            sample_sales_df, dataset="hard_sales", profile="full", sample_rows=2
        ),
    ):
        json.dumps(result, ensure_ascii=False, allow_nan=False)
        assert json.loads(catalog.render(result, format="json")) == result
    for identifier, _, _ in _entries():
        json.dumps(catalog.describe(identifier), allow_nan=False)
    assert sample_sales_df.equals(original)


def test_actual_sales_and_info_schema(sample_sales_df, sample_info_df):
    for name, df in (("hard_sales", sample_sales_df), ("hard_info", sample_info_df)):
        result = catalog.inspect_frame(df, dataset=name, profile="full")
        assert result["validation"]["status"] == "schema_match"
        assert result["validation"]["key"]["duplicate_rows"] == 0
    result = catalog.inspect_frame(
        sample_sales_df, dataset="hard_sales", profile="full"
    )
    assert result["observed"]["date_ranges"]["report_date"]["max"] == "2021-04-04"
    assert result["observed"]["weekly_gap_candidates"]["count"] > 0


def test_annotation_contract(sample_info_df):
    from gamedata.hard_annotation import _delta_annotation, _refine_annotation

    df = pl.DataFrame(
        {
            "id": [1],
            "annotation_date": [date(2020, 11, 12)],
            "hw": ["PS5"],
            "note": ["発売"],
            "level": [0],
            "report_date": [date(2020, 11, 15)],
        }
    )
    actual = _refine_annotation(_delta_annotation(df, sample_info_df))
    assert (
        catalog.inspect_frame(actual, dataset="hard_annotation")["validation"]["status"]
        == "schema_match"
    )


@pytest.mark.parametrize("name", ["weekly_sales", "monthly_sales"])
@pytest.mark.parametrize("maker", [False, True])
def test_output_variant_and_period_cumulative(sample_sales_df, name, maker):
    info = catalog.describe(f"function:{name}", params={"maker_mode": maker})
    actual = getattr(g, name)(sample_sales_df, begin=date(2021, 1, 1), maker_mode=maker)
    result = catalog.inspect_frame(actual, dataset=info["output_dataset"])
    assert result["validation"]["status"] == "schema_match"
    dimension = "maker_name" if maker else "hw"
    assert dimension in info["required_columns"]
    if not maker:
        assert actual.filter(pl.col("hw") == "NSW")["sum_units"][0] == 40000
        assert (
            sample_sales_df.filter(
                (pl.col("hw") == "NSW") & (pl.col("report_date") == date(2021, 1, 3))
            )["sum_units"][0]
            == 165000
        )
    assert (
        "抽出後"
        in catalog.describe(info["output_dataset"])["columns"]["sum_units"]["summary"]
    )


@pytest.mark.parametrize("mode", ["week", "month", "year", "w"])
def test_delta_output_variant(sample_sales_df, mode):
    info = catalog.describe(
        "function:cumulative_sales_by_delta_long", params={"mode": mode}
    )
    actual = g.cumulative_sales_by_delta_long(
        sample_sales_df.sort("report_date"), mode=mode
    )
    assert (
        catalog.inspect_frame(actual, dataset=info["output_dataset"])["validation"][
            "status"
        ]
        == "schema_match"
    )


def test_monthly_long_output_and_recipe(sample_sales_df):
    actual = g.monthly_sales_long(sample_sales_df)
    assert (
        catalog.inspect_frame(actual, dataset="monthly_sales_long")["validation"][
            "status"
        ]
        == "schema_match"
    )
    for name in ("monthly_sales", "compare_launch_cumulative", "extract_sales"):
        code = catalog.describe(f"recipe:{name}")["code"]
        result = eval(
            code, {"g": g, "date": date, "hard_sales_all_df": sample_sales_df}
        )
        assert isinstance(result, pl.DataFrame)


def test_forecast_output_contract():
    rows = []
    for year in (2019, 2020):
        for quarter, month, units in ((1, 3, 100), (2, 6, 200), (3, 9, 300), (4, 12, 400)):
            rows.append((year, quarter, date(year, month, 28), units))
    rows.append((2021, 1, date(2021, 3, 28), 100))
    sales = pl.DataFrame(rows, schema=["year", "q_num", "report_date", "units"], orient="row").with_columns(
        pl.lit("N").alias("hw"), pl.lit("Nintendo").alias("maker_name"),
        pl.lit(100).alias("ma52w"), pl.col("units").cum_sum().alias("sum_units"),
    )
    actual = g.forecast_year_end_all(sales)
    info = catalog.describe("function:forecast_year_end_all")
    assert info["output_dataset"] == "dataset:year_end_forecast"
    assert catalog.inspect_frame(actual, dataset="year_end_forecast")["validation"]["status"] == "schema_match"


def test_correction_and_fiscal_semantics(sample_sales_df):
    from gamedata.hard_sales import _with_derived_columns

    original = sample_sales_df["units"].to_list()
    actual = _with_derived_columns(sample_sales_df)
    assert actual["units"].to_list() == original  # no double adjustment
    assert actual.filter(pl.col("report_date") == date(2021, 4, 4))[
        "fiscal_year"
    ].unique().to_list() == [2022]
    assert "再加算" in catalog.describe("column:hard_sales.units")["caveats"][0]
    assert "期末年" in catalog.describe("column:hard_sales.fiscal_year")["summary"]


def test_unknown_extra_missing_and_empty(sample_sales_df):
    result = catalog.inspect_frame(sample_sales_df)
    assert result["dataset"] is None
    assert result["definition"] is None
    assert result["candidates"][0]["dataset"] == "hard_sales"
    df = sample_sales_df.drop("units").with_columns(
        pl.lit("x").alias("custom"), pl.col("year").cast(pl.String)
    )
    result = catalog.inspect_frame(df, dataset="hard_sales")
    assert result["validation"]["missing_columns"] == ["units"]
    assert result["validation"]["extra_columns"] == ["custom"]
    assert result["validation"]["dtype_mismatches"][0]["column"] == "year"
    for df in (pl.DataFrame(), sample_sales_df.head(0)):
        result = catalog.inspect_frame(
            df, dataset="hard_sales", profile="full", sample_rows=1
        )
        assert result["observed"]["rows"] == 0


def test_duplicate_and_null_keys(sample_sales_df):
    df = pl.concat([sample_sales_df, sample_sales_df.head(1)]).with_columns(
        pl.lit(None).cast(pl.String).alias("weekly_id")
    )
    result = catalog.inspect_frame(df, dataset="hard_sales", profile="full")
    assert result["validation"]["key"]["null_rows"] == df.height
    assert result["validation"]["key"]["duplicate_rows"] == df.height - 1


def test_bounded_observations_and_unusual_values():
    df = pl.DataFrame(
        {
            "hw": [f"H{i}" for i in range(30)],
            "value": [float("nan")] * 30,
            "binary": [b"x"] * 30,
        }
    )
    result = catalog.inspect_frame(df, sample_rows=2)
    assert result["observed"]["dimensions"]["hw"]["count"] == 30
    assert len(result["observed"]["dimensions"]["hw"]["values"]) == 20
    assert result["observed"]["dimensions"]["hw"]["truncated"]
    assert len(result["observed"]["sample"]["items"]) == 2
    json.dumps(result, allow_nan=False)


def test_search_and_isolation():
    assert (
        catalog.search("発売からの累計を比較")["items"][0]["id"]
        == "recipe:compare_launch_cumulative"
    )
    assert (
        catalog.search("monthly_sales_long", kind="function")["items"][0]["id"]
        == "function:monthly_sales_long"
    )
    assert catalog.search("", kind="function")["total"] == len(FUNCTIONS)
    assert catalog.search("xyzxyz")["total"] == 0
    result = catalog.describe("dataset:hard_sales")
    result["columns"].clear()
    assert catalog.describe("dataset:hard_sales")["columns"]
    assert set(catalog.describe("dataset:hard_sales", sections=["key"])) == {
        "id",
        "kind",
        "schema_version",
        "summary",
        "key",
    }
    # All links are resolvable.
    for identifier, _, _ in _entries():
        for related in catalog.describe(identifier).get("related", []):
            catalog.describe(related)
    assert all(spec["columns"] for spec in DATASETS.values())


def test_errors():
    with pytest.raises(TypeError):
        catalog.inspect_frame(pl.LazyFrame())
    with pytest.raises(KeyError):
        catalog.describe("dataset:unknown")
    with pytest.raises(ValueError):
        catalog.describe("function:weekly_sales", params={"unknown": True})
    with pytest.raises(ValueError):
        catalog.describe(
            "function:cumulative_sales_by_delta_long", params={"mode": "quarter"}
        )
    with pytest.raises(ValueError):
        catalog.search("", limit=0)
    with pytest.raises(ValueError):
        catalog.inspect_frame(pl.DataFrame(), sample_rows=100)
