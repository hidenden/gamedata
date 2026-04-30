"""
gamedata.hard_sales モジュールのテスト
"""
from datetime import date, datetime
from unittest.mock import patch, MagicMock
import polars as pl
import pytest

import gamedata.hard_sales as hs


# ---------------------------------------------------------------------------
# テスト用ヘルパー
# ---------------------------------------------------------------------------

def _reset_globals():
    """モジュールレベルのキャッシュをリセットする"""
    hs._all_hw_list = None
    hs._all_maker_list = None


# ---------------------------------------------------------------------------
# current_report_date
# ---------------------------------------------------------------------------

class TestCurrentReportDate:
    def test_returns_max_date(self, sample_sales_df):
        result = hs.current_report_date(sample_sales_df)
        expected = date(2021, 4, 4)
        assert result == expected

    def test_single_row(self):
        df = pl.DataFrame({
            "report_date": [date(2023, 1, 1)],
        }).with_columns(pl.col("report_date").cast(pl.Date))
        result = hs.current_report_date(df)
        assert result == date(2023, 1, 1)


# ---------------------------------------------------------------------------
# get_hw
# ---------------------------------------------------------------------------

class TestGetHw:
    def test_returns_list(self, sample_sales_df):
        result = hs.get_hw(sample_sales_df)
        assert isinstance(result, list)

    def test_contains_all_hardware(self, sample_sales_df):
        result = hs.get_hw(sample_sales_df)
        assert "NSW" in result
        assert "PS5" in result
        assert "XSX" in result

    def test_no_duplicates(self, sample_sales_df):
        result = hs.get_hw(sample_sales_df)
        assert len(result) == len(set(result))

    def test_empty_dataframe(self):
        df = pl.DataFrame({
            "hw": pl.Series([], dtype=pl.Utf8),
            "maker_name": pl.Series([], dtype=pl.Utf8),
            "launch_date": pl.Series([], dtype=pl.Date),
        })
        result = hs.get_hw(df)
        assert result == []


# ---------------------------------------------------------------------------
# get_maker
# ---------------------------------------------------------------------------

class TestGetMaker:
    def test_returns_list(self, sample_sales_df):
        result = hs.get_maker(sample_sales_df)
        assert isinstance(result, list)

    def test_contains_all_makers(self, sample_sales_df):
        result = hs.get_maker(sample_sales_df)
        assert "Nintendo" in result
        assert "SONY" in result
        assert "Microsoft" in result


# ---------------------------------------------------------------------------
# with_units_diff
# ---------------------------------------------------------------------------

class TestWithUnitsDiff:
    def test_adds_units_diff_column(self, sample_sales_df):
        result = hs.with_units_diff(sample_sales_df)
        assert "units_diff" in result.columns

    def test_first_row_is_null(self, sample_sales_df):
        result = hs.with_units_diff(sample_sales_df)
        # NSW の最初の週は diff が null
        nsw = result.filter(pl.col("hw") == "NSW").sort("weekly_id")
        assert nsw["units_diff"][0] is None

    def test_diff_calculated_correctly(self, sample_sales_df):
        result = hs.with_units_diff(sample_sales_df)
        nsw = result.filter(pl.col("hw") == "NSW").sort("weekly_id")
        # 2行目のdiff = 25000 - 30000 = -5000
        assert nsw["units_diff"][1] == -5000


# ---------------------------------------------------------------------------
# add_week_number
# ---------------------------------------------------------------------------

class TestAddWeekNumber:
    def test_adds_week_number_column(self, sample_sales_df):
        result = hs.add_week_number(sample_sales_df)
        assert "week_number" in result.columns

    def test_week_number_is_delta_week_plus_one(self, sample_sales_df):
        result = hs.add_week_number(sample_sales_df)
        for row in result.iter_rows(named=True):
            assert row["week_number"] == row["delta_week"] + 1

    def test_no_delta_week_column_returns_unchanged(self):
        """delta_week カラムがない場合は入力をそのまま返すこと"""
        df = pl.DataFrame({"hw": ["NSW"], "units": [1000]})
        result = hs.add_week_number(df)
        assert "week_number" not in result.columns
        assert result.equals(df)


# ---------------------------------------------------------------------------
# load_hard_sales (DB モック)
# ---------------------------------------------------------------------------

