"""
gamedata.plot_line モジュールのテスト
"""
import matplotlib
matplotlib.use("Agg")

from datetime import datetime, date
from unittest.mock import patch, MagicMock
import polars as pl
import pytest
from matplotlib.figure import Figure

import gamedata.hard_sales as hs
import gamedata.hard_event as he
import gamedata.hard_info as hi
import gamedata.plot_util as pu
import gamedata.plot_line as pl_line


@pytest.fixture(autouse=True)
def disable_dispfunc():
    """テスト中は dispfunc を None に設定してポップアップを防ぐ"""
    original = pu.get_dispfunc()
    pu.set_dispfunc(None)
    yield
    pu.set_dispfunc(original)


class TestWeekfloatToDatetime:
    """_weekfloat_to_datetime 関数のテスト"""

    def test_week_one(self):
        from datetime import datetime
        result = pl_line._weekfloat_to_datetime(1.0)
        assert result == datetime(1970, 1, 4, 0, 0, 0)

    def test_negative_value_raises(self):
        with pytest.raises(ValueError):
            pl_line._weekfloat_to_datetime(-1.0)

    def test_half_week(self):
        from datetime import datetime, timedelta
        result = pl_line._weekfloat_to_datetime(1.5)
        expected = datetime(1970, 1, 4) + timedelta(days=3.5)
        assert result == expected

    def test_large_week_number(self):
        """大きな週番号で正しく変換されること"""
        result = pl_line._weekfloat_to_datetime(2878.0)
        assert result.year == 2025


class TestWeeklyPlotOnAdd:
    """_weekly_plot_on_add 関数のテスト"""

    def _make_sel(self, x, y, label="NSW"):
        sel = MagicMock()
        line = MagicMock()
        line.get_label.return_value = label
        sel.artist = line
        sel.target = (x, y)
        return sel

    def test_large_x_formats_as_date(self):
        """x > 1500 の場合、日付文字列フォーマットになること"""
        sel = self._make_sel(x=2878.0, y=10000)
        pl_line._weekly_plot_on_add(sel)
        call_text = sel.annotation.set_text.call_args[0][0]
        assert "NSW" in call_text
        assert "2025" in call_text

    def test_small_x_formats_as_number(self):
        """x <= 1500 の場合、数値フォーマットになること"""
        sel = self._make_sel(x=100.0, y=10000)
        pl_line._weekly_plot_on_add(sel)
        call_text = sel.annotation.set_text.call_args[0][0]
        assert "100" in call_text


