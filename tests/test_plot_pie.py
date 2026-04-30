"""
gamedata.plot_pie モジュールのテスト
"""
import matplotlib
matplotlib.use("Agg")

from unittest.mock import patch
import polars as pl
import pytest
from matplotlib.figure import Figure

import gamedata.hard_sales as hs
import gamedata.plot_util as pu
import gamedata.plot_pie as pp


@pytest.fixture(autouse=True)
def disable_dispfunc():
    """テスト中は dispfunc を None に設定してポップアップを防ぐ"""
    original = pu.get_dispfunc()
    pu.set_dispfunc(None)
    yield
    pu.set_dispfunc(original)


class TestPlotMakerSharePie:
    """plot_maker_share_pie 関数のテスト"""

    def test_returns_figure_and_dataframe(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pp.plot_maker_share_pie()
        assert isinstance(fig, Figure)
        assert isinstance(df, pl.DataFrame)

    def test_with_year_range(self, sample_sales_df):
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pp.plot_maker_share_pie(begin_year=2020, end_year=2021)
        assert isinstance(fig, Figure)

    def test_single_year_n_equals_1(self, sample_sales_df):
        """n=1 (単年) の場合、axes がリストに変換されること"""
        with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
            fig, df = pp.plot_maker_share_pie(begin_year=2021, end_year=2021)
        assert isinstance(fig, Figure)

    def test_dispfunc_is_called(self, sample_sales_df):
        """dispfunc が None でない場合に呼ばれること"""
        called = []
        pu.set_dispfunc(lambda fig: called.append(fig))
        try:
            with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
                fig, df = pp.plot_maker_share_pie(begin_year=2021, end_year=2021)
            assert len(called) == 1
        finally:
            pu.set_dispfunc(None)

    def test_transparent_mode(self, sample_sales_df):
        pu.set_transparent_mode(True)
        try:
            with patch.object(hs, "load_hard_sales", return_value=sample_sales_df):
                fig, df = pp.plot_maker_share_pie()
            assert isinstance(fig, Figure)
        finally:
            pu.set_transparent_mode(False)
