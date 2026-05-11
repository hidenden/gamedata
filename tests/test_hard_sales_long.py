"""
gamedata.hard_sales_long モジュールのテスト
"""
from datetime import date, datetime
import polars as pl
import pytest

from gamedata import hard_sales_long as lng


class TestSalesLong:
    """sales_long 関数のテスト"""

    def test_returns_dataframe(self, sample_sales_df):
        result = lng.sales_long(sample_sales_df)
        assert isinstance(result, pl.DataFrame)

    def test_has_expected_columns(self, sample_sales_df):
        result = lng.sales_long(sample_sales_df)
        assert set(result.columns) == {"report_date", "hw", "units"}

    def test_filter_by_hw(self, sample_sales_df):
        result = lng.sales_long(sample_sales_df, hw=["NSW"])
        assert set(result["hw"].unique().to_list()) == {"NSW"}

    def test_filter_excludes_other_hw(self, sample_sales_df):
        result = lng.sales_long(sample_sales_df, hw=["NSW"])
        assert "XSX" not in result["hw"].to_list()

    def test_no_hw_filter_all_data(self, sample_sales_df):
        result = lng.sales_long(sample_sales_df)
        assert result.height > 0
        assert "NSW" in result["hw"].to_list()

    def test_with_begin_and_end(self, sample_sales_df):
        begin = date(2020, 1, 1)
        end = date(2020, 12, 31)
        result = lng.sales_long(sample_sales_df, begin=begin, end=end)
        assert all(d <= end for d in result["report_date"].to_list())
        assert all(d >= begin for d in result["report_date"].to_list())

    def test_with_begin_only(self, sample_sales_df):
        begin = date(2021, 1, 1)
        result = lng.sales_long(sample_sales_df, begin=begin)
        assert all(d >= begin for d in result["report_date"].to_list())

    def test_with_end_only(self, sample_sales_df):
        end = date(2020, 12, 31)
        result = lng.sales_long(sample_sales_df, end=end)
        assert all(d <= end for d in result["report_date"].to_list())

    def test_sorted_by_report_date(self, sample_sales_df):
        result = lng.sales_long(sample_sales_df)
        dates = result["report_date"].to_list()
        assert dates == sorted(dates)


class TestMonthlySalesLong:
    """monthly_sales_long 関数のテスト"""

    def test_returns_dataframe(self, sample_sales_df):
        result = lng.monthly_sales_long(sample_sales_df)
        assert isinstance(result, pl.DataFrame)

    def test_has_expected_columns(self, sample_sales_df):
        result = lng.monthly_sales_long(sample_sales_df)
        assert set(result.columns) == {"year_month", "year", "month", "hw", "monthly_units"}

    def test_month_column_is_date(self, sample_sales_df):
        result = lng.monthly_sales_long(sample_sales_df)
        assert result["year_month"].dtype == pl.Date

    def test_filter_by_hw(self, sample_sales_df):
        result = lng.monthly_sales_long(sample_sales_df, hw=["NSW"])
        assert set(result["hw"].unique().to_list()) == {"NSW"}

    def test_with_date_range(self, sample_sales_df):
        begin = datetime(2020, 1, 1)
        end = datetime(2020, 12, 31)
        result = lng.monthly_sales_long(sample_sales_df, begin=begin, end=end)
        assert result.height > 0

    def test_sorted_by_month(self, sample_sales_df):
        result = lng.monthly_sales_long(sample_sales_df)
        months = result["year_month"].to_list()
        assert months == sorted(months)

    def test_monthly_units_positive(self, sample_sales_df):
        result = lng.monthly_sales_long(sample_sales_df)
        assert (result["monthly_units"] > 0).all()


