"""
gamedata.hard_event モジュールのテスト
"""
from datetime import date, datetime
from unittest.mock import patch, MagicMock
import polars as pl
import pytest

from gamedata import hard_event as he


class TestLoadHardEvent:
    """load_hard_event 関数のテスト (DB をモック)"""

    def _make_raw_df(self):
        return pl.DataFrame({
            "event_date": ["2020-01-05", "2020-11-15"],
            "hw": ["NSW", "PS5"],
            "event_name": ["NSW ソフト発売", "PS5 発売"],
            "event_type": ["soft", "hard"],
            "priority": [1.0, 1.0],
        })

    def test_returns_dataframe(self):
        raw = self._make_raw_df()
        with patch("sqlite3.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            with patch("polars.read_database", return_value=raw):
                result = he.load_hard_event()
        assert isinstance(result, pl.DataFrame)

    def test_event_date_is_date_type(self):
        raw = self._make_raw_df()
        with patch("sqlite3.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            with patch("polars.read_database", return_value=raw):
                result = he.load_hard_event()
        assert result["event_date"].dtype == pl.Date

    def test_report_date_column_added(self):
        raw = self._make_raw_df()
        with patch("sqlite3.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            with patch("polars.read_database", return_value=raw):
                result = he.load_hard_event()
        assert "report_date" in result.columns

    def test_sunday_event_report_date_same_as_event_date(self):
        """event_date が日曜の場合、report_date = event_date であること"""
        # 2020-01-05 は日曜日
        raw = pl.DataFrame({
            "event_date": ["2020-01-05"],
            "hw": ["NSW"],
            "event_name": ["test"],
            "event_type": ["soft"],
            "priority": [1.0],
        })
        with patch("sqlite3.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            with patch("polars.read_database", return_value=raw):
                result = he.load_hard_event()
        assert result["report_date"][0] == date(2020, 1, 5)

    def test_non_sunday_event_report_date_next_sunday(self):
        """event_date が日曜でない場合、report_date が直近の日曜になること"""
        # 2020-01-06 (月曜) → 次の日曜は 2020-01-12
        raw = pl.DataFrame({
            "event_date": ["2020-01-06"],
            "hw": ["NSW"],
            "event_name": ["test"],
            "event_type": ["soft"],
            "priority": [1.0],
        })
        with patch("sqlite3.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            with patch("polars.read_database", return_value=raw):
                result = he.load_hard_event()
        assert result["report_date"][0] == date(2020, 1, 12)


class TestEventMasks:
    """EventMasks 定数のテスト"""

    def test_event_mask_middle(self):
        assert isinstance(he.EVENT_MASK_MIDDLE, dict)
        assert "hard" in he.EVENT_MASK_MIDDLE

    def test_event_mask_long(self):
        assert isinstance(he.EVENT_MASK_LONG, dict)
        assert "hard" in he.EVENT_MASK_LONG

    def test_event_mask_short(self):
        assert isinstance(he.EVENT_MASK_SHORT, dict)
        assert "hard" in he.EVENT_MASK_SHORT

    def test_event_mask_all(self):
        assert isinstance(he.EVENT_MASK_ALL, dict)
        assert "hard" in he.EVENT_MASK_ALL


class TestMaskEvent:
    """mask_event 関数のテスト"""

    def test_returns_dataframe(self, sample_event_df):
        result = he.mask_event(sample_event_df, he.EVENT_MASK_MIDDLE)
        assert isinstance(result, pl.DataFrame)

    def test_filters_by_event_type(self, sample_event_df):
        """event_mask に含まれない event_type は除外されること"""
        mask = {"soft": 5.0}  # soft のみ
        result = he.mask_event(sample_event_df, mask)
        assert all(et == "soft" for et in result["event_type"].to_list())

    def test_filters_by_priority(self, sample_event_df):
        """priority が閾値を超えるものは除外されること"""
        mask = {"sale": 2.0}  # sale の priority <= 2.0 のみ
        result = he.mask_event(sample_event_df, mask)
        # priority=3.0 の XSX sale は除外される
        for row in result.iter_rows(named=True):
            assert row["priority"] <= 2.0

    def test_all_mask_returns_all_types(self, sample_event_df):
        """EVENT_MASK_ALL では全てのイベントが通過すること"""
        result = he.mask_event(sample_event_df, he.EVENT_MASK_ALL)
        assert result.height > 0

    def test_mask_priority_column_not_in_result(self, sample_event_df):
        """mask_priority カラムが結果に含まれないこと"""
        result = he.mask_event(sample_event_df, he.EVENT_MASK_MIDDLE)
        assert "mask_priority" not in result.columns


class TestDeltaEvent:
    """delta_event 関数のテスト"""

    def test_returns_dataframe(self, sample_event_df, sample_info_df):
        result = he.delta_event(sample_event_df, sample_info_df)
        assert isinstance(result, pl.DataFrame)

    def test_has_delta_week_column(self, sample_event_df, sample_info_df):
        result = he.delta_event(sample_event_df, sample_info_df)
        assert "delta_week" in result.columns

    def test_delta_week_is_non_negative(self, sample_event_df, sample_info_df):
        result = he.delta_event(sample_event_df, sample_info_df)
        for val in result["delta_week"].to_list():
            assert val is None or val >= 0

    def test_has_expected_columns(self, sample_event_df, sample_info_df):
        result = he.delta_event(sample_event_df, sample_info_df)
        expected_cols = {"report_date", "event_date", "hw", "event_name", "event_type", "priority", "delta_week"}
        assert expected_cols.issubset(set(result.columns))


class TestFilterEvent:
    """filter_event 関数のテスト"""

    def test_returns_dataframe(self, sample_event_df):
        result = he.filter_event(sample_event_df, event_mask=he.EVENT_MASK_ALL)
        assert isinstance(result, pl.DataFrame)

    def test_start_date_filter(self, sample_event_df):
        start = date(2021, 1, 1)
        result = he.filter_event(sample_event_df, start_date=start, event_mask=he.EVENT_MASK_ALL)
        assert all(d >= start for d in result["report_date"].to_list())

    def test_end_date_filter(self, sample_event_df):
        end = date(2020, 12, 31)
        result = he.filter_event(sample_event_df, end_date=end, event_mask=he.EVENT_MASK_ALL)
        assert all(d <= end for d in result["report_date"].to_list())

    def test_hw_filter(self, sample_event_df):
        result = he.filter_event(sample_event_df, hw=["NSW"], event_mask=he.EVENT_MASK_ALL)
        assert all(hw == "NSW" for hw in result["hw"].to_list())

    def test_empty_hw_list_no_filter(self, sample_event_df):
        """hw=[] の場合はフィルタなしであること"""
        result_no_filter = he.filter_event(sample_event_df, event_mask=he.EVENT_MASK_ALL)
        result_empty_hw = he.filter_event(sample_event_df, hw=[], event_mask=he.EVENT_MASK_ALL)
        assert result_no_filter.height == result_empty_hw.height


class TestAddEventPositions:
    """add_event_positions 関数のテスト"""

    def test_returns_dataframe(self, sample_event_df, sample_sales_df):
        pivot_df = sample_sales_df.pivot(
            index="report_date", on="hw", values="units", aggregate_function="last"
        ).sort("report_date")
        result = he.add_event_positions(sample_event_df, pivot_df, event_mask=he.EVENT_MASK_ALL)
        assert isinstance(result, pl.DataFrame)

    def test_has_x_pos_and_y_pos(self, sample_event_df, sample_sales_df):
        pivot_df = sample_sales_df.pivot(
            index="report_date", on="hw", values="units", aggregate_function="last"
        ).sort("report_date")
        result = he.add_event_positions(sample_event_df, pivot_df, event_mask=he.EVENT_MASK_ALL)
        assert "x_pos" in result.columns
        assert "y_pos" in result.columns

    def test_empty_result_when_no_match(self, sample_event_df):
        """report_date がピボットに存在しない場合、空 DataFrame が返ること"""
        pivot_df = pl.DataFrame({
            "report_date": [date(1990, 1, 1)],
            "NSW": [100],
        }).with_columns(pl.col("report_date").cast(pl.Date))
        result = he.add_event_positions(sample_event_df, pivot_df, event_mask=he.EVENT_MASK_ALL)
        assert result.height == 0

    def test_empty_result_when_hw_not_in_pivot(self, sample_event_df, sample_sales_df):
        """pivot_df に hw カラムが存在しない場合のハンドリング"""
        # NSW のみのピボットに PS5 のイベントがある場合
        pivot_df = sample_sales_df.filter(pl.col("hw") == "NSW").pivot(
            index="report_date", on="hw", values="units", aggregate_function="last"
        ).sort("report_date")
        # sample_event_df には NSW, PS5, XSX のイベントがあるが NSW のみのピボットなので
        # PS5, XSX のイベントは除外される
        result = he.add_event_positions(sample_event_df, pivot_df, event_mask=he.EVENT_MASK_ALL)
        assert isinstance(result, pl.DataFrame)


class TestAddEventPositionsDelta:
    """add_event_positions_delta 関数のテスト"""

    def test_returns_dataframe(self, sample_event_df_with_delta, sample_sales_df):
        pivot_delta_df = sample_sales_df.pivot(
            index="delta_week", on="hw", values="sum_units", aggregate_function="last"
        ).sort("delta_week")
        result = he.add_event_positions_delta(
            sample_event_df_with_delta, pivot_delta_df, event_mask=he.EVENT_MASK_ALL
        )
        assert isinstance(result, pl.DataFrame)

    def test_has_x_pos_and_y_pos(self, sample_event_df_with_delta, sample_sales_df):
        pivot_delta_df = sample_sales_df.pivot(
            index="delta_week", on="hw", values="sum_units", aggregate_function="last"
        ).sort("delta_week")
        result = he.add_event_positions_delta(
            sample_event_df_with_delta, pivot_delta_df, event_mask=he.EVENT_MASK_ALL
        )
        assert "x_pos" in result.columns
        assert "y_pos" in result.columns

    def test_empty_result_when_no_match(self, sample_event_df_with_delta):
        """delta_week がピボットに存在しない場合、空 DataFrame が返ること"""
        pivot_delta_df = pl.DataFrame({
            "delta_week": [99999],
            "NSW": [100],
        }).with_columns(pl.col("delta_week").cast(pl.Int32))
        result = he.add_event_positions_delta(
            sample_event_df_with_delta, pivot_delta_df, event_mask=he.EVENT_MASK_ALL
        )
        assert result.height == 0