class TestPlotCumulativeSalesByDelta:
    """plot_cumulative_sales_by_delta 関数のテスト"""

    def test_returns_figure_and_dataframe(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pl_line.plot_cumulative_sales_by_delta(hw=["NSW"])
        assert isinstance(fig, Figure)
        assert isinstance(df, pl.DataFrame)

    def test_month_mode(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pl_line.plot_cumulative_sales_by_delta(mode="month")
        assert isinstance(fig, Figure)

    def test_year_mode(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pl_line.plot_cumulative_sales_by_delta(mode="year")
        assert isinstance(fig, Figure)

    def test_with_event_mask(self, sample_sales_df, sample_event_df, sample_info_df):
        """event_mask 指定時に annotation_positioner が呼ばれること"""
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df), \
             patch.object(he, "load_hard_event", return_value=sample_event_df), \
             patch.object(hi, "load_hard_info", return_value=sample_info_df):
            fig, df = pl_line.plot_cumulative_sales_by_delta(
                hw=["NSW"], event_mask=he.EVENT_MASK_ALL
            )
        assert isinstance(fig, Figure)

    def test_with_grid(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pl_line.plot_cumulative_sales_by_delta(xgrid=10, ygrid=100000)
        assert isinstance(fig, Figure)


class TestPlotSales:
    """plot_sales 関数のテスト"""

    def test_week_mode(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pl_line.plot_sales(mode="week")
        assert isinstance(fig, Figure)

    def test_month_mode(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pl_line.plot_sales(mode="month")
        assert isinstance(fig, Figure)

    def test_quarter_mode(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pl_line.plot_sales(mode="quarter")
        assert isinstance(fig, Figure)

    def test_year_mode(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pl_line.plot_sales(mode="year")
        assert isinstance(fig, Figure)

    def test_with_event_mask_week_mode(self, sample_sales_df, sample_event_df):
        """event_mask + mode="week" で annotation_positioner が有効になること"""
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df), \
             patch.object(he, "load_hard_event", return_value=sample_event_df):
            fig, df = pl_line.plot_sales(
                hw=["NSW"], event_mask=he.EVENT_MASK_ALL, mode="week"
            )
        assert isinstance(fig, Figure)

    def test_with_event_mask_month_mode_prints_warning(self, sample_sales_df, capsys):
        """event_mask + mode != "week" の場合にワーニングが出力されること"""
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pl_line.plot_sales(
                hw=["NSW"], event_mask=he.EVENT_MASK_ALL, mode="month"
            )
        captured = capsys.readouterr()
        assert "Warning" in captured.out

    def test_area_mode(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pl_line.plot_sales(hw=["NSW", "PS5"], area=True)
        assert isinstance(fig, Figure)

    def test_with_ticklabelsize(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pl_line.plot_sales(ticklabelsize=8)
        assert isinstance(fig, Figure)

    def test_transparent_mode(self, sample_sales_df):
        pu.set_transparent_mode(True)
        try:
            with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
                fig, df = pl_line.plot_sales()
            assert isinstance(fig, Figure)
        finally:
            pu.set_transparent_mode(False)


class TestPlotSalesByDelta:
    """plot_sales_by_delta 関数のテスト"""

    def test_week_mode(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pl_line.plot_sales_by_delta(mode="week")
        assert isinstance(fig, Figure)

    def test_month_mode(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pl_line.plot_sales_by_delta(mode="month")
        assert isinstance(fig, Figure)

    def test_year_mode(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pl_line.plot_sales_by_delta(mode="year")
        assert isinstance(fig, Figure)

    def test_with_event_mask_week(self, sample_sales_df, sample_event_df, sample_info_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df), \
             patch.object(he, "load_hard_event", return_value=sample_event_df), \
             patch.object(hi, "load_hard_info", return_value=sample_info_df):
            fig, df = pl_line.plot_sales_by_delta(
                hw=["NSW"], event_mask=he.EVENT_MASK_ALL, mode="week"
            )
        assert isinstance(fig, Figure)

    def test_with_event_mask_non_week_prints_warning(self, sample_sales_df, capsys):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pl_line.plot_sales_by_delta(
                event_mask=he.EVENT_MASK_ALL, mode="month"
            )
        captured = capsys.readouterr()
        assert "Warning" in captured.out


class TestPlotSalesWithOffset:
    """plot_sales_with_offset 関数のテスト"""

    def test_returns_figure_and_dataframe(self, sample_sales_df):
        hw_periods = [{"hw": "NSW", "begin": datetime(2020, 1, 1)}]
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pl_line.plot_sales_with_offset(hw_periods=hw_periods)
        assert isinstance(fig, Figure)
        assert isinstance(df, pl.DataFrame)


class TestPlotCumulativeSales:
    """plot_cumulative_sales 関数のテスト"""

    def test_week_mode(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pl_line.plot_cumulative_sales(hw=["NSW"], mode="week")
        assert isinstance(fig, Figure)

    def test_month_mode(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pl_line.plot_cumulative_sales(hw=["NSW"], mode="month")
        assert isinstance(fig, Figure)

    def test_year_mode(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pl_line.plot_cumulative_sales(hw=["NSW"], mode="year")
        assert isinstance(fig, Figure)

    def test_with_event_mask_week(self, sample_sales_df, sample_event_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df), \
             patch.object(he, "load_hard_event", return_value=sample_event_df):
            fig, df = pl_line.plot_cumulative_sales(
                hw=["NSW"], event_mask=he.EVENT_MASK_ALL, mode="week"
            )
        assert isinstance(fig, Figure)

    def test_with_event_mask_month_prints_warning(self, sample_sales_df, capsys):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pl_line.plot_cumulative_sales(
                hw=["NSW"], event_mask=he.EVENT_MASK_ALL, mode="month"
            )
        captured = capsys.readouterr()
        assert "Warning" in captured.out


class TestPlotCumsumDiffs:
    """plot_cumsum_diffs 関数のテスト"""

    def test_returns_figure_and_dataframe(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pl_line.plot_cumsum_diffs([("NSW", "PS5")])
        assert isinstance(fig, Figure)
        assert isinstance(df, pl.DataFrame)


class TestPlotSalesPaseDiff:
    """plot_sales_pase_diff 関数のテスト"""

    def _make_shared_delta_df(self):
        """NSW と PS5 が同一 delta_week を持つテスト用 DataFrame を作成する (両方の発売日を同じにする)"""
        from datetime import date
        common_launch = date(2020, 1, 5)
        base_dates = [date(2020, 1, 5), date(2020, 1, 12), date(2020, 1, 19)]
        rows = []
        for i, rd in enumerate(base_dates):
            bd = date(rd.year, rd.month, rd.day - 6 if rd.day > 6 else 1)
            delta = (rd - common_launch).days
            delta_week = delta // 7
            for hw, maker, full in [
                ("NSW", "Nintendo", "Nintendo Switch"),
                ("PS5", "SONY", "PlayStation5"),
            ]:
                sum_u = (i + 1) * 10000 if hw == "NSW" else (i + 1) * 8000
                rows.append({
                    "weekly_id": f"{hw}-{i+1:04d}",
                    "begin_date": bd,
                    "end_date": rd,
                    "report_date": rd,
                    "quarter": "2020Q1",
                    "period_date": 7,
                    "hw": hw,
                    "units": 10000,
                    "adjust_units": 10000,
                    "year": rd.year,
                    "month": rd.month,
                    "mday": rd.day,
                    "week": 1,
                    "delta_day": delta,
                    "delta_week": delta_week,
                    "delta_month": 0,
                    "delta_year": 0,
                    "avg_units": 1428,
                    "sum_units": sum_u,
                    "launch_date": common_launch,
                    "maker_name": maker,
                    "full_name": full,
                })
        return pl.DataFrame(rows).with_columns([
            pl.col("begin_date").cast(pl.Date),
            pl.col("end_date").cast(pl.Date),
            pl.col("report_date").cast(pl.Date),
            pl.col("launch_date").cast(pl.Date),
        ])

    def test_returns_figure_and_dataframe(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pl_line.plot_sales_pase_diff("NSW", "PS5")
        assert isinstance(fig, Figure)
        assert isinstance(df, pl.DataFrame)

    def test_invalid_base_hw_in_combine_raises(self):
        """combine_report_dates で存在しないハードが検出された場合に ValueError が発生すること"""
        shared_df = self._make_shared_delta_df()
        # NSW のない DataFrame を 2回目の呼び出しに使う
        no_nsw_df = shared_df.filter(pl.col("hw") == "PS5")
        with patch.object(hs, "load_hard_sales", side_effect=[shared_df, no_nsw_df]):
            with pytest.raises(ValueError, match="Invalid hardware"):
                pl_line.plot_sales_pase_diff("NSW", "PS5")

    def test_missing_delta_weeks_raises(self):
        """combine_report_dates で delta_week が欠損している場合に ValueError が発生すること"""
        shared_df = self._make_shared_delta_df()
        min_week = shared_df.filter(pl.col("hw") == "NSW")["delta_week"].min()
        # NSW は delta_week=min_week のみ残す (他の週を除外)
        truncated_df = shared_df.filter(
            (pl.col("hw") != "NSW") |
            ((pl.col("hw") == "NSW") & (pl.col("delta_week") == min_week))
        )
        with patch.object(hs, "load_hard_sales", side_effect=[shared_df, truncated_df]):
            with pytest.raises(ValueError, match="does not have all required"):
                pl_line.plot_sales_pase_diff("NSW", "PS5")

    def test_with_ymax_and_ybottom(self, sample_sales_df):
        """ymax と ybottom が設定されること"""
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pl_line.plot_sales_pase_diff("NSW", "PS5", ymax=100000, ybottom=-100000)
        assert isinstance(fig, Figure)


class TestPlotSalesDispFunc:
    """_plot_sales の dispfunc ブランチのテスト"""

    def test_dispfunc_is_called(self, sample_sales_df):
        """dispfunc が None でない場合に呼ばれること"""
        called = []
        pu.set_dispfunc(lambda fig: called.append(fig))
        try:
            with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
                fig, df = pl_line.plot_sales(hw=["NSW"])
            assert len(called) == 1
        finally:
            pu.set_dispfunc(None)

    def test_ymax_parameter(self, sample_sales_df):
        """ymax パラメータが設定されること"""
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pl_line.plot_sales(hw=["NSW"], ymax=500000)
        assert isinstance(fig, Figure)