class TestQuarterlySalesLong:
    """quarterly_sales_long 関数のテスト"""

    def test_returns_dataframe(self, sample_sales_df):
        result = lng.quarterly_sales_long(sample_sales_df)
        assert isinstance(result, pl.DataFrame)

    def test_has_expected_columns(self, sample_sales_df):
        result = lng.quarterly_sales_long(sample_sales_df)
        assert set(result.columns) == {"quarter", "hw", "quarterly_units"}

    def test_filter_by_hw(self, sample_sales_df):
        result = lng.quarterly_sales_long(sample_sales_df, hw=["NSW"])
        assert set(result["hw"].unique().to_list()) == {"NSW"}

    def test_with_date_range(self, sample_sales_df):
        begin = datetime(2020, 1, 1)
        end = datetime(2020, 12, 31)
        result = lng.quarterly_sales_long(sample_sales_df, begin=begin, end=end)
        assert result.height > 0

    def test_sorted_by_quarter(self, sample_sales_df):
        result = lng.quarterly_sales_long(sample_sales_df)
        quarters = result["quarter"].to_list()
        assert quarters == sorted(quarters)

    def test_quarterly_units_positive(self, sample_sales_df):
        result = lng.quarterly_sales_long(sample_sales_df)
        assert (result["quarterly_units"] > 0).all()


class TestYearlySalesLong:
    """yearly_sales_long 関数のテスト"""

    def test_returns_dataframe(self, sample_sales_df):
        result = lng.yearly_sales_long(sample_sales_df)
        assert isinstance(result, pl.DataFrame)

    def test_has_expected_columns(self, sample_sales_df):
        result = lng.yearly_sales_long(sample_sales_df)
        assert set(result.columns) == {"year", "hw", "yearly_units"}

    def test_filter_by_hw(self, sample_sales_df):
        result = lng.yearly_sales_long(sample_sales_df, hw=["NSW"])
        assert set(result["hw"].unique().to_list()) == {"NSW"}

    def test_with_date_range(self, sample_sales_df):
        begin = datetime(2020, 1, 1)
        end = datetime(2020, 12, 31)
        result = lng.yearly_sales_long(sample_sales_df, begin=begin, end=end)
        assert result.height > 0

    def test_sorted_by_year(self, sample_sales_df):
        result = lng.yearly_sales_long(sample_sales_df)
        years = result["year"].to_list()
        assert years == sorted(years)

    def test_yearly_units_positive(self, sample_sales_df):
        result = lng.yearly_sales_long(sample_sales_df)
        assert (result["yearly_units"] > 0).all()


class TestCumulativeSalesLong:
    """cumulative_sales_long 関数のテスト"""

    def test_returns_dataframe_week_mode(self, sample_sales_df):
        result = lng.cumulative_sales_long(sample_sales_df, mode="week")
        assert isinstance(result, pl.DataFrame)

    def test_returns_dataframe_month_mode(self, sample_sales_df):
        result = lng.cumulative_sales_long(sample_sales_df, mode="month")
        assert isinstance(result, pl.DataFrame)

    def test_returns_dataframe_year_mode(self, sample_sales_df):
        result = lng.cumulative_sales_long(sample_sales_df, mode="year")
        assert isinstance(result, pl.DataFrame)

    def test_week_mode_has_expected_columns(self, sample_sales_df):
        result = lng.cumulative_sales_long(sample_sales_df, mode="week")
        assert set(result.columns) == {"report_date", "hw", "sum_units"}

    def test_full_name_mode_uses_full_name_column(self, sample_sales_df):
        result = lng.cumulative_sales_long(sample_sales_df, full_name=True)
        assert "full_name" in result.columns
        assert "hw" not in result.columns

    def test_filter_by_hw(self, sample_sales_df):
        result = lng.cumulative_sales_long(sample_sales_df, hw=["NSW"])
        assert set(result["hw"].unique().to_list()) == {"NSW"}

    def test_with_date_range(self, sample_sales_df):
        begin = datetime(2020, 1, 1)
        end = datetime(2020, 12, 31)
        result = lng.cumulative_sales_long(sample_sales_df, begin=begin, end=end)
        assert result.height > 0

    def test_month_mode_has_report_date_column(self, sample_sales_df):
        result = lng.cumulative_sales_long(sample_sales_df, mode="month")
        assert "report_date" in result.columns

    def test_year_mode_has_report_date_column(self, sample_sales_df):
        result = lng.cumulative_sales_long(sample_sales_df, mode="year")
        assert "report_date" in result.columns

    def test_unknown_mode_raises_value_error(self, sample_sales_df):
        with pytest.raises(ValueError):
            lng.cumulative_sales_long(sample_sales_df, mode="unknown")


