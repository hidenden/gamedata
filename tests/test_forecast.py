"""gamedata.forecast の年末予測モデルを検証する。"""

from datetime import date

import polars as pl
import pytest

import gamedata as g


def _forecast_sales_df() -> pl.DataFrame:
    rows = []
    # Nintendoは2019・2020年の完全な四半期履歴を持つ。Q1=年販の10%。
    for year in (2019, 2020):
        for quarter, report_date, units in (
            (1, date(year, 3, 31), 100),
            (2, date(year, 6, 30), 200),
            (3, date(year, 9, 30), 300),
            (4, date(year, 12, 31), 400),
        ):
            rows.append(("N", "Nintendo", year, quarter, report_date, units))
    # Sonyには履歴を持たせず、全メーカー季節性へのフォールバックを確認する。
    rows.extend(
        [
            ("S", "Sony", 2021, 1, date(2021, 3, 31), 50),
            ("N", "Nintendo", 2021, 1, date(2021, 3, 31), 100),
        ]
    )
    df = pl.DataFrame(
        rows,
        schema=["hw", "maker_name", "year", "q_num", "report_date", "units"],
        orient="row",
    ).with_columns(
        pl.col("report_date").cast(pl.Date),
        pl.lit(70).cast(pl.Int64).alias("ma52w"),
    )
    return (
        df.sort(["hw", "report_date"])
        .with_columns(pl.col("units").cum_sum().over("hw").alias("sum_units"))
    )


def test_quarter_share_uses_maker_history_and_global_fallback():
    result = g.forecast_year_end_quarter_share(_forecast_sales_df(), as_of=date(2021, 3, 31))
    assert result.columns == [
        "model", "as_of", "hw", "maker_name", "actual_ytd_units",
        "forecast_remaining_units", "forecast_year_units",
    ]
    assert result.filter(pl.col("hw") == "N")["forecast_year_units"][0] == 1000
    # Sony has no complete maker history, but receives Nintendo's global Q1=10% profile.
    assert result.filter(pl.col("hw") == "S")["forecast_year_units"][0] == 500


def test_yoy_model_keeps_new_hardware_forecast_null():
    result = g.forecast_year_end_yoy_seasonal(_forecast_sales_df(), as_of=date(2021, 3, 31))
    assert result.filter(pl.col("hw") == "N")["forecast_year_units"][0] == 1000
    assert result.filter(pl.col("hw") == "S")["forecast_year_units"][0] is None


def test_52w_model_uses_saved_weekly_average():
    result = g.forecast_year_end_52w(_forecast_sales_df(), as_of=date(2021, 3, 31))
    nintendo = result.filter(pl.col("hw") == "N").row(0, named=True)
    # 3月31日から年末まで275日、週平均70台を日割りして加算する。
    assert nintendo["forecast_remaining_units"] == 2750
    assert nintendo["forecast_year_units"] == 2850


def test_all_models_filter_hardware_and_add_cumulative_forecast():
    sales = _forecast_sales_df()
    result = g.forecast_year_end_all(sales, as_of=date(2099, 1, 1), hw=["N"])
    assert result["hw"].unique().to_list() == ["N"]
    assert set(result["model"].to_list()) == {
        "trailing_52w", "maker_quarter_share", "yoy_seasonal", "median_ensemble",
    }
    assert "forecast_cumulative_units" in result.columns
    assert result["as_of"].unique().to_list() == [date(2021, 3, 31)]
    assert result.filter(pl.col("model") == "median_ensemble")["forecast_year_units"][0] is not None


@pytest.mark.parametrize(
    ("fn", "kwargs"),
    [
        (g.forecast_year_end_quarter_share, {"history_years": 0}),
        (g.forecast_year_end_yoy_seasonal, {"scale_bounds": (2.0, 1.0)}),
    ],
)
def test_invalid_model_arguments_raise_value_error(fn, kwargs):
    with pytest.raises(ValueError):
        fn(_forecast_sales_df(), **kwargs)


def test_input_contract_errors_are_actionable():
    with pytest.raises(ValueError, match="必要な列"):
        g.forecast_year_end_all(pl.DataFrame({"hw": ["N"]}))
    with pytest.raises(ValueError, match="販売実績"):
        g.forecast_year_end_all(_forecast_sales_df().head(0))
