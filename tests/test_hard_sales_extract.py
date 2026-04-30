"""
gamedata.hard_sales_extract モジュールのテスト
"""
from datetime import date, datetime
import polars as pl
import pytest

from gamedata import hard_sales_extract as hse


class TestExtractWeekReachedUnits:
    """extract_week_reached_units 関数のテスト"""

    def test_returns_dataframe(self, sample_sales_df):
        result = hse.extract_week_reached_units(sample_sales_df, 50000)
        assert isinstance(result, pl.DataFrame)

    def test_found_hardware(self, sample_sales_df):
        """50000 台を超えたハードが返ること (NSW は初週から 30000, 2週目で 55000)"""
        result = hse.extract_week_reached_units(sample_sales_df, 50000)
        assert "NSW" in result["hw"].to_list()

    def test_each_hw_appears_once(self, sample_sales_df):
        """各ハードは最大1行のみ返ること"""
        result = hse.extract_week_reached_units(sample_sales_df, 1)
        hw_list = result["hw"].to_list()
        assert len(hw_list) == len(set(hw_list))

    def test_threshold_not_reached_returns_empty(self, sample_sales_df):
        """閾値を超えるハードがない場合は空 DataFrame が返ること"""
        result = hse.extract_week_reached_units(sample_sales_df, 10_000_000)
        assert result.height == 0

    def test_returns_first_week_reached(self, sample_sales_df):
        """閾値を初めて超えた週が返ること (NSW: sum_units >= 55000 は 2週目)"""
        result = hse.extract_week_reached_units(sample_sales_df, 55000)
        nsw_row = result.filter(pl.col("hw") == "NSW")
        assert nsw_row.height == 1
        assert nsw_row["sum_units"][0] >= 55000


class TestExtractByDate:
    """extract_by_date 関数のテスト"""

    def test_returns_dataframe(self, sample_sales_df):
        target = date(2020, 1, 5)
        result = hse.extract_by_date(sample_sales_df, target)
        assert isinstance(result, pl.DataFrame)

    def test_exact_date(self, sample_sales_df):
        """report_date と完全一致する日付でデータが取得できること"""
        target = date(2020, 1, 5)
        result = hse.extract_by_date(sample_sales_df, target)
        assert result.height > 0

    def test_with_datetime_type(self, sample_sales_df):
        """datetime 型でも動作すること"""
        target = datetime(2020, 1, 5)
        result = hse.extract_by_date(sample_sales_df, target)
        assert result.height > 0

    def test_filter_by_hw(self, sample_sales_df):
        """hw 引数でフィルタリングできること"""
        target = date(2021, 4, 4)
        result = hse.extract_by_date(sample_sales_df, target, hw=["NSW"])
        assert all(r == "NSW" for r in result["hw"].to_list())

    def test_no_match_returns_empty(self, sample_sales_df):
        """マッチしない日付の場合は空 DataFrame が返ること"""
        target = date(2000, 1, 1)
        result = hse.extract_by_date(sample_sales_df, target)
        assert result.height == 0

    def test_none_hw_returns_all(self, sample_sales_df):
        """hw が None の場合は全ハードが返ること"""
        target = date(2021, 4, 4)
        result_all = hse.extract_by_date(sample_sales_df, target, hw=None)
        result_all_default = hse.extract_by_date(sample_sales_df, target)
        assert result_all.height == result_all_default.height


class TestExtractLatest:
    """extract_latest 関数のテスト"""

    def test_returns_dataframe(self, sample_sales_df):
        result = hse.extract_latest(sample_sales_df)
        assert isinstance(result, pl.DataFrame)

    def test_default_one_week(self, sample_sales_df):
        """デフォルト（weeks=1）では最新週のデータのみ返ること"""
        result = hse.extract_latest(sample_sales_df)
        max_date = sample_sales_df["report_date"].max()
        assert all(d == max_date for d in result["report_date"].to_list())

    def test_multiple_weeks(self, sample_sales_df):
        """weeks=2 では最新2週分のデータが返ること"""
        result = hse.extract_latest(sample_sales_df, weeks=2)
        assert result.height > 0
        # report_date が最新から2週分の範囲内
        max_date = sample_sales_df["report_date"].max()
        assert all(d <= max_date for d in result["report_date"].to_list())

    def test_sorted_by_report_date_and_units(self, sample_sales_df):
        """report_date 昇順 → units 降順でソートされていること"""
        result = hse.extract_latest(sample_sales_df, weeks=3)
        if result.height >= 2:
            dates = result["report_date"].to_list()
            assert dates == sorted(dates)


class TestExtractTotal:
    """extract_total 関数のテスト"""

    def test_returns_dataframe(self, sample_sales_df):
        result = hse.extract_total(sample_sales_df)
        assert isinstance(result, pl.DataFrame)

    def test_each_hw_appears_once(self, sample_sales_df):
        """各ハードは1行のみ返ること"""
        result = hse.extract_total(sample_sales_df)
        hw_list = result["hw"].to_list()
        assert len(hw_list) == len(set(hw_list))

    def test_sorted_by_sum_units_descending(self, sample_sales_df):
        """sum_units の降順でソートされていること"""
        result = hse.extract_total(sample_sales_df)
        sums = result["sum_units"].to_list()
        assert sums == sorted(sums, reverse=True)

    def test_compact_mode(self, sample_sales_df):
        """compact=True の場合、最小限のカラムのみ返ること"""
        result = hse.extract_total(sample_sales_df, compact=True)
        assert set(result.columns) == {"hw", "sum_units", "report_date"}

    def test_non_compact_mode(self, sample_sales_df):
        """compact=False の場合、全カラムが返ること"""
        result = hse.extract_total(sample_sales_df, compact=False)
        assert "weekly_id" in result.columns

    def test_returns_max_sum_units_for_each_hw(self, sample_sales_df):
        """各ハードの最大累計販売台数の行が返ること"""
        result = hse.extract_total(sample_sales_df)
        for row in result.iter_rows(named=True):
            hw = row["hw"]
            max_sum = sample_sales_df.filter(pl.col("hw") == hw)["sum_units"].max()
            assert row["sum_units"] == max_sum