class TestSalesByDeltaLong:
    """sales_by_delta_long 関数のテスト"""

    def test_returns_dataframe_week_mode(self, sample_sales_df):
        result = lng.sales_by_delta_long(sample_sales_df, mode="week")
        assert isinstance(result, pl.DataFrame)

    def test_returns_dataframe_month_mode(self, sample_sales_df):
        result = lng.sales_by_delta_long(sample_sales_df, mode="month")
        assert isinstance(result, pl.DataFrame)

    def test_returns_dataframe_year_mode(self, sample_sales_df):
        result = lng.sales_by_delta_long(sample_sales_df, mode="year")
        assert isinstance(result, pl.DataFrame)

    def test_week_mode_has_delta_week_column(self, sample_sales_df):
        result = lng.sales_by_delta_long(sample_sales_df, mode="week")
        assert "delta_week" in result.columns

    def test_month_mode_has_delta_month_column(self, sample_sales_df):
        result = lng.sales_by_delta_long(sample_sales_df, mode="month")
        assert "delta_month" in result.columns

    def test_year_mode_has_delta_year_column(self, sample_sales_df):
        result = lng.sales_by_delta_long(sample_sales_df, mode="year")
        assert "delta_year" in result.columns

    def test_invalid_mode_raises_value_error(self, sample_sales_df):
        with pytest.raises(ValueError):
            lng.sales_by_delta_long(sample_sales_df, mode="invalid")

    def test_filter_by_hw(self, sample_sales_df):
        result = lng.sales_by_delta_long(sample_sales_df, hw=["NSW"])
        assert set(result["hw"].unique().to_list()) == {"NSW"}

    def test_full_name_mode(self, sample_sales_df):
        result = lng.sales_by_delta_long(sample_sales_df, full_name=True)
        assert "full_name" in result.columns
        assert "hw" not in result.columns

    def test_with_begin_end(self, sample_sales_df):
        result = lng.sales_by_delta_long(sample_sales_df, begin=10, end=200)
        assert isinstance(result, pl.DataFrame)
        assert (result["delta_week"] >= 10).all()
        assert (result["delta_week"] <= 200).all()

    def test_units_column_present(self, sample_sales_df):
        result = lng.sales_by_delta_long(sample_sales_df, mode="week")
        assert "units" in result.columns


class TestSalesWithOffsetLong:
    """sales_with_offset_long 関数のテスト"""

    def test_returns_dataframe(self, sample_sales_df):
        hw_periods = [{"hw": "NSW", "begin": datetime(2020, 1, 1)}]
        result = lng.sales_with_offset_long(sample_sales_df, hw_periods)
        assert isinstance(result, pl.DataFrame)

    def test_has_expected_columns(self, sample_sales_df):
        hw_periods = [{"hw": "NSW", "begin": datetime(2020, 1, 1), "label": "NSW"}]
        result = lng.sales_with_offset_long(sample_sales_df, hw_periods)
        assert set(result.columns) == {"offset_week", "label", "units"}

    def test_default_label_contains_hw_name(self, sample_sales_df):
        hw_periods = [{"hw": "NSW", "begin": datetime(2020, 1, 5)}]
        result = lng.sales_with_offset_long(sample_sales_df, hw_periods)
        assert any("NSW" in lbl for lbl in result["label"].to_list())

    def test_custom_label(self, sample_sales_df):
        hw_periods = [{"hw": "NSW", "begin": datetime(2020, 1, 1), "label": "NSW2020~"}]
        result = lng.sales_with_offset_long(sample_sales_df, hw_periods)
        assert "NSW2020~" in result["label"].to_list()

    def test_multiple_hw_periods(self, sample_sales_df):
        hw_periods = [
            {"hw": "NSW", "begin": datetime(2020, 1, 1), "label": "NSW"},
            {"hw": "PS5", "begin": datetime(2021, 1, 1), "label": "PS5"},
        ]
        result = lng.sales_with_offset_long(sample_sales_df, hw_periods)
        labels = set(result["label"].to_list())
        assert "NSW" in labels
        assert "PS5" in labels

    def test_end_parameter_limits_rows_per_hw(self, sample_sales_df):
        hw_periods = [{"hw": "NSW", "begin": datetime(2020, 1, 1), "label": "NSW"}]
        result = lng.sales_with_offset_long(sample_sales_df, hw_periods, end=2)
        assert result.height <= 2

    def test_sorted_by_offset_week(self, sample_sales_df):
        hw_periods = [{"hw": "NSW", "begin": datetime(2020, 1, 1), "label": "NSW"}]
        result = lng.sales_with_offset_long(sample_sales_df, hw_periods)
        weeks = result["offset_week"].to_list()
        assert weeks == sorted(weeks)


