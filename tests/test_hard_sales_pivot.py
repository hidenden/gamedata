"""
gamedata.hard_sales_pivot モジュールのテスト
"""
from datetime import date, datetime
import polars as pl
import pytest

from gamedata import hard_sales_pivot as pv


class TestPivotSales:
    """pivot_sales 関数のテスト"""

    def test_returns_dataframe(self, sample_sales_df):
        result = pv.pivot_sales(sample_sales_df)
        assert isinstance(result, pl.DataFrame)

    def test_report_date_as_index(self, sample_sales_df):
        result = pv.pivot_sales(sample_sales_df)
        assert "report_date" in result.columns

    def test_hw_as_columns(self, sample_sales_df):
        result = pv.pivot_sales(sample_sales_df, hw=["NSW", "PS5"])
        assert "NSW" in result.columns

    def test_filter_by_hw(self, sample_sales_df):
        result = pv.pivot_sales(sample_sales_df, hw=["NSW"])
        assert "NSW" in result.columns
        assert "XSX" not in result.columns

    def test_with_date_range(self, sample_sales_df):
        begin = date(2020, 1, 1)
        end = date(2020, 12, 31)
        result = pv.pivot_sales(sample_sales_df, begin=begin, end=end)
        assert all(d <= end for d in result["report_date"].to_list())

    def test_with_begin_only(self, sample_sales_df):
        begin = date(2021, 1, 1)
        result = pv.pivot_sales(sample_sales_df, begin=begin)
        assert all(d >= begin for d in result["report_date"].to_list())

    def test_with_end_only(self, sample_sales_df):
        end = date(2020, 12, 31)
        result = pv.pivot_sales(sample_sales_df, end=end)
        assert all(d <= end for d in result["report_date"].to_list())

    def test_no_filter_all_data(self, sample_sales_df):
        result = pv.pivot_sales(sample_sales_df)
        assert result.height > 0


class TestPivotMonthlySales:
    """pivot_monthly_sales 関数のテスト"""

    def test_returns_dataframe(self, sample_sales_df):
        result = pv.pivot_monthly_sales(sample_sales_df)
        assert isinstance(result, pl.DataFrame)

    def test_has_month_column(self, sample_sales_df):
        result = pv.pivot_monthly_sales(sample_sales_df)
        assert "month" in result.columns

    def test_filter_by_hw(self, sample_sales_df):
        result = pv.pivot_monthly_sales(sample_sales_df, hw=["NSW"])
        assert "NSW" in result.columns

    def test_with_date_range(self, sample_sales_df):
        begin = datetime(2020, 1, 1)
        end = datetime(2020, 12, 31)
        result = pv.pivot_monthly_sales(sample_sales_df, begin=begin, end=end)
        assert result.height > 0


class TestPivotQuarterlySales:
    """pivot_quarterly_sales 関数のテスト"""

    def test_returns_dataframe(self, sample_sales_df):
        result = pv.pivot_quarterly_sales(sample_sales_df)
        assert isinstance(result, pl.DataFrame)

    def test_has_quarter_column(self, sample_sales_df):
        result = pv.pivot_quarterly_sales(sample_sales_df)
        assert "quarter" in result.columns

    def test_filter_by_hw(self, sample_sales_df):
        result = pv.pivot_quarterly_sales(sample_sales_df, hw=["NSW"])
        assert "NSW" in result.columns

    def test_with_date_range(self, sample_sales_df):
        begin = datetime(2020, 1, 1)
        end = datetime(2020, 12, 31)
        result = pv.pivot_quarterly_sales(sample_sales_df, begin=begin, end=end)
        assert result.height > 0


class TestPivotYearlySales:
    """pivot_yearly_sales 関数のテスト"""

    def test_returns_dataframe(self, sample_sales_df):
        result = pv.pivot_yearly_sales(sample_sales_df)
        assert isinstance(result, pl.DataFrame)

    def test_has_year_column(self, sample_sales_df):
        result = pv.pivot_yearly_sales(sample_sales_df)
        assert "year" in result.columns

    def test_filter_by_hw(self, sample_sales_df):
        result = pv.pivot_yearly_sales(sample_sales_df, hw=["NSW"])
        assert "NSW" in result.columns

    def test_with_date_range(self, sample_sales_df):
        begin = datetime(2020, 1, 1)
        end = datetime(2020, 12, 31)
        result = pv.pivot_yearly_sales(sample_sales_df, begin=begin, end=end)
        assert result.height > 0


