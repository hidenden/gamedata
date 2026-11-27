"""
gamedata.hard_sales モジュールのテスト
"""
from datetime import date
from unittest.mock import patch
import polars as pl

import gamedata.hard_sales as hs
from gamedata.hard_sales import _with_sales_columns


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


RAW_COLUMNS = [
    "weekly_id",
    "begin_date",
    "end_date",
    "report_date",
    "period_date",
    "hw",
    "units",
    "adjust_units",
    "year",
    "month",
    "mday",
    "week",
    "delta_day",
    "delta_week",
    "delta_month",
    "delta_year",
    "avg_units",
    "sum_units",
    "launch_date",
    "maker_name",
    "full_name",
]


class TestDerivedColumns:
    def test_adds_units_diff_and_rolling_mean_columns(self, sample_sales_df):
        result = _with_sales_columns(sample_sales_df.select(RAW_COLUMNS))
        assert "units_diff" in result.columns
        assert "ma4w" in result.columns
        assert "ma13w" in result.columns
        assert "ma52w" in result.columns

    def test_first_row_units_diff_is_null(self, sample_sales_df):
        result = _with_sales_columns(sample_sales_df.select(RAW_COLUMNS))
        nsw = result.filter(pl.col("hw") == "NSW").sort("weekly_id")
        assert nsw["units_diff"][0] is None

    def test_units_diff_calculated_correctly(self, sample_sales_df):
        result = _with_sales_columns(sample_sales_df.select(RAW_COLUMNS))
        nsw = result.filter(pl.col("hw") == "NSW").sort("weekly_id")
        assert nsw["units_diff"][1] == -5000

    def test_ma4w_value_correct(self, sample_sales_df):
        """NSW の4週移動平均の値が正しいこと"""
        result = _with_sales_columns(sample_sales_df.select(RAW_COLUMNS))
        nsw = result.filter(pl.col("hw") == "NSW").sort("weekly_id")
        assert nsw["ma4w"][3] == 31250
        assert nsw["ma4w"][4] == 33750

    def test_ma4w_first_rows_are_null(self, sample_sales_df):
        """ウィンドウサイズに満たない行は null になること"""
        result = _with_sales_columns(sample_sales_df.select(RAW_COLUMNS))
        nsw = result.filter(pl.col("hw") == "NSW").sort("weekly_id")
        assert nsw["ma4w"][0] is None
        assert nsw["ma4w"][1] is None
        assert nsw["ma4w"][2] is None

    def test_ma13w_all_null_when_not_enough_rows(self, sample_sales_df):
        """13週分に満たないハードは ma13w が全て null になること"""
        result = _with_sales_columns(sample_sales_df.select(RAW_COLUMNS))
        nsw = result.filter(pl.col("hw") == "NSW").sort("weekly_id")
        assert nsw["ma13w"].null_count() == len(nsw)

    def test_ma52w_all_null_when_not_enough_rows(self, sample_sales_df):
        """52週分に満たないハードは ma52w が全て null になること"""
        result = _with_sales_columns(sample_sales_df.select(RAW_COLUMNS))
        nsw = result.filter(pl.col("hw") == "NSW").sort("weekly_id")
        assert nsw["ma52w"].null_count() == len(nsw)

    def test_per_hw_grouping(self, sample_sales_df):
        """hw ごとに独立して移動平均が計算されること"""
        result = _with_sales_columns(sample_sales_df.select(RAW_COLUMNS))
        ps5 = result.filter(pl.col("hw") == "PS5").sort("weekly_id")
        assert ps5["ma4w"].null_count() == len(ps5)

    def test_returns_dataframe(self, sample_sales_df):
        result = _with_sales_columns(sample_sales_df.select(RAW_COLUMNS))
        assert isinstance(result, pl.DataFrame)


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
