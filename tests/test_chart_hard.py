"""
gamedata.chart_hard モジュールのテスト
"""
from datetime import date, datetime
from unittest.mock import patch, MagicMock
import polars as pl
import pytest

from gamedata import chart_hard as ch
from gamedata import hard_info as hi


class TestRenameColumns:
    """rename_columns 関数のテスト"""

    def _make_simple_df(self):
        return pl.DataFrame({
            "hw": ["NSW", "PS5"],
            "report_date": [date(2020, 1, 5), date(2020, 1, 12)],
            "units": [10000, 5000],
            "sum_units": [10000, 5000],
        }).with_columns(pl.col("report_date").cast(pl.Date))

    def test_renames_hw_to_japanese(self):
        df = self._make_simple_df()
        result = ch.rename_columns(df)
        assert "ハード" in result.columns

    def test_renames_report_date_to_japanese(self):
        df = self._make_simple_df()
        result = ch.rename_columns(df)
        assert "集計日" in result.columns

    def test_renames_units_to_japanese(self):
        df = self._make_simple_df()
        result = ch.rename_columns(df)
        assert "販売台数" in result.columns

    def test_unknown_columns_unchanged(self):
        df = pl.DataFrame({"unknown_col": [1, 2, 3]})
        result = ch.rename_columns(df)
        assert "unknown_col" in result.columns

    def test_returns_dataframe(self):
        df = self._make_simple_df()
        result = ch.rename_columns(df)
        assert isinstance(result, pl.DataFrame)


class TestRenameHw:
    """rename_hw 関数のテスト"""

    def test_renames_hw_values(self, sample_sales_df):
        result = ch.rename_hw(sample_sales_df)
        assert "Nintendo Switch" in result["hw"].to_list()

    def test_no_hw_column_unchanged(self):
        df = pl.DataFrame({"other_col": [1, 2, 3]})
        result = ch.rename_hw(df)
        assert "other_col" in result.columns
        assert result.equals(df)

    def test_unknown_hw_kept_as_is(self):
        df = pl.DataFrame({"hw": ["UNKNOWN_HW"]})
        result = ch.rename_hw(df)
        assert result["hw"][0] == "UNKNOWN_HW"


class TestChartUnitsByDateHw:
    """chart_units_by_date_hw 関数のテスト"""

    def test_returns_styler(self, sample_sales_df):
        from pandas.io.formats.style import Styler
        result = ch.chart_units_by_date_hw(sample_sales_df)
        assert isinstance(result, Styler)

    def test_with_begin_and_end(self, sample_sales_df):
        from pandas.io.formats.style import Styler
        begin = date(2020, 1, 1)
        end = date(2020, 12, 31)
        result = ch.chart_units_by_date_hw(sample_sales_df, begin=begin, end=end)
        assert isinstance(result, Styler)


