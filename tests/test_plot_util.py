"""
gamedata.plot_util モジュールのテスト
"""
import pytest
import matplotlib
from unittest.mock import MagicMock, patch
from matplotlib.figure import Figure

import gamedata.plot_util as pu


class TestFigSize:
    """figsize のゲッター・セッターのテスト"""

    def setup_method(self):
        """デフォルト値に戻す"""
        pu.set_figsize(10, 5)

    def test_get_figsize_default(self):
        assert pu.get_figsize() == (10, 5)

    def test_set_figsize(self):
        pu.set_figsize(20, 10)
        assert pu.get_figsize() == (20, 10)

    def test_figsize_is_tuple(self):
        assert isinstance(pu.get_figsize(), tuple)


class TestTransparentMode:
    """transparent mode のゲッター・セッターのテスト"""

    def setup_method(self):
        pu.set_transparent_mode(False)

    def test_default_is_false(self):
        assert pu.get_transparent_mode() is False

    def test_set_transparent_mode_true(self):
        pu.set_transparent_mode(True)
        assert pu.get_transparent_mode() is True

    def test_set_transparent_mode_false(self):
        pu.set_transparent_mode(True)
        pu.set_transparent_mode(False)
        assert pu.get_transparent_mode() is False


class TestAxisLabels:
    """AxisLabels クラスのテスト"""

    def test_default_values(self):
        labels = pu.AxisLabels()
        assert labels.title is None
        assert labels.xlabel is None
        assert labels.ylabel is None
        assert labels.legend is None

    def test_custom_values(self):
        labels = pu.AxisLabels(title="T", xlabel="X", ylabel="Y", legend="L")
        assert labels.title == "T"
        assert labels.xlabel == "X"
        assert labels.ylabel == "Y"
        assert labels.legend == "L"


class TestTickParams:
    """TickParams クラスのテスト"""

    def test_default_values(self):
        tp = pu.TickParams()
        assert tp.axis == "x"
        assert tp.which == "major"
        assert tp.labelsize == 10
        assert tp.rotation is None

    def test_custom_values(self):
        tp = pu.TickParams(axis="y", which="minor", labelsize=8, rotation=45)
        assert tp.axis == "y"
        assert tp.which == "minor"
        assert tp.labelsize == 8
        assert tp.rotation == 45


class TestDispFunc:
    """dispfunc のゲッター・セッターのテスト"""

    def setup_method(self):
        pu.set_dispfunc(pu.auto_dispfunc)

    def test_get_dispfunc_returns_callable(self):
        func = pu.get_dispfunc()
        assert callable(func)

    def test_set_dispfunc(self):
        new_func = lambda fig: None
        pu.set_dispfunc(new_func)
        assert pu.get_dispfunc() is new_func

    def test_set_dispfunc_none(self):
        pu.set_dispfunc(None)
        assert pu.get_dispfunc() is None


class TestAutoDispFunc:
    """auto_dispfunc 関数のテスト"""

    def test_inline_backend_calls_display(self):
        """inline バックエンドの場合 display が呼ばれること"""
        mock_fig = MagicMock(spec=Figure)
        with patch("matplotlib.get_backend", return_value="module://matplotlib_inline.backend_inline"):
            with patch("gamedata.plot_util.display") as mock_display:
                pu.auto_dispfunc(mock_fig)
        mock_display.assert_called_once_with(mock_fig)

    def test_ipympl_backend_calls_plt_show(self):
        """ipympl バックエンドの場合 plt.show が呼ばれること"""
        mock_fig = MagicMock(spec=Figure)
        with patch("matplotlib.get_backend", return_value="module://ipympl.backend_nbagg"):
            with patch("matplotlib.pyplot.show") as mock_show:
                pu.auto_dispfunc(mock_fig)
        mock_show.assert_called_once()

    def test_nbagg_backend_calls_plt_show(self):
        """nbagg バックエンドの場合 plt.show が呼ばれること"""
        mock_fig = MagicMock(spec=Figure)
        with patch("matplotlib.get_backend", return_value="nbagg"):
            with patch("matplotlib.pyplot.show") as mock_show:
                pu.auto_dispfunc(mock_fig)
        mock_show.assert_called_once()

    def test_widget_backend_calls_plt_show(self):
        """widget バックエンドの場合 plt.show が呼ばれること"""
        mock_fig = MagicMock(spec=Figure)
        with patch("matplotlib.get_backend", return_value="widget"):
            with patch("matplotlib.pyplot.show") as mock_show:
                pu.auto_dispfunc(mock_fig)
        mock_show.assert_called_once()

    def test_unknown_backend_prints_message(self, capsys):
        """未知のバックエンドの場合 print が呼ばれること"""
        mock_fig = MagicMock(spec=Figure)
        with patch("matplotlib.get_backend", return_value="Agg"):
            pu.auto_dispfunc(mock_fig)
        captured = capsys.readouterr()
        assert "Unable to output figure" in captured.out
