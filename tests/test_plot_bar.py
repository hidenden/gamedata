"""
gamedata.plot_bar モジュールのテスト
"""
import matplotlib
matplotlib.use("Agg")  # テスト用にAggバックエンドを使用

from datetime import datetime, date
from unittest.mock import patch, MagicMock
import pandas as pd
import polars as pl
import pytest
from matplotlib.figure import Figure

import gamedata.hard_sales as hs
import gamedata.plot_util as pu
import gamedata.plot_bar as pb


@pytest.fixture(autouse=True)
def disable_dispfunc():
    """テスト中は dispfunc を None に設定してポップアップを防ぐ"""
    original = pu.get_dispfunc()
    pu.set_dispfunc(None)
    yield
    pu.set_dispfunc(original)


class TestBarOnAdd:
    """_bar_on_add 関数のテスト"""

    def _make_sel(self, x_pos, width, height, facecolor):
        sel = MagicMock()
        rect = MagicMock()
        ax = MagicMock()
        rect.axes = ax
        rect.get_x.return_value = x_pos
        rect.get_width.return_value = width
        rect.get_height.return_value = height
        rect.get_facecolor.return_value = facecolor
        sel.artist = rect
        return sel

    def test_with_int_month_index(self):
        """index が月（int <= 12）の場合、月ラベルになること"""
        df = pd.DataFrame({"units": [100, 200]}, index=[1, 2])
        sel = self._make_sel(x_pos=0.0, width=0.8, height=100, facecolor=(1, 0, 0, 1))
        color2label = {(1, 0, 0, 1): "NSW"}
        pb._bar_on_add(sel, df, color2label)
        call_text = sel.annotation.set_text.call_args[0][0]
        assert "月" in call_text

    def test_with_int_year_index(self):
        """index が年（int > 12）の場合、年ラベルになること"""
        df = pd.DataFrame({"units": [100]}, index=[2020])
        sel = self._make_sel(x_pos=0.0, width=0.8, height=100, facecolor=(1, 0, 0, 1))
        color2label = {(1, 0, 0, 1): "NSW"}
        pb._bar_on_add(sel, df, color2label)
        call_text = sel.annotation.set_text.call_args[0][0]
        assert "年" in call_text

    def test_with_string_index(self):
        """index が文字列の場合"""
        df = pd.DataFrame({"units": [100]}, index=["NSW"])
        sel = self._make_sel(x_pos=0.0, width=0.8, height=100, facecolor=(1, 0, 0, 1))
        color2label = {}
        pb._bar_on_add(sel, df, color2label)
        sel.annotation.set_text.assert_called_once()

    def test_with_out_of_range_index(self):
        """idx が index の範囲外の場合、x_label が空文字になること"""
        df = pd.DataFrame({"units": [100]}, index=[0])
        # idx = int(10 + 0.8/2 + 0.5) = 10+0.9 -> int(10.9) = 10
        sel = self._make_sel(x_pos=10.0, width=0.8, height=100, facecolor=(1, 0, 0, 1))
        color2label = {(1, 0, 0, 1): "NSW"}
        pb._bar_on_add(sel, df, color2label)
        call_text = sel.annotation.set_text.call_args[0][0]
        # x_label == "" なので見出し部分は "NSW: \n..."
        assert "NSW" in call_text

    def test_unknown_color_series_is_unknown(self):
        """color が color2label に存在しない場合、'unknown' が返ること"""
        df = pd.DataFrame({"units": [100]}, index=[0])
        sel = self._make_sel(x_pos=0.0, width=0.8, height=100, facecolor=(0, 0, 0, 1))
        color2label = {}
        pb._bar_on_add(sel, df, color2label)
        call_text = sel.annotation.set_text.call_args[0][0]
        assert "unknown" in call_text