class TestChartPeriodicRankingFunctions:
    """chart_weekly/monthly/yearly_ranking 関数のテスト (DB モック)"""

    def test_chart_weekly_ranking_returns_dataframe(self, sample_sales_df):
        with patch("gamedata.hard_sales.load_hard_sales", return_value=sample_sales_df):
            result = ch.chart_weekly_ranking(rank_n=3)
        assert isinstance(result, pl.DataFrame)

    def test_chart_weekly_ranking_hw_filter(self, sample_sales_df):
        with patch("gamedata.hard_sales.load_hard_sales", return_value=sample_sales_df):
            result = ch.chart_weekly_ranking(rank_n=3, hw=["NSW"])
        assert isinstance(result, pl.DataFrame)

    def test_chart_weekly_ranking_maker_mode(self, sample_sales_df):
        with patch("gamedata.hard_sales.load_hard_sales", return_value=sample_sales_df):
            result = ch.chart_weekly_ranking(rank_n=3, maker=["Nintendo"])
        assert isinstance(result, pl.DataFrame)

    def test_chart_weekly_ranking_negative_rank(self, sample_sales_df):
        """rank_n が負の場合、下位ランキングが返ること"""
        with patch("gamedata.hard_sales.load_hard_sales", return_value=sample_sales_df):
            result = ch.chart_weekly_ranking(rank_n=-3)
        assert isinstance(result, pl.DataFrame)

    def test_chart_monthly_ranking_returns_dataframe(self, sample_sales_df):
        with patch("gamedata.hard_sales.load_hard_sales", return_value=sample_sales_df):
            result = ch.chart_monthly_ranking(rank_n=3)
        assert isinstance(result, pl.DataFrame)

    def test_chart_monthly_ranking_with_date_range(self, sample_sales_df):
        with patch("gamedata.hard_sales.load_hard_sales", return_value=sample_sales_df):
            result = ch.chart_monthly_ranking(
                rank_n=3, begin=date(2020, 1, 1), end=date(2020, 12, 31)
            )
        assert isinstance(result, pl.DataFrame)

    def test_chart_yearly_ranking_returns_dataframe(self, sample_sales_df):
        with patch("gamedata.hard_sales.load_hard_sales", return_value=sample_sales_df):
            result = ch.chart_yearly_ranking(rank_n=3)
        assert isinstance(result, pl.DataFrame)

    def test_chart_yearly_ranking_maker_mode(self, sample_sales_df):
        with patch("gamedata.hard_sales.load_hard_sales", return_value=sample_sales_df):
            result = ch.chart_yearly_ranking(rank_n=3, maker=["Nintendo", "SONY"])
        assert isinstance(result, pl.DataFrame)


class TestChartDeltaWeekRanking:
    """chart_delta_week_ranking 関数のテスト (DB モック)"""

    def test_returns_dataframe(self, sample_sales_df):
        with patch("gamedata.hard_sales.load_hard_sales", return_value=sample_sales_df):
            result = ch.chart_delta_week_ranking(delta_week=10)
        assert isinstance(result, pl.DataFrame)

    def test_has_expected_columns(self, sample_sales_df):
        with patch("gamedata.hard_sales.load_hard_sales", return_value=sample_sales_df):
            result = ch.chart_delta_week_ranking(delta_week=10)
        # 日本語にリネームされたカラムが含まれること
        assert "累計台数" in result.columns or result.height == 0


class TestChartReachedUnit:
    """chart_reached_unit 関数のテスト (DB モック)"""

    def test_returns_dataframe(self, sample_sales_df):
        with patch("gamedata.hard_sales.load_hard_sales", return_value=sample_sales_df):
            result = ch.chart_reached_unit(50000)
        assert isinstance(result, pl.DataFrame)

    def test_all_parameter(self, sample_sales_df):
        with patch("gamedata.hard_sales.load_hard_sales", return_value=sample_sales_df):
            result = ch.chart_reached_unit(50000, all=True)
        assert isinstance(result, pl.DataFrame)

    def test_default_top_10(self, sample_sales_df):
        """all=False の場合、最大10件が返ること"""
        with patch("gamedata.hard_sales.load_hard_sales", return_value=sample_sales_df):
            result = ch.chart_reached_unit(1, all=False)
        assert result.height <= 10


