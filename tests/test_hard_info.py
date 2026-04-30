"""
gamedata.hard_info モジュールのテスト
"""
from unittest.mock import patch, MagicMock
import polars as pl
import pytest
from datetime import date

from gamedata import hard_info as hi


class TestHardColors:
    """HARD_COLORS 定数および get_hard_colors/get_hard_color 関数のテスト"""

    def test_hard_colors_is_dict(self):
        """HARD_COLORS が辞書型であること"""
        assert isinstance(hi.HARD_COLORS, dict)

    def test_known_hardware_color(self):
        """既知のハードの色が正しく返ること"""
        assert hi.HARD_COLORS["NSW"] == "#FD1A2D"
        assert hi.HARD_COLORS["PS5"] == "#1d64ff"

    def test_get_hard_colors_returns_list(self):
        """get_hard_colors がリストを返すこと"""
        result = hi.get_hard_colors(["NSW", "PS5"])
        assert isinstance(result, list)
        assert len(result) == 2

    def test_get_hard_colors_known(self):
        """既知ハードの色が HARD_COLORS と一致すること"""
        result = hi.get_hard_colors(["NSW", "PS5"])
        assert result[0] == hi.HARD_COLORS["NSW"]
        assert result[1] == hi.HARD_COLORS["PS5"]

    def test_get_hard_colors_unknown_returns_black(self):
        """未知ハードの色が 'black' であること"""
        result = hi.get_hard_colors(["UNKNOWN_HW"])
        assert result == ["black"]

    def test_get_hard_colors_empty_list(self):
        """空リストを渡すと空リストが返ること"""
        result = hi.get_hard_colors([])
        assert result == []

    def test_get_hard_color_known(self):
        """get_hard_color が既知ハードの色を返すこと"""
        result = hi.get_hard_color("NSW")
        assert result == hi.HARD_COLORS["NSW"]

    def test_get_hard_color_unknown(self):
        """get_hard_color が未知ハードに対して 'black' を返すこと"""
        result = hi.get_hard_color("UNKNOWN")
        assert result == "black"


class TestMakerColors:
    """MAKER_COLORS 定数および get_maker_colors 関数のテスト"""

    def test_maker_colors_is_dict(self):
        """MAKER_COLORS が辞書型であること"""
        assert isinstance(hi.MAKER_COLORS, dict)

    def test_known_maker_color(self):
        """既知メーカーの色が正しく返ること"""
        assert hi.MAKER_COLORS["Nintendo"] == "#E60012"

    def test_get_maker_colors_returns_list(self):
        """get_maker_colors がリストを返すこと"""
        result = hi.get_maker_colors(["Nintendo", "SONY"])
        assert isinstance(result, list)
        assert len(result) == 2

    def test_get_maker_colors_known(self):
        """既知メーカーの色が MAKER_COLORS と一致すること"""
        result = hi.get_maker_colors(["Nintendo", "SONY"])
        assert result[0] == hi.MAKER_COLORS["Nintendo"]
        assert result[1] == hi.MAKER_COLORS["SONY"]

    def test_get_maker_colors_unknown_returns_black(self):
        """未知メーカーの色が 'black' であること"""
        result = hi.get_maker_colors(["UNKNOWN_MAKER"])
        assert result == ["black"]

    def test_get_maker_colors_empty_list(self):
        """空リストを渡すと空リストが返ること"""
        result = hi.get_maker_colors([])
        assert result == []


class TestHardNames:
    """HARD_NAMES 定数および get_hard_names/get_hard_dict 関数のテスト"""

    def test_hard_names_is_dict(self):
        """HARD_NAMES が辞書型であること"""
        assert isinstance(hi.HARD_NAMES, dict)

    def test_known_hardware_name(self):
        """既知ハードの名前が正しく返ること"""
        assert hi.HARD_NAMES["NSW"] == "Nintendo Switch"
        assert hi.HARD_NAMES["PS5"] == "PlayStation5"

    def test_get_hard_names_returns_list(self):
        """get_hard_names がリストを返すこと"""
        result = hi.get_hard_names(["NSW", "PS5"])
        assert isinstance(result, list)
        assert len(result) == 2

    def test_get_hard_names_known(self):
        """既知ハードの名前が HARD_NAMES と一致すること"""
        result = hi.get_hard_names(["NSW", "PS5"])
        assert result[0] == "Nintendo Switch"
        assert result[1] == "PlayStation5"

    def test_get_hard_names_unknown_returns_unknown(self):
        """未知ハードは 'unknown' が返ること"""
        result = hi.get_hard_names(["UNKNOWN_HW"])
        assert result == ["unknown"]

    def test_get_hard_names_empty_list(self):
        """空リストを渡すと空リストが返ること"""
        result = hi.get_hard_names([])
        assert result == []

    def test_get_hard_dict_returns_dict(self):
        """get_hard_dict が辞書を返すこと"""
        result = hi.get_hard_dict()
        assert isinstance(result, dict)

    def test_get_hard_dict_is_hard_names(self):
        """get_hard_dict の戻り値が HARD_NAMES と同一であること"""
        result = hi.get_hard_dict()
        assert result is hi.HARD_NAMES


class TestLoadHardInfo:
    """load_hard_info 関数のテスト (DB をモック)"""

    def _make_mock_df(self):
        return pl.DataFrame({
            "id": ["NSW", "PS5"],
            "launch_date": ["2017-03-03", "2020-11-12"],
            "maker_name": ["Nintendo", "SONY"],
            "full_name": ["Nintendo Switch", "PlayStation5"],
        })

    def test_load_hard_info_returns_dataframe(self):
        """load_hard_info が Polars DataFrame を返すこと"""
        mock_df = self._make_mock_df()
        with patch("sqlite3.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            with patch("polars.read_database", return_value=mock_df):
                result = hi.load_hard_info()
        assert isinstance(result, pl.DataFrame)

    def test_load_hard_info_launch_date_is_date_type(self):
        """load_hard_info の launch_date カラムが Date 型であること"""
        mock_df = self._make_mock_df()
        with patch("sqlite3.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            with patch("polars.read_database", return_value=mock_df):
                result = hi.load_hard_info()
        assert result["launch_date"].dtype == pl.Date