class TestPlotMonthlyBarByYear:
    """plot_monthly_bar_by_year 関数のテスト"""

    def test_returns_figure_and_dataframe(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pb.plot_monthly_bar_by_year("NSW")
        assert isinstance(fig, Figure)
        assert isinstance(df, pl.DataFrame)

    def test_with_ticklabelsize(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pb.plot_monthly_bar_by_year("NSW", ticklabelsize=8)
        assert isinstance(fig, Figure)

    def test_with_ymax(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pb.plot_monthly_bar_by_year("NSW", ymax=50000)
        assert isinstance(fig, Figure)

    def test_with_transparent_mode(self, sample_sales_df):
        pu.set_transparent_mode(True)
        try:
            with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
                fig, df = pb.plot_monthly_bar_by_year("NSW")
            assert isinstance(fig, Figure)
        finally:
            pu.set_transparent_mode(False)


class TestPlotQuarterlyBarByYear:
    """plot_quarterly_bar_by_year 関数のテスト"""

    def test_returns_figure_and_dataframe(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pb.plot_quarterly_bar_by_year("NSW")
        assert isinstance(fig, Figure)
        assert isinstance(df, pl.DataFrame)

    def test_with_ticklabelsize(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pb.plot_quarterly_bar_by_year("NSW", ticklabelsize=8)
        assert isinstance(fig, Figure)


class TestPlotMonthlyBarByHard:
    """plot_monthly_bar_by_hard 関数のテスト"""

    def test_returns_figure_and_dataframe(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pb.plot_monthly_bar_by_hard(["NSW", "PS5"])
        assert isinstance(fig, Figure)
        assert isinstance(df, pl.DataFrame)

    def test_stacked_mode(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pb.plot_monthly_bar_by_hard(["NSW", "PS5"], stacked=True)
        assert isinstance(fig, Figure)

    def test_with_ticklabelsize(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pb.plot_monthly_bar_by_hard(["NSW"], ticklabelsize=8)
        assert isinstance(fig, Figure)


class TestPlotQuarterlyBarByHard:
    """plot_quarterly_bar_by_hard 関数のテスト"""

    def test_returns_figure_and_dataframe(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pb.plot_quarterly_bar_by_hard(["NSW", "PS5"])
        assert isinstance(fig, Figure)
        assert isinstance(df, pl.DataFrame)

    def test_stacked_mode(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pb.plot_quarterly_bar_by_hard(["NSW"], stacked=True)
        assert isinstance(fig, Figure)

    def test_with_ticklabelsize(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pb.plot_quarterly_bar_by_hard(["NSW"], ticklabelsize=8)
        assert isinstance(fig, Figure)


class TestPlotMonthlyBarByHardYear:
    """plot_monthly_bar_by_hard_year 関数のテスト"""

    def test_returns_figure_and_dataframe(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pb.plot_monthly_bar_by_hard_year([("NSW", 2020)])
        assert isinstance(fig, Figure)
        assert isinstance(df, pl.DataFrame)

    def test_stacked_mode(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pb.plot_monthly_bar_by_hard_year([("NSW", 2020)], stacked=True)
        assert isinstance(fig, Figure)

    def test_with_ticklabelsize(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pb.plot_monthly_bar_by_hard_year([("NSW", 2020)], ticklabelsize=8)
        assert isinstance(fig, Figure)


class TestPlotQuarterlyBarByHardYear:
    """plot_quarterly_bar_by_hard_year 関数のテスト"""

    def test_returns_figure_and_dataframe(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pb.plot_quarterly_bar_by_hard_year([("NSW", 2020)])
        assert isinstance(fig, Figure)
        assert isinstance(df, pl.DataFrame)

    def test_with_ticklabelsize(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pb.plot_quarterly_bar_by_hard_year([("NSW", 2020)], ticklabelsize=8)
        assert isinstance(fig, Figure)


class TestPlotYearlyBarByHard:
    """plot_yearly_bar_by_hard 関数のテスト"""

    def test_returns_figure_and_dataframe(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pb.plot_yearly_bar_by_hard(["NSW", "PS5"])
        assert isinstance(fig, Figure)
        assert isinstance(df, pl.DataFrame)

    def test_stacked_mode(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pb.plot_yearly_bar_by_hard(["NSW"], stacked=True)
        assert isinstance(fig, Figure)

    def test_with_ticklabelsize(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pb.plot_yearly_bar_by_hard(["NSW"], ticklabelsize=8)
        assert isinstance(fig, Figure)


class TestPlotYearlyBarByMonth:
    """plot_yearly_bar_by_month 関数のテスト"""

    def test_returns_figure_and_dataframe(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pb.plot_yearly_bar_by_month(month=1)
        assert isinstance(fig, Figure)
        assert isinstance(df, pl.DataFrame)

    def test_with_ticklabelsize(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pb.plot_yearly_bar_by_month(month=1, ticklabelsize=8)
        assert isinstance(fig, Figure)


class TestPlotDeltaYearlyBar:
    """plot_delta_yearly_bar 関数のテスト"""

    def test_returns_figure_and_dataframe(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pb.plot_delta_yearly_bar(["NSW"])
        assert isinstance(fig, Figure)
        assert isinstance(df, pl.DataFrame)

    def test_with_delta_begin_end(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pb.plot_delta_yearly_bar(["NSW"], delta_begin=0, delta_end=5)
        assert isinstance(fig, Figure)

    def test_with_ticklabelsize(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pb.plot_delta_yearly_bar(["NSW"], ticklabelsize=8)
        assert isinstance(fig, Figure)


class TestPlotMakerShareBar:
    """plot_maker_share_bar 関数のテスト"""

    def test_returns_figure_and_dataframe(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pb.plot_maker_share_bar()
        assert isinstance(fig, Figure)
        assert isinstance(df, pl.DataFrame)

    def test_with_date_range(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pb.plot_maker_share_bar(begin=date(2020, 1, 1), end=date(2021, 12, 31))
        assert isinstance(fig, Figure)

    def test_with_ticklabelsize(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pb.plot_maker_share_bar(ticklabelsize=8)
        assert isinstance(fig, Figure)


class TestPlotBarShowValues:
    """_plot_bar の show_values ブランチのテスト"""

    def _make_data_aggregator(self, sample_sales_df):
        import polars as pl
        import pandas as pd

        def data_aggregator(hard_sales_df):
            return pl.DataFrame({
                "year": [2020, 2021],
                "Nintendo": [100000, 80000],
            })
        return data_aggregator

    def test_show_values_stacked(self, sample_sales_df):
        """stacked=True + show_values=True のブランチ"""
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            # plot_maker_share_bar は stacked=True, show_values=True を使う
            fig, df = pb.plot_maker_share_bar()
        assert isinstance(fig, Figure)

    def test_show_values_non_stacked_horizontal(self, sample_sales_df):
        """stacked=False + show_values=True + horizontal=True のブランチ"""
        data_aggregator = self._make_data_aggregator(sample_sales_df)
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pb._plot_bar(
                data_aggregator=data_aggregator,
                stacked=False,
                horizontal=True,
                show_values=True,
            )
        assert isinstance(fig, Figure)

    def test_show_values_non_stacked_vertical(self, sample_sales_df):
        """stacked=False + show_values=True + horizontal=False のブランチ"""
        data_aggregator = self._make_data_aggregator(sample_sales_df)
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pb._plot_bar(
                data_aggregator=data_aggregator,
                stacked=False,
                horizontal=False,
                show_values=True,
            )
        assert isinstance(fig, Figure)

    def test_dispfunc_is_called(self, sample_sales_df):
        """dispfunc が None でない場合に呼ばれること"""
        called_with = []
        pu.set_dispfunc(lambda fig: called_with.append(fig))
        try:
            with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
                fig, df = pb.plot_monthly_bar_by_year("NSW")
            assert len(called_with) == 1
        finally:
            pu.set_dispfunc(None)

    def test_on_add_closure(self, sample_sales_df):
        """mplcursors の on_add クロージャが _bar_on_add を呼ぶこと"""
        captured_callbacks = {}

        class MockCursor:
            def connect(self, event_name):
                def decorator(fn):
                    captured_callbacks[event_name] = fn
                    return fn
                return decorator

        with patch("gamedata.plot_bar.mplcursors.cursor", return_value=MockCursor()):
            with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
                fig, df = pb.plot_monthly_bar_by_year("NSW")

        # クロージャを手動で呼び出す
        assert "add" in captured_callbacks
        sel = MagicMock()
        rect = MagicMock()
        rect.get_x.return_value = 0.0
        rect.get_width.return_value = 0.8
        rect.get_height.return_value = 1000.0
        rect.get_facecolor.return_value = (1, 0, 0, 1)
        sel.artist = rect
        captured_callbacks["add"](sel)
        sel.annotation.set_text.assert_called_once()