class TestCumulativeSalesByDeltaLong:
    """cumulative_sales_by_delta_long 関数のテスト"""

    def test_returns_dataframe_week_mode(self, sample_sales_df):
        result = lng.cumulative_sales_by_delta_long(sample_sales_df, mode="week")
        assert isinstance(result, pl.DataFrame)

    def test_returns_dataframe_month_mode(self, sample_sales_df):
        result = lng.cumulative_sales_by_delta_long(sample_sales_df, mode="month")
        assert isinstance(result, pl.DataFrame)

    def test_returns_dataframe_year_mode(self, sample_sales_df):
        result = lng.cumulative_sales_by_delta_long(sample_sales_df, mode="year")
        assert isinstance(result, pl.DataFrame)

    def test_week_mode_has_delta_week_column(self, sample_sales_df):
        result = lng.cumulative_sales_by_delta_long(sample_sales_df, mode="week")
        assert "delta_week" in result.columns

    def test_month_mode_has_delta_month_column(self, sample_sales_df):
        result = lng.cumulative_sales_by_delta_long(sample_sales_df, mode="month")
        assert "delta_month" in result.columns

    def test_year_mode_has_delta_year_column(self, sample_sales_df):
        result = lng.cumulative_sales_by_delta_long(sample_sales_df, mode="year")
        assert "delta_year" in result.columns

    def test_invalid_mode_raises_value_error(self, sample_sales_df):
        with pytest.raises(ValueError):
            lng.cumulative_sales_by_delta_long(sample_sales_df, mode="invalid")

    def test_filter_by_hw(self, sample_sales_df):
        result = lng.cumulative_sales_by_delta_long(sample_sales_df, hw=["NSW"])
        assert set(result["hw"].unique().to_list()) == {"NSW"}

    def test_with_begin_end(self, sample_sales_df):
        result = lng.cumulative_sales_by_delta_long(sample_sales_df, begin=10, end=200)
        assert isinstance(result, pl.DataFrame)
        assert (result["delta_week"] >= 10).all()
        assert (result["delta_week"] <= 200).all()

    def test_sum_units_column_present(self, sample_sales_df):
        result = lng.cumulative_sales_by_delta_long(sample_sales_df, mode="week")
        assert "sum_units" in result.columns


class TestMakerLong:
    """maker_long 関数のテスト"""

    def test_returns_dataframe(self, sample_sales_df):
        result = lng.maker_long(sample_sales_df)
        assert isinstance(result, pl.DataFrame)

    def test_has_expected_columns(self, sample_sales_df):
        result = lng.maker_long(sample_sales_df)
        assert set(result.columns) == {"year", "maker_name", "yearly_units"}

    def test_with_year_range(self, sample_sales_df):
        result = lng.maker_long(sample_sales_df, begin_year=2020, end_year=2021)
        assert result.height > 0

    def test_sorted_by_year(self, sample_sales_df):
        result = lng.maker_long(sample_sales_df)
        years = result["year"].to_list()
        assert years == sorted(years)

    def test_known_maker_names_present(self, sample_sales_df):
        result = lng.maker_long(sample_sales_df)
        makers = set(result["maker_name"].to_list())
        assert "Nintendo" in makers
        assert "SONY" in makers
        assert "Microsoft" in makers

    def test_yearly_units_positive(self, sample_sales_df):
        result = lng.maker_long(sample_sales_df)
        assert (result["yearly_units"] > 0).all()

    def test_begin_year_only(self, sample_sales_df):
        result = lng.maker_long(sample_sales_df, begin_year=2021)
        assert result.height > 0

    def test_end_year_only(self, sample_sales_df):
        result = lng.maker_long(sample_sales_df, end_year=2020)
        assert result.height > 0
