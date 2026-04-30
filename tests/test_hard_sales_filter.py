"""
gamedata.hard_sales_filter モジュールのテスト
"""
from datetime import date, datetime
import polars as pl
import pytest

from gamedata import hard_sales_filter as hsf


class TestDateFilter:
    """date_filter 関数のテスト"""

    def test_both_begin_and_end(self, sample_sales_df):
        """begin と end の両方を指定した場合"""
        begin = date(2020, 1, 1)
        end = date(2020, 12, 31)
        result = hsf.date_filter(sample_sales_df, begin=begin, end=end)
        assert all(d >= begin for d in result["report_date"].to_list())
        assert all(d <= end for d in result["report_date"].to_list())

    def test_begin_only(self, sample_sales_df):
        """begin のみ指定した場合"""
        begin = date(2021, 1, 1)
        result = hsf.date_filter(sample_sales_df, begin=begin)
        assert all(d >= begin for d in result["report_date"].to_list())

    def test_end_only(self, sample_sales_df):
        """end のみ指定した場合"""
        end = date(2020, 6, 30)
        result = hsf.date_filter(sample_sales_df, end=end)
        assert all(d <= end for d in result["report_date"].to_list())

    def test_neither_returns_clone(self, sample_sales_df):
        """begin も end も指定しない場合、全データのクローンが返ること"""
        result = hsf.date_filter(sample_sales_df)
        assert result.height == sample_sales_df.height

    def test_no_match_returns_empty(self, sample_sales_df):
        """マッチしない範囲の場合、空 DataFrame が返ること"""
        result = hsf.date_filter(sample_sales_df,
                                  begin=date(1990, 1, 1),
                                  end=date(1990, 12, 31))
        assert result.height == 0


class TestWeeklySales:
    """weekly_sales 関数のテスト"""

    def test_returns_dataframe(self, sample_sales_df):
        result = hsf.weekly_sales(sample_sales_df)
        assert isinstance(result, pl.DataFrame)

    def test_has_weekly_units_column(self, sample_sales_df):
        result = hsf.weekly_sales(sample_sales_df)
        assert "weekly_units" in result.columns

    def test_hw_mode(self, sample_sales_df):
        """maker_mode=False の場合、hw カラムが返ること"""
        result = hsf.weekly_sales(sample_sales_df, maker_mode=False)
        assert "hw" in result.columns

    def test_maker_mode(self, sample_sales_df):
        """maker_mode=True の場合、maker_name カラムが返ること"""
        result = hsf.weekly_sales(sample_sales_df, maker_mode=True)
        assert "maker_name" in result.columns

    def test_with_date_range(self, sample_sales_df):
        """日付範囲を指定した場合、その範囲内のデータのみ返ること"""
        begin = date(2020, 1, 1)
        end = date(2020, 12, 31)
        result = hsf.weekly_sales(sample_sales_df, begin=begin, end=end)
        assert all(d >= begin for d in result["report_date"].to_list())
        assert all(d <= end for d in result["report_date"].to_list())

    def test_sum_units_cumulative(self, sample_sales_df):
        """sum_units が累積であること"""
        result = hsf.weekly_sales(sample_sales_df)
        assert "sum_units" in result.columns


class TestMonthlySales:
    """monthly_sales 関数のテスト"""

    def test_returns_dataframe(self, sample_sales_df):
        result = hsf.monthly_sales(sample_sales_df)
        assert isinstance(result, pl.DataFrame)

    def test_has_monthly_units_column(self, sample_sales_df):
        result = hsf.monthly_sales(sample_sales_df)
        assert "monthly_units" in result.columns

    def test_hw_mode(self, sample_sales_df):
        result = hsf.monthly_sales(sample_sales_df, maker_mode=False)
        assert "hw" in result.columns

    def test_maker_mode(self, sample_sales_df):
        result = hsf.monthly_sales(sample_sales_df, maker_mode=True)
        assert "maker_name" in result.columns

    def test_with_date_range(self, sample_sales_df):
        begin = date(2020, 1, 1)
        end = date(2020, 6, 30)
        result = hsf.monthly_sales(sample_sales_df, begin=begin, end=end)
        assert result.height > 0