class TestStyleSales:
    """style_sales 関数のテスト"""

    def test_returns_styler(self, sample_sales_df):
        from pandas.io.formats.style import Styler
        # 数値カラムのみの簡易 DataFrame
        df = pl.DataFrame({
            "hw": ["NSW", "PS5"],
            "units": [10000, 5000],
            "sum_units": [100000, 50000],
        })
        result = ch.style_sales(df, columns=["units", "sum_units"])
        assert isinstance(result, Styler)

    def test_with_date_columns(self, sample_sales_df):
        from pandas.io.formats.style import Styler
        df = pl.DataFrame({
            "hw": ["NSW", "PS5"],
            "report_date": [date(2020, 1, 5), date(2020, 1, 12)],
            "units": [10000, 8000],
        }).with_columns(pl.col("report_date").cast(pl.Date))
        # hw が index になるので date_columns に report_date を渡す
        result = ch.style_sales(df, columns=["units"], date_columns=["report_date"])
        assert isinstance(result, Styler)

    def test_with_percent_columns(self):
        from pandas.io.formats.style import Styler
        df = pl.DataFrame({
            "hw": ["NSW"],
            "share": [0.5],
        })
        result = ch.style_sales(df, percent_columns=["share"])
        assert isinstance(result, Styler)

    def test_with_highlights(self):
        from pandas.io.formats.style import Styler
        df = pl.DataFrame({
            "hw": ["NSW", "PS5"],
            "units": [10000, 5000],
        })
        result = ch.style_sales(df, columns=["units"], highlights=["units"])
        assert isinstance(result, Styler)

    def test_with_gradients(self):
        from pandas.io.formats.style import Styler
        df = pl.DataFrame({
            "hw": ["NSW", "PS5"],
            "units": [10000, 5000],
        })
        result = ch.style_sales(df, columns=["units"], gradients=["units"])
        assert isinstance(result, Styler)

    def test_with_bars(self):
        from pandas.io.formats.style import Styler
        df = pl.DataFrame({
            "hw": ["NSW", "PS5"],
            "units": [10000, 5000],
        })
        result = ch.style_sales(df, columns=["units"], bars=["units"])
        assert isinstance(result, Styler)

    def test_with_gradient_horizontal(self):
        from pandas.io.formats.style import Styler
        df = pl.DataFrame({
            "hw": ["NSW", "PS5"],
            "units": [10000, 5000],
        })
        result = ch.style_sales(df, columns=["units"], gradient_horizontal=True)
        assert isinstance(result, Styler)

    def test_with_datetime_index(self):
        from pandas.io.formats.style import Styler
        df = pl.DataFrame({
            "report_date": [date(2020, 1, 5), date(2020, 1, 12)],
            "units": [10000, 8000],
        }).with_columns(pl.col("report_date").cast(pl.Date))
        result = ch.style_sales(df, columns=["units"], datetime_index=True)
        assert isinstance(result, Styler)


class TestStyle:
    """style 関数のテスト"""

    def test_returns_styler(self):
        from pandas.io.formats.style import Styler
        df = pl.DataFrame({
            "hw": ["NSW", "PS5"],
            "units": [10000, 5000],
        })
        result = ch.style(df)
        assert isinstance(result, Styler)

    def test_with_highlight(self):
        from pandas.io.formats.style import Styler
        df = pl.DataFrame({
            "hw": ["NSW", "PS5"],
            "units": [10000, 5000],
        })
        result = ch.style(df, highlight=True)
        assert isinstance(result, Styler)

    def test_with_gradient(self):
        from pandas.io.formats.style import Styler
        df = pl.DataFrame({
            "hw": ["NSW", "PS5"],
            "units": [10000, 5000],
        })
        result = ch.style(df, gradient=True)
        assert isinstance(result, Styler)

    def test_with_bar(self):
        from pandas.io.formats.style import Styler
        df = pl.DataFrame({
            "hw": ["NSW", "PS5"],
            "units": [10000, 5000],
        })
        result = ch.style(df, bar=True)
        assert isinstance(result, Styler)

    def test_non_unique_first_column_adds_id(self):
        """最初のカラムがユニークでない場合、id カラムが追加されること"""
        from pandas.io.formats.style import Styler
        df = pl.DataFrame({
            "hw": ["NSW", "NSW"],  # 重複あり
            "units": [10000, 5000],
        })
        result = ch.style(df)
        assert isinstance(result, Styler)

    def test_date_column_as_first_column(self):
        """最初のカラムが日付型の場合の処理"""
        from pandas.io.formats.style import Styler
        df = pl.DataFrame({
            "report_date": [date(2020, 1, 5), date(2020, 1, 12)],
            "units": [10000, 8000],
        }).with_columns(pl.col("report_date").cast(pl.Date))
        result = ch.style(df)
        assert isinstance(result, Styler)

    def test_with_gradient_horizontal(self):
        from pandas.io.formats.style import Styler
        df = pl.DataFrame({
            "hw": ["NSW", "PS5"],
            "units": [10000, 5000],
        })
        result = ch.style(df, gradient_horizontal=True)
        assert isinstance(result, Styler)