class TestPivotCumulativeSales:
    """pivot_cumulative_sales 関数のテスト"""

    def test_returns_dataframe_week_mode(self, sample_sales_df):
        result = pv.pivot_cumulative_sales(sample_sales_df, mode="week")
        assert isinstance(result, pl.DataFrame)

    def test_returns_dataframe_month_mode(self, sample_sales_df):
        result = pv.pivot_cumulative_sales(sample_sales_df, mode="month")
        assert isinstance(result, pl.DataFrame)

    def test_returns_dataframe_year_mode(self, sample_sales_df):
        result = pv.pivot_cumulative_sales(sample_sales_df, mode="year")
        assert isinstance(result, pl.DataFrame)

    def test_filter_by_hw(self, sample_sales_df):
        result = pv.pivot_cumulative_sales(sample_sales_df, hw=["NSW"])
        assert "NSW" in result.columns

    def test_full_name_mode(self, sample_sales_df):
        result = pv.pivot_cumulative_sales(sample_sales_df, full_name=True)
        assert "Nintendo Switch" in result.columns

    def test_with_date_range(self, sample_sales_df):
        begin = datetime(2020, 1, 1)
        end = datetime(2020, 12, 31)
        result = pv.pivot_cumulative_sales(sample_sales_df, begin=begin, end=end)
        assert result.height > 0


class TestPivotSalesByDelta:
    """pivot_sales_by_delta 関数のテスト"""

    def test_returns_dataframe_week_mode(self, sample_sales_df):
        result = pv.pivot_sales_by_delta(sample_sales_df, mode="week")
        assert isinstance(result, pl.DataFrame)

    def test_returns_dataframe_month_mode(self, sample_sales_df):
        result = pv.pivot_sales_by_delta(sample_sales_df, mode="month")
        assert isinstance(result, pl.DataFrame)

    def test_returns_dataframe_year_mode(self, sample_sales_df):
        result = pv.pivot_sales_by_delta(sample_sales_df, mode="year")
        assert isinstance(result, pl.DataFrame)

    def test_invalid_mode_raises_error(self, sample_sales_df):
        with pytest.raises(ValueError):
            pv.pivot_sales_by_delta(sample_sales_df, mode="invalid")

    def test_filter_by_hw(self, sample_sales_df):
        result = pv.pivot_sales_by_delta(sample_sales_df, hw=["NSW"])
        assert "NSW" in result.columns

    def test_full_name_mode(self, sample_sales_df):
        result = pv.pivot_sales_by_delta(sample_sales_df, full_name=True)
        assert "Nintendo Switch" in result.columns

    def test_with_begin_end(self, sample_sales_df):
        result = pv.pivot_sales_by_delta(sample_sales_df, begin=10, end=200)
        assert isinstance(result, pl.DataFrame)


class TestPivotSalesWithOffset:
    """pivot_sales_with_offset 関数のテスト"""

    def test_returns_dataframe(self, sample_sales_df):
        hw_periods = [
            {"hw": "NSW", "begin": datetime(2020, 1, 1)},
        ]
        result = pv.pivot_sales_with_offset(sample_sales_df, hw_periods)
        assert isinstance(result, pl.DataFrame)

    def test_has_offset_week_column(self, sample_sales_df):
        hw_periods = [
            {"hw": "NSW", "begin": datetime(2020, 1, 1)},
        ]
        result = pv.pivot_sales_with_offset(sample_sales_df, hw_periods)
        assert "offset_week" in result.columns

    def test_custom_label(self, sample_sales_df):
        hw_periods = [
            {"hw": "NSW", "begin": datetime(2020, 1, 1), "label": "NSW2020~"},
        ]
        result = pv.pivot_sales_with_offset(sample_sales_df, hw_periods)
        assert "NSW2020~" in result.columns

    def test_default_label(self, sample_sales_df):
        """label が省略された場合、デフォルトラベルが使われること"""
        hw_periods = [
            {"hw": "NSW", "begin": datetime(2020, 1, 5)},
        ]
        result = pv.pivot_sales_with_offset(sample_sales_df, hw_periods)
        # デフォルトラベル: "NSW:2020.01.05〜"
        assert any("NSW" in col for col in result.columns)

    def test_multiple_hw_periods(self, sample_sales_df):
        hw_periods = [
            {"hw": "NSW", "begin": datetime(2020, 1, 1), "label": "NSW"},
            {"hw": "PS5", "begin": datetime(2021, 1, 1), "label": "PS5"},
        ]
        result = pv.pivot_sales_with_offset(sample_sales_df, hw_periods)
        assert "NSW" in result.columns
        assert "PS5" in result.columns

    def test_end_parameter_limits_rows(self, sample_sales_df):
        hw_periods = [
            {"hw": "NSW", "begin": datetime(2020, 1, 1), "label": "NSW"},
        ]
        result = pv.pivot_sales_with_offset(sample_sales_df, hw_periods, end=2)
        assert result.height <= 2