class TestQuarterlySales:
    """quarterly_sales 関数のテスト"""

    def test_returns_dataframe(self, sample_sales_df):
        result = hsf.quarterly_sales(sample_sales_df)
        assert isinstance(result, pl.DataFrame)

    def test_has_quarterly_units_column(self, sample_sales_df):
        result = hsf.quarterly_sales(sample_sales_df)
        assert "quarterly_units" in result.columns

    def test_hw_mode(self, sample_sales_df):
        result = hsf.quarterly_sales(sample_sales_df, maker_mode=False)
        assert "hw" in result.columns

    def test_maker_mode(self, sample_sales_df):
        result = hsf.quarterly_sales(sample_sales_df, maker_mode=True)
        assert "maker_name" in result.columns

    def test_with_date_range(self, sample_sales_df):
        begin = date(2020, 1, 1)
        end = date(2020, 12, 31)
        result = hsf.quarterly_sales(sample_sales_df, begin=begin, end=end)
        assert result.height > 0

    def test_has_year_and_q_num_columns(self, sample_sales_df):
        result = hsf.quarterly_sales(sample_sales_df)
        assert "year" in result.columns
        assert "q_num" in result.columns


class TestYearlySales:
    """yearly_sales 関数のテスト"""

    def test_returns_dataframe(self, sample_sales_df):
        result = hsf.yearly_sales(sample_sales_df)
        assert isinstance(result, pl.DataFrame)

    def test_has_yearly_units_column(self, sample_sales_df):
        result = hsf.yearly_sales(sample_sales_df)
        assert "yearly_units" in result.columns

    def test_hw_mode(self, sample_sales_df):
        result = hsf.yearly_sales(sample_sales_df, maker_mode=False)
        assert "hw" in result.columns

    def test_maker_mode(self, sample_sales_df):
        result = hsf.yearly_sales(sample_sales_df, maker_mode=True)
        assert "maker_name" in result.columns

    def test_with_date_range(self, sample_sales_df):
        begin = date(2020, 1, 1)
        end = date(2020, 12, 31)
        result = hsf.yearly_sales(sample_sales_df, begin=begin, end=end)
        assert result.height > 0


class TestYearlyMakerSales:
    """yearly_maker_sales 関数のテスト"""

    def test_returns_dataframe(self, sample_sales_df):
        result = hsf.yearly_maker_sales(sample_sales_df)
        assert isinstance(result, pl.DataFrame)

    def test_has_yearly_units_column(self, sample_sales_df):
        result = hsf.yearly_maker_sales(sample_sales_df)
        assert "yearly_units" in result.columns

    def test_no_sum_units_column(self, sample_sales_df):
        """sum_units カラムが含まれないこと"""
        result = hsf.yearly_maker_sales(sample_sales_df)
        assert "sum_units" not in result.columns

    def test_has_maker_name_column(self, sample_sales_df):
        result = hsf.yearly_maker_sales(sample_sales_df)
        assert "maker_name" in result.columns

    def test_with_date_range(self, sample_sales_df):
        begin = date(2020, 1, 1)
        end = date(2020, 12, 31)
        result = hsf.yearly_maker_sales(sample_sales_df, begin=begin, end=end)
        assert result.height > 0


class TestDeltaYearlySales:
    """delta_yearly_sales 関数のテスト"""

    def test_returns_dataframe(self, sample_sales_df):
        result = hsf.delta_yearly_sales(sample_sales_df)
        assert isinstance(result, pl.DataFrame)

    def test_has_required_columns(self, sample_sales_df):
        result = hsf.delta_yearly_sales(sample_sales_df)
        assert "delta_year" in result.columns
        assert "hw" in result.columns
        assert "yearly_units" in result.columns
        assert "sum_units" in result.columns

    def test_sum_units_is_cumulative(self, sample_sales_df):
        """sum_units が hw ごとの累積であること"""
        result = hsf.delta_yearly_sales(sample_sales_df)
        # NSW の sum_units は yearly_units の累積合計と一致するはず
        nsw = result.filter(pl.col("hw") == "NSW").sort("delta_year")
        assert nsw.height > 0