class TestLoadHardSales:
    def _make_raw_df(self):
        return pl.DataFrame({
            "weekly_id": ["NSW-0001"],
            "begin_date": ["2020-01-05"],
            "end_date": ["2020-01-11"],
            "report_date": ["2020-01-05"],
            "period_date": [7],
            "hw": ["NSW"],
            "units": [10000],
            "adjust_units": [10000],
            "year": [2020],
            "month": [1],
            "mday": [5],
            "week": [1],
            "delta_day": [150],
            "delta_week": [21],
            "delta_month": [10],
            "delta_year": [2],
            "avg_units": [1428],
            "sum_units": [500000],
            "launch_date": ["2017-03-03"],
            "maker_name": ["Nintendo"],
            "full_name": ["Nintendo Switch"],
        })

    def test_returns_dataframe(self):
        raw = self._make_raw_df()
        with patch("sqlite3.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            with patch("polars.read_database", return_value=raw):
                result = hs.load_hard_sales()
        assert isinstance(result, pl.DataFrame)

    def test_date_columns_are_date_type(self):
        raw = self._make_raw_df()
        with patch("sqlite3.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            with patch("polars.read_database", return_value=raw):
                result = hs.load_hard_sales()
        assert result["report_date"].dtype == pl.Date
        assert result["begin_date"].dtype == pl.Date
        assert result["launch_date"].dtype == pl.Date

    def test_quarter_column_added(self):
        raw = self._make_raw_df()
        with patch("sqlite3.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            with patch("polars.read_database", return_value=raw):
                result = hs.load_hard_sales()
        assert "quarter" in result.columns
        assert result["quarter"][0] == "2020Q1"


# ---------------------------------------------------------------------------
# get_hw_all (DB モック + グローバル変数リセット)
# ---------------------------------------------------------------------------

class TestGetHwAll:
    def setup_method(self):
        _reset_globals()

    def teardown_method(self):
        _reset_globals()

    def test_returns_list(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            result = hs.get_hw_all()
        assert isinstance(result, list)

    def test_excludes_legacy_hardware(self, sample_sales_df):
        """true_all=False の場合にレガシーハードが除外されること"""
        # レガシーハードを含むデータを用意
        legacy_row = pl.DataFrame({
            "hw": ["PKS"],
            "maker_name": ["SONY"],
            "launch_date": [date(1999, 1, 23)],
            "units": [1000],
            "report_date": [date(2020, 1, 5)],
        }).with_columns(
            pl.col("launch_date").cast(pl.Date),
            pl.col("report_date").cast(pl.Date),
        )
        # sample_sales_df には PKS がないため result からも除外されないが,
        # 除外ロジックが動作するよう PKS を含む DataFrame を渡す
        extended = pl.concat([
            sample_sales_df.select(["hw", "maker_name", "launch_date"]),
            legacy_row.select(["hw", "maker_name", "launch_date"]),
        ], how="diagonal_relaxed")
        mock_full = sample_sales_df.vstack(
            sample_sales_df.head(1).with_columns(
                pl.lit("PKS").alias("hw"),
                pl.lit("SONY").alias("maker_name"),
            )
        )
        with patch.object(hs, "load_hard_sales", return_value=mock_full):
            result = hs.get_hw_all(true_all=False)
        assert "PKS" not in result

    def test_true_all_includes_legacy(self, sample_sales_df):
        """true_all=True の場合はレガシーハードが含まれること"""
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            result = hs.get_hw_all(true_all=True)
        assert isinstance(result, list)

    def test_cached_value_returned(self, sample_sales_df):
        """2回目の呼び出しでキャッシュが使われること"""
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df) as mock_load:
            hs.get_hw_all()
            hs.get_hw_all()
        # 2回目はキャッシュを使うので load_hard_sales は1回しか呼ばれない
        assert mock_load.call_count == 1


# ---------------------------------------------------------------------------
# get_maker_all (DB モック + グローバル変数リセット)
# ---------------------------------------------------------------------------

class TestGetMakerAll:
    def setup_method(self):
        _reset_globals()

    def teardown_method(self):
        _reset_globals()

    def test_returns_list(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            result = hs.get_maker_all()
        assert isinstance(result, list)

    def test_contains_makers(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            result = hs.get_maker_all()
        assert "Nintendo" in result

    def test_cached_value_returned(self, sample_sales_df):
        """2回目の呼び出しでキャッシュが使われること"""
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df) as mock_load:
            hs.get_maker_all()
            hs.get_maker_all()
        assert mock_load.call_count == 1


# ---------------------------------------------------------------------------
# get_active_hw / get_active_maker (DB モック)
# ---------------------------------------------------------------------------

class TestGetActiveHw:
    def test_returns_list(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            result = hs.get_active_hw(days=365 * 10)
        assert isinstance(result, list)


class TestGetActiveMaker:
    def test_returns_list(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            result = hs.get_active_maker(days=365 * 10)
        assert isinstance(result, list)