class TestPivotCumulativeSalesByDelta:
    """pivot_cumulative_sales_by_delta 関数のテスト"""

    def test_returns_dataframe_week_mode(self, sample_sales_df):
        result = pv.pivot_cumulative_sales_by_delta(sample_sales_df, mode="week")
        assert isinstance(result, pl.DataFrame)

    def test_returns_dataframe_month_mode(self, sample_sales_df):
        result = pv.pivot_cumulative_sales_by_delta(sample_sales_df, mode="month")
        assert isinstance(result, pl.DataFrame)

    def test_returns_dataframe_year_mode(self, sample_sales_df):
        result = pv.pivot_cumulative_sales_by_delta(sample_sales_df, mode="year")
        assert isinstance(result, pl.DataFrame)

    def test_invalid_mode_raises_error(self, sample_sales_df):
        with pytest.raises(ValueError):
            pv.pivot_cumulative_sales_by_delta(sample_sales_df, mode="invalid")

    def test_filter_by_hw(self, sample_sales_df):
        result = pv.pivot_cumulative_sales_by_delta(sample_sales_df, hw=["NSW"])
        assert "NSW" in result.columns

    def test_with_begin_end(self, sample_sales_df):
        result = pv.pivot_cumulative_sales_by_delta(sample_sales_df, begin=10, end=200)
        assert isinstance(result, pl.DataFrame)


class TestPivotMaker:
    """pivot_maker 関数のテスト"""

    def test_returns_dataframe(self, sample_sales_df):
        result = pv.pivot_maker(sample_sales_df)
        assert isinstance(result, pl.DataFrame)

    def test_has_year_column(self, sample_sales_df):
        result = pv.pivot_maker(sample_sales_df)
        assert "year" in result.columns

    def test_with_year_range(self, sample_sales_df):
        result = pv.pivot_maker(sample_sales_df, begin_year=2020, end_year=2021)
        assert result.height > 0

    def test_maker_columns_in_desired_order(self, sample_sales_df):
        result = pv.pivot_maker(sample_sales_df)
        cols = result.columns
        # Nintendo, SONY, Microsoft の順に並ぶ（存在する場合）
        existing = [c for c in ["Nintendo", "SONY", "Microsoft"] if c in cols]
        actual = [c for c in cols if c in ["Nintendo", "SONY", "Microsoft"]]
        assert actual == existing


class TestCumsumDiffs:
    """cumsum_diffs 関数のテスト"""

    def test_returns_dataframe(self, sample_sales_df):
        # base=PS5, cmp=NSW → NSW.sum - PS5.sum が正になるため filter を通過
        result = pv.cumsum_diffs(sample_sales_df, [("PS5", "NSW")])
        assert isinstance(result, pl.DataFrame)

    def test_has_weeks_column(self, sample_sales_df):
        result = pv.cumsum_diffs(sample_sales_df, [("PS5", "NSW")])
        assert "weeks" in result.columns

    def test_single_pair_result(self, sample_sales_df):
        """1ペアの場合に結果が返ること"""
        result = pv.cumsum_diffs(sample_sales_df, [("PS5", "NSW")])
        assert result.height > 0

    def test_multiple_pairs(self, sample_sales_df):
        # NSW の cumsum は常に PS5/XSX より大きいので base に小さい方を入れる
        result = pv.cumsum_diffs(sample_sales_df, [("PS5", "NSW"), ("XSX", "NSW")])
        assert isinstance(result, pl.DataFrame)
        # XSX は PS5 より少ない週数しかないため 0行になる可能性があるが型はチェックする
